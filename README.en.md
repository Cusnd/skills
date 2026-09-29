# Personal Agent Skills

[![validate](https://github.com/Cusnd/skills/actions/workflows/validate.yml/badge.svg)](https://github.com/Cusnd/skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

English | [简体中文](README.md)

This is a personally maintained collection of agent skills by [SorenLiu](https://github.com/Cusnd), intended for Codex, the ChatGPT desktop app, and other environments compatible with the Agent Skills format. It is not an official OpenAI project and does not represent any referenced third-party service.

The repository follows a personal, issue-only maintenance model: bug reports and feature requests are welcome, but pull requests are disabled and external code contributions are not accepted. The MIT License still permits forks, modifications, and independent distributions that comply with its terms.

## Skills

| Skill | Purpose | Platform and dependencies | Invocation policy |
| --- | --- | --- | --- |
| [`frontend-design-concept`](frontend-design-concept/SKILL.md) | Distill aesthetic knowledge into a vivid, specific, editable design description before frontend work; deliver the concept alone or implement and verify the page as requested. | No tool dependency for ideation; implementation and visual verification use the target project's stack and available browser capabilities. | Implicit matching is allowed by default; use `$frontend-design-concept` to invoke it explicitly. |
| [`ima-pdf-extractor`](ima-pdf-extractor/SKILL.md) | Save original files, PDFs, notes, articles, or knowledge-base content that a user is authorized to export from the Windows `ima.copilot` client while keeping credentials and signed URLs local. | Windows; direct-resource scripts use only the Python 3.10+ standard library; structured content may require controlled, browser-local capabilities. | Explicit invocation only: `$ima-pdf-extractor`. |
| [`orchestrate-workflow`](orchestrate-workflow/SKILL.md) | Keep the invoking session as orchestrator for medium or complex tasks when the user requests multi-agent or independent-session orchestration; delegate all concrete execution for complex tasks. | An agent environment with real subagents or independent executor contexts; capabilities depend on the host's callable tools. | Implicit matching is allowed by default; explicit `$orchestrate-workflow` invocation is recommended. |
| [`pdf-watermark-removal`](pdf-watermark-removal/SKILL.md) | Inspect user-authorized PDFs, remove recurring watermarks or explicitly requested promotional pages with the least destructive method, and verify both structure and rendering. | Requires PDF parsers, renderers, and image-inspection capabilities available to the agent; the repository does not bind one toolchain. | Implicit matching is allowed by default; explicit `$pdf-watermark-removal` invocation is recommended. |

### `frontend-design-concept`

- Describes the site's character, composition, reading sequence, and experience in coherent prose so the aesthetic direction can be read and revised.
- Derives visual decisions from content and purpose, connecting desired impressions to position, proportion, typography, color, and interaction rather than supplying style labels alone.
- Delivers the description independently for concept-only requests; for implementation requests, presents the concept before continuing and waits when the user explicitly requests review first.
- Compares actual rendering with the design intent and usability, distinguishing technical checks from completed visual verification.

### `ima-pdf-extractor`

- Prefers the original resource exposed by a preview instead of guessing files from Chromium cache blocks.
- Operates only on explicitly identified content the user is authorized to export; visibility in the client is not treated as bulk-export permission.
- Reuses established targets, title terms, and authorization; asks only about ambiguity, missing scope, or an action the user must perform. Verifies scope and mode before bulk download. Notes default to Markdown; URLs and articles default to saved links, with offline copies generated on request.
- Some observed IMA request shapes are not public APIs and may drift with client releases. Re-observe the current local session when they fail instead of weakening credential boundaries.
- Tokens, cookies, account identifiers, raw session contents, signed URLs, and query signatures must not enter chat, logs, filenames, or persistent artifacts.

### `orchestrate-workflow`

- Keeps the invoking session responsible for orchestration and user communication, retaining user intent, overall decisions, and coordination context. Ordinary small tasks are excluded.
- Medium tasks can use subagents to own focused work. Complex tasks delegate investigation, implementation, verification, integration, and follow-up fixes to real executor contexts while the orchestrator assesses results and coordinates delivery.
- Chooses parallel or serial work from ownership boundaries and dependencies, hands off relevant task context while isolating host orchestration policy, and preserves actual authorization. Delegation and YOLO mode do not expand permission for external actions.

### `pdf-watermark-removal`

- Uses PDF object structure and rendered pages to identify the watermark representation before choosing object removal, narrow cropping/redaction, or user-approved raster reconstruction.
- Always writes a derivative and never overwrites the source PDF; the source hash must remain unchanged.
- A watermark-only request does not include page deletion. Removes only explicitly requested pages, or verified promotional pages when promotional-page cleanup is part of the request.
- Fails closed when a watermark overlaps content that cannot be recovered reliably, and never describes masking, cropping, or image repair as lossless removal.

## Installation

Codex discovers local skills from locations including the user-level `$HOME/.agents/skills` directory and repository-level `.agents/skills` directories. See the [official OpenAI Skills documentation](https://learn.chatgpt.com/docs/build-skills) for the complete discovery rules. This repository distributes one skill per top-level directory; install only the directory you need.

### Windows PowerShell: copy one skill

```powershell
git clone https://github.com/Cusnd/skills.git
Set-Location .\skills

$target = Join-Path $HOME ".agents\skills\ima-pdf-extractor"
if (Test-Path -LiteralPath $target) { throw "Target already exists: $target" }
New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
Copy-Item -Recurse -LiteralPath ".\ima-pdf-extractor" -Destination $target
```

Replace `ima-pdf-extractor` with the desired skill name from the catalog above to install another skill. Inspect local changes before replacing any existing target directory.

### macOS/Linux: symlink one skill

```bash
git clone https://github.com/Cusnd/skills.git
cd skills

mkdir -p "$HOME/.agents/skills"
test ! -e "$HOME/.agents/skills/pdf-watermark-removal"
ln -s "$(pwd)/pdf-watermark-removal" "$HOME/.agents/skills/pdf-watermark-removal"
```

Codex normally detects skill changes automatically. Restart Codex if a newly installed skill does not appear.

## Invocation

In Codex CLI or the IDE extension, type `$` to select a skill or name it directly in the prompt:

```text
$frontend-design-concept write a vivid, specific design description for this website, then implement the frontend from that description.

$ima-pdf-extractor save this PDF that I opened in ima.copilot and am authorized to export.

$orchestrate-workflow keep this session as orchestrator, preserve my intent, and delegate implementation and verification of this complex task to real executors.

$pdf-watermark-removal inspect these PDFs, preserve the sources, and produce verified watermark-free copies.
```

Invoking a skill does not expand task authorization. Established authorization and choices remain valid within the current task without repeated confirmation; added scope, forced application termination, CDP troubleshooting, and raster reconstruction remain subject to each skill's applicable authorization checks and stopping conditions. Temporary content and deliverables stay outside the source repository.

Deliver once applicable verification passes; add checks only for new changes, failures, or unresolved concerns. Batch tasks retain verified results and report failures individually; a URL fallback does not count as a completed offline copy.

## Security and privacy

- Process only content you own or are authorized to handle.
- Never put tokens, cookies, authorization headers, signed URLs, IMA session files, account identifiers, private documents, or screenshots/logs containing those values in a public Issue.
- Report vulnerabilities privately through GitHub Private Vulnerability Reporting as described in [`SECURITY.md`](SECURITY.md).
- Skills in this repository do not grant additional rights to third-party services, content, or interfaces.

## Issues and maintenance

- [Bug report](https://github.com/Cusnd/skills/issues/new?template=bug_report.yml): report a reproducible skill or repository problem.
- [Feature request](https://github.com/Cusnd/skills/issues/new?template=feature_request.yml): suggest an improvement or a new personally maintained capability.
- Pull requests are disabled. The maintainer evaluates Issues and implements accepted changes directly in the repository.

See [`AGENTS.md`](AGENTS.md) for the repository maintenance contract. Run the local structural check with:

```text
python scripts/validate_repo.py
```

## License

Repository source and documentation are available under the [MIT License](LICENSE). The license does not cover third-party content processed or downloaded through a skill.
