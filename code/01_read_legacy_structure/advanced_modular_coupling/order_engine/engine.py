"""结算编排：把计价、折扣、券、税、运费、风控、库存、积分、通知串起来。"""

from . import db
from . import context
from . import pricing
from . import discounts
from . import coupons
from . import taxship
from . import risk
from . import inventory
from . import loyalty
from . import notify
from . import store
from . import config

REGION = "cn"


def reset_all():
    db.reset()
    context.CTX.clear()


def checkout(items, user, coupon=None, region="cn", use_points=0, dry_run=False):
    global REGION
    REGION = region
    context.begin(user, items, region)
    oid = store.next_id()

    sub = pricing.compute_subtotal(items)
    context.put("total", sub)

    discounts.apply_vip()
    coupons.apply_coupon(coupon)

    used_pts = 0
    if use_points and config.FLAGS["enable_loyalty"]:
        used_pts = loyalty.burn(user, use_points)
        t = context.get("total", 0.0) - used_pts / 100.0
        context.put("total", max(0.0, t))

    taxship.apply_tax()
    taxship.apply_shipping()

    total = round(context.get("total", 0.0), 2)
    line_items = context.get("line_items", [])

    s = 0
    if config.FLAGS["enable_risk"]:
        s = risk.score(total)

    status = "confirmed"
    reserved = False
    if not dry_run:
        reserved = inventory.reserve(oid, items)
        if not reserved:
            status = "out_of_stock"

    if config.FLAGS["enable_risk"] and risk.rejected(s):
        order = {"id": oid, "user": user.get("id"), "region": region,
                 "items": line_items, "total": total, "status": "rejected",
                 "risk": s, "breakdown": context.snapshot()}
        if not dry_run:
            store.save(order)
        store.emit("order_rejected", {"order_id": oid, "risk": s})
        return order

    earned = 0
    if config.FLAGS["enable_loyalty"] and status == "confirmed" and not dry_run:
        earned = loyalty.earn(user, items)

    order = {"id": oid, "user": user.get("id"), "region": region,
             "items": line_items, "total": total, "status": status,
             "risk": s, "points_earned": earned, "points_used": used_pts,
             "currency": config.CURRENCY.get(region, "CNY"),
             "breakdown": context.snapshot()}

    if not dry_run and status == "confirmed":
        store.save(order)
        notify.send(user, order)
    return order


def quote(items, user, coupon=None, region="cn"):
    o = checkout(items, user, coupon=coupon, region=region, dry_run=True)
    return round(o["total"], 2)
