"""极简计价：给 workflow（lint + pytest）一个真实可跑的对象。"""

from typing import Iterable, Mapping


def line_total(price: float, qty: int, discount: float = 0.0) -> float:
    """单行金额 = price * qty * (1 - discount)，保留两位。"""
    if price < 0:
        raise ValueError("price 不能为负")
    if qty < 0:
        raise ValueError("qty 不能为负")
    if not 0.0 <= discount < 1.0:
        raise ValueError("discount 取值范围 [0, 1)")
    return round(price * qty * (1.0 - discount), 2)


def cart_total(items: Iterable[Mapping[str, float]]) -> float:
    """购物车合计：每行取 price/qty/discount 累加。"""
    total = 0.0
    for it in items:
        total += line_total(
            float(it["price"]),
            int(it["qty"]),
            float(it.get("discount", 0.0)),
        )
    return round(total, 2)
