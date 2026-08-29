#!/usr/bin/env python3
"""Validate the repository's skill layout without third-party dependencies."""

from __future__ import annotations

import ast
import re
import sys
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESERVED_DIRECTORIES = {"docs", "scripts"}
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
README_SKILL_LINK = re.compile(r"\(([^)\s]+/SKILL\.md)(?:#[^)]*)?\)")
OPENAI_INTERFACE_FIELD = re.compile(
    r"^\s+(display_name|short_description|default_prompt):\s*(.+?)\s*$",
    re.MULTILINE,
)

REQUIRED_FILES = (
    Path("README.md"),
    Path("README.en.md"),
    Path("AGENTS.md"),
    Path("SECURITY.md"),
    Path("LICENSE"),
    Path(".gitignore"),
    Path(".gitattributes"),
    Path(".github/ISSUE_TEMPLATE/bug_report.yml"),
    Path(".github/ISSUE_TEMPLATE/feature_request.yml"),
    Path(".github/ISSUE_TEMPLATE/config.yml"),
    Path(".github/workflows/validate.yml"),
)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_utf8(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        errors.append(f"{relative(path)}: not valid UTF-8 ({error})")
    except OSError as error:
        errors.append(f"{relative(path)}: cannot be read ({error})")
    return None


def yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def parse_skill_frontmatter(
    skill_dir: Path, errors: list[str]
) -> dict[str, str] | None:
    skill_md = skill_dir / "SKILL.md"
    content = read_utf8(skill_md, errors)
    if content is None:
        return None

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        errors.append(f"{relative(skill_md)}: must start with YAML frontmatter")
        return None

    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        errors.append(f"{relative(skill_md)}: frontmatter has no closing delimiter")
        return None

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key in {"name", "description"}:
            fields[key] = yaml_scalar(value)

    for field in ("name", "description"):
        if not fields.get(field):
            errors.append(f"{relative(skill_md)}: missing non-empty frontmatter field {field!r}")
    return fields


def discover_skills(errors: list[str]) -> list[Path]:
    skills: list[Path] = []
    for path in sorted(ROOT.iterdir(), key=lambda item: item.name.casefold()):
        if not path.is_dir() or path.name.startswith(".") or path.name in RESERVED_DIRECTORIES:
            continue
        if not (path / "SKILL.md").is_file():
            errors.append(f"{path.name}/: non-reserved top-level directory has no SKILL.md")
            continue
        skills.append(path)
    if not skills:
        errors.append("repository: no skill directories found")
    return skills


def validate_skills(skills: list[Path], errors: list[str]) -> None:
    seen_names: set[str] = set()
    for skill_dir in skills:
        fields = parse_skill_frontmatter(skill_dir, errors)
        if not fields or not fields.get("name"):
            continue
        name = fields["name"]
        if not SKILL_NAME.fullmatch(name):
            errors.append(
                f"{relative(skill_dir / 'SKILL.md')}: name {name!r} must use lowercase letters, digits, and hyphens"
            )
        if name != skill_dir.name:
            errors.append(
                f"{relative(skill_dir / 'SKILL.md')}: frontmatter name {name!r} does not match folder {skill_dir.name!r}"
            )
        if name in seen_names:
            errors.append(f"{relative(skill_dir)}: duplicate skill name {name!r}")
        seen_names.add(name)

        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if openai_yaml.exists():
            content = read_utf8(openai_yaml, errors)
            if content is None:
                continue
            if not re.search(r"^interface:\s*$", content, re.MULTILINE):
                errors.append(f"{relative(openai_yaml)}: missing top-level interface mapping")
            values = {
                key: yaml_scalar(value)
                for key, value in OPENAI_INTERFACE_FIELD.findall(content)
            }
            for field in ("display_name", "short_description", "default_prompt"):
                if not values.get(field):
                    errors.append(f"{relative(openai_yaml)}: missing non-empty interface.{field}")


def normalized_link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        raw = raw[1 : raw.index(">")]
    else:
        raw = raw.split(maxsplit=1)[0]
    return urllib.parse.unquote(raw)


def validate_markdown_links(markdown_files: list[Path], errors: list[str]) -> None:
    for markdown in markdown_files:
        content = read_utf8(markdown, errors)
        if content is None:
            continue
        for match in MARKDOWN_LINK.finditer(content):
            target = normalized_link_target(match.group(1))
            if not target or target.startswith("#"):
                continue
            parsed = urllib.parse.urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith("/"):
                continue
            local_part = parsed.path
            if not local_part:
                continue
            candidate = (markdown.parent / local_part).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                line = content.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{relative(markdown)}:{line}: local link escapes the repository: {target}"
                )
                continue
            if not candidate.exists():
                line = content.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{relative(markdown)}:{line}: missing local link target {target}"
                )


