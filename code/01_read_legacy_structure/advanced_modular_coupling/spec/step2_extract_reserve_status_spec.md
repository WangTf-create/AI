# Step 2 小步安全重构 Spec（提取库存预留与状态决策职责）

## 1. 目标

在 `order_engine/engine.py` 中，将 `checkout` 里的以下职责块提取为私有函数：

- `dry_run` 分支判断
- `inventory.reserve` 调用
- `status` 状态决策

目标是降低 `checkout` 主流程复杂度，同时保持行为完全不变。

## 2. 约束

- 保留现有 public API：`checkout`、`quote`、`reset_all`。
- 保留现有入口、参数、返回结构与外部行为。
- 仅重构一个职责块：库存预留与状态决策。
- 不顺手修 bug，不新增功能，不调整业务执行顺序。

## 3. 重构范围

- 允许改动：`order_engine/engine.py`
- 不改动：`order_engine` 其他文件、`tests` 目录、Step1 spec

## 4. 当前行为基线（必须保持）

### 4.1 `dry_run` 行为

- `dry_run=True`：不调用 `inventory.reserve`，状态保持为 `confirmed`。
- `dry_run=False`：调用 `inventory.reserve`，失败则状态为 `out_of_stock`，成功为 `confirmed`。

### 4.2 风控与库存的先后顺序

- 必须保持先执行库存预留，再执行风控拒单判定的现状顺序。

### 4.3 冲突条件下状态表现

- 同时触发缺货与风控拒单时，最终状态仍为 `rejected`（由后续风控分支覆盖）。

## 5. 实施步骤

1. 在 `engine.py` 中新增私有函数（示例：`_reserve_and_pick_status(oid, items, dry_run)`）。
2. 将 `checkout` 中原有库存预留+状态判断代码替换为该函数调用。
3. 保持风控分支、落库、事件、通知等代码位置与条件不变。

## 6. 验证步骤

- 目录：`code/01_read_legacy_structure/advanced_modular_coupling`
- 命令：`pytest -q`

## 7. 失败处理规则

若测试失败，按以下顺序处理：

1. 先解释失败对应的行为变化。
2. 做最小修复恢复原行为。
3. 重新运行全部特征测试直至通过。

## 8. 完成标准

- 仅完成单职责重构，diff 可 review。
- 全部特征测试通过。
