"""sqlite 连接与表结构。orders / inventory / reservations / audit / events 都落这里。"""

import os
import sqlite3

_DEFAULT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "order_engine.db"))

_state = {"path": _DEFAULT_PATH, "conn": None}

SEED_INVENTORY = {
    "SKU-FRESH-1": 100, "SKU-FRESH-2": 50,
    "SKU-BOOK-1": 200, "SKU-BOOK-2": 30,
    "SKU-ELEC-1": 20, "SKU-ELEC-2": 5,
    "SKU-CLOTH-1": 80, "SKU-LUX-1": 3,
    "SKU-DIGI-1": 999999, "SKU-GROC-1": 300,
}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id            TEXT PRIMARY KEY,
    user          TEXT,
    region        TEXT,
    status        TEXT,
    total         REAL,
    points_earned INTEGER DEFAULT 0,
    points_used   INTEGER DEFAULT 0,
    currency      TEXT,
    items_json    TEXT,
    breakdown_json TEXT
);
CREATE TABLE IF NOT EXISTS inventory (
    sku   TEXT PRIMARY KEY,
    stock INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS reservations (
    order_id TEXT,
    sku      TEXT,
    qty      INTEGER
);
CREATE TABLE IF NOT EXISTS audit (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    msg TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    kind    TEXT,
    payload TEXT
);
CREATE TABLE IF NOT EXISTS seq (
    name TEXT PRIMARY KEY,
    val  INTEGER
);
"""


def configure(path):
    """切换数据库文件（测试用临时库时调）。"""
    if _state["conn"] is not None:
        _state["conn"].close()
        _state["conn"] = None
    _state["path"] = os.path.abspath(path)


def conn():
    if _state["conn"] is None:
        c = sqlite3.connect(_state["path"])
        c.row_factory = sqlite3.Row
        _state["conn"] = c
        _ensure(c)
    return _state["conn"]


def _ensure(c):
    c.executescript(_SCHEMA)
    if c.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] == 0:
        c.executemany("INSERT INTO inventory(sku, stock) VALUES (?, ?)",
                      list(SEED_INVENTORY.items()))
    if c.execute("SELECT COUNT(*) FROM seq WHERE name='order'").fetchone()[0] == 0:
        c.execute("INSERT INTO seq(name, val) VALUES ('order', 1000)")
    c.commit()


def reset():
    """清库重建 + 重新灌种子库存。重复跑/测试前调。"""
    c = conn()
    c.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS inventory;
        DROP TABLE IF EXISTS reservations;
        DROP TABLE IF EXISTS audit;
        DROP TABLE IF EXISTS events;
        DROP TABLE IF EXISTS seq;
    """)
    _ensure(c)
