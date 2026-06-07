# Step 1 小步安全重构 Spec（提取订单组装职责）

## 1. 目标

在 `order_engine/engine.py` 中，对 `checkout` 函数进行一次单职责小步重构：  
将“订单返回结构组装”从流程编排中提取为私有辅助函数，降低重复代码与认知负担。

## 2. 约束

- 保留现有 public API：`checkout`、`quote`、`reset_all`。
- 保留现有入口与调用方式，不调整参数和默认值。
- 保留现有返回结构与外部行为。
- 一次只改一个职责块：仅处理“订单字典组装”职责。
- 不顺手修 bug，不新增功能，不调整业务顺序。

## 3. 重构范围

- 允许改动：`order_engine/engine.py`
- 不改动：`order_engine` 其他模块与 `tests` 目录

## 4. 当前行为基线（必须保持）

### 4.1 拒单分支返回结构

拒单路径返回字段保持当前集合：

- `id`
- `user`
- `region`
- `items`
- `total`
- `status`（固定为 `rejected`）
- `risk`
- `breakdown`

### 4.2 非拒单分支返回结构

正常路径返回字段保持当前集合：

- `id`
- `user`
- `region`
- `items`
- `total`
- `status`
- `risk`
- `points_earned`
- `points_used`
- `currency`
- `breakdown`

### 4.3 行为不变要求

- `store.save`、`store.emit`、`notify.send` 的调用条件与调用时机不变。
- `inventory.reserve`、`risk.score`、`risk.rejected` 的执行顺序不变。
- `dry_run` 路径的现有副作用保持不变（包括当前已被特征测试锁定的行为）。

## 5. 实施步骤

1. 在 `engine.py` 内新增私有辅助函数（示例名：`_build_order_payload`）。
2. 该函数支持按现有两类字段集合组装订单字典：
   - 拒单返回结构
   - 非拒单返回结构
3. 在 `checkout` 的拒单分支与非拒单分支替换为该函数调用。
4. 不改变分支判断条件与副作用调用代码。

## 6. 验证步骤

每完成本步后运行全部特征测试：

- 目录：`code/01_read_legacy_structure/advanced_modular_coupling`
- 命令：`pytest -q`

## 7. 失败处理规则

若测试失败，按以下顺序处理：

1. 先说明失败对应的行为变化（哪条基线被破坏）。
2. 做最小修复，让行为恢复到特征测试锁定的现状。
3. 重新运行全部特征测试，直到全绿。

## 8. 完成标准

- 变更仅聚焦一个职责块（订单组装）。
- diff 保持小且可 review。
- 全部特征测试通过。
