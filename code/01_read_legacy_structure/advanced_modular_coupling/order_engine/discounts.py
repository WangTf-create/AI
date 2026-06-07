"""品类折扣与 VIP 折扣。"""

from . import config
from . import context


def category_discount(item):
    p = item["price"] * item["qty"]
    c = item.get("cat")
    r = config.CATEGORY_RULES.get(c)
    if not r:
        return p
    if c == "book":
        if item["qty"] >= r["q2"]:
            p = p * r["r2"]
        elif item["qty"] >= r["q1"]:
            p = p * r["r1"]
    else:
        if item["qty"] >= r["q"]:
            p = p * r["rate"]
    return p


def apply_vip():
    user = context.get("user", {})
    t = context.get("total", 0.0)
    if user.get("vip"):
        lv = user.get("vip_level", 1)
        rate = config.VIP_RATES.get(lv, config.VIP_RATES[5] if lv > 5 else 1.0)
        t = t * rate
    context.put("total", t)
    context.put("after_vip", t)
    return t
