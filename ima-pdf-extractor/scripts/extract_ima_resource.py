from __future__ import annotations

import argparse
import hashlib
import mimetypes
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from extract_ima_pdf import (
    URL_PATTERN,
    decode_query_component,
    newest_session,
    query_value_raw,
    read_session,
    request_safe_url,
    safe_title,
    term_offsets,
)


IMA_ROOT_HOST = "ima.qq.com"
HTML_PREFIX = re.compile(br"^\s*(?:<!doctype\s+html|<html\b)", re.IGNORECASE)


@dataclass(frozen=True)
class Candidate:
    distance: int
    offset: int
    title: str
    origin_url: str
    resource_path: str
    resource_name: str


def is_ima_host(host: str | None) -> bool:
    if not host:
        return False
    folded = host.casefold().rstrip(".")
    return folded == IMA_ROOT_HOST or folded.endswith(f".{IMA_ROOT_HOST}")


def normalized_extension(value: str | None) -> str | None:
    if value is None:
        return None
    extension = value.strip().casefold()
    if not extension:
        return None
    return extension if extension.startswith(".") else f".{extension}"


def candidate_name(path: str, title: str) -> str:
    name = urllib.parse.unquote(Path(path).name)
    return name or title or "unnamed-resource"


def extract_candidates(
    data: bytes,
    offsets: list[tuple[int, str]],
    extension: str | None,
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for match in URL_PATTERN.finditer(data):
        distance = min(abs(match.start() - offset) for offset, _ in offsets)
        if distance > 10_000:
            continue
        outer = urllib.parse.urlsplit(match.group(0).decode("utf-8"))
        for raw_origin in query_value_raw(outer.query, "originUrl"):
            origin_bytes = urllib.parse.unquote_to_bytes(raw_origin.replace("+", " "))
            origin = urllib.parse.quote_from_bytes(
                origin_bytes,
                safe="%:/?&=+#@!$'()*,-._~;[]",
            )
            inner = urllib.parse.urlsplit(origin)
            if inner.scheme.casefold() != "https" or not is_ima_host(inner.hostname):
                continue
            raw_titles = query_value_raw(inner.query, "media_title")
            title = decode_query_component(raw_titles[0]) if raw_titles else ""
            name = candidate_name(inner.path, title)
            suffix = Path(urllib.parse.unquote(inner.path)).suffix.casefold()
            if extension and suffix != extension:
                continue
            candidates.append(
                Candidate(distance, match.start(), title, origin, inner.path, name)
            )
    return candidates


def choose_candidate(candidates: list[Candidate], terms: list[str]) -> Candidate:
    folded_terms = [term.casefold() for term in terms]

    def title_score(candidate: Candidate) -> int:
        haystack = f"{candidate.title} {candidate.resource_name}".casefold()
        return sum(len(term) for term in folded_terms if term in haystack)

    return min(
        candidates,
        key=lambda candidate: (
            -title_score(candidate),
            candidate.distance,
            -candidate.offset,
        ),
    )


def signed_urls_for_resource(
    candidates: list[Candidate], resource_path: str
) -> list[str]:
    urls: list[str] = []
    for candidate in sorted(candidates, key=lambda item: item.offset, reverse=True):
        if candidate.resource_path == resource_path and candidate.origin_url not in urls:
            urls.append(candidate.origin_url)
    return urls


def validate_body(body: bytes, content_type: str, extension: str) -> list[str]:
    if not body:
        raise RuntimeError("The resource response was empty")
    checks: list[str] = []
    media_type = content_type.partition(";")[0].strip().casefold()

    if extension == ".pdf":
        if not body.startswith(b"%PDF-"):
            raise RuntimeError("The selected .pdf response has no PDF header")
        checks.append("pdf_header")
    elif extension in {".docx", ".xlsx", ".pptx", ".zip", ".epub"}:
        if not body.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
            raise RuntimeError("The selected ZIP-based resource has no ZIP signature")
        checks.append("zip_signature")
    elif extension == ".png":
        if not body.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError("The selected .png response has no PNG signature")
        checks.append("png_signature")
    elif extension in {".jpg", ".jpeg"}:
        if not body.startswith(b"\xff\xd8\xff"):
            raise RuntimeError("The selected JPEG response has no JPEG signature")
        checks.append("jpeg_signature")
    elif extension == ".gif":
        if not body.startswith((b"GIF87a", b"GIF89a")):
            raise RuntimeError("The selected .gif response has no GIF signature")
        checks.append("gif_signature")

    if HTML_PREFIX.match(body) and extension not in {".html", ".htm"}:
        raise RuntimeError("The resource returned HTML instead of the expected file")
    if media_type in {"application/json", "text/html"} and extension not in {
        ".json",
        ".html",
        ".htm",
    }:
        raise RuntimeError(
            f"The response type {media_type!r} does not match the selected resource"
        )
    checks.append("nonempty")
    return checks


def download(urls: list[str], extension: str) -> tuple[bytes, int, str, list[str]]:
    last_error: Exception | None = None
    accept = mimetypes.types_map.get(extension, "application/octet-stream")
    for url in urls:
        request = urllib.request.Request(
            request_safe_url(url),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/147.0.0.0 Safari/537.36"
                ),
                "Referer": "https://ima.qq.com/",
                "Accept": f"{accept},*/*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                status = response.status
                content_type = response.headers.get("Content-Type", "")
            if status != 200:
                raise RuntimeError(f"Unexpected HTTP status {status}")
            checks = validate_body(body, content_type, extension)
            return body, status, content_type, checks
        except (OSError, urllib.error.URLError, RuntimeError) as error:
            last_error = error
    raise RuntimeError(f"All {len(urls)} signed URL candidates failed") from last_error


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Extract a user-authorized original resource from an ima.copilot "
            "Tabs_* session without printing its signed URL"
        )
    )
    parser.add_argument("--session", type=Path, help="Explicit Tabs_* file")
    parser.add_argument("--term", action="append", required=True, help="Target title term")
    parser.add_argument(
        "--extension",
        help="Required resource extension, for example .docx, .xlsx, .png, or .pdf",
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    extension = normalized_extension(args.extension) or args.output.suffix.casefold()
    if not extension:
        raise RuntimeError("Provide --extension or an output filename with a suffix")

    session = newest_session(args.session)
    data = read_session(session)
    offsets = term_offsets(data, args.term)
    if not offsets:
        raise RuntimeError("None of the target terms were found in the newest session")

    candidates = extract_candidates(data, offsets, extension)
    if not candidates:
        raise RuntimeError(f"No nearby ima {extension} originUrl was found")
    selected = choose_candidate(candidates, args.term)
    urls = signed_urls_for_resource(candidates, selected.resource_path)
    body, status, content_type, checks = download(urls, extension)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(body)
    print("session", session.name)
    print("matched_title", safe_title(selected.title))
    print("resource_name", safe_title(selected.resource_name))
    print("extension", extension)
    print("status", status)
    print("content_type", content_type)
    print("checks", ",".join(checks))
    print("bytes", len(body))
    print("sha256", hashlib.sha256(body).hexdigest().upper())
    print("output", args.output.resolve())


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
