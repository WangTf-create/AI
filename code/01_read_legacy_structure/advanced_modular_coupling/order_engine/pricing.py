"""计价：购物车 → 小计。"""

from . import discounts
from . import context
from . import engine


def compute_subtotal(items):
    region = getattr(engine, "REGION", "cn")
    sub = 0.0
    lines = []
    for it in items:
        p = discounts.category_discount(it)
        if region == "eu":
            p = round(p, 2)
        lines.append({"sku": it.get("sku"), "cat": it.get("cat"),
                      "qty": it["qty"], "line": p})
        sub += p
    context.put("subtotal", sub)
    context.put("line_items", lines)
    return sub
