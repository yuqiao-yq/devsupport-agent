# ADR-0002：使用 uv、src 布局与 Pyright

- 状态：Accepted
- 日期：2026-09-04

## 背景与约束

本机系统 Python 为 3.9.6，不应被项目安装或升级覆盖。项目需要一套适合 AI 辅助开发、可以稳定复现并且易于审查的 Python 工程基线。

## 考虑过的方案

1. 直接使用系统 Python 和 `pip`。
2. 使用 `venv`、`pip` 和手工维护的 requirements 文件。
3. 使用 `uv` 统一管理 Python、虚拟环境、直接依赖和锁文件。

包布局考虑过仓库根部的 `app/` 和 `src/devsupport_agent/`；类型检查考虑过 mypy 和 Pyright。

## 决定

- 使用 `uv` 管理 Python 3.12、`.venv`、依赖和 `uv.lock`。
- 使用 `src/devsupport_agent/` 作为 Python 包目录。
- 使用 pytest 运行测试、Ruff 负责格式与 lint、Pyright strict 负责静态类型检查。
- 分发名使用连字符 `devsupport-agent`，Python 导入包使用下划线 `devsupport_agent`。

## 正面影响

- 不依赖或污染系统 Python。
- 锁文件可以让本地和 CI 获得一致的依赖解析结果。
- `src/` 布局可以更早发现打包和导入配置错误。
- Pyright 的类型模型与 TypeScript 开发经验较容易建立对应关系。

## 代价与风险

- 初期需要理解分发名、导入包名、构建后端和可编辑安装之间的区别。
- 新增工具会带来少量配置成本。
- strict 类型检查可能暴露第三方库类型信息不完整的问题，应局部处理，而不是全局关闭检查。

## 验证方法

- 从 `backend/` 执行 `uv sync --locked` 后可以导入包。
- 导入路径必须位于 `backend/src/devsupport_agent/`。
- pytest、Ruff 和 Pyright 在本地及后续 CI 中通过。

## 重新评估条件

只有在目标部署环境不支持当前工具链，或类型检查器对核心依赖产生无法局部处理的系统性问题时重新评估。
