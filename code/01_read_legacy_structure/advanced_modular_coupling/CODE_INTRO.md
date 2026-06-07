# advanced_modular_coupling 现状拆解（只读）

> 范围：`code/01_read_legacy_structure/advanced_modular_coupling`  
> 目标：记录当前实现现状，供后续重构前“先锁行为”使用。  
> 说明：本文只描述现状，不给重构方案，不修复问题。

---

## 1) public API / 入口清单（下游可能依赖的调用面）

### 包级公开 API（`order_engine/__init__.py`）

- `checkout(items, user, coupon=None, region="cn", use_points=0, dry_run=False)`  
  - 主结算入口；下游最可能直接依赖。
- `quote(items, user, coupon=None, region="cn")`  
  - 询价入口（内部复用 `checkout(..., dry_run=True)`）。
- `reset_all()`  
  - 清库+清上下文；测试/演示脚本常用。
- 同时公开模块对象：`config`、`store`、`inventory`、`context`  
  - 下游可直接调用其函数和可变全局配置，属于高耦合调用面。

### 脚本入口（`runner.py`）

- `main()` + `if __name__ == "__main__": main()`  
  - 演示用入口，会调用 `oe.reset_all()` 与多次 `oe.checkout()`。

### 可被下游绕过编排直接调用的“次级入口”

- `store.*`：`next_id/get/all_orders/events/audit_log/save/emit/audit`  
- `inventory.*`：`stock/all_stock/reservations/reserve/release/reconcile`  
- `config.*`：`register_promo_pack/set_flag` + 多个全局 dict（可直接改）  
- `context.*`：`begin/get/put/snapshot`（全局上下文字典）

---

## 2) 职责板块拆分（以及当前散落位置）

### A. 结算编排与流程控制

- 文件：`order_engine/engine.py`
- 关键函数：`checkout`、`quote`、`reset_all`
- 现状：一个函数串联计价、折扣、优惠券、积分抵扣、税费、运费、风控、库存、持久化、通知。

### B. 定价与折扣规则

- 文件：`order_engine/pricing.py`、`order_engine/discounts.py`
- 关键函数：`compute_subtotal`、`category_discount`、`apply_vip`
- 现状：  
  - 品类折扣在 `discounts.category_discount`。  
  - VIP 折扣在 `discounts.apply_vip`。  
  - `pricing.compute_subtotal` 负责行项目+小计，并对 EU 行项目做 round。

### C. 优惠券规则

- 文件：`order_engine/coupons.py`、`order_engine/config.py`
- 关键函数：`apply_coupon`、`_resolve`、`register_promo_pack`
- 现状：  
  - 券类型（fixed/percent/freeship）在 `apply_coupon`。  
  - 券数据在 `config.COUPONS`。  
  - `coupons.py` 导入时直接执行 `config.register_promo_pack()`（导入副作用）。

### D. 税费与运费

- 文件：`order_engine/taxship.py`、`order_engine/config.py`
- 关键函数：`apply_tax`、`apply_shipping`
- 现状：  
  - 税率来自 `config.TAX`。  
  - 运费规则来自 `config.SHIPPING`。  
  - 免邮门槛判断基于 `subtotal`，不是 `total`。

### E. 风控决策

- 文件：`order_engine/risk.py`、`order_engine/config.py`
- 关键函数：`score`、`rejected`
- 现状：  
  - 基于黑名单、金额、件数、新客、奢侈品组合加分。  
  - 拒单阈值来自 `config.RISK["reject"]`。

### F. 库存预留与对账

- 文件：`order_engine/inventory.py`
- 关键函数：`reserve`、`release`、`reconcile`、`stock`
- 现状：  
  - 预留与库存扣减写 sqlite。  
  - 对账识别“非 confirmed 但仍有 reservations”的占库存。

### G. 积分体系

- 文件：`order_engine/loyalty.py`
- 关键函数：`earn`、`burn`、`_own_subtotal`
- 现状：  
  - 积分抵扣直接改 `user["loyalty_points"]`。  
  - 积分发放基数由 `loyalty._own_subtotal` 自己计算（未复用 `pricing.compute_subtotal`）。

### H. 持久化 / 事件 / 审计

- 文件：`order_engine/db.py`、`order_engine/store.py`
- 关键函数：`db.conn/reset/configure`、`store.save/emit/audit`
- 现状：  
  - 单 sqlite 连接 + 全局状态。  
  - 订单、库存、预留、事件、审计、序列号全部落同库。

### I. 通知

- 文件：`order_engine/notify.py`
- 关键函数：`send`
- 现状：  
  - 通知不走外部通道，只写 audit + event。

---

## 3) 状态地图（隐式输入 / 输出）

### 3.1 数据库状态（sqlite）

- 文件：`order_engine/db.py`
- 全局连接状态：`_state = {"path", "conn"}`
- 表：
  - `orders`
  - `inventory`
  - `reservations`
  - `audit`
  - `events`
  - `seq`
- 种子数据：
  - `SEED_INVENTORY` 首次建库注入库存
  - `seq.order` 初始化为 `1000`

### 3.2 全局变量 / 模块级可变状态

- `engine.REGION`：被 `checkout` 写入，被 `pricing.compute_subtotal` 读取。
- `context.CTX`：跨步骤共享上下文字典。
- `config.CATEGORY_RULES / VIP_RATES / TAX / SHIPPING / CURRENCY / COUPONS / FLAGS / RISK / LOYALTY_RATE`：全局可变配置。
- `db._state`：连接与路径全局单例。

### 3.3 “缓存”与会话态

- 长连接 `db._state["conn"]` 可视作进程级连接缓存。
- `context.CTX` 是一次结算链路的共享临时态（但为全局 dict）。

