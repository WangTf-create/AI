# `order_system.py` 现状导读（只读分析）

本文只描述现状，不给重构方案，不修任何 bug。

## 1) Public API / 入口清单（下游可能依赖调用面）

### 1.1 名义公开面（`__all__`）

当前模块通过 `__all__` 暴露了大量入口，实际形成“宽公共面”：

- 结算主入口与历史入口：
  - `OrderSystem.checkout`
  - `dispatch_checkout`
  - `calc_v0` / `calc_v1` / `calc_v2`
  - `checkout_v3_experimental`
  - `legacy_calc` / `legacy_calc_total` / `get_price` / `quick_total`
- 流程编排入口：
  - `CheckoutFacade.place_order`
  - `BatchProcessor.run`
- 业务子系统入口：
  - `CartValidator`、`RefundEngine`、`InventoryAdmin`
  - `TaxCalculator`、`ShippingCalculator`、`PromoEngine`
  - `RegionalSettlement`
  - `GiftCardService`、`SubscriptionBilling`、`PaymentSimulator`
  - `ReportBuilder`、`Analytics`、`TaxFilingReport`
  - `CouponIssuer`、`WarehouseRouter`、`NotificationDispatcher`
  - `OrderRepository`、`OrderStateMachine`、`ConfigManager`
  - `CustomerSegmentation`、`PriceQuoteBuilder`、`SettlementReconciler`
  - `PriceExplainer`、`OrderEnricher`、`ShippingLabelPrinter`、`GiftWrapService`、`InventoryForecast`
- 模块级工具入口：
  - `reset_state`、`seed_demo_data`、`demo_full_pipeline`
  - `format_money`、`country_to_region`、`audit_config_consistency`

### 1.2 事实上的外部入口（即使不在 `__all__` 也可能被直接 import）

- 数据库/状态控制：
  - `configure_db`（切换 DB 文件）
  - `health_check`（运维自检）
- 迁移与展示工具：
  - `migrate_v1_orders_to_v2`
  - `render_notification`
  - `convert_currency`、`estimate_delivery_days`、`cart_weight` 等

### 1.3 入口分层现状（调用面风险）

- **同一业务有多入口并行**：`dispatch_checkout`、`OrderSystem.checkout`、`CheckoutFacade.place_order`、`calc_v*`、`RegionalSettlement`、`checkout_v3_experimental`、`PriceQuoteBuilder.build`。
- **“兼容入口”仍在实际暴露**：`legacy_*`、`quick_total`、`get_price` 继续可被新代码误用。
- **调用方可能绕过统一门面**：模块注释明确提到“很多调用方直接 import 内部符号”。

---

## 2) 职责板块拆分（以及散落位置）

当前仅一个文件：`order_system.py`。职责高度耦合且重复实现明显。

- **结算核心（主链路）**
  - `OrderSystem.checkout`
  - 同时包含：计价、品类折扣、VIP、券、税、运费、积分、风控、库存预留、落库、通知
- **历史结算实现**
  - `calc_v0` / `calc_v1` / `calc_v2`
  - 兼容函数：`legacy_calc` / `legacy_calc_total` / `get_price` / `quick_total`
- **实验/替代结算实现**
  - `checkout_v3_experimental`
  - `RegionalSettlement.settle_*`
  - `PriceQuoteBuilder.build`
  - `SettlementReconciler`（多实现对账器）
- **税与运费子系统**
  - 税：`TaxCalculator` 与 `OrderSystem.checkout` 内联税逻辑并存
  - 运费：`ShippingCalculator` 与 `OrderSystem.checkout` 内联运费逻辑并存
- **促销与券**
  - 基础券：`COUPON_CATALOG` + `OrderSystem.checkout` 分支
  - 活动促销：`PromoEngine`
  - 券运营写入：`CouponIssuer`（改全局券目录）
- **库存与仓储**
  - 总库存/预留：`_INVENTORY`、`_RESERVATIONS`、`OrderSystem.reserve/release`
  - 后台库存：`InventoryAdmin`
  - 仓路由：`WarehouseRouter`（独立库存 `WAREHOUSE_STOCK`）
  - 预测：`InventoryForecast`
