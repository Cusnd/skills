# Personal Agent Skills

[![validate](https://github.com/Cusnd/skills/actions/workflows/validate.yml/badge.svg)](https://github.com/Cusnd/skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.en.md) | 简体中文

这是由 [SorenLiu](https://github.com/Cusnd) 个人维护的 agent skills 集合，面向 Codex、ChatGPT 桌面端及其他兼容 Agent Skills 格式的环境。本仓库不是 OpenAI 官方项目，也不代表相关第三方服务。

仓库当前采用个人维护、Issue-only 模式：欢迎提交问题报告和功能建议，但 Pull requests 已关闭，不接受外部代码贡献。MIT 许可证仍允许你 fork、修改和独立发布符合许可证要求的版本。

## Skills

| Skill | 用途 | 平台与依赖 | 调用策略 |
| --- | --- | --- | --- |
| [`frontend-design-concept`](frontend-design-concept/SKILL.md) | 从艺术视角理解风格与感受，以形态、色彩、空间、材质和动势形成可修改的设计描述，再按请求实现前端。 | 构思阶段不绑定工具；实现与视觉验证使用目标项目的技术栈及可用的浏览器能力。 | 默认允许匹配调用；可使用 `$frontend-design-concept` 明确指定。 |
| [`ima-pdf-extractor`](ima-pdf-extractor/SKILL.md) | 从 Windows `ima.copilot` 客户端保存用户有权导出的原始文件、PDF、笔记、文章或知识库内容，并将登录凭据和签名 URL 留在本地。 | Windows；直接资源脚本使用 Python 3.10+ 标准库；结构化内容可能需要受控的浏览器本地能力。 | 仅显式调用：`$ima-pdf-extractor`。 |
| [`orchestrate-workflow`](orchestrate-workflow/SKILL.md) | 在用户请求多代理或独立会话编排的中等、复杂任务中，由当前会话协调真实执行器完成交付；复杂任务的具体执行全部委派。 | 支持真实子代理或独立执行上下文的 agent 环境；具体能力以宿主可调用工具为准。 | 默认允许匹配调用；建议使用 `$orchestrate-workflow` 明确指定。 |
| [`pdf-watermark-removal`](pdf-watermark-removal/SKILL.md) | 检查用户授权的 PDF，以破坏性最低的方法移除重复水印或明确指定的宣传页，并同时进行结构和渲染验证。 | 需要 agent 可用的 PDF 解析器、渲染器及图像检查能力；仓库不绑定单一工具链。 | 默认允许匹配调用；建议使用 `$pdf-watermark-removal` 明确指定。 |

### `frontend-design-concept`

- 先建立艺术构想，用连贯的文字描绘形色、空间、触感与动势，让人能想象画面，再补充界面实现依据。
- 理解“扁平”“飘逸的尾感”等风格与感受词，允许情绪、装饰与视觉张力，不把它们立即简化为 CSS 效果或组件清单。
- 只要求构思时独立交付描述；要求实现时先呈现构思再继续，用户明确要求先审核时才等待确认。
- 实现后先回看整体表现力与局部细节，再检查阅读和操作；技术检查通过不等于艺术构想成立。

### `ima-pdf-extractor`

- 优先保存预览中暴露的原始资源，而不是从 Chromium 缓存块猜测文件。
- 仅处理用户明确指定且有权导出的内容；不会把“客户端可见”当作批量导出授权。
- 沿用已明确的目标、关键词和授权，仅在目标歧义、范围缺失或需要用户操作时提问；批量下载前核实范围与模式。笔记默认 Markdown，URL 和文章默认保存链接，离线副本按请求生成。
- IMA 的部分请求形态并非公开 API，可能随客户端版本变化；失效时应重新观察当前本地会话，而不是放宽凭据边界。
- token、cookie、账号标识、原始会话内容、签名 URL 和查询签名不得进入聊天、日志、文件名或持久化产物。

### `orchestrate-workflow`

- 当前会话持续承担编排与用户沟通，保留用户意图、总体决策和协调上下文；普通小任务不适用。
- 中等任务可直接使用子代理承担聚焦工作；复杂任务的调查、实现、验证、集成和后续修复全部交给真实执行上下文，编排会话评估结果并协调交付。
- 按工作边界和依赖选择并行或串行，交接任务所需上下文并隔离宿主编排策略；沿用实际授权，不因委派或 YOLO 模式扩大外部操作权限。

### `pdf-watermark-removal`

- 先结合 PDF 对象结构与页面渲染确定水印表示，再选择对象删除、窄范围裁剪/遮盖或经用户接受的栅格修复。
- 始终写入新的派生文件，不覆盖源 PDF；源文件哈希必须保持不变。
- 仅去水印的请求不包含删页；仅删除用户明确指定的页面，或在请求包含宣传页清理时经检查确认的宣传页。
- 对无法可靠恢复的正文重叠水印采取失败关闭，不把遮盖、裁剪或图像修复描述为无损删除。

## 安装

Codex 会从用户级 `$HOME/.agents/skills` 以及仓库级 `.agents/skills` 等位置发现本地 skills。详细规则见 [OpenAI Skills 官方文档](https://learn.chatgpt.com/docs/build-skills)。本仓库按“一个顶层目录对应一个 skill”分发；只安装你需要的目录。

### Windows PowerShell：复制单个 skill

```powershell
git clone https://github.com/Cusnd/skills.git
Set-Location .\skills

$target = Join-Path $HOME ".agents\skills\ima-pdf-extractor"
if (Test-Path -LiteralPath $target) { throw "Target already exists: $target" }
New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
Copy-Item -Recurse -LiteralPath ".\ima-pdf-extractor" -Destination $target
```

如需安装另一个 skill，将示例中的 `ima-pdf-extractor` 替换为上方目录表中所需的 skill 名称。已有目标目录时先检查本地修改，不要直接覆盖。

### macOS/Linux：符号链接单个 skill

```bash
git clone https://github.com/Cusnd/skills.git
cd skills

mkdir -p "$HOME/.agents/skills"
test ! -e "$HOME/.agents/skills/pdf-watermark-removal"
ln -s "$(pwd)/pdf-watermark-removal" "$HOME/.agents/skills/pdf-watermark-removal"
```

Codex 通常会自动检测 skill 变化；若新安装项没有出现，请重启 Codex。

## 调用

在 Codex CLI 或 IDE 中输入 `$` 选择 skill，或在提示中直接点名：

```text
$frontend-design-concept 为这个网站先从艺术角度展开构思，写出形色、空间与动势的设计描述，再据此实现前端。

$ima-pdf-extractor 保存我已在 ima.copilot 中打开并有权导出的这份 PDF。

$orchestrate-workflow 由当前会话协调真实执行器完成这个复杂任务，保留我的意图，并委派实现和验证。

$pdf-watermark-removal 检查这些 PDF，保留源文件并生成通过验证的去水印副本。
```

调用 skill 不会扩大任务授权。已明确的授权和选项在当前任务中继续有效，无需重复确认；新增范围、强制结束应用、CDP 调试和栅格重建等仍遵守各 skill 的适用授权与停止条件。临时内容和交付文件保存在源码仓库之外。

完成适用验证后直接交付，仅因新修改、失败或未解决疑点追加检查。批量任务保留通过验证的结果，逐项报告失败；链接回退不等同于离线副本已完成。

## 安全与隐私

- 仅处理你拥有或获准处理的内容。
- 不要在公开 Issue 中提交 token、cookie、授权头、签名 URL、IMA 会话文件、账号标识、私人文档或包含这些数据的截图/日志。
- 安全漏洞请按 [`SECURITY.md`](SECURITY.md) 通过 GitHub Private Vulnerability Reporting 私下报告。
- 仓库中的 skill 不授予对第三方服务、内容或接口的额外访问权。

## Issues 与维护

- [Bug report](https://github.com/Cusnd/skills/issues/new?template=bug_report.yml)：报告可复现的 skill 或仓库问题。
- [Feature request](https://github.com/Cusnd/skills/issues/new?template=feature_request.yml)：建议改进现有 skill 或新增个人维护能力。
- Pull requests 已关闭。维护者会自行评估 Issue，并在仓库中直接实现接受的变更。

仓库维护约定见 [`AGENTS.md`](AGENTS.md)。本地结构检查入口为：

```text
python scripts/validate_repo.py
```

## 许可证

本仓库源码和文档采用 [MIT License](LICENSE)。该许可证不覆盖通过 skill 处理或下载的第三方内容。
