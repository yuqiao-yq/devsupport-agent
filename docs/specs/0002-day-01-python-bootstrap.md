# SPEC-0002：Day 1 Python 工程基线

- 状态：Verified
- 日期：2026-09-04
- 对应路线：Week 01 / Day 01
- 对应 Issue：[#1](https://github.com/yuqiao-yq/devsupport-agent/issues/1)
- 对应 PR：[#2](https://github.com/yuqiao-yq/devsupport-agent/pull/2)

## 目标

建立一个可重复安装、可导入、可格式检查、可静态检查、可测试的 Python 后端最小工程，为后续 Issue 领域模型和业务逻辑提供稳定基础。

## 范围

- 使用 `uv` 管理项目 Python、虚拟环境、依赖和锁文件。
- 项目使用 Python 3.12，不修改或替换 macOS 系统 Python。
- 采用 `src/devsupport_agent/` 包布局。
- 添加 Pydantic 运行时依赖，以及 pytest、Ruff、Pyright 开发依赖。
- 创建一个只验证包安装与导入的 smoke test。
- 记录并执行 Day 1 的全部验收命令。

## 非目标

- 不实现 Issue Schema、Service、Repository 或 CLI。
- 不引入 FastAPI、SQLAlchemy、模型 SDK 或部署配置。
- 不创建尚未使用的空模块。
- 不追求测试覆盖率指标。

## 验收标准

- [x] `uv run python --version` 显示 Python 3.12.x。
- [x] `uv lock --check` 确认锁文件与项目配置一致。
- [x] `uv sync --locked` 可以从锁文件同步环境。
- [x] `devsupport_agent` 的导入路径来自 `backend/src/`。
- [x] `uv run ruff format --check .` 通过。
- [x] `uv run ruff check .` 通过。
- [x] `uv run pyright` 通过且没有类型错误。
- [x] `uv run pytest -q` 显示一条 smoke test 通过。
- [x] `git diff --check` 通过。

## 需要本人理解的内容

1. `pyproject.toml` 描述项目、依赖和工具配置；`uv.lock` 固定解析后的完整依赖版本。
2. `.python-version` 选择项目 Python，不会改变系统 Python。
3. `.venv/` 是本机可重建环境，不进入 Git；`uv.lock` 必须进入 Git。
4. `src/` 布局要求项目先被正确安装，避免从仓库当前目录产生误导性的导入成功。
5. pytest、Ruff、Pyright 分别验证运行行为、代码风格/常见错误和静态类型。

## 实现与验证证据

- Python：3.12.14，由 `uv` 管理；系统 Python 3.9.6 未修改。
- `uv lock --check`：锁文件有效。
- 包导入位置：`backend/src/devsupport_agent/__init__.py`。
- Ruff format：3 个 Python 文件格式正确。
- Ruff lint：全部检查通过。
- Pyright：0 errors，0 warnings。
- pytest：1 passed。
- 实现提交：[`cb5ce97`](https://github.com/yuqiao-yq/devsupport-agent/commit/cb5ce97)。
- 理解验收：学习者已确认理解核心关系，并于 2026-09-04 批准合并。
- PR：[#2](https://github.com/yuqiao-yq/devsupport-agent/pull/2)。