- **订单持久化/仓储抽象**
  - SQLite 表包装：`_OrderTable` / `_InventoryTable` / `_ReservationTable` / `_EventTable` / `_AuditTable` / `_GiftCardTable` / `_PaymentTable`
  - 仓储层：`OrderRepository`（软删、分页、筛选）
  - 旧查询层：`LegacyDBAdapter`
- **支付与争议**
  - 支付：`PaymentSimulator`
  - 争议：`DisputeCenter`
- **通知与展示**
  - 通知发送 A：`OrderSystem.notify`
  - 通知发送 B：`NotificationDispatcher.dispatch`
  - 文案：`render_notification` + `NOTIFY_TEMPLATES`
  - 展示：`ReceiptPrinter`、`PriceExplainer`、`OrderEnricher`、`ShippingLabelPrinter`
- **积分与会员**
  - 下单积分：`OrderSystem.earn_points/burn_points` + checkout 写回
  - 会员积分中心：`LoyaltyManager`
- **风控**
  - 结算内风控：`OrderSystem.risk_score`
  - 扩展风控：`ExtRiskEngine.evaluate`
- **配置与环境**
  - 全局配置常量（税/券/运费/规则）
  - 动态开关：`FEATURE_FLAGS` + `ConfigManager`
  - 环境重置/造数：`reset_state`、`seed_demo_data`、`demo_full_pipeline`

---

## 3) 状态地图（隐式输入输出）

## 3.1 数据库（SQLite，隐式持久化）

通过 `_db_state` + `_conn()` 连接 `order_system.db`，表如下：

- `orders`：订单 JSON
- `inventory`：库存
- `reservations`：预留库存
- `audit`：审计日志文本
- `events`：事件 JSON
- `gift_cards`：礼品卡余额
- `payments`：支付记录 JSON
- `seq`：订单序列

初始化入口：`_ensure()`（会灌种子库存、初始化序列）。
环境切换入口：`configure_db(path)`。
清空重建入口：`reset_state()`。

## 3.2 全局变量 / 内存态

- 强业务全局态：
  - `_INVENTORY`、`_RESERVATIONS`、`_ORDERS`、`_PAYMENTS`、`_GIFT_CARDS`
  - `_AUDIT_LOG`、`_EVENTS`
- 纯内存会话/缓存：
  - `_CACHE`
  - `_SESSION`（`current_user`、`last_region`）
- 全局配置可变：
  - `FEATURE_FLAGS`
  - `TAX_TABLE`
  - `COUPON_CATALOG`（被 `CouponIssuer` 动态改写）

## 3.3 配置类输入（静态规则）

- 品类折扣：`CATEGORY_RULES`
- VIP：`VIP_TIERS`
- 券目录：`COUPON_CATALOG`
- 税率：`TAX_TABLE`
- 币种换算：`CURRENCY_RATES`
- 运费：`SHIPPING_TABLE`、`SHIPPING_ZONES`
- 免税品类：`TAX_EXEMPT_CATEGORIES`
- 风控：`RISK_RULES`、`EXT_RISK_RULES`
- 积分：`LOYALTY_RATE`、`LOYALTY_TIER_BONUS`、`REDEEM_CATALOG`
- 状态流转：`ORDER_STATES`、`ALLOWED_TRANSITIONS`
- 其他：`SEASONAL_PROMOS`、`TIERED_PROMO`、`PAYMENT_METHODS`、`BUNDLES`、`ROUNDING_POLICY`

## 3.4 事件输出（副作用）

- 统一事件流通过 `_emit` 写入 `_EVENTS` / `events` 表，典型事件：
  - `order_confirmed`、`order_rejected`、`order_refunded`
  - `subscription_renewed`
  - `payment_captured`、`payment_refunded`
  - `giftcard_issued`
  - `notification_sent`
  - `dispute_opened`

## 3.5 日志输出（副作用）

- `_audit` 写入 `_AUDIT_LOG` / `audit` 表。
- 多数子系统都直接记审计：库存、支付、通知、礼品卡、配置变更、争议等。

## 3.6 函数入参与就地修改（隐式 I/O）

