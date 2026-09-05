---
name: ima-pdf-extractor
description: Extract user-authorized original files, PDFs, notes, articles, or knowledge-base content from the Windows ima.copilot client while keeping signed URLs and login credentials local. Use only when explicitly invoked.
---

# ima Content Extractor

Recover the requested content from the Windows `ima.copilot` client and deliver verified local files. Select the route by source representation; preserve original bytes for direct resources and identify rendered notes or articles as derivatives.

## Resolve the task

Use the request, prior context, and safe local inspection to identify the target, discriminating title terms, and output location. Continue within existing explicit authorization; ask only for missing scope or authorization, information needed to distinguish candidates, or an action the user must perform. State routine defaults and proceed rather than asking the user to repeat known information.

Keep temporary downloads, manifests, and deliverables outside this source repository. Use the requested destination when suitable, otherwise a task-specific local output directory outside the repository. If the user changes the destination or narrows the scope, apply that change to remaining work and reuse verified results that still match the request.

## Authorization and secret boundary

- Require an explicit invocation and a clearly identified target or knowledge-base scope.
- Operate only on content the user owns or is authorized to export. Do not treat “visible in ima” as proof that bulk export is permitted.
- Keep signed URLs, query signatures, IMA `token`, `refreshToken`, cookies, account identifiers, and raw session contents out of chat, logs, filenames, command output, and persistent artifacts.
- Keep extraction local. Do not send IMA `accountInfo` or credentials to the reverse-engineered third-party service at `124.156.134.34`, or to any replacement service.
- Do not ask the user to paste tokens. Prefer the current ima session, a browser-local request, or a freshly opened preview.

## Route by content type

1. **Original preview resource — preferred for PDFs and ordinary attachments.** Use the exact item's loaded standalone preview and search the newest Chromium `Tabs_*` snapshot for the nearby signed `originUrl`. Ask the user to open and load the preview only when it is not already available.
   - For PDF-only work, use `scripts/extract_ima_pdf.py`; its stricter PDF checks remain authoritative.
   - For another original file type, use `scripts/extract_ima_resource.py`, normally with at least two discriminating `--term` values and an `--extension` filter.
2. **IMA note.** Use the authenticated ima page locally to resolve the note, retrieve its structured content, and render it with attachments in the requested format, defaulting to Markdown. Read [references/content-extraction.md](references/content-extraction.md) before acting.
3. **WeChat article or URL knowledge item.** Preserve the URL when that is the source representation; when the user asks for an offline copy, save HTML and localize referenced images. Read the reference first.
4. **Knowledge-base or folder export.** Establish the exact user-authorized knowledge base and folder scope before enumeration. Reuse specified output mode and incremental/full choices; ask for missing choices and verify the resolved scope and mode before bulk download. Read the reference before enumerating or downloading.

Prefer the narrowest route that preserves the source exactly. Do not enumerate an entire knowledge base when a standalone preview already exposes the requested original file.

## Session-resource workflow

1. Locate `%LOCALAPPDATA%/ima.copilot/User Data/Default/Sessions/Tabs_*` and use the newest file.
2. If it is locked, ask the user to exit ima normally. Closing the window may leave ima in the tray. Do not force-terminate it without current, explicit approval after warning about unsaved state.
3. Derive exact, discriminating title terms such as organization, ticker, date, subtitle, or filename from the resolved task. Use at least two when possible. If candidates remain ambiguous, request only the distinguishing information before downloading.
   - The CLIs rank candidates and download the best match; they do not establish uniqueness. When identity is uncertain, use the scripts' parsing helpers locally to compare candidates in memory before invoking the downloader. Expose only sanitized distinguishing titles, never candidate objects, signed URLs, or raw session records.
4. Download first into the task's temporary directory outside the repository. Never print or persist the signed URL.
5. Check the sanitized `matched_title`, `resource_name`, response type, size, signature checks, and SHA-256 before accepting the candidate.
6. If every signed candidate is unauthorized or expired, have the user reopen the preview, allow it to load, exit ima normally, and retry against the new session. If authentication or permission failures persist after this refresh, stop the affected extraction and report the unresolved item; retain verified results without widening scope.

Examples in PowerShell (`<task-work-dir>` must be outside the repository):

```powershell
& python scripts/extract_ima_pdf.py `
  --term "China Overseas Land" `
  --term "0688.HK" `
  --term "1H26" `
  --output "<task-work-dir>/candidate.pdf"

& python scripts/extract_ima_resource.py `
  --term "project specification" `
  --term "2026-08" `
  --extension ".docx" `
  --output "<task-work-dir>/candidate.docx"
```

## Verification and delivery

- Preserve original bytes for direct resources. Do not remove promotional covers or trailing pages unless the user asks for a modified derivative.
- PDF: use `pypdf` for page count, encryption state, requested terms, and embedded JavaScript; render representative pages with Poppler and inspect the images. Do not use `pdftoppm -singlefile` for arbitrary page sampling.
- Office/ZIP-based files: validate the ZIP container and expected internal structure, then inspect content using the appropriate document skill or library.
- Images/audio/video: validate the container, dimensions or duration, and representative decoding rather than trusting the extension.
- Notes/HTML: verify the title, substantive text, attachment count, localized links, and absence of accidental credential material.
- Batch export: report requested scope, discovered and exported counts, skips/failures, byte totals, and a manifest of output hashes. Do not silently widen scope after partial failures.
- Copy verified deliverables to the task's user-facing output directory with stable descriptive names. Report the path, size, format-specific checks, and SHA-256.
- If ima was exited for extraction, restart it normally after the session snapshot is no longer needed.
- Complete the applicable checks, then deliver. Repeat or broaden verification only after a change, failure, or unresolved concern. Lead the report with verified outputs and any incomplete items; distinguish a fallback representation from the requested original or offline copy.

## Failure boundaries

- Do not use Chromium cache blocks as the primary source and do not identify a resource from magic bytes alone.
- Do not expose raw session records; they may contain browsing history and signed parameters.
- CDP is optional for browser-local structured extraction, not required for direct session resources. Do not relaunch ima with debugging flags unless the user separately authorizes CDP troubleshooting.
- Undocumented IMA endpoints can drift. Re-observe the current authenticated page locally when a known request shape fails; do not weaken credential handling or fall back to the third-party backend.
- Stop and report the boundary if the only available route requires bypassing an access restriction, sharing credentials, or reconstructing unavailable server-side logic.
