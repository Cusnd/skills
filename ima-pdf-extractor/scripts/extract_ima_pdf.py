from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


IMA_HOST = "res-skb.ima.qq.com"
URL_PATTERN = re.compile(rb"chrome-extension://[^\x00\s\"<>]+")


@dataclass(frozen=True)
class Candidate:
    distance: int
    offset: int
    title: str
    origin_url: str
    resource_path: str


def decode_query_component(value: str) -> str:
    raw = urllib.parse.unquote_to_bytes(value.replace("+", " "))
    for encoding in ("utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def query_value_raw(query: str, key: str) -> list[str]:
    values: list[str] = []
    for part in query.split("&"):
        raw_key, separator, raw_value = part.partition("=")
        if separator and urllib.parse.unquote_plus(raw_key) == key:
            values.append(raw_value)
    return values


def newest_session(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise RuntimeError("LOCALAPPDATA is unavailable")
    session_dir = (
        Path(local_app_data)
        / "ima.copilot"
        / "User Data"
        / "Default"
        / "Sessions"
    )
    sessions = sorted(
        session_dir.glob("Tabs_*"), key=lambda path: path.stat().st_mtime, reverse=True
    )
    if not sessions:
        raise RuntimeError(f"No Tabs_* session file found under {session_dir}")
    return sessions[0]


def read_session(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except PermissionError as error:
        raise RuntimeError(
            "The newest ima session is locked. Exit ima normally, including its tray "
            "process, then rerun. Do not silently fall back to an older session."
        ) from error


def term_offsets(data: bytes, terms: list[str]) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for term in terms:
        for needle in (term.encode("utf-8"), term.encode("utf-16-le")):
            start = 0
            while True:
                offset = data.find(needle, start)
                if offset < 0:
                    break
                found.append((offset, term))
                start = offset + len(needle)
    return found


def extract_candidates(data: bytes, offsets: list[tuple[int, str]]) -> list[Candidate]:
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
            if inner.netloc != IMA_HOST or not inner.path.lower().endswith(".pdf"):
                continue
            raw_titles = query_value_raw(inner.query, "media_title")
            title = decode_query_component(raw_titles[0]) if raw_titles else ""
            candidates.append(
                Candidate(distance, match.start(), title, origin, inner.path)
            )
    return candidates


def choose_candidate(candidates: list[Candidate], terms: list[str]) -> Candidate:
    folded_terms = [term.casefold() for term in terms]

    def title_score(candidate: Candidate) -> int:
        folded_title = candidate.title.casefold()
        return sum(len(term) for term in folded_terms if term in folded_title)

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


def request_safe_url(url: str) -> str:
    """Encode raw spaces/non-ASCII while preserving ima's existing escapes."""
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%:@!$&'()*+,;=-._~")
    query = urllib.parse.quote(parts.query, safe="%=&+/:?@!$'()*,-._~;")
    fragment = urllib.parse.quote(parts.fragment, safe="%=&+/:?@!$'()*,-._~;")
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, path, query, fragment)
    )


def download(urls: list[str]) -> tuple[bytes, int, str]:
    last_error: Exception | None = None
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
                "Accept": "application/pdf,*/*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                status = response.status
                content_type = response.headers.get("Content-Type", "")
            if status == 200 and body.startswith(b"%PDF-"):
                return body, status, content_type
            last_error = RuntimeError(
                f"Unexpected response: status={status}, type={content_type!r}, "
                f"bytes={len(body)}"
            )
        except (OSError, urllib.error.URLError) as error:
            last_error = error
    raise RuntimeError(f"All {len(urls)} signed URL candidates failed") from last_error


def safe_title(value: str) -> str:
    return " ".join(value.replace("\x00", " ").split())[:500]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract a user-authorized PDF from an ima.copilot Tabs_* session"
    )
    parser.add_argument("--session", type=Path, help="Explicit Tabs_* file")
    parser.add_argument("--term", action="append", required=True, help="Target title term")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    session = newest_session(args.session)
    data = read_session(session)
    offsets = term_offsets(data, args.term)
    if not offsets:
        raise RuntimeError("None of the target terms were found in the newest session")

    candidates = extract_candidates(data, offsets)
    if not candidates:
        raise RuntimeError("No nearby ima PDF originUrl was found")
    selected = choose_candidate(candidates, args.term)
    urls = signed_urls_for_resource(candidates, selected.resource_path)
    body, status, content_type = download(urls)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(body)
    print("session", session.name)
    print("matched_title", safe_title(selected.title))
    print("status", status)
    print("content_type", content_type)
    print("bytes", len(body))
    print("ends_with_eof", b"%%EOF" in body[-2048:])
    print("sha256", hashlib.sha256(body).hexdigest().upper())
    print("output", args.output.resolve())


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
