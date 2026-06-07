# 提交约定（链条一：让 AI 的改动可追溯、可管理）

一个 issue → 一个分支 → 若干 commit → 一个 PR → 合并后自动关 issue。

## 分支
`<type>/<issue号>-<短描述>`，例如 `fix/142-coupon-threshold`、`refactor/88-split-checkout`。

## commit message
```
<type>(<scope>): <一句话做了什么>

<可选正文：为什么这么改，而不是怎么改>

Refs #142
```
`type`：feat / fix / refactor / test / docs / chore / build / ci

## PR
- 标题沿用 commit 首行风格
- 正文写 `Closes #142`（合并即自动关闭 issue）
- **一个 PR 只做一件事**：重构（行为不变）和改 bug（行为变）分两个 PR

## 为什么这条链条对 coding agent 尤其关键
agent 一次只看得到代码库的一小块。issue 把"做什么、验收标准、不要动哪里"写清楚，
就是给 agent 划边界；分支 + 小步 commit + PR 让它的产出**可逐步 review、可回退、可追溯**——
出问题时一眼能定位是哪一步、哪条 commit 引入的。这正是"有序管理 AI 产出"的地基。
