# Demo 项目 Agent 规则

> 给 coding agent 的项目宪法。每次改动 demo 前先读本文件和 `spec/README.md`。

## 1. 不可妥协项

### Git 分支与提交（全局）

- **禁止在 `main` 上直接改代码或 spec**。所有修改必须在任务分支上进行，分支名格式：`<prefix>/<任务名>`。
- 允许的前缀：`feature/`、`bugfix/`、`update/`、`refactor/`、`docs/`。
- **禁止擅自提交**：只有用户明确说「可以提交」时，才执行 `git commit` / `git push`。
- 细则见 `spec/governance/GIT_GOVERNANCE_SPEC.md`。

### 项目范围

- 这是**静态演示站点**，不引入后端、构建工具或框架，除非 spec 里明确规划并经过对账。
- 改动若触及对外可见行为（文案、布局、配色、导航），**先查 spec、改完同步 spec**。
- 示例页必须能在浏览器中直接打开 `index.html` 正常展示，不许依赖本地服务器才能看。

## 2. Issue 处理纪律

- **局部调整**（改文案、调样式、修排版）：直接改 `index.html`，同步相关 spec，在 issue 上说明验证方式（浏览器打开截图或描述）。
- **影响设计**（新增页面、改信息架构、改品牌口径）：先写或更新 `spec/planned/` 中的 spec，经确认后再实现。
- **分类不确定时**：当作"影响设计"处理，先对齐方案再改代码。

## 3. Spec 状态对账

- `spec/` 是 demo 的**状态账本**：品牌、首页结构、文案口径、未来页面都记在这里。
- 动手前确认相关 spec 在 `planned/`、`implemented/` 还是 `governance/`。
- 功能落地后，把 spec 从 `planned/` 移到 `implemented/`，补实现锚点，并更新 `spec/README.md` 清单。
- 收尾时 grep 相关术语，确保 `spec/`、`index.html`、文案口径一致。

## 4. 编辑纪律

- 保持单文件静态页的简洁性，样式优先内联在 `index.html`，不随意拆文件。
- 中文注释用 UTF-8；用户可见文案用中文；`console` 或调试信息用英文（本 demo 一般不需要）。
- 不要覆盖与本次任务无关的改动。
