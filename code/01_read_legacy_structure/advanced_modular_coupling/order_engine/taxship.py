"""税与运费。"""

from . import config
from . import context


def apply_tax():
    region = context.get("region", "cn")
    t = context.get("total", 0.0)
    rate = config.TAX.get(region, 0.0)
    tax = t * rate
    t = t + tax
    context.put("tax", tax)
    context.put("total", t)
    return t


def apply_shipping():
    region = context.get("region", "cn")
    cfg = config.SHIPPING.get(region, config.SHIPPING["cn"])
    items = context.get("items", [])
    weight = sum(it.get("weight", 0.5) * it["qty"] for it in items)
    ship = 0.0
    if context.get("force_freeship"):
        ship = 0.0
    else:
        sub = context.get("subtotal", 0.0)
        if sub >= cfg["free"]:
            ship = 0.0
        else:
            ship = cfg["base"] + cfg["per_kg"] * weight
    t = context.get("total", 0.0) + ship
    if region == "eu":
        t = round(t, 2)
    context.put("shipping", ship)
    context.put("total", t)
    return t
