# advanced_modular_coupling 当前行为 Spec（特征测试基线）

> 目的：锁住当前行为，不判断行为是否合理。  
> 范围：`order_engine` public API 与可观察副作用。  
> 约束：每条测试使用临时数据库 + 全局状态恢复。

## 测试隔离约束

- 测试框架：`pytest`
- 每条测试切换到独立临时 sqlite（`db.configure(tmp_db)`）
- 每条测试前执行 `reset_all()`
- 对 `config` 全局可变配置做快照并在测试后恢复
- 清理并恢复 `context.CTX`、`engine.REGION`

## 需要锁住的行为面

1. public API 与返回结构
- `checkout(...)` 成功路径返回固定字段结构
- 成功路径会产生落库/事件/审计副作用

2. 可疑行为（必须按「现状」锁定）
- 现状：`quote()`（dry_run）仍会递增 `seq.order`
- 现状：`quote()` 风控拒绝时仍会写 `order_rejected` 事件
- 现状：先预留库存，再判风控拒单；拒单后 reservation 可残留
- 现状：缺货与风控同时触发时最终状态为 `rejected`
- 现状：券阈值边界符不同（fixed 用 `>=`，percent 用 `>`）
- 现状：积分基数来自 `loyalty._own_subtotal`，与 `pricing` 口径可分叉
- 现状：EU 路径存在行级 round + 总额 round
- 现状：导入 `coupons` 会改写全局配置（导入副作用）
- 现状：`checkout` 会原地修改输入 `user["loyalty_points"]`

## 测试清单（按主题分文件）

### `tests/test_api_surface.py`

- `test_checkout_public_api_shape_and_side_effects`

### `tests/test_quote_current_behavior.py`

- `test_quote_current_dry_run_still_increments_order_sequence`
- `test_quote_current_risk_rejection_still_emits_event_in_dry_run`

### `tests/test_risk_inventory_current_behavior.py`

- `test_checkout_current_reserve_happens_before_risk_and_leaks_on_reject`
- `test_checkout_current_rejected_overrides_out_of_stock_when_both_happen`

### `tests/test_pricing_loyalty_current_behavior.py`

- `test_checkout_current_coupon_threshold_operator_diff_fixed_vs_percent`
- `test_checkout_current_loyalty_base_differs_from_pricing_subtotal_for_book_bulk`
- `test_checkout_current_eu_rounding_path_line_and_total_rounding`
- `test_import_current_coupons_module_import_mutates_global_config`
- `test_checkout_current_mutates_input_user_loyalty_points_in_place`

### `tests/conftest.py`

- `isolated_state`（autouse）：临时数据库 + 全局状态快照恢复
- `user_factory`：统一构造测试用户
