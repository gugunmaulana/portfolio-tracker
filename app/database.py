import json
import sqlite3
import os
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db")

DEFAULT_PORTFOLIO_CONFIG = {
    "user_id": "default_user",
    "target_financial_freedom": 8844000000.0,
    "total_outgoings": 91457683.0,
    "cash_balance": 7525939.0, # Sisa saldo kas / Reksadana / BPJS
    "target_annual_min_return": 10.0,
    "target_annual_ideal_return": 20.0,
    "currency_base": "IDR",
    "categories": [
        {
            "id": "core_radar",
            "name": "CORE RADAR — 3 Best ETF",
            "subtitle": "Pondasi Index US & Semikonduktor",
            "color": "blue",
            "items": [
                {
                    "ticker": "VOO",
                    "name": "500 best US companies",
                    "category": "core_radar",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 20.0,
                    "pe_good": 23.0,
                    "pe_exp": 27.0
                },
                {
                    "ticker": "QQQ",
                    "name": "100 best tech firms",
                    "category": "core_radar",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 22.0,
                    "pe_good": 26.0,
                    "pe_exp": 32.0
                },
                {
                    "ticker": "SMH",
                    "name": "25 chip and AI stock",
                    "category": "core_radar",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 22.0,
                    "pe_good": 28.0,
                    "pe_exp": 35.0
                }
            ]
        },
        {
            "id": "war_nemesis",
            "name": "WAR NEMESIS & ANCHOR ASSETS",
            "subtitle": "Crypto Anchor & Safe Haven / Hedge",
            "color": "amber",
            "items": [
                {
                    "ticker": "BTC-USD",
                    "name": "Crypto Anchor (Bitcoin)",
                    "category": "war_nemesis",
                    "currency": "USD",
                    "invested_idr": 30008546.0,
                    "quantity": 0.022855,
                    "avg_price_usd": 74441.0,
                    "pe_great": None,
                    "pe_good": None,
                    "pe_exp": None
                },
                {
                    "ticker": "GC=F",
                    "name": "FX / Hedge (Gold USD / XAU)",
                    "category": "war_nemesis",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": None,
                    "pe_good": None,
                    "pe_exp": None
                }
            ]
        },
        {
            "id": "global_stock",
            "name": "US & GLOBAL MONOPOLY STOCK",
            "subtitle": "Tech Backbone & Semiconductor Chokepoint",
            "color": "indigo",
            "items": [
                {
                    "ticker": "BRK-B",
                    "name": "Mesin alokasi modal W.Buffet",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 15.0,
                    "pe_good": 20.0,
                    "pe_exp": 24.0
                },
                {
                    "ticker": "COST",
                    "name": "Raja konsumen",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 35.0,
                    "pe_good": 45.0,
                    "pe_exp": 50.0
                },
                {
                    "ticker": "JPM",
                    "name": "Raja perbankan global",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 11.0,
                    "pe_good": 14.0,
                    "pe_exp": 16.0
                },
                {
                    "ticker": "V",
                    "name": "Mesin tol ekonomi dunia",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 22.0,
                    "pe_good": 28.0,
                    "pe_exp": 32.0
                },
                {
                    "ticker": "MSFT",
                    "name": "Tech Backbone (Cloud / AI)",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 3003107.0,
                    "quantity": 0.43,
                    "avg_price_usd": 395.0,
                    "pe_great": 26.0,
                    "pe_good": 32.0,
                    "pe_exp": 38.0
                },
                {
                    "ticker": "AAPL",
                    "name": "Tech Backbone (Consumer Tech)",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 22.0,
                    "pe_good": 28.0,
                    "pe_exp": 32.0
                },
                {
                    "ticker": "META",
                    "name": "Tech Backbone (Social / AI)",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 980477.0,
                    "quantity": 0.1,
                    "avg_price_usd": 575.0,
                    "pe_great": 20.0,
                    "pe_good": 26.0,
                    "pe_exp": 30.0
                },
                {
                    "ticker": "AMZN",
                    "name": "Tech Backbone (E-Commerce & AWS)",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 30.0,
                    "pe_good": 40.0,
                    "pe_exp": 48.0
                },
                {
                    "ticker": "GOOGL",
                    "name": "Tech Backbone (Search & AI)",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 20.0,
                    "pe_good": 24.0,
                    "pe_exp": 28.0
                },
                {
                    "ticker": "AVGO",
                    "name": "Semiconductor Chokepoint",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 25.0,
                    "pe_good": 32.0,
                    "pe_exp": 38.0
                },
                {
                    "ticker": "TSM",
                    "name": "Semiconductor Foundry Chokepoint",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 18.0,
                    "pe_good": 22.0,
                    "pe_exp": 26.0
                },
                {
                    "ticker": "NVDA",
                    "name": "Semiconductor AI Compute Lead",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 28.0,
                    "pe_good": 36.0,
                    "pe_exp": 45.0
                },
                {
                    "ticker": "ASML",
                    "name": "Semiconductor Lithography Chokepoint",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 30.0,
                    "pe_good": 40.0,
                    "pe_exp": 52.0
                },
                {
                    "ticker": "LLY",
                    "name": "Health Signal & Biotech Monopoly",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 35.0,
                    "pe_good": 45.0,
                    "pe_exp": 55.0
                }
            ]
        },
        {
            "id": "satellites",
            "name": "EXTENDED RADAR — Indonesia & Crypto Satellites",
            "subtitle": "Diversifikasi Lokal IHSG & High-Beta Crypto",
            "color": "emerald",
            "items": [
                {
                    "ticker": "BBCA.JK",
                    "name": "Raja Perbankan Swasta RI",
                    "category": "satellites",
                    "currency": "IDR",
                    "invested_idr": 18224999.0,
                    "quantity": 25.0,
                    "avg_price_idr": 7290.0,
                    "is_lot": True,
                    "pe_great": 20.0,
                    "pe_good": 25.0,
                    "pe_exp": 30.0
                },
                {
                    "ticker": "BBRI.JK",
                    "name": "Raja Mikro & Dividen RI",
                    "category": "satellites",
                    "currency": "IDR",
                    "invested_idr": 1056000.0,
                    "quantity": 3.0,
                    "avg_price_idr": 3520.0,
                    "is_lot": True,
                    "pe_great": 11.0,
                    "pe_good": 14.0,
                    "pe_exp": 18.0
                },
                {
                    "ticker": "UNTR.JK",
                    "name": "Raja Alat Berat & Tambang RI",
                    "category": "satellites",
                    "currency": "IDR",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_idr": 0.0,
                    "is_lot": True,
                    "pe_great": 5.0,
                    "pe_good": 7.0,
                    "pe_exp": 9.0
                },
                {
                    "ticker": "BREN.JK",
                    "name": "Energi Terbarukan RI",
                    "category": "satellites",
                    "currency": "IDR",
                    "invested_idr": 407000.0,
                    "quantity": 1.0,
                    "avg_price_idr": 4070.0,
                    "is_lot": True,
                    "pe_great": 12.0,
                    "pe_good": 16.0,
                    "pe_exp": 22.0
                },
                {
                    "ticker": "ETH-USD",
                    "name": "Ethereum Smart Contract Platform",
                    "category": "satellites",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": None,
                    "pe_good": None,
                    "pe_exp": None
                },
                {
                    "ticker": "MSTR",
                    "name": "MicroStrategy Bitcoin Proxy",
                    "category": "satellites",
                    "currency": "USD",
                    "invested_idr": 29317750.0,
                    "quantity": 11.17,
                    "avg_price_usd": 151.73,
                    "pe_great": None,
                    "pe_good": None,
                    "pe_exp": None
                }
            ]
        },
        {
            "id": "watchlist",
            "name": "WATCHLIST — AI Infrastructure & Energy Grid",
            "subtitle": "Rantai Pasok Semikonduktor, Software & Nuklir",
            "color": "cyan",
            "items": [
                {
                    "ticker": "KLAC",
                    "name": "Raja metrology semikonduktor",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 20.0,
                    "pe_good": 26.0,
                    "pe_exp": 32.0
                },
                {
                    "ticker": "AMAT",
                    "name": "Infrastruktur chip global",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 18.0,
                    "pe_good": 23.0,
                    "pe_exp": 28.0
                },
                {
                    "ticker": "LRCX",
                    "name": "Chokepoint etching wafer",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 18.0,
                    "pe_good": 24.0,
                    "pe_exp": 30.0
                },
                {
                    "ticker": "ETN",
                    "name": "Raja elektrifikasi & daya",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 22.0,
                    "pe_good": 28.0,
                    "pe_exp": 34.0
                },
                {
                    "ticker": "RTX",
                    "name": "Aerospace & Defense",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 16.0,
                    "pe_good": 20.0,
                    "pe_exp": 25.0
                },
                {
                    "ticker": "SNPS",
                    "name": "Infrastruktur Software EDA Chip",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 401000.0,
                    "quantity": 0.06,
                    "avg_price_usd": 464.53,
                    "pe_great": 28.0,
                    "pe_good": 36.0,
                    "pe_exp": 45.0
                },
                {
                    "ticker": "CEG",
                    "name": "Tenaga AI + Listrik + Nuklir",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 447865.0,
                    "quantity": 0.104,
                    "avg_price_usd": 261.46,
                    "pe_great": 23.0,
                    "pe_good": 30.0,
                    "pe_exp": 40.0
                },
                {
                    "ticker": "PWR",
                    "name": "Grid Listrik & Transmisi AS",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 24.0,
                    "pe_good": 32.0,
                    "pe_exp": 40.0
                },
                {
                    "ticker": "CCJ",
                    "name": "Uranium Cycle (Bahan Bakar Nuklir)",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 25.0,
                    "pe_good": 35.0,
                    "pe_exp": 45.0
                },
                {
                    "ticker": "VRT",
                    "name": "Infrastruktur Data Center & Cooling AI",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 22.0,
                    "pe_good": 30.0,
                    "pe_exp": 38.0
                }
            ]
        }
    ]
}


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password_hash TEXT,
        name TEXT,
        target_financial_freedom REAL DEFAULT 8844000000.0,
        total_outgoings REAL DEFAULT 91457683.0,
        cash_balance REAL DEFAULT 7525939.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Table portfolio_items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        category TEXT,
        ticker TEXT,
        name TEXT,
        currency TEXT DEFAULT 'USD',
        invested_idr REAL DEFAULT 0.0,
        quantity REAL DEFAULT 0.0,
        avg_price REAL DEFAULT 0.0,
        is_lot INTEGER DEFAULT 0,
        pe_great REAL,
        pe_good REAL,
        pe_exp REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Seed default user if not exists
    cursor.execute("SELECT id FROM users WHERE id = 'default_user'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (id, email, password_hash, name, target_financial_freedom, total_outgoings, cash_balance) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("default_user", "investor@antigravity.ai", "demo_hash", "Master Investor", 8844000000.0, 91457683.0, 7525939.0)
        )
        
        for category in DEFAULT_PORTFOLIO_CONFIG["categories"]:
            for item in category["items"]:
                avg_p = item.get("avg_price_usd") if item.get("currency") == "USD" else item.get("avg_price_idr", 0.0)
                cursor.execute("""
                INSERT INTO portfolio_items (user_id, category, ticker, name, currency, invested_idr, quantity, avg_price, is_lot, pe_great, pe_good, pe_exp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "default_user",
                    item.get("category"),
                    item.get("ticker"),
                    item.get("name"),
                    item.get("currency", "USD"),
                    item.get("invested_idr", 0.0),
                    item.get("quantity", 0.0),
                    avg_p or 0.0,
                    1 if item.get("is_lot") else 0,
                    item.get("pe_great"),
                    item.get("pe_good"),
                    item.get("pe_exp")
                ))
    
    conn.commit()
    conn.close()


def get_user_portfolio(user_id: str = "default_user") -> Dict[str, Any]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return DEFAULT_PORTFOLIO_CONFIG
    
    cursor.execute("SELECT * FROM portfolio_items WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    items_by_cat = {}
    for r in rows:
        cat = r["category"]
        if cat not in items_by_cat:
            items_by_cat[cat] = []
        items_by_cat[cat].append({
            "id": r["id"],
            "ticker": r["ticker"],
            "name": r["name"],
            "category": r["category"],
            "currency": r["currency"],
            "invested_idr": float(r["invested_idr"] or 0.0),
            "quantity": float(r["quantity"] or 0.0),
            "avg_price": float(r["avg_price"] or 0.0),
            "is_lot": bool(r["is_lot"]),
            "pe_great": r["pe_great"],
            "pe_good": r["pe_good"],
            "pe_exp": r["pe_exp"]
        })
    
    categories = []
    cat_metadata = {
        "core_radar": ("CORE RADAR — 3 Best ETF", "Pondasi Index US & Semikonduktor", "blue"),
        "war_nemesis": ("WAR NEMESIS & ANCHOR ASSETS", "Crypto Anchor & Safe Haven / Hedge", "amber"),
        "global_stock": ("US & GLOBAL MONOPOLY STOCK", "Tech Backbone & Semiconductor Chokepoint", "indigo"),
        "satellites": ("EXTENDED RADAR — Indonesia & Crypto Satellites", "Diversifikasi Lokal IHSG & High-Beta Crypto", "emerald"),
        "watchlist": ("WATCHLIST — AI Infrastructure & Energy Grid", "Rantai Pasok Semikonduktor, Software & Nuklir", "cyan")
    }
    
    for cat_id, (name, subtitle, color) in cat_metadata.items():
        categories.append({
            "id": cat_id,
            "name": name,
            "subtitle": subtitle,
            "color": color,
            "items": items_by_cat.get(cat_id, [])
        })
        
    return {
        "user_id": user["id"],
        "user_name": user["name"],
        "target_financial_freedom": float(user["target_financial_freedom"]),
        "total_outgoings": float(user["total_outgoings"]),
        "cash_balance": float(user["cash_balance"]),
        "target_annual_min_return": 10.0,
        "target_annual_ideal_return": 20.0,
        "currency_base": "IDR",
        "categories": categories
    }


def update_user_settings(user_id: str, target_ff: float, total_outgoings: float, cash_balance: float):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users SET target_financial_freedom = ?, total_outgoings = ?, cash_balance = ? WHERE id = ?
    """, (target_ff, total_outgoings, cash_balance, user_id))
    conn.commit()
    conn.close()


