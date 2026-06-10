# Demo Spec 索引

> Updated: 2026-06-10（Git 治理 + Electron 客户端）

## 用途

`spec/` 是 demo 静态站点的**状态账本**：品牌口径、页面结构、文案规范与未来扩展都记在这里。coding agent 和人在每次相关改动时持续对账。

## 目录布局

```text
spec/
├── README.md                 # 本索引
├── SPEC_TEMPLATE.md          # 单条 spec 模板
├── governance/               # 持续生效的规则
├── planned/                  # 已设计、未落地
├── implemented/              # 已落地 + 实现锚点
└── archived/                 # 搁置 / 废弃
    ├── deferred/
    └── deprecated/
```

## 生命周期

1. 新设计 → 在 `planned/<feature-domain>/` 写 spec（用 [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md)）。
2. 在 `index.html` 落地 → 移到 `implemented/<feature-domain>/`，补锚点，更新本 README。
3. 只部分落地 → 留在 `planned/`，记录剩余验收标准。
4. 不再需要 → 移到 `archived/`，保留决策摘要。

## 当前 spec 清单

| 路径 | 状态 | 一句话 |
|---|---|---|
| `governance/PROJECT_GOVERNANCE_SPEC.md` | governance | 项目范围、技术约束、验收方式 |
| `governance/GIT_GOVERNANCE_SPEC.md` | governance | 分支前缀纪律、用户授权后提交 |
| `governance/CONTENT_GOVERNANCE_SPEC.md` | governance | 文案与 slogan 口径 |
| `implemented/homepage/HOMEPAGE_SPEC.md` | implemented | 首页结构与区块契约 |
| `implemented/branding/BRANDING_SPEC.md` | implemented | 品牌色、logo、slogan |
| `planned/navigation/NAVIGATION_PAGES_SPEC.md` | planned | 导航对应子页面（未建） |

## 当前运行方式

- 浏览器预览：直接打开 `index.html`
- 桌面客户端：在 `demo/` 执行 `npm install` 后运行 `npm run start`