### 3.4 配置输入

- 主要来自 `config.py` 的常量 dict 与 `FLAGS`。  
- 运行中可通过 `config.set_flag()` 和直接改 dict 改变行为。  
- `coupons` 模块导入时会改写 `config.COUPONS` 与 `FLAGS["promo_pack_loaded"]`。

### 3.5 事件输出

- `store.emit(...)` 写 `events` 表：
  - `order_rejected`
  - `points_earned`
  - `order_confirmed`

### 3.6 日志/审计输出

- `store.audit(...)` 写 `audit` 表。
- 多处调用：
  - `store.save` 后写审计
  - `inventory.reserve/release` 写审计
  - `notify.send` 写审计

### 3.7 业务对象副作用

- `loyalty.burn/earn` 会原地修改传入的 `user` dict（`loyalty_points`）。

---

## 4) 系统里并存的多套实现 / 多套规则

1. **品类折扣存在两套实现路径**
   - `discounts.category_discount`（主结算用）
   - `loyalty._own_subtotal`（积分发放基数用）
   - 两者细节不一致：`book` 在 `discounts` 有两档（2件95折、5件8折），在 `loyalty` 只有“2件95折”一档。

2. **金额阈值比较规则不一致**
   - fixed 券：`t >= threshold`
   - percent 券：`t > threshold`
   - 同为“门槛券”，边界比较符不同。

3. **区域/精度规则分散**
   - `engine.REGION`（全局）影响 `pricing.compute_subtotal` 是否 EU 行级 round。
   - `taxship.apply_shipping` 对 EU 再做一次总额 round。
   - 精度规则分散在不同步骤，不在同一处统一定义。

4. **免邮规则与应付总额规则并存**
   - 免邮看 `subtotal`（未税前、折扣前后关系由流程决定）。
   - 风控看 `total`（税费+运费后）。
   - 两类规则基于不同金额口径。

---

## 5) 可疑行为清单（像 bug，但重构前必须先锁原样）

1. **`quote()` 可能产生持久化副作用**
   - `quote -> checkout(dry_run=True)` 仍会先 `store.next_id()`，导致 `seq` 递增。
   - 若风控拒绝，`checkout` 在拒单分支会无条件 `store.emit("order_rejected", ...)`，即使 `dry_run=True` 也会写 `events`。

2. **先预留库存，再判风控拒单**
   - `checkout` 中 `inventory.reserve(...)` 发生在风控拒绝判断之前。
   - 拒单后未看到自动 `inventory.release(...)`，可能造成 reservations 残留（`reconcile` 也在识别这类现象）。

3. **拒单优先级覆盖缺货状态**
   - 先因库存不足置 `status="out_of_stock"`，随后若风控也拒绝，函数直接走拒单返回，最终状态是 `rejected`。

4. **积分发放基数可能与结算小计不一致**
   - `earn` 使用 `loyalty._own_subtotal`，不是 `pricing.compute_subtotal` 的结果。
   - 特别是 `book` 数量>=5场景，积分基数和订单小计存在潜在偏差。

5. **模块导入即改配置**
   - `coupons.py` 顶层执行 `config.register_promo_pack()`，导入动作本身会改变全局券表与 flag。

6. **全局状态导致调用顺序敏感**
   - `engine.REGION`、`context.CTX`、`config.FLAGS` 均为全局可变对象，行为依赖调用先后和共享进程状态。

7. **`reset_all()` 只重置部分全局态**
   - 清库+清 `CTX`，但不会回滚 `config` 里被动态改过的配置，也不会恢复 import 副作用前状态。

---

## 6) 第一批应补的特征测试（锁现状，不评判对错）

> 这些测试目标是“把当前行为钉住”，不是“验证理想业务规则”。

1. **`quote` 的副作用特征**
   - 调一次 `quote` 后，`seq` 是否递增。
   - 在可触发风控拒绝的 `quote` 场景下，`events` 是否新增 `order_rejected`。

2. **“先预留后拒单”特征**
   - 构造高风险订单：`checkout` 返回 `rejected` 后，`reservations` 是否仍有该单占用；`reconcile()["leak"]` 是否为真。

3. **缺货+风控并发条件下状态归属**
   - 同时触发库存不足和风控拒绝，断言最终返回状态是当前实现给出的那个值（预期应锁为 `rejected`）。

4. **积分基数与结算小计分叉**
   - 使用 `book` 大数量（>=5）场景，断言 `points_earned` 基数按 `loyalty._own_subtotal` 当前逻辑计算，而非 `pricing` 结果。

5. **优惠券阈值边界比较符**
   - 在金额恰好等于 threshold 时：  
     - `fixed` 券应生效  
     - `percent` 券按当前逻辑不生效（`>` 而非 `>=`）

6. **导入副作用特征**
   - 仅导入 `order_engine.coupons` 后，断言 `config.COUPONS` 包含 `SPRING30/PCT30/FREESHIP`，且 `promo_pack_loaded=True`。

7. **EU 精度路径特征**
   - EU 区域下，锁定行项目 round 与运费后总额 round 的当前数值表现。

8. **用户对象原地修改特征**
   - `use_points` 与积分发放场景后，传入 `user` dict 中 `loyalty_points` 的当前变更行为应被锁定。

---

## 7) 结论（现状口径）

当前系统是“模块拆开但共享全局态很重”的编排型实现：业务规则分散在多个文件，但通过 `context.CTX`、`engine.REGION`、`config` 全局字典与 sqlite 单库强耦合在一起；此外存在导入副作用、dry_run 副作用、以及多处规则口径并存。重构前应先用特征测试把这些行为逐条锁住。
