# SPEC-0003：Day 2 Issue 数据契约

- 状态：Review（实现与自动检查完成，待学习者理解验收）
- 日期：2026-09-04
- 对应路线：Week 01 / Day 02
- 对应 Issue：[#1](https://github.com/yuqiao-yq/devsupport-agent/issues/1)
- 对应 PR：[#3](https://github.com/yuqiao-yq/devsupport-agent/pull/3)

## 目标

使用 Pydantic 定义 Issue 的创建输入、部分更新输入和读取输出，让来自 CLI、JSON 或未来 HTTP API 的不可信数据先经过统一校验，再进入业务逻辑。

## 范围

- 定义 `IssuePriority`：`low`、`medium`、`high`。
- 定义 `IssueStatus`：`open`、`closed`。
- 定义 `IssueCreate`、`IssueUpdate`、`IssueRead`。
- 明确字段的必填性、默认值、长度、空白处理和额外字段行为。
- 验证枚举、UUID、带时区时间和 JSON 兼容序列化。
- 校验后的 Schema 作为不可直接赋值修改的值对象使用。
- 使用确定性单元测试覆盖正常路径和失败路径。

## 非目标

- 不实现 Service、Repository、JSON 文件读写或 CLI。
- 不在 Schema 中生成 ID、当前时间或执行状态流转。
- 不引入 FastAPI、数据库、模型 SDK或其他新依赖。
- 不定义未来 HTTP 接口的状态码或错误响应格式。

## 字段契约

### 枚举

| 类型 | 合法值 | 说明 |
|---|---|---|
| `IssuePriority` | `low`、`medium`、`high` | 创建时默认 `medium` |
| `IssueStatus` | `open`、`closed` | 由后续 Service 管理，不允许通过普通更新输入修改 |

### Schema

| Schema | 字段 | 必填 | 约束或默认值 |
|---|---|---:|---|
| `IssueCreate` | `title` | 是 | 去除首尾空白后长度为 1～200 |
|  | `description` | 否 | 默认 `""`，去除首尾空白后最多 2000 字符 |
|  | `priority` | 否 | 默认 `medium` |
| `IssueUpdate` | `title` | 否 | 与创建标题约束相同；提供时不能是 `null` |
|  | `description` | 否 | 与创建描述约束相同；允许 `""` 表示清空，不能是 `null` |
|  | `priority` | 否 | 合法枚举值；提供时不能是 `null` |
| `IssueRead` | `id` | 是 | 合法 UUID |
|  | `title`、`description`、`priority` | 是 | 不使用创建输入的默认值掩盖缺失数据 |
|  | `status` | 是 | 合法状态枚举 |
|  | `created_at`、`updated_at` | 是 | 只接受 datetime 或 ISO 8601 字符串，必须包含时区；拒绝隐式 Unix 时间戳；`updated_at` 不早于 `created_at` |

所有 Schema 都拒绝未声明字段，避免字段拼写错误或调用方越权输入被静默忽略。

## 关键语义

- `IssueCreate` 只接收调用方可以决定的内容；ID、状态和时间由后续 Service 生成。
- `IssueUpdate` 是部分更新：字段省略表示“不修改”，但整个请求至少包含一个字段。
- `null` 不表示“不修改”。显式传入 `null` 会被拒绝，防止调用方的错误输入被静默忽略。
- `description=""` 是一个有效变更，表示主动清空描述。
- Python 对象内部保留 UUID、datetime 和 Enum 类型；跨 JSON 边界时使用 `model_dump(mode="json")` 得到字符串值。
- 校验后的模型被冻结，不能通过属性赋值绕过约束。后续 Service 合并更新后必须重新调用 `model_validate()`；不能把 `model_copy(update=...)` 当作不可信输入的校验入口。

## 失败与边界矩阵

| 输入场景 | 预期行为 |
|---|---|
| 标题为 `""` 或只有空白 | 校验失败，错误定位到 `title` |
| 标题超过 200 字符 | 校验失败 |
| priority/status 不在枚举中 | 校验失败，错误定位到对应字段 |
| 创建输入包含 `id`、`status` 等系统字段 | 作为额外字段拒绝 |
| `IssueUpdate()` 没有任何字段 | 校验失败 |
| 更新字段显式传入 `null` | 校验失败 |
| 更新 description 为 `""` | 校验成功，表示清空描述 |
| 读取模型的时间没有时区 | 校验失败 |
| 读取模型的时间是 Unix 数字时间戳 | 校验失败，避免隐式转换掩盖输入格式错误 |
| `updated_at` 早于 `created_at` | 校验失败 |
| 校验后直接给字段重新赋值 | 校验失败，模型保持冻结 |

## 验收标准

- [x] 三个 Schema 与两个 Enum 符合字段契约。
- [x] 标题和描述会去除首尾空白，空白标题被拒绝。
- [x] 创建默认值明确且可通过测试证明。
- [x] 部分更新能区分字段省略、显式 `null` 和空字符串。
- [x] 系统字段不能通过创建或普通更新输入注入。
- [x] 读取输出能验证 UUID、状态、带时区时间及时间顺序。
- [x] `model_dump(mode="json")` 生成标准库可以编码的数据。
- [x] Schema 单元测试、Ruff、Pyright 与完整 pytest 均通过。
- [ ] 学习者能解释输入/输出模型分离、运行时校验和静态类型检查的区别。

## 测试计划

| 层级 | 场景 | 预期结果 | 实现位置 |
|---|---|---|---|
| Schema 单元测试 | 合法创建及默认值 | 生成规范化的 `IssueCreate` | `backend/tests/test_issue_schemas.py` |
| Schema 单元测试 | 空白/超长标题、非法枚举、额外字段 | 抛出 `ValidationError` | 同上 |
| Schema 单元测试 | 合法、空和含 `null` 的部分更新 | 正确生成变更或拒绝 | 同上 |
| Schema 单元测试 | 合法与非法读取数据 | 正确解析或拒绝 | 同上 |
| Schema 单元测试 | JSON 模式序列化 | UUID、Enum、时间变为 JSON 字符串 | 同上 |

## 代码导读

| 代码概念 | 在本实现中的作用 |
|---|---|
| `Annotated[T, Field(...)]` | 在保留 Python 类型 `T` 的同时附加长度等运行时约束 |
| `_IssueSchema` | 前导下划线表示包内部基类；集中配置拒绝额外字段、字符串 trim 和冻结模型 |
| `Self` | 表示 validator 返回当前模型类型，而不是某个固定父类 |
| `field_validator(mode="before")` | 在 Pydantic 自动转换之前拦截数字时间戳，并显式解析 ISO 时间 |
| `model_validator(mode="after")` | 字段各自有效后，再检查空更新、显式 `null` 或两个时间的相互关系；成功时必须返回 `self` |
| `model_fields_set` | 记录调用方实际提供了哪些字段，用来区分“省略”与默认的 `None` |
| `model_dump(exclude_unset=True)` | 只导出本次更新实际提交的字段，供后续 Service 合并 |
| `model_dump(mode="json")` | 把 UUID、datetime 和 Enum 转成 JSON 可编码值 |
| `frozen=True` | 阻止校验后直接赋值；它不代表 `model_copy(update=...)` 会重新校验 |

## 需要本人理解的内容

1. 类型注解描述期望类型，Pydantic 在运行时把不可信输入校验并转换为符合约束的对象。
2. `IssueCreate`、`IssueUpdate`、`IssueRead` 面向不同数据流，不能用一个“全字段可选”的模型代替。
3. `T | None` 与“字段可以省略”不是同一个概念；更新模型需要显式规定省略与 `null` 的语义。
4. `extra="forbid"` 能阻止拼错字段或系统字段被静默丢弃。
5. Python 模式和 JSON 模式序列化用途不同；持久化或传输时需要 JSON 兼容值。
6. Schema 负责结构校验，创建 ID、状态流转和查找记录属于 Service 的业务规则。

## AI 实现边界

AI 可以实现 Schema 与测试初稿、运行质量检查并解释行为。学习者负责确认字段契约，预测边界输入结果，并在合并前完成理解验收。

## 实现与验证证据

- 首次失败测试：测试先运行，因 `devsupport_agent.issues` 尚不存在而产生预期的 `ModuleNotFoundError`。
- Schema 测试：`uv run pytest -q tests/test_issue_schemas.py` → 26 passed。
- Ruff format：6 files already formatted。
- Ruff lint：All checks passed。
- Pyright：0 errors，0 warnings。
- 完整 pytest：27 passed。
- 实现提交：[`6c9c2ca`](https://github.com/yuqiao-yq/devsupport-agent/commit/6c9c2ca)。
- 理解验收：待完成。

## 参考资料

- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic Fields](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Pydantic Serialization](https://docs.pydantic.dev/latest/concepts/serialization/)
