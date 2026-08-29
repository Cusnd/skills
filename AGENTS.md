# Repository maintenance / 仓库维护

## Authority / 权威边界

- Treat this repository as the source of truth. User-level copies such as `$HOME/.agents/skills` are deployment targets; update them only under a current, explicit request.
- Preserve each skill's authorization, secret-handling, invocation, and failure boundaries unless the current request explicitly changes them.
- Use Issues as intake. Leave working-tree changes uncommitted and unpushed until the user explicitly authorizes Git publication; external pull requests are outside this repository's workflow.

## Structure / 结构

- Every non-hidden top-level directory except `docs/` and `scripts/` is one skill and must contain `SKILL.md`.
- Match the folder to the frontmatter `name`; use lowercase letters, digits, and hyphens.
- Keep shared workflow and hard boundaries in `SKILL.md`. Put branch-specific detail in a linked `references/` file and deterministic reusable operations in `scripts/`.
- When editing `agents/openai.yaml`, keep UI metadata aligned with the skill and preserve unrelated `policy` and `dependencies` fields.
- Add only resources with a current caller. Do not create per-skill READMEs, placeholders, generated catalogs, or duplicate instructions.

## Change loop / 变更闭环

1. Inspect the target skill, its linked resources, and current tests before editing; completion means every affected caller and boundary is accounted for.
2. Make the narrowest change that satisfies the requested behavior; completion means unrelated skill files and installed copies remain unchanged.
3. When a skill is added, renamed, or removed, update the catalog links in both `README.md` and `README.en.md`; completion means both inventories equal the discovered skill set.
4. Keep credentials, session files, signed URLs, downloaded user content, and real private samples outside the repository; completion means the staged set contains none of them.
5. Run the checks below; completion means every applicable check passes and failures are reported without weakening validation.

## Checks / 校验

```text
python scripts/validate_repo.py
python ima-pdf-extractor/scripts/extract_ima_pdf.py --help
python ima-pdf-extractor/scripts/extract_ima_resource.py --help
git diff --check
```

For a new or substantially changed skill, also run the current `skill-creator` `quick_validate.py` against that skill. On Windows, set `PYTHONUTF8=1` before invoking the official validator so UTF-8 Markdown is not decoded with the legacy console code page.

Functional checks must match the change. IMA extraction tests require a user-authorized local target and must not expose the session or signed URL. PDF transformations require an unchanged source hash plus structural and rendered-output evidence.
