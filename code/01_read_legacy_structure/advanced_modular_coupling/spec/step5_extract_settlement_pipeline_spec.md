# Step 5 小步安全重构 Spec（提取结算流水线职责）

## 1. 目标

在 `order_engine/engine.py` 中，将 `checkout` 的结算前半段流水线提取为私有函数，仅做流程搬移，不改变业务规则。

## 2. 约束

- 保留现有 public API：`checkout`、`quote`、`reset_all`。
- 保留现有入口、参数、返回结构与外部行为。
- 一次只重构一个职责块：结算前半段流水线。
- 不顺手修 bug，不新增功能，不调整调用顺序。

## 3. 重构范围

- 允许改动：`order_engine/engine.py`
- 文档补充：新增本 Step5 spec 到 `spec/`
- 不改动：`order_engine` 其他模块、`tests`

## 4. 当前行为基线（必须保持）

流水线顺序保持如下：

1. `pricing.compute_subtotal(items)`
2. `context.put("total", sub)`
3. `discounts.apply_vip()`
4. `coupons.apply_coupon(coupon)`
5. `used_pts = _apply_loyalty_points(user, use_points)`
6. `taxship.apply_tax()`
7. `taxship.apply_shipping()`

并保持：

- 积分抵扣发生在税运计算前。
- `quote` 的 dry_run 副作用不变。
- 拒单分支副作用与返回结构不变。

## 5. 实施步骤

1. 新增私有函数（示例：`_run_settlement_pipeline(items, user, coupon, use_points)`）。
2. 将上述流水线完整搬移到新函数，函数返回 `used_pts`。
3. `checkout` 中以函数调用替换原内联流水线逻辑，调用位置不变。

## 6. 验证步骤

- 目录：`code/01_read_legacy_structure/advanced_modular_coupling`
- 命令：`pytest -q`

## 7. 失败处理规则

若测试失败，按以下顺序处理：

1. 先解释失败对应的行为变化。
2. 做最小修复恢复现状行为。
3. 重新运行全部特征测试直至通过。

## 8. 完成标准

- 仅完成结算流水线单职责提取，diff 可 review。
- 全量特征测试通过。
