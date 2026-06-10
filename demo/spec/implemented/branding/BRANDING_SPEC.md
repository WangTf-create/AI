# 品牌视觉 SPEC

- **状态**：implemented
- **领域（feature-domain）**：branding
- **更新于**：2026-06-10
- **负责人**：demo 维护者

## 1. 背景 / 目标

统一 demo 首页的品牌识别：配色、logo 形态、slogan 高亮规则，避免迭代时视觉漂移。

## 2. 契约

### 配色

| 用途 | 色值 | CSS 位置 |
|---|---|---|
| 背景渐变起点 | `#001a4d` | `body` background |
| 背景渐变中段 | `#003087` | `body` background |
| 背景渐变终点 | `#005eb8` | `body` background |
| 品牌红（logo 弧线、主按钮） | `#e4002b` | `.logo-icon::before`、`.btn-primary` |
| 主按钮 hover | `#c40024` | `.btn-primary:hover` |
| slogan 高亮金 | `#ffd700` | `.hero .tagline em`、`.service-card h3` |

### Logo

- 红色向上弧线（CSS `border-radius` 半圆），位于品牌名左侧。
- 品牌名字号 `1.4rem`，字重 700。

### Slogan

- 文案：**普通人攒钱，高手让钱自己去飞**
- 「让钱自己去飞」为 `<em>` 高亮段。
- 主视觉上方有对称「翅膀」装饰（`.wings`），与 slogan 意象一致。

### 字体

- 栈：`"Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif`

## 3. 验收标准

- [x] 背景为花旗蓝渐变，主 CTA 为品牌红
- [x] logo 弧线可见且为红色
- [x] slogan 高亮段为金色
- [x] 与 `CONTENT_GOVERNANCE_SPEC.md` slogan 一致

## 4. 实现锚点

- 实现：`index.html` — `.logo-icon`（L42-58）、`.hero .tagline`（L254-255）、`.wings`（L250-253）、`body` 背景（L16）
- 文案治理：`spec/governance/CONTENT_GOVERNANCE_SPEC.md`

## 5. 兼容性影响

- 改主色或 slogan 须同步 `CONTENT_GOVERNANCE_SPEC.md`。
- 废弃 slogan「给你钱安一个会飞的翅膀」— 已替换，不再使用。

## 6. 变更记录

| 日期 | 改了什么 | 关联 issue / PR |
|---|---|---|
| 2026-06-10 | 初版品牌 spec；slogan 定为公众号风格对比句 | — |
