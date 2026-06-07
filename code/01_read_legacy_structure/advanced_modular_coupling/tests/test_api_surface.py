from order_engine import checkout, store


def test_checkout_public_api_shape_and_side_effects(user_factory):
    # 中文注释：锁住现状 - checkout 成功路径返回结构固定，且会产生落库/事件/审计副作用
    items = [{"sku": "SKU-FRESH-1", "cat": "fresh", "price": 20, "qty": 1, "weight": 1.0}]
    order = checkout(items, user_factory(), region="cn")
    assert set(order.keys()) == {
        "id", "user", "region", "items", "total", "status", "risk",
        "points_earned", "points_used", "currency", "breakdown",
    }
    assert order["status"] == "confirmed"
    assert store.get(order["id"]) is not None
    ev = store.events()
    assert any(e["kind"] == "points_earned" for e in ev)
    assert any(e["kind"] == "order_confirmed" for e in ev)
    logs = store.audit_log()
    assert any(m.startswith("save ") for m in logs)
    assert any(m.startswith("reserved ") for m in logs)
    assert any(m.startswith("notify ") for m in logs)
