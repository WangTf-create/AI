import importlib

import pytest

from order_engine import checkout, config, store


def test_checkout_current_coupon_threshold_operator_diff_fixed_vs_percent(user_factory):
    # 中文注释：锁住现状 - 优惠券阈值边界比较符不一致（fixed: >=，percent: >）
    items = [{"sku": "SKU-BOOK-1", "cat": "other", "price": 100, "qty": 1}]
    fixed_order = checkout(items, user_factory(), coupon={"type": "fixed", "amount": 10, "threshold": 100}, region="cn")
    percent_order = checkout(items, user_factory(), coupon={"type": "percent", "rate": 0.1, "threshold": 100}, region="cn")
    assert fixed_order["breakdown"]["after_coupon"] == pytest.approx(90.0)
    assert percent_order["breakdown"]["after_coupon"] == pytest.approx(100.0)


def test_checkout_current_loyalty_base_differs_from_pricing_subtotal_for_book_bulk(user_factory):
    # 中文注释：锁住现状 - points_earned 基数取 loyalty._own_subtotal，与 pricing subtotal 在 book>=5 时分叉
    items = [{"sku": "SKU-BOOK-1", "cat": "book", "price": 100, "qty": 5}]
    order = checkout(items, user_factory(loyalty_points=0), region="cn")
    pricing_sub = order["breakdown"]["subtotal"]
    points_event = [e for e in store.events() if e["kind"] == "points_earned"][-1]
    assert pricing_sub == pytest.approx(400.0)
    assert points_event["payload"]["base"] == pytest.approx(475.0)
    assert order["points_earned"] == 475


def test_checkout_current_eu_rounding_path_line_and_total_rounding(user_factory):
    # 中文注释：锁住现状 - EU 结算路径同时存在行项目 round 与总额 round
    items = [{"sku": "SKU-ELEC-1", "cat": "electronics", "price": 9.999, "qty": 3, "weight": 0.5}]
    order = checkout(items, user_factory(), region="eu")
    assert order["items"][0]["line"] == pytest.approx(28.5)
    assert order["breakdown"]["shipping"] == pytest.approx(21.0)
    assert order["total"] == pytest.approx(55.2)


def test_import_current_coupons_module_import_mutates_global_config():
    # 中文注释：锁住现状 - import coupons 触发注册券包，直接改写 COUPONS 与 FLAGS
    config.COUPONS.clear()
    config.COUPONS.update({
        "FIX10": {"type": "fixed", "amount": 10, "threshold": 100},
        "PCT10": {"type": "percent", "rate": 0.1, "threshold": 100},
        "PCT20": {"type": "percent", "rate": 0.2, "threshold": 200},
    })
    config.FLAGS["promo_pack_loaded"] = False
    import order_engine.coupons as coupons_module
    importlib.reload(coupons_module)
    assert "SPRING30" in config.COUPONS
    assert "PCT30" in config.COUPONS
    assert "FREESHIP" in config.COUPONS
    assert config.FLAGS["promo_pack_loaded"] is True


def test_checkout_current_mutates_input_user_loyalty_points_in_place(user_factory):
    # 中文注释：锁住现状 - checkout 会原地修改传入 user.loyalty_points（先 burn 再 earn）
    items = [{"sku": "SKU-BOOK-1", "cat": "book", "price": 100, "qty": 5}]
    user = user_factory(loyalty_points=200)
    order = checkout(items, user, region="cn", use_points=50)
    assert order["points_used"] == 50
    assert order["points_earned"] == 475
    assert user["loyalty_points"] == 625
