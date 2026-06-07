"""订单持久化 + 审计 + 事件，落在 sqlite。"""

import json

from . import db


def next_id():
    c = db.conn()
    c.execute("UPDATE seq SET val = val + 1 WHERE name = 'order'")
    val = c.execute("SELECT val FROM seq WHERE name = 'order'").fetchone()[0]
    c.commit()
    return "ORD-%d" % val


def audit(msg):
    c = db.conn()
    c.execute("INSERT INTO audit(msg) VALUES (?)", (str(msg),))
    c.commit()


def emit(kind, payload):
    c = db.conn()
    c.execute("INSERT INTO events(kind, payload) VALUES (?, ?)", (kind, json.dumps(payload)))
    c.commit()


def save(order):
    c = db.conn()
    c.execute(
        """INSERT OR REPLACE INTO orders
           (id, user, region, status, total, points_earned, points_used,
            currency, items_json, breakdown_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (order["id"], order.get("user"), order.get("region"), order.get("status"),
         order.get("total"), order.get("points_earned", 0), order.get("points_used", 0),
         order.get("currency"), json.dumps(order.get("items", [])),
         json.dumps(order.get("breakdown", {}))),
    )
    c.commit()
    audit("save %s total=%s status=%s" % (order["id"], order.get("total"), order.get("status")))
    return order["id"]


def _row_to_order(row):
    return {
        "id": row["id"], "user": row["user"], "region": row["region"],
        "status": row["status"], "total": row["total"],
        "points_earned": row["points_earned"], "points_used": row["points_used"],
        "currency": row["currency"],
        "items": json.loads(row["items_json"] or "[]"),
        "breakdown": json.loads(row["breakdown_json"] or "{}"),
    }


def get(order_id):
    row = db.conn().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return _row_to_order(row) if row else None


def all_orders():
    rows = db.conn().execute("SELECT * FROM orders").fetchall()
    return [_row_to_order(r) for r in rows]


def events():
    rows = db.conn().execute("SELECT kind, payload FROM events ORDER BY id").fetchall()
    return [{"kind": r["kind"], "payload": json.loads(r["payload"])} for r in rows]


def audit_log():
    rows = db.conn().execute("SELECT msg FROM audit ORDER BY id").fetchall()
    return [r["msg"] for r in rows]
