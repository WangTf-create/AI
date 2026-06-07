# Step 4 小步安全重构 Spec（提取积分抵扣职责）

## 1. 目标

在 `order_engine/engine.py` 中，将 `checkout` 中“积分抵扣并回写 total”的职责提取为私有函数，降低主流程复杂度，保持行为不变。

## 2. 约束

- 保留现有 public API：`checkout`、`quote`、`reset_all`。
- 保留现有入口、参数、返回结构与外部行为。
- 一次只重构一个职责块：积分抵扣金额计算与 total 回写。
- 不顺手修 bug，不新增功能，不调整流程顺序。

## 3. 重构范围

- 允许改动：`order_engine/engine.py`
- 文档补充：新增本 Step4 spec 到 `spec/`
- 不改动：`order_engine` 其他模块、`tests`

## 4. 当前行为基线（必须保持）

- `use_points` 为真且 `enable_loyalty=True` 时：
  - 调用 `loyalty.burn(user, use_points)` 计算实际使用积分。
  - 按 `used_pts / 100.0` 抵扣当前 `context.total`。
  - `total` 下限保持 `0.0`（`max(0.0, t)`）。
- 其它情况下不执行积分抵扣，`used_pts` 保持 `0`。
- 传入 `user` 对象仍按现状被原地修改（由 `burn` 实现决定）。

## 5. 实施步骤

1. 新增私有函数（示例：`_apply_loyalty_points(user, use_points)`）。
2. 在函数内完整搬移原有积分抵扣逻辑，返回 `used_pts`。
3. `checkout` 中以函数调用替换原内联逻辑，不改变调用位置。

## 6. 验证步骤

- 目录：`code/01_read_legacy_structure/advanced_modular_coupling`
- 命令：`pytest -q`

## 7. 失败处理规则

若测试失败，按以下顺序处理：

1. 先解释失败对应的行为变化。
2. 做最小修复恢复现状行为。
3. 重新运行全部特征测试直至通过。

## 8. 完成标准

- 仅完成积分抵扣单职责提取，diff 可 review。
- 全量特征测试通过。
