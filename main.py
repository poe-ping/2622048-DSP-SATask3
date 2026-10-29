"""ECサイトのログをSQLiteに格納し、SQLで集計する課題。

学習者が編集するのは、原則として SCHEMA_SQL と VIEWS_SQL の2箇所です。
"""

import csv
import json
import sqlite3
from pathlib import Path
from contextlib import closing


# 課題1：下のSQLに users / products / events のCREATE TABLE文を記述する。
SCHEMA_SQL = """
-- TODO: CREATE TABLE文を記述する。
"""


# 課題2：下のSQLに category_stats / region_stats のCREATE VIEW文を記述する。
VIEWS_SQL = """
-- TODO: CREATE VIEW文を記述する。
"""


def load_log(conn: sqlite3.Connection, log_path: Path) -> None:
    """ec.log を読み込む。ここは変更しなくてよい。"""
    users = []
    products = []
    events = []

    with log_path.open(encoding="utf-8", newline="") as f:
        for line_number, fields in enumerate(csv.reader(f), 1):
            if not fields or fields[0].startswith("#"):
                continue
            kind, *values = fields
            if kind == "USER" and len(values) == 2:
                users.append(tuple(values))
            elif kind == "PRODUCT" and len(values) == 2:
                products.append(tuple(values))
            elif kind == "EVENT" and len(values) == 5:
                event_id, user_id, product_id, event_type, amount = values
                events.append(
                    (event_id, user_id, product_id, event_type,
                     int(amount) if amount else None)
                )
            else:
                raise ValueError(f"ec.logの{line_number}行目が不正です: {fields}")

    # 外部キー制約があるので、参照される側から登録する。
    with conn:
        conn.executemany(
            "INSERT INTO users (user_id, region) VALUES (?, ?)", users
        )
        conn.executemany(
            "INSERT INTO products (product_id, category) VALUES (?, ?)", products
        )
        conn.executemany(
            "INSERT INTO events "
            "(event_id, user_id, product_id, event_type, amount) "
            "VALUES (?, ?, ?, ?, ?)", events
        )


def collect_result(conn: sqlite3.Connection) -> dict:
    """VIEWの結果をJSON用の辞書にまとめる。ここは変更しなくてよい。"""
    conn.row_factory = sqlite3.Row
    category = conn.execute(
        "SELECT category, purchase_count, revenue "
        "FROM category_stats ORDER BY category"
    ).fetchall()
    region = conn.execute(
        "SELECT region, unique_buyers "
        "FROM region_stats ORDER BY region"
    ).fetchall()
    return {
        "category_stats": [dict(row) for row in category],
        "region_stats": [dict(row) for row in region],
    }


def main() -> None:
    folder = Path(__file__).resolve().parent
    log_path = folder / "ec.log"
    db_path = folder / "ec.db"

    # 何度実行しても初期状態からDBを作り直す。
    if db_path.exists():
        db_path.unlink()

    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_SQL)
        load_log(conn, log_path)
        conn.executescript(VIEWS_SQL)
        result = collect_result(conn)

    # 標準出力にはJSONだけを出す（自動採点用）。
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