def validate_readme_inventories(skills: list[Path], errors: list[str]) -> None:
    discovered = {skill.name for skill in skills}
    for readme_name in ("README.md", "README.en.md"):
        readme = ROOT / readme_name
        content = read_utf8(readme, errors)
        if content is None:
            continue
        listed: set[str] = set()
        for target in README_SKILL_LINK.findall(content):
            parsed = urllib.parse.urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            parts = Path(parsed.path).parts
            if len(parts) == 2 and parts[1] == "SKILL.md":
                listed.add(parts[0])
        if listed != discovered:
            missing = sorted(discovered - listed)
            extra = sorted(listed - discovered)
            details: list[str] = []
            if missing:
                details.append(f"missing={','.join(missing)}")
            if extra:
                details.append(f"extra={','.join(extra)}")
            errors.append(f"{readme_name}: skill catalog mismatch ({'; '.join(details)})")


def validate_python(python_files: list[Path], errors: list[str]) -> None:
    for python_file in python_files:
        content = read_utf8(python_file, errors)
        if content is None:
            continue
        try:
            ast.parse(content, filename=relative(python_file))
        except SyntaxError as error:
            errors.append(
                f"{relative(python_file)}:{error.lineno or 1}: Python syntax error: {error.msg}"
            )


def validate_repository_controls(errors: list[str]) -> None:
    for required in REQUIRED_FILES:
        if not (ROOT / required).is_file():
            errors.append(f"{required.as_posix()}: required repository file is missing")

    workflow = ROOT / ".github" / "workflows" / "validate.yml"
    if workflow.is_file():
        content = read_utf8(workflow, errors)
        if content is not None:
            if re.search(r"^\s*pull_request(?:_target)?:", content, re.MULTILINE):
                errors.append(f"{relative(workflow)}: pull request triggers are not allowed")
            for trigger in ("push:", "workflow_dispatch:"):
                if trigger not in content:
                    errors.append(f"{relative(workflow)}: missing {trigger.rstrip(':')} trigger")
            if not re.search(r"^\s*contents:\s*read\s*$", content, re.MULTILINE):
                errors.append(f"{relative(workflow)}: workflow must declare contents: read")

    issue_config = ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
    if issue_config.is_file():
        content = read_utf8(issue_config, errors)
        if content is not None and not re.search(
            r"^blank_issues_enabled:\s*false\s*$", content, re.MULTILINE
        ):
            errors.append(f"{relative(issue_config)}: blank issues must be disabled")


def main() -> int:
    errors: list[str] = []
    skills = discover_skills(errors)
    validate_skills(skills, errors)

    markdown_files = sorted(
        (path for path in ROOT.rglob("*.md") if ".git" not in path.parts),
        key=lambda path: relative(path),
    )
    python_files = sorted(
        (path for path in ROOT.rglob("*.py") if ".git" not in path.parts),
        key=lambda path: relative(path),
    )
    validate_markdown_links(markdown_files, errors)
    validate_readme_inventories(skills, errors)
    validate_python(python_files, errors)
    validate_repository_controls(errors)

    if errors:
        print(f"Repository validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Repository validation passed: "
        f"skills={len(skills)} markdown={len(markdown_files)} python={len(python_files)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
