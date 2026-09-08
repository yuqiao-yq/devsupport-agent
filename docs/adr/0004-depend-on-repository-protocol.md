# ADR-0004：Service 依赖 Repository Protocol

- 状态：Accepted
- 日期：2026-09-08

## 背景与约束

Issue Service 需要保存和查询完整 Issue，但 Day 3 尚未引入 JSON 或数据库。业务流程不能绑定某个字典、文件路径或未来数据库 Session，否则更换存储时会迫使 Service 和测试一起修改。

同时，Python 类型注解不会在运行时自动执行契约，因此必须区分“方法签名兼容”和“行为语义一致”。

## 考虑过的方案

1. `IssueService` 直接创建或操作内存字典，后续再改成 JSON。
2. 定义抽象基类，要求所有 Repository 显式继承。
3. 定义 `typing.Protocol`，让 Service 依赖最小行为，具体 adapter 通过结构化类型满足它。

## 决定

选择方案 3：

- `IssueRepository` 只声明当前用例需要的 `add()`、`get()`。
- `IssueService` 的构造器只接受该 Protocol，不 import 具体 adapter。
- `InMemoryIssueRepository` 不继承 Protocol，但用兼容方法满足静态类型检查。
- Repository 的“重复 ID 不得覆盖”等行为由可复用于所有 adapter 的契约测试保证，而不是假设 Protocol 能证明。
- Day 4 增加 JSON adapter 时，将它加入同一组 Repository contract tests。

## 正面影响

- Service 测试不依赖文件系统，业务失败与 I/O 失败可以分开定位。
- 更换存储 adapter 不需要改变 Service 接口。
- 测试 fake 只需提供相同方法，不必继承生产类。
- Protocol 保持最小，并会随真实用例渐进扩展。

## 代价与风险

- Protocol 只提供静态签名约束，不能在运行时阻止错误实现。
- `add()` 的冲突语义、`get()` 的缺失语义仍需文档和共享契约测试。
- 当前同步接口适合本地文件和 SQLite；未来若存储全面异步，需要重新评估接口形态。
- 不同 adapter 可能返回值相等但对象身份不同，调用方不得依赖 `is`。

## 验证方法

- Pyright strict 验证 `InMemoryIssueRepository` 和不继承 Protocol 的 recording fake 均可注入 Service。
- Service 测试确认 create/get 只经过 Repository 方法。
- Repository contract tests 对每个 adapter 验证新增、未知 ID 和重复 ID 不覆盖。
- 测试只比较返回值，不要求 adapter 返回同一个 Python 实例。

## 重新评估条件

当出现事务边界、跨多个 Repository 的原子操作、全面异步 I/O，或 Protocol 方法持续膨胀时，再评估 Unit of Work、ABC 或更细的端口。
