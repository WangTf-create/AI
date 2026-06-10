# 项目治理 SPEC（governance）

- **状态**：governance（持续生效）
- **更新于**：2026-06-10（Electron 客户端）

## 范围

- 本 demo 是**花旗银行**主题的静态展示首页，用于课程演示 spec 驱动协作。
- 交付物：`demo/index.html`（页面）+ `demo/main.js`（Electron 主进程）+ `demo/package.json`（运行脚本与依赖）+ `demo/spec/`（契约账本）+ `demo/AGENTS.md`（agent 规则）。

## 技术约束

- 页面层保持纯 HTML + 内联 CSS；桌面壳使用 Electron（Node.js + Electron 依赖）。
- 支持两种预览方式：浏览器直接打开 `index.html`，或执行 `npm run start` 启动 Electron 客户端。
- 响应式：至少支持桌面（>768px）与移动端（<=768px）两种布局（见首页 media query）。

## 改动流程

1. 查 `spec/README.md` 和相关 spec。
2. 局部文案 / 样式调整：改 `index.html`，同步 `implemented/` 或 `governance/` 中对应 spec。
3. 新页面 / 新模块：先在 `planned/` 写 spec，落地后迁入 `implemented/`。
4. 收尾更新 `spec/README.md` 清单。

## 验收

- [ ] `index.html` 在 Chrome / Edge 最新版可直接打开，无控制台报错（本页无 JS，标准为无 broken 资源）
- [ ] `npm run start` 可启动 Electron 客户端并加载首页
- [ ] 中文文案无乱码，`<meta charset="UTF-8">` 存在
- [ ] 改动与 spec 描述一致，README 清单已更新
