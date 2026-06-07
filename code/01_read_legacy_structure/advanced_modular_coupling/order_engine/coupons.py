"""优惠券。"""

from . import config
from . import context
from . import discounts  # noqa: F401

config.register_promo_pack()


def _resolve(coupon):
    if coupon is None:
        return None
    if isinstance(coupon, str):
        return config.COUPONS.get(coupon)
    return coupon


def apply_coupon(coupon):
    c = _resolve(coupon)
    t = context.get("total", 0.0)
    if c:
        ct = c.get("type")
        if ct == "fixed":
            if t >= c.get("threshold", 0):
                t = t - c["amount"]
        elif ct == "percent":
            if t > c.get("threshold", 0):
                t = t * (1 - c["rate"])
        elif ct == "freeship":
            context.put("force_freeship", True)
    if t < 0:
        t = 0.0
    context.put("total", t)
    context.put("after_coupon", t)
    return t
