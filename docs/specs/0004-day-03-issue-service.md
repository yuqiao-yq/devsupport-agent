# SPEC-0004：Day 3 Issue Service 与 Repository 边界

- 实现状态：Verified（本地技术检查通过）
- 理解状态：Pending（AID-006～007 Open）
- 日期：2026-09-08
- 对应路线：Week 01 / Day 03
- 对应 Issue：[#1](https://github.com/yuqiao-yq/devsupport-agent/issues/1)
- 对应 PR：[#4](https://github.com/yuqiao-yq/devsupport-agent/pull/4)

## 目标

通过 Issue 创建和查询两个用例建立 Service 与 Repository 的最小边界：Service 负责业务流程和系统字段，Repository 只负责完整 Issue 的存取，并且 Service 不依赖具体存储实现。

## 范围

- 定义 `IssueRepository` Protocol，包含 `add()`、`get()`。
- 实现 `InMemoryIssueRepository`，作为第一个可运行的存储适配器。
- 实现 `IssueService.create()`、`IssueService.get()`。
- 定义稳定的 `IssueNotFoundError`、`IssueAlreadyExistsError`。
- 为 Service 注入 UUID factory 和 clock，使测试无需修改全局函数且完全确定。
- 使用 Day 2 的 `IssueCreate` 作为输入、`IssueRead` 作为完整状态和输出。

## 非目标

- 不实现 `list`、`update`、`close`；它们在后续切片扩展。
- 不读写 JSON 文件，不处理文件不存在、损坏或权限错误。
- 不实现 CLI、HTTP API、数据库、事务、并发或鉴权。
- 不引入通用 CRUD 基类、Unit of Work、事件系统或新依赖。
- 不在 Repository 中生成 ID、时间、初始状态或面向调用方的业务错误。

## 分层职责

| 层 | 负责 | 不负责 |
|---|---|---|
| Schema | 校验输入/输出结构与字段约束 | 查找数据、生成系统字段、保存数据 |
| Service | 编排用例；生成 ID/时间；决定初始状态；把“未找到”转换为业务错误 | 了解字典、JSON、文件路径或数据库细节 |
| Repository Protocol | 声明 Service 所需的最小存取行为 | 提供运行时数据校验或具体存储逻辑 |
| In-memory adapter | 在内存字典中实现 add/get；阻止重复 ID 覆盖 | 决定创建流程或如何向用户展示错误 |

## 调用链

### 创建

```text
IssueCreate
→ IssueService.create
→ id_factory() 与 clock() 各调用一次
→ 组合 OPEN 状态和完整字段
→ IssueRead 再次校验
→ IssueRepository.add
→ 返回 IssueRead
```

### 查询

```text
UUID
→ IssueService.get
→ IssueRepository.get
→ 找到：返回 IssueRead
→ 未找到：抛出 IssueNotFoundError
```

## 接口契约

### `IssueRepository`

```python
class IssueRepository(Protocol):
    def add(self, issue: IssueRead) -> None: ...
    def get(self, issue_id: UUID) -> IssueRead | None: ...
```

- `add()` 只接收完整且已校验的 `IssueRead`。
- 相同 ID 已存在时抛出 `IssueAlreadyExistsError`，不能覆盖原记录。
- `get()` 找到时返回对应对象，不存在时返回 `None`。
- Repository 不把 `None` 转成 `IssueNotFoundError`；这是 Service 对查询用例的解释。
- Protocol 依靠结构化类型检查：实现类只要提供兼容方法即可，不要求继承 Protocol。

### `IssueService.create()`

- 保留 `IssueCreate` 中经过校验的 title、description、priority。
- ID 来自注入的 `id_factory`。
- `created_at` 和 `updated_at` 使用同一次 `clock` 结果。
- 初始状态固定为 `IssueStatus.OPEN`。
- 构造完整数据时调用 `IssueRead` 校验，不使用 `model_copy(update=...)`。
- Repository 成功保存后才返回 Issue。
- ID 冲突时原样传播 `IssueAlreadyExistsError`，不自动重试或静默换 ID。

### `IssueService.get()`

- 使用传入的 UUID 调用 Repository。
- 找到时原样返回完整 `IssueRead`，不产生写操作。
- 未找到时抛出包含目标 ID 的 `IssueNotFoundError`。

## 依赖注入

生产默认值：

- `id_factory=uuid4`
- `clock` 返回带 UTC 时区的当前时间

测试注入固定函数，以证明结果来源并避免依赖真实时间或随机 UUID。clock 必须返回带时区的 datetime；若配置错误，`IssueRead` 的校验应暴露问题，而不是静默补时区。

## 错误语义

| 场景 | 产生位置 | 对外行为 | 数据变化 |
|---|---|---|---|
| 查询未知 ID | Service | `IssueNotFoundError(issue_id)` | 无 |
| 新增重复 ID | Repository adapter | `IssueAlreadyExistsError(issue_id)` | 保留原记录，不覆盖 |
| clock 返回无时区时间 | Schema（由 Service 构造触发） | `ValidationError`，表示依赖配置/代码错误 | 不调用 `add()` |
| 输入标题或优先级非法 | Day 2 Schema | 调用 Service 前已失败 | 无 |

## 验收标准

- [x] Service 的类型只依赖 `IssueRepository` Protocol，不依赖内存实现。
- [x] 创建时 UUID factory 和 clock 各调用一次，两个时间完全相同，状态为 `open`。
- [x] 创建成功后 Repository 可以使用相同 ID 查询到该对象。
- [x] 查询未知 ID 抛出包含该 ID 的 `IssueNotFoundError`。
- [x] 重复 ID 抛出 `IssueAlreadyExistsError`，且原对象不被覆盖。
- [x] 无时区 clock 结果被拒绝，失败前没有写入。
- [x] 实现中没有 JSON、CLI、FastAPI、数据库或新增依赖。
- [x] Service、Repository contract、Ruff、Pyright 与完整 pytest 均通过。
- [ ] 学习者能解释 Schema、Service、Repository 的职责及依赖注入的目的。

## 测试计划

| 场景 | 关键断言 |
|---|---|
| 创建 Issue | 固定 ID、OPEN 状态、相同时间和输入内容均正确 |
| 注入依赖调用次数 | UUID factory、clock 各调用一次 |
| 查询已存在 Issue | 返回保存的对象，不产生额外写入 |
| 查询未知 Issue | 类型化错误包含目标 UUID |
| 重复 ID | 抛出冲突错误，原记录保持不变 |
| 无时区 clock | 完整模型校验失败，Repository 中没有记录 |
| Repository 契约 | 每个 adapter 都运行相同的 add/get、未知 ID、重复 ID 不覆盖测试 |
| 结构化替换 | 一个不继承 Protocol 的 recording fake 可传入 Service 并通过 Pyright |

## 需要本人理解的内容

1. 为什么 Service 不应直接 import 或创建 JSON Repository？
2. Protocol 与继承某个具体基类有什么区别？Pyright 能证明什么、不能证明什么？
3. 为什么 UUID 和时间要注入，而不是在测试中修改全局函数？
4. Repository 返回 `None`，为什么由 Service 决定它代表“业务上未找到”？
5. 为什么 Repository 接收完整 `IssueRead`，而不是未完成的 `IssueCreate`？
6. 为什么通过 `IssueRead(...)` 构造器或 `model_validate()` 重新验证完整状态，而不能把 `model_copy(update=...)` 当作校验入口？

## 代码导读

| 概念 | 在本实现中的作用 |
|---|---|
| `Protocol` | 描述 Service 需要的 `add/get` 方法；实现类不必继承它 |
| 结构化类型 | “方法形状兼容即可”；由 Pyright 检查，Python 运行时不会自动执行类型注解 |
| adapter | `InMemoryIssueRepository` 把端口映射到字典；未来 JSON 是另一个实现 |
| dependency injection | 构造 Service 时传入 Repository、UUID factory 和 clock，而不是在方法内部固定创建 |
| fake | `RecordingRepository` 是有简单行为的测试替身，用来观察 Service 如何调用端口 |
| contract test | 对每个 adapter 执行相同行为测试，补足 Protocol 无法证明的冲突/缺失语义 |
| 类型化错误 | 错误类型与目标 UUID 一起表达稳定失败，不依赖解析英文字符串 |

## AI 实现边界

AI 可以实现 Protocol、内存适配器、Service、类型化错误和测试初稿，并运行完整检查。学习者负责理解分层调用链、预测至少一个业务失败场景；未完成内容如实登记 AI Debt，合并不等于掌握。

## 实现与验证证据

- 首次失败测试：测试先运行，因 `InMemoryIssueRepository` 尚不存在而产生预期 ImportError。
- Service 测试：`uv run pytest -q tests/test_issue_service.py` → 6 passed。
- Repository contract tests：3 passed；当前运行 `in-memory` adapter，Day 4 加入 JSON adapter。
- Ruff format：11 files already formatted。
- Ruff lint：All checks passed。
- Pyright：0 errors，0 warnings。
- 完整 pytest：37 passed。
- 实现提交：[`a89e79d`](https://github.com/yuqiao-yq/devsupport-agent/commit/a89e79d)。
- 理解验收：待完成。

## 参考资料

- [Python 3.12 `typing.Protocol`](https://docs.python.org/3.12/library/typing.html#typing.Protocol)
- [Python 3.12 `datetime`](https://docs.python.org/3.12/library/datetime.html)
- [Python 3.12 `uuid`](https://docs.python.org/3.12/library/uuid.html)
