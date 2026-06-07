"""下单通知。"""

from . import config
from . import store


def send(user, order):
    if not config.FLAGS["enable_notify"]:
        return
    msg = "订单 %s 已确认，应付 %.2f" % (order["id"], order["total"])
    store.audit("notify %s: %s" % (user.get("id"), msg))
    store.emit("order_confirmed", {"order_id": order["id"], "total": order["total"]})
