"""风控打分。"""

from . import config
from . import context


def score(amount):
    user = context.get("user", {})
    items = context.get("items", [])
    s = 0
    if user.get("blacklist"):
        s += 100
    if amount > config.RISK["hard"]:
        s += 100
    elif amount > config.RISK["soft"]:
        s += 40
    if sum(i["qty"] for i in items) > config.RISK["items"]:
        s += 30
    if user.get("new") and amount > 3000:
        s += 25
    for it in items:
        if it.get("cat") == "luxury" and it["price"] * it["qty"] > 5000:
            s += 20
            break
    context.put("risk", s)
    return s


def rejected(s):
    return s >= config.RISK["reject"]
