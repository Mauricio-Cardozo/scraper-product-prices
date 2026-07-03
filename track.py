#!/usr/bin/env python3
"""Compare current prices against the last known snapshot."""

import argparse, csv, sqlite3, sys
from datetime import datetime
from pathlib import Path

DB = Path("output") / "price_history.db"


def _init_db():
    Path("output").mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price TEXT,
            source TEXT,
            checked_at TEXT
        )
    """)
    conn.commit()
    return conn


def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_snapshot(conn, rows: list[dict], source: str):
    now = datetime.now().isoformat()
    for row in rows:
        # Intenta encontrar precio en cualquiera de los formatos comunes
        price = row.get("precio_sugerido") or row.get("price") or row.get("precio_dropshipping") or "0"
        name = row.get("nombre") or row.get("name") or "?"
        conn.execute(
            "INSERT INTO prices (name, price, source, checked_at) VALUES (?, ?, ?, ?)",
            (name, price, source, now),
        )
    conn.commit()


def get_last(conn) -> dict:
    rows = conn.execute("""
        SELECT name, price FROM prices
        WHERE id IN (SELECT MAX(id) FROM prices GROUP BY name)
    """).fetchall()
    return {r[0]: r[1] for r in rows}


def main():
    parser = argparse.ArgumentParser(description="Compare prices against last snapshot")
    parser.add_argument("csv", help="Current CSV snapshot from scraper")
    parser.add_argument("--all", action="store_true", help="Show all products, not just changes")
    args = parser.parse_args()

    current = load_csv(args.csv)
    conn = _init_db()
    source = Path(args.csv).stem

    last = get_last(conn)
    save_snapshot(conn, current, source)
    conn.close()

    changes = []
    for row in current:
        name = row.get("nombre") or row.get("name") or "?"
        new_price = row.get("precio_sugerido") or row.get("price") or row.get("precio_dropshipping") or "0"
        old_price = last.get(name)

        if old_price is None:
            changes.append((name, "-", new_price, "+NEW"))
        elif old_price != new_price:
            diff = int(float(new_price)) - int(float(old_price))
            arrow = "🔺" if diff > 0 else "🔻"
            changes.append((name, old_price, new_price, f"{diff:+d} {arrow}"))

    if not changes:
        print("✓ No price changes.")
        return

    print(f"{'Product':<35} {'Old':<10} {'New':<10} {'Change'}")
    print("-" * 70)
    for name, old, new, change in changes:
        print(f"{name:<35} {old:<10} {new:<10} {change}")


if __name__ == "__main__":
    main()
