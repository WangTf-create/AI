# code/ — 代码说明

这个目录按课程小节组织，每个文件夹对应讲义正文中的一段演示。序号和讲义 § 小节一一对应，跳号是因为多个小节共用同一套代码。

## 目录

| 文件夹 | 对应讲义 | 用途 | 怎么跑 |
|---|---|---|---|
| `01_read_legacy_structure/` | §2–§5 | 两套遗留订单系统，分别演示"体量"和"结构"两种难度 | 见下方 |
| `04_live_spec_template/` | §7 | spec 治理模板（AGENTS.md + 分状态目录 + 模板），可直接复制到自己项目 | 阅读 + 复制 |
| `05_github_pipeline/` | §8 | GitHub workflow 最小可跑样例：CI、issue/PR 模板 | 见下方 |
| `_backup_instructor/` | — | 课程参考资料，不需要看 | — |

> 为什么没有 `02_` 和 `03_`？因为 §2（读懂代码）、§3（spec + 特征测试）、§4（小步重构）、§5（结构复杂度）用的都是 `01_` 里的同一套遗留代码，所以合并了，不重复放。

## 01_read_legacy_structure/ — 遗留订单系统

两套可独立运行的遗留代码，分别对应真实大项目的两种"难"：

**god_file_order_system/（§2–§4）**

3000+ 行的上帝文件。一个 `OrderSystem` 类包了计价、折扣、VIP、券、税、运费、积分、库存、风控、持久化、通知、报表。核心入口是 250 行的 `checkout()`。

```bash
cd 01_read_legacy_structure/god_file_order_system
python order_system.py
```

**advanced_modular_coupling/（§5）**

14 个模块的订单引擎。行数不多，但模块之间靠全局可变状态、近循环依赖、共享 context 和 import 副作用绑在一起——单看每个文件都正常，合起来才出事。

```bash
cd 01_read_legacy_structure/advanced_modular_coupling
python runner.py
```

## 04_live_spec_template/ — spec 治理模板

一套可以直接复制到自己项目里的目录结构：

- `AGENTS.md` — 写给 coding agent 的项目规则
- `spec/governance/` — 长期规则（测试口径、发布、兼容边界）
- `spec/planned/` — 已设计、未落地
- `spec/implemented/` — 已落地，带实现锚点
- `spec/archived/` — 搁置或废弃
- `spec/SPEC_TEMPLATE.md` — 单条 spec 模板

不需要安装依赖，直接阅读模板文件，按自己的项目改即可。

## 05_github_pipeline/ — GitHub workflow 最小样例

一个 `orderkit` 最小 Python 包，配了完整的 CI 工件：

```bash
cd 05_github_pipeline
pip install -e ".[dev]"
ruff check src tests
pytest -q
```

- `.github/workflows/ci.yml` — 本地命令搬到 Actions 的最小版本（lint + pytest，设为 required check）
- `.github/ISSUE_TEMPLATE/task.md` — issue 模板（验收标准、不要动的范围）
- `.github/pull_request_template.md` — PR 模板（自检清单）
