# Week 01：Python 工程基础与 Issue CLI

- 周期：2026-09-04 ～ 进行中
- 状态：进行中（Day 1 已合并；Day 2 实现与自动检查完成，待理解验收）
- 对应 Issue：[#1](https://github.com/yuqiao-yq/devsupport-agent/issues/1)
- 对应 PR：Day 1 [#2](https://github.com/yuqiao-yq/devsupport-agent/pull/2)；Day 2 [#3](https://github.com/yuqiao-yq/devsupport-agent/pull/3)

## 本周目标

建立可运行、可测试的 Python 工程，实现基于 Pydantic Schema、Service/Repository 分层和 JSON 持久化的 Issue 命令行工具，并能解释每条命令的完整执行流程。

本周不做 FastAPI、HTTP 接口或数据库接入。

## 验收标准

- [x] Python 工程能够按 README 中的命令安装并运行。
- [x] 使用 Pydantic 定义 Issue 的创建、更新与读取数据结构及校验规则。
- [ ] Service 负责业务规则，Repository 负责 JSON 文件读写，两者职责清晰。
- [ ] CLI 支持 `create`、`list`、`show`、`update`、`close` 命令。
- [ ] 数据在程序退出并重新运行后仍可从 JSON 文件恢复。
- [ ] 非法输入、未知 Issue ID 和文件读写异常都有明确行为。
- [ ] 完成 12～15 个确定性测试，覆盖核心成功路径与失败路径。
- [ ] 我能不看代码说明调用链、数据结构、持久化过程和主要失败点。
- [x] 本周新增的 AI 债务已记录，至少清理一项。

## 完成的功能

| 功能 | 状态 | 验证方式 | 相关提交/PR |
|---|---|---|---|
| Python 工程初始化 | 已完成 | `uv sync --locked` + 全部 Day 1 检查 | [`cb5ce97`](https://github.com/yuqiao-yq/devsupport-agent/commit/cb5ce97) / [#2](https://github.com/yuqiao-yq/devsupport-agent/pull/2) |
| Pydantic Issue Schemas | 已实现，待理解验收 | 26 条 Schema 测试 + 完整质量检查 | [`6c9c2ca`](https://github.com/yuqiao-yq/devsupport-agent/commit/6c9c2ca) / [#3](https://github.com/yuqiao-yq/devsupport-agent/pull/3) |
| Service/Repository 分层 | 未开始 | Service 单元测试 | |
| JSON 持久化 | 未开始 | 临时文件测试与重启验证 | |
| `create` / `list` / `show` | 未开始 | CLI 测试 | |
| `update` / `close` | 未开始 | CLI 测试 | |

## 调用链与我的理解

```text
终端命令
→ CLI：解析参数
→ Pydantic Schema：校验并转换输入
→ Service：执行业务规则
→ Repository：读取或写入 JSON 文件
→ Service：返回 Issue 或业务错误
→ CLI：格式化结果并设置退出状态
```

用自己的话回答：

1. 每条命令从哪个文件、哪个函数进入？
2. CLI、Schema、Service 和 Repository 各自负责什么？
3. Issue 如何从命令行参数变成 Python 对象，再写入 JSON？
4. `update` 与 `close` 如何找到并修改正确的 Issue？
5. JSON 文件不存在、内容损坏或目标 ID 不存在时会发生什么？
6. 哪些测试分别证明校验、业务规则、持久化和 CLI 行为正确？

## 数据结构

| Schema/模型 | 用途 | 必填字段 | 约束 | 使用位置 |
|---|---|---|---|---|
| IssueCreate | 创建 Issue | `title` | 标题 1～200；描述默认空字符串且最多 2000；优先级默认 `medium`；拒绝系统字段 | CLI → Service |
| IssueUpdate | 部分更新 Issue | 至少一个变更字段 | 可改标题、描述、优先级；字段省略表示不改；拒绝 `null` 与状态修改；允许空字符串清空描述 | CLI → Service |
| IssueRead | 对外展示完整 Issue | 全部字段 | UUID；合法优先级/状态；时间带时区且更新时间不早于创建时间；无默认值掩盖缺失数据 | Service → CLI |

## CLI 命令清单

| 命令 | 输入 | 成功输出 | 失败场景 | 状态 |
|---|---|---|---|---|
| `create` | 待填写 | 新建的 Issue | 非法字段、无法写入 | 未开始 |
| `list` | 待填写 | Issue 列表 | 无法读取数据 | 未开始 |
| `show` | Issue ID | 指定 Issue | ID 不存在 | 未开始 |
| `update` | Issue ID 与变更字段 | 更新后的 Issue | ID 不存在、字段非法 | 未开始 |
| `close` | Issue ID | 关闭后的 Issue | ID 不存在 | 未开始 |

## AI 协作记录

### AI 实现了什么

- 安装 `uv`，并用它安装项目专用 Python 3.12.14。
- 初始化 `backend/` 的 `src/` 包布局、依赖锁和质量工具配置。
- 创建包入口、smoke test、后端 README、Day 1 SPEC 与工程 ADR。
- 执行依赖同步、导入、格式、lint、类型和测试检查。
- 先编写 Day 2 SPEC，再用测试定义 Issue Schema 契约并保留一次预期失败。
- 实现 `IssuePriority`、`IssueStatus`、`IssueCreate`、`IssueUpdate`、`IssueRead` 及 26 条 Schema 测试。
- 新增 ADR-0003，记录为何分离创建、更新和读取 Schema。

### 我重点审查了什么

- [x] `pyproject.toml` 只包含 Day 1 需要的依赖和质量工具，没有提前引入框架。
- [x] `.python-version`、`.venv` 和 `uv.lock` 的职责清晰。
- [x] `devsupport_agent` 实际从 `backend/src/` 导入，而不是依赖临时 `PYTHONPATH`。
- [x] smoke test 只证明包可被正确安装和导入，没有虚构业务行为。
- [ ] CLI 只负责参数解析与结果展示，没有混入业务规则或直接操作 JSON。
- [ ] Service 负责 Issue 的创建、查询、更新和关闭规则。
- [ ] Repository 只处理数据存取，并能被测试替身替换。
- [ ] Pydantic Schema 的必填项、可选项和边界校验符合规格。
- [ ] JSON 的读取、写回、文件不存在和内容损坏行为明确。
- [ ] 测试使用临时文件，没有污染真实学习数据。
- [ ] 没有引入不必要的依赖或无关重构。

### 我亲手验证或修改了什么

- 学习者完成 Day 1 概念理解检查，确认理解项目 Python 隔离、依赖声明/锁定/安装三者关系、`src/` 布局以及三类质量工具的职责，并批准合并 PR #2。
- Day 2 待学习者完成：解释三个 Schema 的职责，预测 omitted / `null` / `""` 的行为，并选择一个未覆盖边界、给出预期后指示 AI 完成测试。

## 测试计划与证据

目标测试数量：12～15 个。不要只写“测试通过”，应保留可复现的命令与结果摘要。

```text
# uv run python --version
Python 3.12.14

# uv lock --check
锁文件有效

# uv run python -c "import devsupport_agent; print(devsupport_agent.__file__)"
backend/src/devsupport_agent/__init__.py

# uv run ruff format --check .
3 files already formatted

# uv run ruff check .
All checks passed!

# uv run pyright
0 errors, 0 warnings, 0 informations

# uv run pytest -q
27 passed
```

| 测试层级 | 建议场景 | 预期结果 | 实际证据 |
|---|---|---|---|
| Schema | 合法与非法的创建/更新/读取输入 | 正确解析或拒绝 | `uv run pytest -q tests/test_issue_schemas.py` → 26 passed |
| Service | create/list/show/update/close | 业务行为正确 | |
| Repository | JSON 保存后重新加载 | 数据保持一致 | |
| CLI | 五个命令的关键路径 | 输出与退出状态符合约定 | |
| 失败路径 | 未知 ID、损坏文件或写入失败 | 错误明确且不产生错误数据 | |

## 主动制造的失败场景

| 场景 | 预期行为 | 首次结果 | 修复或结论 |
|---|---|---|---|
| 创建时标题为空、只有空白或超过 200 字符 | Pydantic 拒绝输入 | 三类输入均按预期失败 | `test_issue_create_rejects_invalid_title` 稳定复现 |
| 更新没有字段或显式传入 `null` | Pydantic 拒绝输入 | 四类输入均按预期失败 | `test_issue_update_rejects_empty_or_null_changes` 稳定复现 |
| 创建/更新尝试写入系统字段 | Pydantic 拒绝额外字段 | `status` 被拒绝 | create/update 两个测试稳定复现 |
| 读取时间传入无时区字符串或 Unix 数字时间戳 | Pydantic 拒绝隐式或含糊时间 | 两类输入均按预期失败 | `test_issue_read_rejects_invalid_system_fields` 稳定复现 |
| `show` / `update` / `close` 使用未知 ID | 返回明确业务错误，不改动原数据 | | |
| JSON 文件不存在 | 按约定初始化为空数据集或给出明确错误 | | |
| JSON 内容损坏 | 明确报错，不静默覆盖原文件 | | |

## 本周架构决策

- [ADR-0002：使用 uv、src 布局与 Pyright](../adr/0002-use-uv-src-layout-and-pyright.md)。
- [ADR-0003：分离 Issue 的创建、更新与读取 Schema](../adr/0003-separate-issue-input-and-output-schemas.md)。

## 遇到的问题

| 问题 | 根因 | 解决方式 | 如何防止再次发生 |
|---|---|---|---|
| 待填写 | | | |

## 尚未理解的内容

- Day 1 的 AID-001、AID-002 已完成初步理解验收并移入已解决列表；周日复盘时再做一次无提示复述，验证记忆是否稳定。
- Day 2 新增 AID-003、AID-004，分别跟踪模型分离与部分更新语义；完成解释和亲手边界测试后再关闭。

## 本周复盘

- 我现在能够解释的内容：
- 我仍需要查资料或实验的内容：
- AI 生成代码中我发现的问题：
- 下周应该继续保持的做法：
- 下周需要调整的做法：

## 下周计划

- [ ] 待填写。
