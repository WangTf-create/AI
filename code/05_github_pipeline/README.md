# GitHub workflow 样例：用 lint + pytest 管住 AI 产出

**核心思路**：AI 能大量产出代码，但进入主干之前，必须先过确定性门禁。这里不演示发包，不讲发布链路，只演示最小可用的团队质量管线：

```text
issue -> branch -> commit -> PR -> GitHub workflow(ruff + pytest) -> 人审 -> merge
```

## 目录里有什么

| 工件 | 作用 |
|---|---|
| [.github/ISSUE_TEMPLATE/task.md](.github/ISSUE_TEMPLATE/task.md) | issue 模板：写清目标、验收标准、不要动的范围。|
| [.github/pull_request_template.md](.github/pull_request_template.md) | PR 模板：要求一个 PR 只做一件事，并列出自检。|
| [COMMIT_CONVENTION.md](COMMIT_CONVENTION.md) | 分支和 commit 约定：让改动能追溯到 issue。|
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | workflow 门禁：push / PR 自动跑 `ruff check src tests` 和 `pytest -q`。|
| [src/orderkit/](src/orderkit/) + [tests/](tests/) | 最小业务代码和测试，让 workflow 有真实对象可跑。|

## 本地等价命令

```bash
pip install -e ".[dev]"
ruff check src tests
pytest -q
```

课堂演示时，先在本地跑通这两步，再打开 `.github/workflows/ci.yml` 对照说明：本地命令搬到 GitHub Actions 后，就能在每次 push / PR 上自动执行。

## workflow 强在哪里

- **自动触发**：push、pull_request、手动 dispatch、定时任务、路径过滤都可以触发。
- **环境一致**：统一 Python 版本和依赖安装方式，避免“我本地可以”的争论。
- **结果可见**：每个 PR 都能看到哪一步红、红在哪条命令。
- **可设门禁**：配合 Branch protection，把 CI 设为 required check，红了不能 merge。
- **可扩展**：今天是 lint + pytest，明天可以加安全扫描、覆盖率、文档构建、矩阵测试。

## Git 管理为什么能保障质量

Git 不是只用来“保存代码历史”。在 AI coding 里，它是质量控制的一部分：

- **issue 划边界**：告诉 AI 做什么、验收标准是什么、不要动哪里。
- **branch 隔离风险**：AI 的改动先留在分支，不直接污染主干。
- **小 commit 可定位**：出问题时能用 diff、blame、bisect 定位是哪一步引入。
- **PR 把变更变成审查对象**：人审看的不是聊天记录，而是可比较、可评论、可回退的 diff。
- **required check 把纪律变成强制**：不是“记得跑测试”，而是“不跑通就合不了”。

## 三条原则

- **AI 没有豁免权**：AI 产出和人产出走同一道 workflow。
- **一个 PR 只做一件事**：重构、修 bug、加功能分开。
- **人审 gate 写死**：CI 绿只是能合并的前提，最终是否合并由人判断。
