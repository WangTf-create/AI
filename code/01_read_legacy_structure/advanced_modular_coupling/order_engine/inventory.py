"""库存与预留，落在 sqlite。"""

from . import db
from . import store


def stock(sku):
    row = db.conn().execute("SELECT stock FROM inventory WHERE sku = ?", (sku,)).fetchone()
    return row["stock"] if row else 0


def all_stock():
    rows = db.conn().execute("SELECT sku, stock FROM inventory").fetchall()
    return {r["sku"]: r["stock"] for r in rows}


def reservations():
    rows = db.conn().execute("SELECT order_id, sku, qty FROM reservations").fetchall()
    out = {}
    for r in rows:
        out.setdefault(r["order_id"], {})[r["sku"]] = r["qty"]
    return out


def _need(items):
    need = {}
    for it in items:
        sku = it.get("sku")
        if sku is None:
            continue
        need[sku] = need.get(sku, 0) + it["qty"]
    return need


def reserve(order_id, items):
    c = db.conn()
    need = _need(items)
    for sku, q in need.items():
        if stock(sku) < q:
            store.audit("reserve fail %s need %d have %d" % (sku, q, stock(sku)))
            return False
    for sku, q in need.items():
        c.execute("UPDATE inventory SET stock = stock - ? WHERE sku = ?", (q, sku))
        c.execute("INSERT INTO reservations(order_id, sku, qty) VALUES (?, ?, ?)",
                  (order_id, sku, q))
    c.commit()
    store.audit("reserved %s for %s" % (need, order_id))
    return True


def release(order_id):
    c = db.conn()
    rows = c.execute("SELECT sku, qty FROM reservations WHERE order_id = ?", (order_id,)).fetchall()
    if not rows:
        return
    for r in rows:
        c.execute("UPDATE inventory SET stock = stock + ? WHERE sku = ?", (r["qty"], r["sku"]))
    c.execute("DELETE FROM reservations WHERE order_id = ?", (order_id,))
    c.commit()
    store.audit("released %s" % order_id)


def reconcile():
    """找出"订单已不是 confirmed、却仍占着预留"的预留行。"""
    c = db.conn()
    rows = c.execute(
        """SELECT r.order_id, r.sku, r.qty, o.status
           FROM reservations r LEFT JOIN orders o ON o.id = r.order_id"""
    ).fetchall()
    orphan = {}
    for r in rows:
        if r["status"] != "confirmed":
            orphan.setdefault(r["order_id"], {"status": r["status"], "held": {}})
            orphan[r["order_id"]]["held"][r["sku"]] = r["qty"]
    return {"leak": bool(orphan), "orphan_reservations": orphan}
