# IMA content extraction routes

Read this reference only for structured notes, articles, or knowledge-base/folder export. Direct PDF and attachment recovery should use the session-resource scripts first.

The request shapes below were recovered from a specific client build and are not public API contracts. Treat them as routing evidence, re-observe current behavior when they drift, and keep all authentication material inside the current local ima/browser context.

## Architecture and trust boundary

The observed exporter used three layers:

1. a local launcher and Chromium extension;
2. direct requests from the extension to `ima.qq.com`;
3. an unrelated cloud service for email login, membership, quota accounting, and `prepare-*` calls.

Only the first two layers are relevant to local extraction. Do not call, emulate, or transmit credentials to the third-party service. Client-side AES wrapping with a hard-coded key is not a safe substitute for TLS and does not make credential upload acceptable.

## Local authentication context

The observed ima web client stored an account object under:

```text
localStorage["ima-universal-local-storage-accountInfo"]
```

Observed fields were `guid`, `uid`, `token`, and `refreshToken`. They are secrets, not deliverables. If a browser-local request must use them:

- read them only inside the live authenticated page or extension execution context;
- do not return them from page evaluation, print them, save them, or interpolate them into shell commands;
- clear temporary in-memory values after the request;
- refresh/reopen the ima page when the session is stale rather than asking the user for tokens.

The web version was observed in the `WEB-VERSION` component of ima's `x-ima-cookie` header. Prefer the current page's own request headers. Avoid hard-coding the exporter's sentinel version.

The observed request header builder combined `IMA-GUID`, `IMA-REFRESH-TOKEN`, `IMA-TOKEN`, `IMA-UID`, `UID-TYPE=2`, `TOKEN-TYPE=14`, `PLATFORM=H5`, `CLIENT-TYPE=256020`, and `WEB-VERSION`, plus an `x-ima-bkn` integer derived from the access token. This is diagnostic evidence; copying the complete header outside the browser violates the secret boundary.

## Content routing observed in the client

| Observed `media_type` | Representation | Local result |
|---|---|---|
| `2` | URL text | Save the resolved URL as UTF-8 `.txt` unless the user requests an offline capture. |
| `6` | WeChat article | For a requested offline copy, preserve HTML and localize images; otherwise preserve the source URL. If capture fails, report the URL fallback as incomplete offline capture. |
| `11` | IMA notebook | Retrieve structured note JSON and render the requested format, defaulting to Markdown, with attachment/image mapping. |
| Other | Direct media/file | Preserve the original bytes from the resolved media URL. |

Do not rely on these numeric values alone. Cross-check title, source path, content type, returned metadata, and current ima behavior.

## Knowledge-base discovery

Observed endpoints:

```text
POST https://ima.qq.com/cgi-bin/knowledge_tab_reader/get_home_page_data
POST https://ima.qq.com/cgi-bin/knowledge_tab_reader/get_knowledge_base_list
POST https://ima.qq.com/cgi-bin/knowledge_tab_reader/get_knowledge_list
POST https://ima.qq.com/cgi-bin/knowledge_tab_reader/get_knowledge_base_home_page
```

The client used paginated requests and recursively collected folders and documents. A safe local implementation should:

1. bind to the exact authenticated ima tab for the task;
2. enumerate only the user-confirmed knowledge base and optional folder subtree;
3. preserve stable IDs internally for deduplication without exposing them in filenames or chat;
4. respect pagination end markers and apply bounded concurrency;
5. keep an explicit manifest of title, relative path, media type, status, size, and output hash;
6. support incremental comparison by stable media ID and update time, while keeping the static content archive separate from download history;
7. stop on repeated authentication or permission failures rather than widening access or refreshing indefinitely.

Before bulk download, show or otherwise verify the resolved knowledge-base title, document count, folder count, destination mode (`directory` or `zip`), and incremental/full choice against the user's authorization. Reuse choices already supplied; ask only for missing choices or a discrepancy that changes scope. Keep the export and manifest outside the source repository.

## Media resolution

Observed routes included:

```text
POST https://ima.qq.com/cgi-bin/s/file_manager/get_media
POST https://ima.qq.com/cgi-bin/file_manager/get_media
POST https://ima.qq.com/cgi-bin/knowledge_tab_reader/get_knowledge
```

The secure route encrypted a request body with a fresh AES-GCM key and wrapped that key with an embedded RSA-OAEP/SHA-256 public key. Do not copy a stale public key from an old build blindly; reuse the current ima page's working request path or re-observe the current public material locally.

Resolve media inside the authenticated browser context and return only the response fields needed by the local downloader. Never log the full response when it includes signed URLs. If a response says the item is deleted, unauthorized, or session-expired, preserve that status in the manifest and do not attempt a permission bypass.

## Notebook extraction

Observed note endpoints:

```text
POST https://ima.qq.com/cgi-bin/notebook/logic/get_doc
POST https://ima.qq.com/cgi-bin/notebook/logic/get_share_know_doc
```

The client parsed `docid` and sometimes `knowledgeId` from the resolved media URL. For an owned/direct note it requested basic content, resources, attachments, cover data, and attachment details. Shared knowledge used the share endpoint with `knowledge_id`.

Expected transformation pipeline:

1. verify the response identifies the requested note;
2. retain the raw structured content in temporary memory until rendering succeeds;
3. build an attachment/link map from note link metadata and media preview URLs;
4. use the requested Markdown or HTML format, defaulting to Markdown when unspecified;
5. render headings, text, emphasis, links, lists/indentation, line breaks, and images;
6. download images into a deterministic adjacent asset directory and rewrite links to relative paths;
7. sanitize Windows filenames and reserved device names without changing the note title inside the document;
8. verify substantive text, image counts, broken links, encoding, and output hash.

The recovered exporter contained a Rust/WASM renderer with a `core_dispatch` entrypoint for Markdown and HTML. A maintained independent implementation may either reuse a user-authorized local copy of that renderer or implement the documented content model anew. Do not claim source fidelity when only the compiled WASM is available.

## Article and URL extraction

- URL item: preserve the URL as text by default. Only crawl it when the user requests an offline copy and the page is within scope.
- WeChat article: preserve the source URL by default. For a requested offline copy, capture substantive article HTML, title, publication metadata when present, and article images. Rewrite image links to stable relative paths and keep a source URL in metadata without embedding cookies or signed parameters.
- If scripts or anti-bot behavior prevent a reliable offline copy, deliver the URL representation and explain the limitation instead of saving an incomplete page as successful.

## Output and failure semantics

- Directory mode preserves the IMA folder hierarchy and writes files atomically when practical.
- ZIP mode should stream entries, finalize only after the queue completes, and treat an interrupted archive as failed rather than deliverable.
- Preserve original file bytes for direct media. Rendered notes/articles are derivatives and should be labeled as such.
- Record per-item success, skip, unauthorized, deleted, expired, conversion failure, and download failure states.
- After a session refresh, persistent authentication or permission failures stop the affected operation. Retain verified results and report incomplete items; a URL fallback does not count as a completed offline copy. Reuse still-applicable results when the user changes the destination or narrows scope.
- Never mark quota, membership, or third-party backend status as part of a local extractor; those are unrelated commercial controls.
