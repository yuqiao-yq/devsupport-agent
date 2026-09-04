# AI Debt

这里记录“AI 已生成或修改、但我尚未充分理解或验证”的内容。它不是普通待办列表，也不能用测试通过自动清空。

## 使用规则

1. 不能清楚解释调用链、边界条件或失败行为时，当天登记。
2. 高风险项（权限、写操作、事务、密钥、Agent 停止条件）在解决前不得合并到主分支。
3. 每周至少清理一项，并留下学习或验证证据。
4. 只有在能够解释、复现并验证后，才把状态改为 `Resolved`。

## 未解决

| ID | 日期 | 风险 | 不理解或未验证的内容 | 涉及文件/功能 | 解决标准 | 状态 |
|---|---|---|---|---|---|---|
| AID-003 | 2026-09-04 | Medium | 为什么创建、部分更新和读取要使用不同 Schema，以及哪些字段必须由系统拥有 | `issues/schemas.py`、ADR-0003 | 能独立解释三个模型的数据方向；指出系统字段为何不能进入创建/普通更新；预测额外字段测试结果 | Open |
| AID-004 | 2026-09-04 | Medium | `IssueUpdate` 中字段省略、显式 `null` 和空字符串的区别，以及 `model_fields_set` / `exclude_unset` 的作用 | `IssueUpdate` 与对应测试 | 能预测三种输入的结果；由学习者选择一个未覆盖边界并给出预期，再指示 AI 完成 red → green 验证 | Open |
| AID-005 | 2026-09-04 | Medium | `frozen=True` 能防止什么，以及为什么 `model_copy(update=...)` 不能用于校验不可信更新 | `_IssueSchema`、ADR-0003 | 能解释冻结与重新校验的边界；指出后续 Service 应如何安全地产生更新后的完整模型 | Open |

风险等级：`High` / `Medium` / `Low`。

## 已解决

| ID | 解决日期 | 我现在的解释 | 验证方式 | 证据 |
|---|---|---|---|---|
| AID-001 | 2026-09-04 | `pyproject.toml` 声明依赖意图，`uv.lock` 固定解析结果，`.venv` 是可重建的本地安装产物 | `uv lock --check`、`uv sync --locked`，学习者确认理解 | [Day 1 PR #2](https://github.com/yuqiao-yq/devsupport-agent/pull/2) |
| AID-002 | 2026-09-04 | `src/` 布局让测试验证正确安装后的包，避免因源码恰好位于当前目录而误导性导入成功 | 检查 `devsupport_agent.__file__` 并运行 smoke test，学习者确认理解 | [Day 1 PR #2](https://github.com/yuqiao-yq/devsupport-agent/pull/2) |

## 清理检查

解决一项 AI 债务前确认：

- [ ] 我能不用 AI，向别人解释它为什么这样工作。
- [ ] 我能指出关键代码的位置和职责。
- [ ] 我验证了至少一个失败或边界场景。
- [ ] 相关测试可以稳定复现结论。
- [ ] 必要时已更新规格、ADR 或周记。
