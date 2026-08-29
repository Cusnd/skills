---
name: ima-pdf-extractor
description: Extract user-authorized original files, PDFs, notes, articles, or knowledge-base content from the Windows ima.copilot client while keeping signed URLs and login credentials local. Use only when explicitly invoked.
---

# ima Content Extractor

Recover content the user is authorized to save from the Windows `ima.copilot` client. Preserve the existing exact-PDF workflow, but route other content by representation instead of treating every preview as a cached PDF.

## Authorization and secret boundary

- Require an explicit invocation and a clearly identified target or knowledge-base scope.
- Operate only on content the user owns or is authorized to export. Do not treat “visible in ima” as proof that bulk export is permitted.
- Keep signed URLs, query signatures, IMA `token`, `refreshToken`, cookies, account identifiers, and raw session contents out of chat, logs, filenames, command output, and persistent artifacts.
- Keep extraction local. Do not send IMA `accountInfo` or credentials to the reverse-engineered third-party service at `124.156.134.34`, or to any replacement service.
- Do not ask the user to paste tokens. Prefer the current ima session, a browser-local request, or a freshly opened preview.

## Route by content type

1. **Original preview resource — preferred for PDFs and ordinary attachments.** Have the user open the exact item as a standalone preview and allow it to load. Search the newest Chromium `Tabs_*` snapshot for the nearby signed `originUrl`.
   - For PDF-only work, use `scripts/extract_ima_pdf.py`; its stricter PDF checks remain authoritative.
   - For another original file type, use `scripts/extract_ima_resource.py`, normally with at least two discriminating `--term` values and an `--extension` filter.
2. **IMA note.** Use the authenticated ima page locally to resolve the note, retrieve its structured content, and render Markdown or HTML with attachments. Read [references/content-extraction.md](references/content-extraction.md) before acting.
3. **WeChat article or URL knowledge item.** Preserve the URL when that is the source representation; when the user asks for an offline copy, save HTML and localize referenced images. Read the reference first.
4. **Knowledge-base or folder export.** Confirm the exact knowledge base, folder scope, output mode, and whether an incremental export is desired. Read the reference before enumerating or downloading.

Prefer the narrowest route that preserves the source exactly. Do not enumerate an entire knowledge base when a standalone preview already exposes the requested original file.

## Session-resource workflow

1. Locate `%LOCALAPPDATA%/ima.copilot/User Data/Default/Sessions/Tabs_*` and use the newest file.
2. If it is locked, ask the user to exit ima normally. Closing the window may leave ima in the tray. Do not force-terminate it without current, explicit approval after warning about unsaved state.
3. Ask for exact, discriminating title terms such as organization, ticker, date, subtitle, or filename. Use at least two when possible.
4. Download first into the current task's temporary/work directory. Never print or persist the signed URL.
5. Check the sanitized `matched_title`, `resource_name`, response type, size, signature checks, and SHA-256 before accepting the candidate.
6. If every signed candidate is unauthorized or expired, have the user reopen the preview, allow it to load, exit ima normally, and retry against the new session.

Examples in PowerShell:

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

## Failure boundaries

- Do not use Chromium cache blocks as the primary source and do not identify a resource from magic bytes alone.
- Do not expose raw session records; they may contain browsing history and signed parameters.
- CDP is optional for browser-local structured extraction, not required for direct session resources. Do not relaunch ima with debugging flags unless the user separately authorizes CDP troubleshooting.
- Undocumented IMA endpoints can drift. Re-observe the current authenticated page locally when a known request shape fails; do not weaken credential handling or fall back to the third-party backend.
- Stop and report the boundary if the only available route requires bypassing an access restriction, sharing credentials, or reconstructing unavailable server-side logic.