- 多处会**就地修改传入对象**：
  - `OrderSystem.checkout` 修改 `user["loyalty_points"]`
  - `LoyaltyManager` 修改 `user`
  - `GiftCardService.apply_to_order` 修改 `order`
  - `GiftWrapService.apply` 修改 `order`
  - `CheckoutFacade.place_order` 在支付失败时改 `order["status"]`
  - `DisputeCenter.resolve` 修改订单状态并改库存

---

## 4) 可能并存的多套实现 / 多套规则

### 4.1 结算实现并存（至少 7 套口径）

- `OrderSystem.checkout`
- `calc_v0`
- `calc_v1`
- `calc_v2`
- `RegionalSettlement.settle_*`
- `checkout_v3_experimental`
- `PriceQuoteBuilder.build`

`SettlementReconciler` 已明确展示“同一单多结果”现实。

### 4.2 税口径并存

- 口径 A：`OrderSystem.checkout` 的总额乘税（粗口径）
- 口径 B：`TaxCalculator` 的按行免税/附加税（细口径）
- `RegionalSettlement` 也有区域私有税逻辑

### 4.3 运费口径并存

- 口径 A：`OrderSystem.checkout` 基于 `SHIPPING_TABLE`
- 口径 B：`ShippingCalculator` 基于 `SHIPPING_ZONES` + 加急 + 重量阶梯
- `estimate_shipping`、`quote`、`PriceQuoteBuilder`、`RegionalSettlement` 各自使用点不同

### 4.4 风控口径并存

- 口径 A：`OrderSystem.risk_score`
- 口径 B：`ExtRiskEngine.evaluate`

两者打分维度与阈值命中项不完全一致。

### 4.5 通知实现并存

- A：`OrderSystem.notify`（简单消息 + `order_confirmed`）
- B：`NotificationDispatcher.dispatch`（渠道路由 + `notification_sent`）

### 4.6 积分体系并存

- A：checkout 内积分赚取/抵扣与写回
- B：`LoyaltyManager` 独立积分体系（等级、兑换、过期、历史）

### 4.7 状态治理并存

- A：业务代码直接写 `order["status"]`
- B：`OrderStateMachine` 合法流转

状态机不是主链路强制路径。

---

## 5) 可疑行为清单（像 bug，但重构前必须先锁行为）

以下是“高疑似问题行为”，建议先当作特征锁定对象，不做语义修复：

- 风控与库存顺序：`checkout` 先预留库存再判风控，`rejected` 单可能留下预留占用（孤儿预留）。
- 拒单仍落库：风控拒单分支会 `save_order`（`dry_run=False` 时）。
- 缺货单也可能落库路径不统一：主流程在 `status=="confirmed"` 才通知与积分写回，但库存/状态变化已发生。
- EU 电子品类有历史双折（额外 `0.95`），仅在 `OrderSystem.checkout` 存在，其他实现缺失。
- 百分比券阈值比较符不一致：`>` 与 `>=` 在不同版本混用。
- 运费免邮判断口径不一致：`quote` 用券前小计，`checkout` 用加税后当前 `t`。
- `PROMO_STACK_MATRIX` 存在但主 checkout 未按该矩阵执行叠加控制。
- `TAX_EXEMPT_CATEGORIES` 存在，但主 checkout 税步骤不读取。
- 税/运费两套表（`SHIPPING_TABLE` vs `SHIPPING_ZONES`）长期并存且结果可能偏差。
- `CartValidator` 非强制前置；`dispatch_checkout` 可绕过校验。
- 多处直接改全局配置（`ConfigManager.set_flag/set_tax_rate`、`CouponIssuer`）导致后续请求行为漂移。
- `OrderSystem.__init__` 中 `self.tax` 为构造时快照；税率动态调整后“旧实例不变，新实例变化”。
- `RefundEngine.refund` 按“重新计价”计算退款，且规则与 checkout 不完全一致。
- `CheckoutFacade.place_order` 支付失败把订单改为 `payment_failed`，该状态不在 `ORDER_STATES` 里。
- `OrderStateMachine` 未被 checkout 主路径使用，系统可出现状态机未覆盖状态。
- `ReportBuilder.to_csv` 手拼 CSV 无转义，字段含逗号会破坏格式。
- `ReportBuilder.gmv`（按订单）与 `gmv_from_events`（按事件）天然可漂移。
- `SubscriptionBilling.renew` 返回订单对象但未落库（与普通下单生命周期不同）。
- `GiftCardService.apply_to_order` 事后改订单总价，可能与支付记录/税报表失配。
- `SettlementReconciler.run` 内部 `reset_state()`，对调用环境有破坏性副作用。
- `country_to_region` 未知国家静默回默认区，可能掩盖映射错误。
- `WarehouseRouter` 使用独立仓库库存，不与 `_INVENTORY` 自动一致。
- `InventoryForecast.days_of_supply` 用历史总消耗近似日耗，且默认 `max(1, used)`，结果偏保守但不透明。