def upsert_portfolio_item(user_id: str, item_data: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if item_data.get("id"):
        cursor.execute("""
        UPDATE portfolio_items SET
            category = ?, ticker = ?, name = ?, currency = ?, invested_idr = ?, quantity = ?, avg_price = ?,
            is_lot = ?, pe_great = ?, pe_good = ?, pe_exp = ?
        WHERE id = ? AND user_id = ?
        """, (
            item_data.get("category"), item_data.get("ticker"), item_data.get("name"),
            item_data.get("currency", "USD"), float(item_data.get("invested_idr") or 0.0),
            float(item_data.get("quantity") or 0.0), float(item_data.get("avg_price") or 0.0),
            1 if item_data.get("is_lot") else 0,
            item_data.get("pe_great"), item_data.get("pe_good"), item_data.get("pe_exp"),
            item_data.get("id"), user_id
        ))
    else:
        cursor.execute("""
        INSERT INTO portfolio_items (user_id, category, ticker, name, currency, invested_idr, quantity, avg_price, is_lot, pe_great, pe_good, pe_exp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, item_data.get("category"), item_data.get("ticker"), item_data.get("name"),
            item_data.get("currency", "USD"), float(item_data.get("invested_idr") or 0.0),
            float(item_data.get("quantity") or 0.0), float(item_data.get("avg_price") or 0.0),
            1 if item_data.get("is_lot") else 0,
            item_data.get("pe_great"), item_data.get("pe_good"), item_data.get("pe_exp")
        ))
    conn.commit()
    conn.close()


def delete_portfolio_item(user_id: str, item_id: int):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM portfolio_items WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
