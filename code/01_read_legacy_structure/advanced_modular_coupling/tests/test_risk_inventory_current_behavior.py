from order_engine import checkout, config, inventory


def test_checkout_current_reserve_happens_before_risk_and_leaks_on_reject(user_factory):
    # 中文注释：锁住现状 - checkout 先 reserve 再判风控；拒单后 reservations 会残留并被 reconcile 识别
    items = [{"sku": "SKU-LUX-1", "cat": "luxury", "price": 6000, "qty": 1}]
    order = checkout(items, user_factory(blacklist=True), region="cn")
    assert order["status"] == "rejected"
    resv = inventory.reservations()
    assert order["id"] in resv and resv[order["id"]]["SKU-LUX-1"] == 1
    rec = inventory.reconcile()
    assert rec["leak"] is True
    assert order["id"] in rec["orphan_reservations"]


def test_checkout_current_rejected_overrides_out_of_stock_when_both_happen(user_factory):
    # 中文注释：锁住现状 - 同时触发缺货与风控拒绝时，最终状态以 rejected 为准
    items = [{"sku": "SKU-LUX-1", "cat": "luxury", "price": 6000, "qty": 4}]
    order = checkout(items, user_factory(blacklist=True), region="cn")
    assert order["status"] == "rejected"
    assert order["risk"] >= config.RISK["reject"]
