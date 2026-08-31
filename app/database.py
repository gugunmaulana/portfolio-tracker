import json
import sqlite3
import os
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db")

DEFAULT_CATEGORIES_DATA = [
    ("core_radar", "default_user", "CORE RADAR — 3 Best ETF", "Pondasi Index US & Semikonduktor", "blue", 1),
    ("war_nemesis", "default_user", "WAR NEMESIS & ANCHOR ASSETS", "Crypto Anchor & Safe Haven / Hedge", "amber", 2),
    ("global_stock", "default_user", "US & GLOBAL MONOPOLY STOCK", "Tech Backbone & Semiconductor Chokepoint", "indigo", 3),
    ("satellites", "default_user", "EXTENDED RADAR — Indonesia & Crypto Satellites", "Diversifikasi Lokal IHSG & High-Beta Crypto", "emerald", 4),
    ("watchlist", "default_user", "WATCHLIST — AI Infrastructure & Energy Grid", "Rantai Pasok Semikonduktor, Software & Nuklir", "cyan", 5),
    ("reksadana", "default_user", "REKSA DANA — Pasar Uang & Pendapatan Tetap", "Posisi Investasi Reksa Dana & Yield Stabil", "teal", 6),
]

DEFAULT_PORTFOLIO_CONFIG = {
    "user_id": "default_user",
    "target_financial_freedom": 8844000000.0,
    "total_outgoings": 91457683.0,
    "cash_balance": 3000000.0, # Sisa saldo kas
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
                    "name": "Konglomerasi Buffett & Kas Masif",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 16.0,
                    "pe_good": 20.0,
                    "pe_exp": 25.0
                },
                {
                    "ticker": "COST",
                    "name": "Ritel Monopoli Membership",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 32.0,
                    "pe_good": 40.0,
                    "pe_exp": 50.0
                },
                {
                    "ticker": "JPM",
                    "name": "Raja Finansial & Perbankan Wall St",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 10.0,
                    "pe_good": 12.5,
                    "pe_exp": 15.0
                },
                {
                    "ticker": "V",
                    "name": "Rel Pembayaran & Finansial Global",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 24.0,
                    "pe_good": 29.0,
                    "pe_exp": 35.0
                },
                {
                    "ticker": "MSFT",
                    "name": "Tech Backbone (Enterprise & Cloud)",
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
                    "name": "Heavy Equipment & Tambang Emas",
                    "category": "satellites",
                    "currency": "IDR",
                    "invested_idr": 2420000.0,
                    "quantity": 1.0,
                    "avg_price_idr": 24200.0,
                    "is_lot": True,
                    "pe_great": 5.0,
                    "pe_good": 6.5,
                    "pe_exp": 8.5
                },
                {
                    "ticker": "BREN.JK",
                    "name": "Energi Terbarukan Panas Bumi RI",
                    "category": "satellites",
                    "currency": "IDR",
                    "invested_idr": 922500.0,
                    "quantity": 1.0,
                    "avg_price_idr": 9225.0,
                    "is_lot": True,
                    "pe_great": 80.0,
                    "pe_good": 120.0,
                    "pe_exp": 180.0
                },
                {
                    "ticker": "ETH-USD",
                    "name": "Smart Contract Platform Leader",
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
                    "name": "Bitcoin Treasury & Hyper-Leverage",
                    "category": "satellites",
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
                },
                {
                    "ticker": "CRWD",
                    "name": "Raja Proteksi Endpoint & AI Security",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 35.0,
                    "pe_good": 48.0,
                    "pe_exp": 65.0
                },
                {
                    "ticker": "SPGI",
                    "name": "Duopoli Rating Obligasi & Lisensi Indeks",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 24.0,
                    "pe_good": 30.0,
                    "pe_exp": 38.0
                },
                {
                    "ticker": "ISRG",
                    "name": "Monopoli Robot Bedah",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 35.0,
                    "pe_good": 45.0,
                    "pe_exp": 60.0
                },
                {
                    "ticker": "PLTR",
                    "name": "Sistem Operasi AI Militer & Enterprise",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 35.0,
                    "pe_good": 50.0,
                    "pe_exp": 75.0
                },
                {
                    "ticker": "TMO",
                    "name": "Pemasok Alat Lab & Sains Terbesar",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 20.0,
                    "pe_good": 26.0,
                    "pe_exp": 34.0
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
    
    # Table categories (Editable & Dynamic Categories)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        name TEXT,
        subtitle TEXT,
        color TEXT DEFAULT 'blue',
        sort_order INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
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

    # Table monthly_records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        year INTEGER DEFAULT 2026,
        month_index INTEGER,
        month_name TEXT,
        total_outgoings REAL DEFAULT 0.0,
        current_networth REAL DEFAULT 0.0,
        investing_power REAL DEFAULT 0.0,
        pnl_idr REAL DEFAULT 0.0,
        pnl_pct REAL DEFAULT 0.0,
        growth_pct REAL DEFAULT 0.0,
        notes TEXT DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Add sort_order column to portfolio_items if not present
    try:
        cursor.execute("ALTER TABLE portfolio_items ADD COLUMN sort_order INTEGER DEFAULT 0")
    except Exception:
        pass

    # Ensure BMRI is removed from core_radar
    cursor.execute("DELETE FROM portfolio_items WHERE UPPER(ticker) LIKE '%BMRI%' AND category = 'core_radar'")

    # Seed default user if not exists
    cursor.execute("SELECT id FROM users WHERE id = 'default_user'")
    if not cursor.fetchone():
        backup_path = os.path.join(os.path.dirname(__file__), "portfolio_state.json")
        loaded_from_json = False
        if os.path.exists(backup_path):
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                cursor.execute(
                    "INSERT INTO users (id, email, password_hash, name, target_financial_freedom, total_outgoings, cash_balance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("default_user", "investor@antigravity.ai", "demo_hash", state.get("user_name", "Master Investor"), state.get("target_financial_freedom", 8844000000.0), state.get("total_outgoings", 91457683.0), state.get("cash_balance", 7525939.0))
                )
                for cat in state.get("categories", []):
                    cursor.execute("""
                    INSERT OR REPLACE INTO categories (id, user_id, name, subtitle, color, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (cat.get("id"), "default_user", cat.get("name"), cat.get("subtitle", ""), cat.get("color", "blue"), cat.get("sort_order", 0)))
                    for item in cat.get("items", []):
                        if "BMRI" in item.get("ticker", "").upper() and cat.get("id") == "core_radar":
                            continue
                        cursor.execute("""
                        INSERT INTO portfolio_items (user_id, category, ticker, name, currency, invested_idr, quantity, avg_price, is_lot, pe_great, pe_good, pe_exp, sort_order)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            "default_user",
                            cat.get("id"),
                            item.get("ticker"),
                            item.get("name"),
                            item.get("currency", "USD"),
                            float(item.get("invested_idr") or 0.0),
                            float(item.get("quantity") or 0.0),
                            float(item.get("avg_price") or 0.0),
                            1 if item.get("is_lot") else 0,
                            item.get("pe_great"),
                            item.get("pe_good"),
                            item.get("pe_exp"),
                            item.get("sort_order", 0)
                        ))
                loaded_from_json = True
            except Exception:
                pass

        if not loaded_from_json:
            cursor.execute(
                "INSERT INTO users (id, email, password_hash, name, target_financial_freedom, total_outgoings, cash_balance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("default_user", "investor@antigravity.ai", "demo_hash", "Master Investor", 8844000000.0, 91457683.0, 7525939.0)
            )
            for category in DEFAULT_PORTFOLIO_CONFIG["categories"]:
                for item in category["items"]:
                    if "BMRI" in item.get("ticker", "").upper() and category.get("id") == "core_radar":
                        continue
                    avg_p = item.get("avg_price_usd") if item.get("currency") == "USD" else item.get("avg_price_idr", 0.0)
                    cursor.execute("""
                    INSERT INTO portfolio_items (user_id, category, ticker, name, currency, invested_idr, quantity, avg_price, is_lot, pe_great, pe_good, pe_exp, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
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

    # Seed default categories if not exist
    cursor.execute("SELECT COUNT(*) FROM categories WHERE user_id = 'default_user'")
    if cursor.fetchone()[0] == 0:
        for cat_id, uid, name, sub, col, ord_idx in DEFAULT_CATEGORIES_DATA:
            cursor.execute("""
            INSERT OR REPLACE INTO categories (id, user_id, name, subtitle, color, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (cat_id, uid, name, sub, col, ord_idx))

    # Seed default monthly records for 2026 if not exist
    cursor.execute("SELECT COUNT(*) FROM monthly_records WHERE user_id = 'default_user' AND year = 2026")
    if cursor.fetchone()[0] == 0:
        default_months = [
            (1, "January", 43917439.0, 39285665.0, 0.0, -4631774.0, -10.55, 0.0),
            (2, "February", 45099478.0, 37095212.0, 1182039.0, -8004266.0, -17.75, -8.58),
            (3, "March", 57989517.0, 47608747.0, 12890039.0, -10380770.0, -17.90, -6.41),
            (4, "April", 62111193.0, 56906866.0, 4121676.0, -5204327.0, -8.38, 10.87),
            (5, "May", 67128411.0, 61162314.0, 5017218.0, -5966097.0, -8.89, -1.34),
            (6, "June", 78442336.0, 56494980.0, 11313925.0, -21947356.0, -27.98, -26.13),
            (7, "July", 88382212.0, 72712908.0, 9939876.0, -15669304.0, -17.73, 11.11),
            (8, "August", 91457683.0, 85256693.0, 3075471.0, -6200990.0, -6.78, 12.98),
            (9, "September", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            (10, "October", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            (11, "November", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            (12, "December", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        ]
        for m_idx, m_name, outg, netw, inv_pwr, pnl_idr, pnl_pct, growth in default_months:
            cursor.execute("""
            INSERT INTO monthly_records (user_id, year, month_index, month_name, total_outgoings, current_networth, investing_power, pnl_idr, pnl_pct, growth_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("default_user", 2026, m_idx, m_name, outg, netw, inv_pwr, pnl_idr, pnl_pct, growth))
    
    # Ensure column_order and visible_columns exist in users table for cross-device permanent sync
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN column_order TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN visible_columns TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN target_financial_freedom_usd REAL DEFAULT 500000.0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN target_mode TEXT DEFAULT 'USD'")
    except Exception:
        pass

    # Ensure default target is 500k USD in USD mode and cash balance is 3,000,000 IDR
    cursor.execute("UPDATE users SET target_financial_freedom_usd = 500000.0, target_mode = 'USD', cash_balance = 3000000.0 WHERE id = 'default_user'")

    # Ensure category reksadana and items exist
    cursor.execute("SELECT COUNT(*) FROM categories WHERE user_id = 'default_user' AND id = 'reksadana'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO categories (id, user_id, name, subtitle, color, sort_order)
        VALUES ('reksadana', 'default_user', 'REKSA DANA — Pasar Uang & Pendapatan Tetap', 'Posisi Investasi Reksa Dana & Yield Stabil', 'teal', 6)
        """)
        
    cursor.execute("SELECT COUNT(*) FROM portfolio_items WHERE user_id = 'default_user' AND category = 'reksadana'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO portfolio_items (user_id, category, ticker, name, currency, invested_idr, quantity, avg_price, is_lot, sort_order)
        VALUES 
        ('default_user', 'reksadana', 'MNC-BAROKAH', 'MNC Dana Syariah Barokah (Pasar Uang)', 'IDR', 4000000.0, 4011553.0, 0.99712, 0, 1),
        ('default_user', 'reksadana', 'CAPITAL-FIXED', 'Capital Fixed Income Fund (Pendapatan Tetap)', 'IDR', 3010000.0, 3063669.0, 0.98248, 0, 2)
        """)

    # Enforce uppercase tickers across all existing database records
    cursor.execute("UPDATE portfolio_items SET ticker = UPPER(TRIM(ticker)) WHERE ticker IS NOT NULL")
    
    conn.commit()
    conn.close()


def sync_realtime_monthly_snapshot(user_id: str = "default_user", portfolio_data: Optional[Dict[str, Any]] = None):
    """Sync current month's record in WIB (UTC+7) with realtime portfolio metrics and rollover at end of month."""
    if not portfolio_data:
        return
    import datetime
    now_wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    cur_year = now_wib.year
    cur_month_idx = now_wib.month

    init_db()
    create_year_records(user_id, cur_year)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    outg = float(portfolio_data.get("total_outgoings_idr") or portfolio_data.get("total_outgoings", 0.0))
    netw = float(portfolio_data.get("current_net_worth_idr") or portfolio_data.get("current_net_worth", 0.0))
    pnl_idr = float(portfolio_data.get("total_pnl_idr", 0.0))
    pnl_pct = float(portfolio_data.get("total_pnl_pct", 0.0))

    prev_month_idx = cur_month_idx - 1
    prev_year = cur_year
    if prev_month_idx < 1:
        prev_month_idx = 12
        prev_year = cur_year - 1

    cursor.execute("SELECT current_networth, total_outgoings FROM monthly_records WHERE user_id = ? AND year = ? AND month_index = ?", (user_id, prev_year, prev_month_idx))
    prev_row = cursor.fetchone()
    prev_netw = float(prev_row[0]) if prev_row and prev_row[0] else 0.0
    prev_outg = float(prev_row[1]) if prev_row and prev_row[1] else 0.0

    growth_pct = 0.0
    if prev_netw > 0 and netw > 0:
        growth_pct = ((netw - prev_netw) / prev_netw) * 100.0

    inv_pwr = (outg - prev_outg) if (prev_outg > 0 and outg >= prev_outg) else 3075471.0
    if inv_pwr <= 0:
        inv_pwr = 3075471.0

    cursor.execute("""
    UPDATE monthly_records SET
        total_outgoings = ?,
        current_networth = ?,
        investing_power = ?,
        pnl_idr = ?,
        pnl_pct = ?,
        growth_pct = ?
    WHERE user_id = ? AND year = ? AND month_index = ?
    """, (outg, netw, inv_pwr, pnl_idr, pnl_pct, round(growth_pct, 2), user_id, cur_year, cur_month_idx))
    conn.commit()
    conn.close()


def get_user_categories(user_id: str = "default_user") -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE user_id = ? ORDER BY sort_order ASC, id ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_category(user_id: str, data: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cat_id = data.get("id", "").strip().lower().replace(" ", "_")
    name = data.get("name", "Kategori Baru")
    subtitle = data.get("subtitle", "")
    color = data.get("color", "blue")
    sort_order = int(data.get("sort_order", 99))
    
    cursor.execute("""
    INSERT INTO categories (id, user_id, name, subtitle, color, sort_order)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        subtitle = excluded.subtitle,
        color = excluded.color,
        sort_order = excluded.sort_order
    """, (cat_id, user_id, name, subtitle, color, sort_order))
    conn.commit()
    conn.close()
    backup_portfolio_state_to_json(user_id)


def delete_category(user_id: str, category_id: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ? AND user_id = ?", (category_id, user_id))
    # Note: we do not delete assets, we can keep them or user can reassign
    conn.commit()
    conn.close()
    backup_portfolio_state_to_json(user_id)


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
    
    # Query categories
    cursor.execute("SELECT * FROM categories WHERE user_id = ? ORDER BY sort_order ASC, id ASC", (user_id,))
    cat_rows = cursor.fetchall()
    
    cursor.execute("SELECT * FROM portfolio_items WHERE user_id = ? ORDER BY sort_order ASC, id ASC", (user_id,))
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
            "pe_exp": r["pe_exp"],
            "sort_order": r["sort_order"] if "sort_order" in r.keys() else 0
        })
    
    categories = []
    seen_cats = set()
    for crow in cat_rows:
        cid = crow["id"]
        seen_cats.add(cid)
        categories.append({
            "id": cid,
            "name": crow["name"],
            "subtitle": crow["subtitle"] or "",
            "color": crow["color"] or "blue",
            "sort_order": crow["sort_order"],
            "items": items_by_cat.get(cid, [])
        })
        
    # Any item with a category not in table
    for cat_id, items in items_by_cat.items():
        if cat_id not in seen_cats:
            categories.append({
                "id": cat_id,
                "name": cat_id.replace("_", " ").upper(),
                "subtitle": "Kategori Kustom",
                "color": "cyan",
                "sort_order": 99,
                "items": items
            })
        
    # Parse saved column settings if available
    saved_col_order = None
    saved_vis_cols = None
    try:
        if "column_order" in user.keys() and user["column_order"]:
            saved_col_order = json.loads(user["column_order"])
        if "visible_columns" in user.keys() and user["visible_columns"]:
            saved_vis_cols = json.loads(user["visible_columns"])
    except Exception:
        pass

    return {
        "user_id": user["id"],
        "user_name": user["name"],
        "target_mode": user["target_mode"] if "target_mode" in user.keys() and user["target_mode"] else "USD",
        "target_financial_freedom_usd": float(user["target_financial_freedom_usd"]) if "target_financial_freedom_usd" in user.keys() and user["target_financial_freedom_usd"] else 500000.0,
        "target_financial_freedom": float(user["target_financial_freedom"]),
        "total_outgoings": float(user["total_outgoings"]),
        "cash_balance": float(user["cash_balance"]),
        "target_annual_min_return": 10.0,
        "target_annual_ideal_return": 20.0,
        "currency_base": "IDR",
        "categories": categories,
        "column_order": saved_col_order,
        "visible_columns": saved_vis_cols
    }


def get_available_years(user_id: str = "default_user") -> List[int]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT year FROM monthly_records WHERE user_id = ? ORDER BY year ASC", (user_id,))
    years = [row[0] for row in cursor.fetchall()]
    conn.close()
    if not years:
        years = [2026]
    return sorted(list(set(years)))


def create_year_records(user_id: str = "default_user", year: int = 2026):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM monthly_records WHERE user_id = ? AND year = ?", (user_id, year))
    if cursor.fetchone()[0] == 0:
        months = [
            (1, "January"), (2, "February"), (3, "March"), (4, "April"),
            (5, "May"), (6, "June"), (7, "July"), (8, "August"),
            (9, "September"), (10, "October"), (11, "November"), (12, "December")
        ]
        for m_idx, m_name in months:
            cursor.execute("""
            INSERT INTO monthly_records (user_id, year, month_index, month_name, total_outgoings, current_networth, investing_power, pnl_idr, pnl_pct, growth_pct, notes)
            VALUES (?, ?, ?, ?, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, '')
            """, (user_id, year, m_idx, m_name))
        conn.commit()
    conn.close()


def get_monthly_records(user_id: str = "default_user", year: int = 2026) -> List[Dict[str, Any]]:
    init_db()
    create_year_records(user_id, year)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monthly_records WHERE user_id = ? AND year = ? ORDER BY month_index ASC", (user_id, year))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        inv_pwr = float(r["investing_power"] or 0.0)
        results.append({
            "id": r["id"],
            "year": r["year"],
            "month_index": r["month_index"],
            "month_name": r["month_name"],
            "total_outgoings": float(r["total_outgoings"] or 0.0),
            "current_networth": float(r["current_networth"] or 0.0),
            "investing_power": inv_pwr,
            "pnl_idr": float(r["pnl_idr"] or 0.0),
            "pnl_pct": float(r["pnl_pct"] or 0.0),
            "growth_pct": float(r["growth_pct"] or 0.0),
            "notes": r["notes"] or ""
        })
    return results


def upsert_monthly_record(user_id: str, record: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    outg = float(record.get("total_outgoings") or 0.0)
    netw = float(record.get("current_networth") or 0.0)
    inv_pwr = float(record.get("investing_power") or 0.0)
    
    pnl_idr = (netw - outg) if outg > 0 else 0.0
    pnl_pct = ((pnl_idr / outg) * 100.0) if outg > 0 else 0.0
    growth_pct = float(record.get("growth_pct") or 0.0)
    
    if record.get("id"):
        cursor.execute("""
        UPDATE monthly_records SET
            total_outgoings = ?, current_networth = ?, investing_power = ?,
            pnl_idr = ?, pnl_pct = ?, growth_pct = ?, notes = ?
        WHERE id = ? AND user_id = ?
        """, (outg, netw, inv_pwr, pnl_idr, pnl_pct, growth_pct, record.get("notes", ""), record.get("id"), user_id))
    else:
        cursor.execute("""
        INSERT INTO monthly_records (user_id, year, month_index, month_name, total_outgoings, current_networth, investing_power, pnl_idr, pnl_pct, growth_pct, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, int(record.get("year", 2026)), int(record.get("month_index", 1)),
            record.get("month_name", "Month"), outg, netw, inv_pwr, pnl_idr, pnl_pct, growth_pct, record.get("notes", "")
        ))
    conn.commit()
    conn.close()


def update_user_settings(user_id: str, target_ff: float, total_outgoings: float, cash_balance: float, target_ff_usd: float = 500000.0, target_mode: str = "USD"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users SET target_financial_freedom = ?, total_outgoings = ?, cash_balance = ?, target_financial_freedom_usd = ?, target_mode = ? WHERE id = ?
    """, (target_ff, total_outgoings, cash_balance, target_ff_usd, target_mode, user_id))
    conn.commit()
    conn.close()
    backup_portfolio_state_to_json(user_id)


def get_user_column_settings(user_id: str = "default_user") -> Dict[str, Any]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT column_order, visible_columns FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        c_order = json.loads(row["column_order"]) if row["column_order"] else None
        v_cols = json.loads(row["visible_columns"]) if row["visible_columns"] else None
        return {"column_order": c_order, "visible_columns": v_cols}
    return {"column_order": None, "visible_columns": None}


def update_user_column_settings(user_id: str, column_order: Optional[List[str]], visible_columns: Optional[Dict[str, bool]]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    c_str = json.dumps(column_order) if column_order is not None else None
    v_str = json.dumps(visible_columns) if visible_columns is not None else None
    cursor.execute("""
    UPDATE users SET column_order = ?, visible_columns = ? WHERE id = ?
    """, (c_str, v_str, user_id))
    conn.commit()
    conn.close()


def upsert_portfolio_item(user_id: str, item_data: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ticker = (item_data.get("ticker") or "").strip().upper()
    if item_data.get("id"):
        cursor.execute("""
        UPDATE portfolio_items SET
            category = ?, ticker = ?, name = ?, currency = ?, invested_idr = ?, quantity = ?, avg_price = ?,
            is_lot = ?, pe_great = ?, pe_good = ?, pe_exp = ?
        WHERE id = ? AND user_id = ?
        """, (
            item_data.get("category"), ticker, item_data.get("name"),
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
            user_id, item_data.get("category"), ticker, item_data.get("name"),
            item_data.get("currency", "USD"), float(item_data.get("invested_idr") or 0.0),
            float(item_data.get("quantity") or 0.0), float(item_data.get("avg_price") or 0.0),
            1 if item_data.get("is_lot") else 0,
            item_data.get("pe_great"), item_data.get("pe_good"), item_data.get("pe_exp")
        ))
    conn.commit()
    conn.close()
    backup_portfolio_state_to_json(user_id)


def delete_portfolio_item(user_id: str, item_id: int):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM portfolio_items WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
    backup_portfolio_state_to_json(user_id)


def move_portfolio_item(user_id: str, item_id: int, target_category: str, target_sort_order: int = 0):
    """Move an asset item to a target category and update its sort order."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE portfolio_items SET category = ?, sort_order = ?
    WHERE id = ? AND user_id = ?
    """, (target_category, target_sort_order, item_id, user_id))
    conn.commit()
    conn.close()
    backup_portfolio_state_to_json(user_id)


def reorder_portfolio_items(user_id: str, item_orders: List[Dict[str, Any]]):
    """Update sort order and category of multiple items."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for item in item_orders:
        item_id = item.get("id")
        category = item.get("category")
        sort_order = item.get("sort_order", 0)
        if item_id:
            cursor.execute("""
            UPDATE portfolio_items SET category = COALESCE(?, category), sort_order = ?
            WHERE id = ? AND user_id = ?
            """, (category, sort_order, item_id, user_id))
    conn.commit()
    conn.close()
    backup_portfolio_state_to_json(user_id)


def reorder_categories(user_id: str, category_orders: List[Dict[str, Any]]):
    """Update sort order of multiple categories."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for cat in category_orders:
        cat_id = cat.get("id")
        sort_order = cat.get("sort_order", 0)
        if cat_id:
            cursor.execute("""
            UPDATE categories SET sort_order = ?
            WHERE id = ? AND user_id = ?
            """, (sort_order, cat_id, user_id))
    conn.commit()
    conn.close()
    backup_portfolio_state_to_json(user_id)


def backup_portfolio_state_to_json(user_id: str = "default_user"):
    """Automatically persist current active user portfolio and categories to a JSON backup file."""
    try:
        data = get_user_portfolio(user_id)
        backup_path = os.path.join(os.path.dirname(__file__), "portfolio_state.json")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pass