---

## 6) 第一批应补的特征测试（锁现状，不改行为）

以下是“先锁后改”的最小关键集，优先覆盖分歧最大的行为面：

### 6.1 入口与路由选择

- `dispatch_checkout` 在 `FEATURE_FLAGS["use_legacy_v1"]` 开/关时分别走 `calc_v1` 与 `OrderSystem.checkout`。
- `get_price` 返回值兼容（dict/number 处理路径）。
- `quick_total` 的默认假设（非 VIP、`cn`、无券）结果锁定。

### 6.2 结算关键分支（`OrderSystem.checkout`）

- 各品类折扣阈值，尤其 EU electronics 双折是否触发。
- VIP 各等级折扣边界（含 `vip_level>=5`）。
- 优惠券分支：`fixed` / `percent` / `firstorder` / `freeship` / `bogo`。
- 负数兜底（优惠后 < 0 归零）。
- EU 逐行 round 与总额 round 开关影响。
- 运费计算：免邮阈值、`force_freeship`、重量默认值 `0.5`。
- 积分抵扣与积分发放基数分区差异（`eu/uk` 税前，其它税后）。
- 风控边界：`reject_score` 上下临界值。

### 6.3 副作用与状态一致性

- `checkout(dry_run=True)` 不应改库存/预留/订单存储。
- `checkout(dry_run=False)` 在 `confirmed/rejected/out_of_stock` 三状态下：
  - 订单是否落库
  - 事件是否写入
  - 库存与预留如何变化
  - 用户积分是否写回
- 风控拒单后预留是否仍存在（锁定当前现实）。
- `reset_state` 会重建表、恢复种子库存、清 `_CACHE/_SESSION`。

### 6.4 多实现差异锁定（防“误统一”）

- 同一输入下 `calc_v0/v1/v2/checkout/regional/v3_exp/quote_builder` 差异快照（可直接用 `SettlementReconciler` 输出做黄金样本）。
- 税口径差异：`OrderSystem.checkout` vs `TaxCalculator.order_tax`。
- 运费口径差异：`OrderSystem.checkout` vs `ShippingCalculator.quote`。
- 风控差异：`OrderSystem.risk_score` vs `ExtRiskEngine.evaluate`。

### 6.5 业务外围高风险链路

- `CheckoutFacade.place_order`：
  - 校验失败中断
  - 支付失败变 `payment_failed`
  - 通知走 `NotificationDispatcher`（非 `OrderSystem.notify`）
- `RefundEngine.refund`：
  - 不可退品类拒绝
  - 退货补库存
  - 退款金额与手续费计算口径
- `DisputeCenter.resolve("refund")`：
  - 状态变化
  - 库存回补
  - 事件写入

### 6.6 报表/导出兼容性

- `ReportBuilder` 的 `gmv`、`gmv_from_events`、`reconcile_gmv` 输出结构。
- `to_csv` / `to_json_like` 的当前字符串格式（即使不完美也先锁）。
- `format_money` 在不同区域的格式化行为（符号位置、小数位、负号）。

---

## 7) 一句话结论（现状）

该模块是“单文件多子系统 + 多套结算并存 + 全局可变状态驱动”的遗留集合体；在重构前，最重要的是先用特征测试锁住**入口选择、结算差异、副作用顺序、全局状态漂移**这四类现有行为。
