from order_engine import quote, store
from order_engine import db


def test_quote_current_dry_run_still_increments_order_sequence(user_factory):
    # 中文注释：锁住现状 - quote(dry_run=True) 不是纯查询，会推进 seq.order
    before = db.conn().execute("SELECT val FROM seq WHERE name='order'").fetchone()["val"]
    _ = quote([{"sku": "SKU-BOOK-1", "cat": "book", "price": 50, "qty": 1}], user_factory(), region="cn")
    after = db.conn().execute("SELECT val FROM seq WHERE name='order'").fetchone()["val"]
    assert after == before + 1


def test_quote_current_risk_rejection_still_emits_event_in_dry_run(user_factory):
    # 中文注释：锁住现状 - quote 触发风控拒绝时，即使 dry_run 也会写入 order_rejected 事件
    items = [{"sku": "SKU-LUX-1", "cat": "luxury", "price": 20000, "qty": 1}]
    _ = quote(items, user_factory(blacklist=True), region="cn")
    assert any(e["kind"] == "order_rejected" for e in store.events())
    assert store.all_orders() == []
