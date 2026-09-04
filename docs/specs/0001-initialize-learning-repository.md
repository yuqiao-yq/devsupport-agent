# SPEC-0001：初始化 Agent 工程学习仓库

- 状态：Accepted
- 日期：2026-09-04

## 目标

建立一个产品优先、可持续维护的 GitHub 仓库，用于承载 16 周 Agent 工程学习、DevSupport Agent 实现和最终求职作品。

## 范围

- 创建项目首页和 16 周路线。
- 建立周记、规格、ADR、AI Debt、Issue 和 PR 模板。
- 建立密钥、数据和生成内容的提交边界。
- 记录 AI 辅助开发中本人负责的审查与验证职责。

## 非目标

- 本任务不创建 Python、React 或 Agent 功能代码。
- 本任务不添加尚未使用的依赖和 CI。
- 本任务不制造空的正式模块目录来表示虚假进度。

## 验收标准

- [x] README 能说明项目目标、目标架构、路线、工程原则和当前状态。
- [x] ROADMAP 覆盖 Week 01 至 Week 16，并包含可核验的验收项。
- [x] Week 01 周记可以记录目标、AI 协作、测试证据、失败和复盘。
- [x] 提供可复用的 SPEC、ADR、Issue 和 PR 模板。
- [x] `.gitignore` 排除常见密钥、环境、依赖、缓存和本地数据库文件。
- [x] `.env.example` 仅包含变量名和安全占位值。
- [x] SECURITY 明确禁止提交公司资料、真实用户数据和未脱敏 Trace。
- [x] 仓库不含真实凭证和公司内部内容。

## 验证证据

初始化提交应通过：

```text
git diff --cached --check
git status --short
```

远端创建后，还应确认默认分支为 `main`，并从 GitHub 页面检查 README 内的相对链接。
