"""下几笔订单，看看结算服务跑起来的样子。

    cd code/01_read_legacy_structure/advanced_modular_coupling
    python runner.py
"""

import order_engine as oe
from order_engine import store, inventory


def main():
    oe.reset_all()

    carts = [
        ("cn", [{"sku": "SKU-FRESH-1", "price": 20, "qty": 3, "cat": "fresh", "weight": 1.0},
                {"sku": "SKU-BOOK-1", "price": 30, "qty": 5, "cat": "book", "weight": 0.4}],
         {"id": "alice", "vip": True, "vip_level": 2, "loyalty_points": 500}, "PCT10"),
        ("us", [{"sku": "SKU-ELEC-1", "price": 1000, "qty": 2, "cat": "electronics", "weight": 3.0}],
         {"id": "bob", "vip": False, "loyalty_points": 0}, None),
        ("eu", [{"sku": "SKU-CLOTH-1", "price": 80, "qty": 4, "cat": "clothing", "weight": 1.2}],
         {"id": "carol", "vip": True, "vip_level": 4, "loyalty_points": 3000}, "FREESHIP"),
        ("cn", [{"sku": "SKU-ELEC-2", "price": 100, "qty": 2, "cat": "electronics", "weight": 2.0}],
         {"id": "dave", "blacklist": True, "loyalty_points": 0}, None),
    ]

    print("下单结果：")
    for region, items, user, coupon in carts:
        o = oe.checkout(items, user, coupon=coupon, region=region)
        print("  %-7s %-7s %-12s total=%-8s points=%s" %
              (o["id"], region, o["status"], o["total"], o.get("points_earned")))

    print("\n库存对账：")
    print(" ", inventory.reconcile())

    print("\n当前库存快照：")
    print(" ", inventory.all_stock())

    print("\n已落库订单数：", len(store.all_orders()))


if __name__ == "__main__":
    main()
