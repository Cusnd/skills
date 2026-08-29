# Security Policy / 安全政策

## Supported version / 支持版本

Only the latest state of the default `main` branch is supported. Historical commits and independently modified forks are not covered by this repository's maintenance policy.

仅支持默认 `main` 分支的最新状态；历史提交和第三方修改后的 fork 不在本仓库维护范围内。

## Private reporting / 私密报告

Use [GitHub Private Vulnerability Reporting](https://github.com/Cusnd/skills/security/advisories/new) for vulnerabilities, unsafe authorization behavior, or accidental credential exposure. Do not open a public Issue for a security-sensitive report.

请通过 [GitHub 私密漏洞报告](https://github.com/Cusnd/skills/security/advisories/new) 提交漏洞、越权行为或意外凭据暴露问题，不要为敏感安全问题创建公开 Issue。

Include only the minimum reproducible information. Describe the affected skill and behavior, but redact or replace all user data.

只提交最小可复现信息；说明受影响的 skill 和行为，并删除或替换所有用户数据。

## Never submit publicly / 禁止公开提交

- Tokens, cookies, authorization headers, refresh tokens, private keys, or account identifiers.
- Signed or temporary download URLs, query signatures, raw browser/IMA session files, or complete network captures.
- Private documents, extracted user content, or screenshots and logs containing any of the above.

- token、cookie、授权头、refresh token、私钥或账号标识；
- 签名/临时下载 URL、查询签名、原始浏览器或 IMA 会话文件、完整网络抓包；
- 私人文档、提取出的用户内容，或包含上述信息的截图和日志。

If a secret was already exposed, revoke or rotate it before reporting. Repository maintainers cannot make an exposed credential safe by deleting a GitHub comment or commit alone.

如果秘密已经泄露，请先吊销或轮换；仅删除 GitHub 评论或提交无法使已暴露的凭据恢复安全。
