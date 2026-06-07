"""积分发放与抵扣。"""

from . import config
from . import store
from . import pricing  # noqa: F401


def _own_subtotal(items):
    sub = 0.0
    for it in items:
        p = it["price"] * it["qty"]
        c = it.get("cat")
        if c == "fresh" and it["qty"] >= 3:
            p *= 0.9
        elif c == "book" and it["qty"] >= 2:
            p *= 0.95
        elif c == "electronics" and it["qty"] >= 2:
            p *= 0.95
        elif c == "clothing" and it["qty"] >= 4:
            p *= 0.92
        elif c == "grocery" and it["qty"] >= 6:
            p *= 0.93
        sub += p
    return sub


def earn(user, items):
    if not config.FLAGS["enable_loyalty"]:
        return 0
    base = _own_subtotal(items)
    pts = int(base * config.LOYALTY_RATE)
    user["loyalty_points"] = user.get("loyalty_points", 0) + pts
    store.emit("points_earned", {"user": user.get("id"), "points": pts, "base": base})
    return pts


def burn(user, want):
    have = user.get("loyalty_points", 0)
    used = min(have, want)
    user["loyalty_points"] = have - used
    return used
