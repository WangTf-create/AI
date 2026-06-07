"""全局配置：折扣/VIP/税/运费/币种/券目录/开关/风控阈值。"""

CATEGORY_RULES = {
    "fresh": {"q": 3, "rate": 0.9},
    "book": {"q1": 2, "r1": 0.95, "q2": 5, "r2": 0.8},
    "electronics": {"q": 2, "rate": 0.95},
    "clothing": {"q": 4, "rate": 0.92},
    "grocery": {"q": 6, "rate": 0.93},
    "luxury": {"q": 999, "rate": 1.0},
    "digital": {"q": 1, "rate": 1.0},
}

VIP_RATES = {0: 1.0, 1: 0.98, 2: 0.95, 3: 0.9, 4: 0.88, 5: 0.85}

TAX = {"cn": 0.0, "us": 0.08, "eu": 0.2, "uk": 0.2, "jp": 0.1}

SHIPPING = {
    "cn": {"base": 8, "per_kg": 2, "free": 99},
    "us": {"base": 12, "per_kg": 3, "free": 150},
    "eu": {"base": 15, "per_kg": 4, "free": 200},
    "uk": {"base": 14, "per_kg": 4, "free": 200},
    "jp": {"base": 10, "per_kg": 3, "free": 120},
}

CURRENCY = {"cn": "CNY", "us": "USD", "eu": "EUR", "uk": "GBP", "jp": "JPY"}

COUPONS = {
    "FIX10": {"type": "fixed", "amount": 10, "threshold": 100},
    "PCT10": {"type": "percent", "rate": 0.1, "threshold": 100},
    "PCT20": {"type": "percent", "rate": 0.2, "threshold": 200},
}

FLAGS = {
    "enable_risk": True,
    "enable_loyalty": True,
    "enable_notify": True,
    "promo_pack_loaded": False,
}

RISK = {"hard": 50000, "soft": 8000, "items": 30, "reject": 80}

LOYALTY_RATE = 1.0


def register_promo_pack():
    COUPONS.update({
        "SPRING30": {"type": "fixed", "amount": 30, "threshold": 200},
        "PCT30": {"type": "percent", "rate": 0.3, "threshold": 500},
        "FREESHIP": {"type": "freeship", "threshold": 0},
    })
    FLAGS["promo_pack_loaded"] = True


def set_flag(name, value):
    FLAGS[name] = value
    return value
