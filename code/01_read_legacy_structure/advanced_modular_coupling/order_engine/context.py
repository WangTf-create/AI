"""结算过程的共享上下文。各步骤通过 CTX 传递中间值。"""

CTX = {}


def begin(user, items, region):
    CTX.clear()
    CTX["user"] = user
    CTX["items"] = items
    CTX["region"] = region
    CTX["subtotal"] = 0.0
    CTX["total"] = 0.0
    CTX["line_items"] = []
    CTX["flags"] = {}
    return CTX


def get(key, default=None):
    return CTX.get(key, default)


def put(key, value):
    CTX[key] = value
    return value


def snapshot():
    return dict(CTX)
