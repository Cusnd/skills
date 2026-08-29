# Agent Requirements

This file is the compact source of truth for current outcomes and constraints. It is not a transcript or activity log.

## Active

<!-- agent-docs:active:start -->
<!-- agent-docs:req:R-20260829-125608-0XH5:start -->
### R-20260829-125608-0XH5: Publish a verified issue-only personal skills repository

- **Created:** 2026-08-29T12:56:08.456Z
- **Updated:** 2026-08-29T13:10:31.166Z
- **Summary:** Publish a verified issue-only personal skills repository
- **Priority:** P2
- **Status:** In Progress
- **Supersedes:** None

#### Acceptance Criteria

- [x] Both existing skill directories remain byte-identical to the pre-change baseline.
- [x] Chinese and English READMEs accurately document both skills, installation, invocation, security boundaries, issue policy, and MIT license.
- [x] Repository maintenance guidance, security policy, ignore rules, issue forms, standard-library validator, and push-only CI are present and internally consistent.
- [x] Local repository validation, both official skill validations, Python CLI smoke checks, Markdown links, and Git diff checks pass.
- [ ] A single authorized initial commit is pushed to the public Cusnd/skills repository with main as default branch.
- [ ] Issues and Actions are enabled; Pull requests, Wiki, Projects, and Discussions are disabled and read back.
- [ ] Secret scanning, push protection, and private vulnerability reporting are enabled or any unavailable setting is reported honestly.
- [ ] No global installed skill copy, test Issue, pull request, collaborator, or deployment is created.

#### Evidence

- `python scripts/validate_repo.py` — passed with 2 skills, 8 Markdown files, and 3 Python files.
- Official `quick_validate.py` — both skills passed under UTF-8 mode.
- Both extractor CLI `--help` smoke checks passed without accessing IMA data.
- YAML parse and sensitive-prefix scan passed for the repository support files.
- SHA-256 comparison — all 7 skill source files matched the installed pre-change baseline; no extra cache remained.
- Explicit staged set — 21 expected files; `git diff --cached --check` passed.

#### Next Step

Create the authorized initial commit, publish it to `Cusnd/skills`, and verify remote settings and CI.

#### Related Sessions

- None yet.
<!-- agent-docs:req:R-20260829-125608-0XH5:end -->
<!-- agent-docs:active:end -->

## Recently Closed

The newest 20 closed Requirements remain here. Older rows move to `archive/requirements/YYYY.md`.

<!-- agent-docs:closed:start -->
| ID | Closed (UTC) | Status | Summary | Evidence | Session |
| --- | --- | --- | --- | --- | --- |
<!-- agent-docs:closed:end -->
