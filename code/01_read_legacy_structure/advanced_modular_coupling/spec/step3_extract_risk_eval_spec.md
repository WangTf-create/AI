# Step 3 小步安全重构 Spec（提取风控评估职责）

## 1. 目标

在 `order_engine/engine.py` 中，将 `checkout` 里的风控职责提取为私有函数：

- 风控评分计算
- 拒单判定条件

目标是降低 `checkout` 主流程复杂度，同时保持行为与返回结构不变。

## 2. 约束

- 保留现有 public API：`checkout`、`quote`、`reset_all`。
- 保留现有入口、参数、返回结构与外部行为。
- 一次只重构一个职责块：风控评估职责。
- 不顺手修 bug，不新增功能，不调整流程顺序。

## 3. 重构范围

- 允许改动：`order_engine/engine.py`
- 不改动：`order_engine` 其他模块、`tests`、Step1/Step2 spec

## 4. 当前行为基线（必须保持）

### 4.1 风控开关行为

- `enable_risk=False` 时，风险分数保持为 `0`。
- `enable_risk=True` 时，风险分数来自 `risk.score(total)`。

### 4.2 拒单判定行为

- 拒单条件保持为当前逻辑：仅在 `enable_risk=True` 且 `risk.rejected(score)` 时进入拒单分支。

### 4.3 流程先后顺序

- 保持先完成税运计算得到 `total`。
- 保持先库存预留，再进入拒单分支判断。
- 保持拒单分支内 `store.save` / `store.emit` 的调用条件与时机不变。

## 5. 实施步骤

1. 在 `engine.py` 新增私有函数：
   - `_compute_risk_score(total)`：封装现有风险分数计算逻辑。
   - `_should_reject_order(risk_score)`：封装现有拒单判定条件。
2. 在 `checkout` 内替换对应内联逻辑，保持参数和返回值等价。
3. 不调整其它业务分支与副作用代码。

## 6. 验证步骤

- 目录：`code/01_read_legacy_structure/advanced_modular_coupling`
- 命令：`pytest -q`

## 7. 失败处理规则

若测试失败，按以下顺序处理：

1. 先解释失败对应的行为变化。
2. 做最小修复恢复现状行为。
3. 重新运行全部特征测试直至通过。

## 8. 完成标准

- 仅完成风控评估单职责提取，diff 可 review。
- 全量特征测试通过。
