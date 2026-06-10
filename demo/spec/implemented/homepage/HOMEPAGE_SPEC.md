# 首页结构 SPEC

- **状态**：implemented
- **领域（feature-domain）**：homepage
- **更新于**：2026-06-10（CTA 外链 + Electron 客户端）
- **负责人**：demo 维护者

## 1. 背景 / 目标

提供花旗银行主题的首页，作为 demo 工程的可视化交付物，并通过 spec 描述页面区块契约，便于后续迭代与 agent 对账。当前页面可通过浏览器直接打开，也可由 Electron 客户端加载。

## 2. 契约（对外行为）

页面自上而下分为五个区块：

| 区块 | 元素 | 行为 |
|---|---|---|
| 顶栏 | `header` + `nav` | 左侧 logo + 品牌名；右侧 4 个导航链接（当前为 `#` 占位） |
| 主视觉 | `main .hero` | 翅膀装饰 + `h1` 标题 + slogan + 双 CTA 按钮（「立即开户」跳转 Google 官网） |
| 服务简介 | `section.services` | 3 列网格卡片（移动端 1 列） |
| 页脚 | `footer` | 版权信息 |

### 不变量

- 单文件 `index.html`，样式内联，不引入外部 CDN。
- `lang="zh-CN"`，`viewport` 已设置，支持移动端折行与导航堆叠。
- 导航项顺序：个人银行 → 企业金融 → 投资理财 → 关于我们。

### 已知缺口

- 顶栏导航与「了解更多」按钮仍为 `href="#"` 占位（见 `planned/navigation/NAVIGATION_PAGES_SPEC.md`）。
- 「立即开户」已跳转 Google 官网 `https://www.google.com/`，新标签页打开。

## 3. 验收标准

- [x] 五大区块均可见且层次清晰
- [x] 桌面端三列服务卡片、移动端单列
- [x] 浏览器直接打开 `index.html` 可完整展示
- [x] Electron 客户端可加载并展示同一首页内容
- [x] 与 `CONTENT_GOVERNANCE_SPEC.md` 文案一致

## 4. 实现锚点

- 实现：`index.html` — `header`（L235-246）、`main .hero`（L248-261）、`section.services`（L263-276）、`footer`（L278-280）
- 样式：`index.html` `<style>` 内各区块对应规则
- 客户端壳：`main.js`（BrowserWindow 加载 `index.html`）
- 治理：`spec/governance/PROJECT_GOVERNANCE_SPEC.md`

## 5. 兼容性影响

- 公共入口：仅 `index.html`，暂无多页面路由。
- 新增子页面属于 planned 范围，需单独 spec。

## 6. 变更记录

| 日期 | 改了什么 | 关联 issue / PR |
|---|---|---|
| 2026-06-10 | 初版首页结构 spec 落地 | — |
| 2026-06-10 | 「立即开户」绑定外链（花旗官网） | — |
| 2026-06-10 | 「立即开户」改为跳转 Google 官网 | — |
| 2026-06-10 | 增加 Electron 客户端壳，首页由桌面端加载 | — |
