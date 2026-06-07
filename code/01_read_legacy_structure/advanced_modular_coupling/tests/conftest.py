import copy
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from order_engine import config, context, engine, reset_all
from order_engine import db


@pytest.fixture(autouse=True)
def isolated_state(tmp_path):
    # 中文注释：每条测试切换到独立临时数据库，避免污染默认库
    db.configure(str(tmp_path / "order_engine_test.db"))
    # 中文注释：保存全局可变配置快照，测试后恢复
    snap = {
        "CATEGORY_RULES": copy.deepcopy(config.CATEGORY_RULES),
        "VIP_RATES": copy.deepcopy(config.VIP_RATES),
        "TAX": copy.deepcopy(config.TAX),
        "SHIPPING": copy.deepcopy(config.SHIPPING),
        "CURRENCY": copy.deepcopy(config.CURRENCY),
        "COUPONS": copy.deepcopy(config.COUPONS),
        "FLAGS": copy.deepcopy(config.FLAGS),
        "RISK": copy.deepcopy(config.RISK),
        "LOYALTY_RATE": config.LOYALTY_RATE,
        "REGION": engine.REGION,
    }
    reset_all()
    yield
    reset_all()
    context.CTX.clear()
    engine.REGION = snap["REGION"]
    config.CATEGORY_RULES.clear()
    config.CATEGORY_RULES.update(snap["CATEGORY_RULES"])
    config.VIP_RATES.clear()
    config.VIP_RATES.update(snap["VIP_RATES"])
    config.TAX.clear()
    config.TAX.update(snap["TAX"])
    config.SHIPPING.clear()
    config.SHIPPING.update(snap["SHIPPING"])
    config.CURRENCY.clear()
    config.CURRENCY.update(snap["CURRENCY"])
    config.COUPONS.clear()
    config.COUPONS.update(snap["COUPONS"])
    config.FLAGS.clear()
    config.FLAGS.update(snap["FLAGS"])
    config.RISK.clear()
    config.RISK.update(snap["RISK"])
    config.LOYALTY_RATE = snap["LOYALTY_RATE"]


@pytest.fixture
def user_factory():
    def _user(**overrides):
        u = {"id": "U-1", "vip": False, "vip_level": 0, "new": False, "loyalty_points": 0}
        u.update(overrides)
        return u

    return _user
