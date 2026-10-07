---
name: modular-spec
description: "以细粒度 Markdown 文档编写和整理 spec，用链接关联各部分；仅在用户明确要求调研时使用独立调研区，并按用户选择将结论合入 spec。"
---

# Modular Spec

轻量约定 spec 的组织。复用项目已有目录、术语和语言；没有既有约定时，采用下面的结构。

## Spec 的组织(simple example)

```text
docs/
  spec/
    index.md            # 项目概述与各份 spec 的链接
    login.md            # 一个具体主题
    session.md          # 另一个具体主题
  research/             # 仅在用户明确要求调研后按需创建
    login-methods.md    # 一个调研问题
```

- 一个文件聚焦一个具体功能、规则或设计问题。能独立说明的内容优先拆分，但保留理解该主题所需的完整上下文。