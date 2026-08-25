import json
import sqlite3
import os
import time
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db")

# Static ETF Look-Through Decomposition (Constituent Weightings for Hidden Concentration)
DEFAULT_ETF_LOOKTHROUGH = {
    "VOO": {
        "name": "Vanguard S&P 500 ETF",
        "underlying": {
            "AAPL": 0.071,
            "MSFT": 0.066,
            "NVDA": 0.061,
            "AMZN": 0.038,
            "META": 0.025,
            "GOOGL": 0.021,
            "BRK-B": 0.017,
            "AVGO": 0.017,
            "JPM": 0.014,
            "LLY": 0.013,
            "COST": 0.008,
            "V": 0.008
        },
        "sectors": {
            "Information Technology": 0.320,
            "Financials": 0.132,
            "Health Care": 0.118,
            "Consumer Discretionary": 0.103,
            "Communication Services": 0.091,
            "Industrials": 0.082,
            "Consumer Staples": 0.058,
            "Energy": 0.036,
            "Others": 0.060
        },
        "geography": {"US": 0.99, "Global": 0.01}
    },
    "QQQ": {
        "name": "Invesco QQQ Trust (Nasdaq 100)",
        "underlying": {
            "AAPL": 0.088,
            "MSFT": 0.082,
            "NVDA": 0.076,
            "AMZN": 0.054,
            "META": 0.046,
            "AVGO": 0.044,
            "GOOGL": 0.028,
            "COST": 0.024,
            "TSM": 0.000,
            "ASML": 0.015
        },
        "sectors": {
            "Information Technology": 0.512,
            "Communication Services": 0.155,
            "Consumer Discretionary": 0.134,
            "Health Care": 0.062,
            "Consumer Staples": 0.057,
            "Industrials": 0.048,
            "Others": 0.032
        },
        "geography": {"US": 0.97, "Global": 0.03}
    },
    "SMH": {
        "name": "VanEck Semiconductor ETF",
        "underlying": {
            "NVDA": 0.235,
            "TSM": 0.128,
            "AVGO": 0.082,
            "ASML": 0.058,
            "AMAT": 0.046,
            "KLAC": 0.045,
            "LRCX": 0.043,
            "QCOM": 0.042,
            "TXN": 0.038,
            "AMD": 0.037
        },
        "sectors": {
            "Semiconductors & Equipment": 0.985,
            "Others": 0.015
        },
        "geography": {"US": 0.78, "Taiwan": 0.13, "Netherlands": 0.06, "Global": 0.03}
    }
}

# Seed Indonesian Tax Framework Rules (Versioned & Authoritative)
DEFAULT_TAX_RULES = [
    {
        "instrument_type": "IDX_EQUITY",
        "jurisdiction": "Indonesia",
        "rate_pct": 0.1,
        "base_desc": "0.1% PPh Final dari Nilai Bruto Transaksi Penjualan Saham di BEI",
        "effective_from": "1997-05-29",
        "effective_to": "Present",
        "source": "PP No. 14/1997 jo PP No. 41/1994",
        "notes": "PPh Final atas penjualan saham Bursa Efek Indonesia. Ditambah 0.5% bila saham pendiri (IPO)."
    },
    {
        "instrument_type": "IDX_DIVIDEND",
        "jurisdiction": "Indonesia",
        "rate_pct": 10.0,
        "base_desc": "10% PPh Final atau 0% (Bebas Pajak) jika direinvestasikan di wilayah NKRI min. 3 tahun",
        "effective_from": "2021-02-17",
        "effective_to": "Present",
        "source": "UU Cipta Kerja No. 11/2020 jo PMK No. 18/PMK.03/2021",
        "notes": "Dividen orang pribadi dalam negeri bebas PPh jika direinvestasikan sesuai ketentuan."
    },
    {
        "instrument_type": "SBN_GOV_BOND",
        "jurisdiction": "Indonesia",
        "rate_pct": 10.0,
        "base_desc": "10% PPh Final atas Bunga/Kupon dan Diskonto Obligasi Pemerintah (SBN/ORI/SR/PBS)",
        "effective_from": "2021-08-30",
        "effective_to": "Present",
        "source": "PP No. 91 Tahun 2021",
        "notes": "Tarif PPh Final atas bunga obligasi diturunkan dari 15% menjadi 10% untuk investor domestik."
    },
    {
        "instrument_type": "MUTUAL_FUND",
        "jurisdiction": "Indonesia",
        "rate_pct": 0.0,
        "base_desc": "Bukan Objek Pajak Penghasilan (PPh 0%)",
        "effective_from": "2008-01-01",
        "effective_to": "Present",
        "source": "UU PPh Pasal 4 Ayat (3) Huruf i",
        "notes": "Keuntungan pembagian laba/NAB reksadana bukan merupakan objek PPh bagi pemegang unit."
    },
    {
        "instrument_type": "PHYSICAL_GOLD",
        "jurisdiction": "Indonesia",
        "rate_pct": 0.25,
        "base_desc": "PPh Pasal 22: 0.25% (NPWP) / 0.5% (Non-NPWP) saat pembelian emas batangan",
        "effective_from": "2023-05-01",
        "effective_to": "Present",
        "source": "PMK No. 48 Tahun 2023",
        "notes": "Penjualan kembali (buyback) > Rp 10 Juta dikenakan PPh 22 sebesar 1.5% (NPWP) / 3% (Non-NPWP)."
    },
    {
        "instrument_type": "CRYPTO_ASSETS",
        "jurisdiction": "Indonesia",
        "rate_pct": 0.21,
        "base_desc": "0.1% PPh Final + 0.11% PPN (Total 0.21%) pada Exchange Terdaftar Bappebti",
        "effective_from": "2022-05-01",
        "effective_to": "Present",
        "source": "PMK No. 68/PMK.03/2022",
        "notes": "Jika exchange non-Bappebti: PPh Final 0.2% + PPN 0.22% (Total 0.42%)."
    },
    {
        "instrument_type": "FOREIGN_SECURITIES",
        "jurisdiction": "US / Global",
        "rate_pct": 0.0,
        "base_desc": "Capital Gain luar negeri digabung dalam SPT Tahunan PPh Orang Pribadi (Tarif Progresif 5% - 35%)",
        "effective_from": "2022-01-01",
        "effective_to": "Present",
        "source": "UU HPP No. 7 Tahun 2021",
        "notes": "Dividen saham US dikenakan US Withholding Tax (WHT) 30% (atau 15% jika Form W-8BEN Tax Treaty)."
    }
]

DEFAULT_PORTFOLIO_CONFIG = {
    "user_id": "default_user",
    "target_financial_freedom": 8844000000.0,
    "total_outgoings": 91457683.0,
    "cash_balance": 7525939.0,
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
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 25.0,
                    "pe_good": 32.0,
                    "pe_exp": 38.0
                },
                {
                    "ticker": "AAPL",
                    "name": "Consumer Ecosystem Monopoly",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 22.0,
                    "pe_good": 28.0,
                    "pe_exp": 35.0
                },
                {
                    "ticker": "META",
                    "name": "Digital Ads & Open AI Leader",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 20.0,
                    "pe_good": 26.0,
                    "pe_exp": 32.0
                },
                {
                    "ticker": "AMZN",
                    "name": "E-Commerce & AWS Cloud Giant",
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
                    "ticker": "GOOGL",
                    "name": "Search, YouTube & AI Infrastructure",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 18.0,
                    "pe_good": 23.0,
                    "pe_exp": 28.0
                },
                {
                    "ticker": "AVGO",
                    "name": "Custom AI ASIC & Networking Giant",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 24.0,
                    "pe_good": 32.0,
                    "pe_exp": 40.0
                },
                {
                    "ticker": "TSM",
                    "name": "Foundry Monopoli Semikonduktor",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 18.0,
                    "pe_good": 24.0,
                    "pe_exp": 30.0
                },
                {
                    "ticker": "NVDA",
                    "name": "Raja komputasi AI & GPU",
                    "category": "global_stock",
                    "currency": "USD",
                    "invested_idr": 12165074.0,
                    "quantity": 6.0,
                    "avg_price_usd": 123.68,
                    "pe_great": 28.0,
                    "pe_good": 38.0,
                    "pe_exp": 48.0
                },
                {
                    "ticker": "ASML",
                    "name": "Monopoli mesin litografi EUV",
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
                    "pe_great": 25.0,
                    "pe_good": 32.0,
                    "pe_exp": 40.0
                },
                {
                    "ticker": "RTX",
                    "name": "Pertahanan & kedirgantaraan",
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
                    "ticker": "SNPS",
                    "name": "Software desain EDA chip",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 35.0,
                    "pe_good": 45.0,
                    "pe_exp": 55.0
                },
                {
                    "ticker": "CEG",
                    "name": "Pembangkit nuklir & energi bersih",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 22.0,
                    "pe_good": 28.0,
                    "pe_exp": 35.0
                },
                {
                    "ticker": "PWR",
                    "name": "Konstruksi grid & infrastruktur AI",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 26.0,
                    "pe_good": 34.0,
                    "pe_exp": 42.0
                },
                {
                    "ticker": "CCJ",
                    "name": "Produsen bahan bakar uranium nuklir",
                    "category": "watchlist",
                    "currency": "USD",
                    "invested_idr": 0.0,
                    "quantity": 0.0,
                    "avg_price_usd": 0.0,
                    "pe_great": 28.0,
                    "pe_good": 38.0,
                    "pe_exp": 48.0
                },
                {
                    "ticker": "VRT",
                    "name": "Pendingin liquid & power data center",
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
    """Initialize or migrate SQLite tables safely without losing any existing records."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Table users (with comprehensive investor settings)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password_hash TEXT,
        name TEXT,
        target_financial_freedom REAL DEFAULT 8844000000.0,
        total_outgoings REAL DEFAULT 91457683.0,
        cash_balance REAL DEFAULT 7525939.0,
        birth_year INTEGER DEFAULT 1999,
        target_retirement_age INTEGER DEFAULT 45,
        monthly_contribution REAL DEFAULT 5000000.0,
        contribution_growth REAL DEFAULT 5.0,
        inflation_rate REAL DEFAULT 3.5,
        expected_return REAL DEFAULT 15.0,
        volatility_assump REAL DEFAULT 18.0,
        withdrawal_rate REAL DEFAULT 4.0,
        risk_tolerance TEXT DEFAULT 'MODERATE_AGGRESSIVE',
        base_currency TEXT DEFAULT 'IDR',
        target_allocations_json TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Helper to check and add missing columns to users
    cursor.execute("PRAGMA table_info(users)")
    existing_user_cols = [row[1] for row in cursor.fetchall()]
    new_user_cols = {
        "birth_year": "INTEGER DEFAULT 1999",
        "target_retirement_age": "INTEGER DEFAULT 45",
        "monthly_contribution": "REAL DEFAULT 5000000.0",
        "contribution_growth": "REAL DEFAULT 5.0",
        "inflation_rate": "REAL DEFAULT 3.5",
        "expected_return": "REAL DEFAULT 15.0",
        "volatility_assump": "REAL DEFAULT 18.0",
        "withdrawal_rate": "REAL DEFAULT 4.0",
        "risk_tolerance": "TEXT DEFAULT 'MODERATE_AGGRESSIVE'",
        "base_currency": "TEXT DEFAULT 'IDR'",
        "target_allocations_json": "TEXT DEFAULT '{}'"
    }
    for col_name, col_type in new_user_cols.items():
        if col_name not in existing_user_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass
    
    # 2. Table portfolio_items (with look-through and categorization)
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
        target_weight REAL DEFAULT 0.0,
        asset_class TEXT DEFAULT 'EQUITY',
        geography TEXT DEFAULT 'GLOBAL',
        sector TEXT DEFAULT 'General',
        tax_category TEXT DEFAULT 'FOREIGN_SECURITIES',
        etf_lookthrough_json TEXT DEFAULT '{}',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    cursor.execute("PRAGMA table_info(portfolio_items)")
    existing_item_cols = [row[1] for row in cursor.fetchall()]
    new_item_cols = {
        "target_weight": "REAL DEFAULT 0.0",
        "asset_class": "TEXT DEFAULT 'EQUITY'",
        "geography": "TEXT DEFAULT 'GLOBAL'",
        "sector": "TEXT DEFAULT 'General'",
        "tax_category": "TEXT DEFAULT 'FOREIGN_SECURITIES'",
        "etf_lookthrough_json": "TEXT DEFAULT '{}'"
    }
    for col_name, col_type in new_item_cols.items():
        if col_name not in existing_item_cols:
            try:
                cursor.execute(f"ALTER TABLE portfolio_items ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass

    # 3. Table monthly_records
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
    
    # 4. Table transactions (full transaction-level accounting)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        ticker TEXT,
        type TEXT, -- BUY, SELL, DIVIDEND, INTEREST, FEE, TAX, DEPOSIT, WITHDRAWAL, FX_CONVERT
        quantity REAL DEFAULT 0.0,
        price REAL DEFAULT 0.0,
        currency TEXT DEFAULT 'USD',
        fees_idr REAL DEFAULT 0.0,
        tax_idr REAL DEFAULT 0.0,
        total_idr REAL DEFAULT 0.0,
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 5. Table liabilities (for True Net Worth = Total Assets - Total Liabilities)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS liabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT,
        type TEXT, -- MORTGAGE, PERSONAL_LOAN, CREDIT_CARD, BUSINESS_DEBT, OTHER
        balance_idr REAL DEFAULT 0.0,
        interest_rate_pct REAL DEFAULT 0.0,
        monthly_payment_idr REAL DEFAULT 0.0,
        remaining_term_months INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 6. Table investment_theses (Thesis Journal)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investment_theses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        ticker TEXT,
        thesis TEXT,
        catalysts TEXT,
        risks TEXT,
        invalidation TEXT,
        status TEXT DEFAULT 'INTACT', -- INTACT, WEAKENING, BROKEN
        review_date TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 7. Table assumption_history (Audit Trail for Assumptions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assumption_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        field_name TEXT,
        old_value TEXT,
        new_value TEXT,
        reason TEXT
    )
    """)

    # 8. Table tax_rules (Versioned Indonesian Tax Framework)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tax_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_type TEXT UNIQUE,
        jurisdiction TEXT,
        rate_pct REAL,
        base_desc TEXT,
        effective_from TEXT,
        effective_to TEXT,
        source TEXT,
        notes TEXT
    )
    """)

    # Seed Tax Rules if empty
    cursor.execute("SELECT COUNT(*) FROM tax_rules")
    if cursor.fetchone()[0] == 0:
        for r in DEFAULT_TAX_RULES:
            cursor.execute("""
            INSERT OR IGNORE INTO tax_rules (instrument_type, jurisdiction, rate_pct, base_desc, effective_from, effective_to, source, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (r["instrument_type"], r["jurisdiction"], r["rate_pct"], r["base_desc"], r["effective_from"], r["effective_to"], r["source"], r["notes"]))

    # Seed default user if not exists
    cursor.execute("SELECT id FROM users WHERE id = 'default_user'")
    if not cursor.fetchone():
        cursor.execute(
            """INSERT INTO users (
                id, email, password_hash, name, target_financial_freedom, total_outgoings, cash_balance,
                birth_year, target_retirement_age, monthly_contribution, contribution_growth,
                inflation_rate, expected_return, volatility_assump, withdrawal_rate, risk_tolerance, base_currency, target_allocations_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "default_user", "investor@antigravity.ai", "demo_hash", "Master Investor",
                8844000000.0, 91457683.0, 7525939.0,
                1999, 45, 5000000.0, 5.0,
                3.5, 15.0, 18.0, 4.0, "MODERATE_AGGRESSIVE", "IDR",
                json.dumps({
                    "core_radar": 35.0,
                    "war_nemesis": 25.0,
                    "global_stock": 25.0,
                    "satellites": 15.0,
                    "watchlist": 0.0
                })
            )
        )
        
        for category in DEFAULT_PORTFOLIO_CONFIG["categories"]:
            for item in category["items"]:
                avg_p = item.get("avg_price_usd") if item.get("currency") == "USD" else item.get("avg_price_idr", 0.0)
                ticker = item.get("ticker", "")
                
                # Derive asset class and geography
                if ticker.startswith("BTC") or ticker.startswith("ETH"):
                    a_class = "CRYPTO"
                    geo = "GLOBAL_CRYPTO"
                    tax_cat = "CRYPTO_ASSETS"
                elif ticker == "GC=F":
                    a_class = "COMMODITY"
                    geo = "GLOBAL"
                    tax_cat = "PHYSICAL_GOLD"
                elif ticker.endswith(".JK"):
                    a_class = "EQUITY"
                    geo = "ID"
                    tax_cat = "IDX_EQUITY"
                elif ticker in ["VOO", "QQQ", "SMH"]:
                    a_class = "ETF"
                    geo = "US"
                    tax_cat = "FOREIGN_SECURITIES"
                else:
                    a_class = "EQUITY"
                    geo = "US"
                    tax_cat = "FOREIGN_SECURITIES"

                lookthrough_data = DEFAULT_ETF_LOOKTHROUGH.get(ticker, {})

                cursor.execute("""
                INSERT INTO portfolio_items (
                    user_id, category, ticker, name, currency, invested_idr, quantity, avg_price,
                    is_lot, pe_great, pe_good, pe_exp, asset_class, geography, sector, tax_category, etf_lookthrough_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "default_user",
                    item.get("category"),
                    ticker,
                    item.get("name"),
                    item.get("currency", "USD"),
                    item.get("invested_idr", 0.0),
                    item.get("quantity", 0.0),
                    avg_p or 0.0,
                    1 if item.get("is_lot") else 0,
                    item.get("pe_great"),
                    item.get("pe_good"),
                    item.get("pe_exp"),
                    a_class,
                    geo,
                    "Technology" if a_class in ["ETF", "EQUITY"] else "Asset",
                    tax_cat,
                    json.dumps(lookthrough_data)
                ))

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
            
    # Seed default sample investment theses if empty
    cursor.execute("SELECT COUNT(*) FROM investment_theses WHERE user_id = 'default_user'")
    if cursor.fetchone()[0] == 0:
        theses = [
            ("NVDA", "Monopoli arsitektur akselerator AI & ekosistem CUDA. Memiliki moat software yang tidak bisa digantikan dalam 5-10 tahun.", "Rilis chip Blackwell & pertumbuhan capex hyperscaler.", "Regulasi ekspor AS & margin kompresi jika custom ASIC meluas.", "INTACT", "2026-12-31"),
            ("BTC-USD", "Jangkar penyimpan nilai terdesentralisasi (Digital Gold) dengan batas suplai 21 juta koin. Proteksi terhadap inflasi fiat global.", "Inflow institusional ETF spot & devaluasi mata uang.", "Pelarangan regulasi global atau risiko kegagalan konsensus.", "INTACT", "2026-12-31"),
            ("BBCA.JK", "Raja dana murah (CASA > 80%) dan mesin kredit swasta terbaik di Asia Tenggara dengan ROE > 20%.", "Pertumbuhan kredit korporasi dan konsumsi kelas menengah RI.", "NPL spike ekstrem akibat krisis makro Indonesia.", "INTACT", "2026-12-31")
        ]
        for t_sym, th, cat, rsk, st, r_date in theses:
            cursor.execute("""
            INSERT INTO investment_theses (user_id, ticker, thesis, catalysts, risks, status, review_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("default_user", t_sym, th, cat, rsk, st, r_date))

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
            
        lookthrough = {}
        try:
            if r["etf_lookthrough_json"]:
                lookthrough = json.loads(r["etf_lookthrough_json"])
        except Exception:
            lookthrough = {}

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
            "target_weight": float(r["target_weight"] or 0.0),
            "asset_class": r["asset_class"] or "EQUITY",
            "geography": r["geography"] or "GLOBAL",
            "sector": r["sector"] or "General",
            "tax_category": r["tax_category"] or "FOREIGN_SECURITIES",
            "lookthrough": lookthrough
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
        
    target_allocs = {}
    try:
        if user["target_allocations_json"]:
            target_allocs = json.loads(user["target_allocations_json"])
    except Exception:
        target_allocs = {}

    return {
        "user_id": user["id"],
        "user_name": user["name"],
        "target_financial_freedom": float(user["target_financial_freedom"]),
        "total_outgoings": float(user["total_outgoings"]),
        "cash_balance": float(user["cash_balance"]),
        "birth_year": int(user["birth_year"] or 1999),
        "target_retirement_age": int(user["target_retirement_age"] or 45),
        "monthly_contribution": float(user["monthly_contribution"] or 5000000.0),
        "contribution_growth": float(user["contribution_growth"] or 5.0),
        "inflation_rate": float(user["inflation_rate"] or 3.5),
        "expected_return": float(user["expected_return"] or 15.0),
        "volatility_assump": float(user["volatility_assump"] or 18.0),
        "withdrawal_rate": float(user["withdrawal_rate"] or 4.0),
        "risk_tolerance": user["risk_tolerance"] or "MODERATE_AGGRESSIVE",
        "target_allocations": target_allocs,
        "target_annual_min_return": 10.0,
        "target_annual_ideal_return": 20.0,
        "currency_base": user["base_currency"] or "IDR",
        "categories": categories
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


def update_user_settings(
    user_id: str,
    target_ff: float,
    total_outgoings: float,
    cash_balance: float,
    birth_year: Optional[int] = None,
    target_retirement_age: Optional[int] = None,
    monthly_contribution: Optional[float] = None,
    contribution_growth: Optional[float] = None,
    inflation_rate: Optional[float] = None,
    expected_return: Optional[float] = None,
    volatility_assump: Optional[float] = None,
    withdrawal_rate: Optional[float] = None,
    risk_tolerance: Optional[str] = None,
    target_allocations_json: Optional[str] = None
):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Audit trail for changes
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    current_u = cursor.fetchone()
    
    cursor.execute("""
    UPDATE users SET
        target_financial_freedom = ?,
        total_outgoings = ?,
        cash_balance = ?,
        birth_year = COALESCE(?, birth_year),
        target_retirement_age = COALESCE(?, target_retirement_age),
        monthly_contribution = COALESCE(?, monthly_contribution),
        contribution_growth = COALESCE(?, contribution_growth),
        inflation_rate = COALESCE(?, inflation_rate),
        expected_return = COALESCE(?, expected_return),
        volatility_assump = COALESCE(?, volatility_assump),
        withdrawal_rate = COALESCE(?, withdrawal_rate),
        risk_tolerance = COALESCE(?, risk_tolerance),
        target_allocations_json = COALESCE(?, target_allocations_json)
    WHERE id = ?
    """, (
        target_ff, total_outgoings, cash_balance,
        birth_year, target_retirement_age, monthly_contribution, contribution_growth,
        inflation_rate, expected_return, volatility_assump, withdrawal_rate, risk_tolerance,
        target_allocations_json, user_id
    ))
    conn.commit()
    conn.close()


def upsert_portfolio_item(user_id: str, item_data: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    target_w = float(item_data.get("target_weight") or 0.0)
    a_class = item_data.get("asset_class") or "EQUITY"
    geo = item_data.get("geography") or "GLOBAL"
    sector = item_data.get("sector") or "General"
    tax_cat = item_data.get("tax_category") or "FOREIGN_SECURITIES"
    lookthrough = item_data.get("etf_lookthrough_json") or "{}"

    if item_data.get("id"):
        cursor.execute("""
        UPDATE portfolio_items SET
            category = ?, ticker = ?, name = ?, currency = ?, invested_idr = ?, quantity = ?, avg_price = ?,
            is_lot = ?, pe_great = ?, pe_good = ?, pe_exp = ?, target_weight = ?, asset_class = ?, geography = ?,
            sector = ?, tax_category = ?, etf_lookthrough_json = ?
        WHERE id = ? AND user_id = ?
        """, (
            item_data.get("category"), item_data.get("ticker"), item_data.get("name"),
            item_data.get("currency", "USD"), float(item_data.get("invested_idr") or 0.0),
            float(item_data.get("quantity") or 0.0), float(item_data.get("avg_price") or 0.0),
            1 if item_data.get("is_lot") else 0,
            item_data.get("pe_great"), item_data.get("pe_good"), item_data.get("pe_exp"),
            target_w, a_class, geo, sector, tax_cat, lookthrough,
            item_data.get("id"), user_id
        ))
    else:
        cursor.execute("""
        INSERT INTO portfolio_items (
            user_id, category, ticker, name, currency, invested_idr, quantity, avg_price,
            is_lot, pe_great, pe_good, pe_exp, target_weight, asset_class, geography, sector, tax_category, etf_lookthrough_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, item_data.get("category"), item_data.get("ticker"), item_data.get("name"),
            item_data.get("currency", "USD"), float(item_data.get("invested_idr") or 0.0),
            float(item_data.get("quantity") or 0.0), float(item_data.get("avg_price") or 0.0),
            1 if item_data.get("is_lot") else 0,
            item_data.get("pe_great"), item_data.get("pe_good"), item_data.get("pe_exp"),
            target_w, a_class, geo, sector, tax_cat, lookthrough
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


# Liabilities & Debts Management (for Net Worth calculation)
def get_user_liabilities(user_id: str = "default_user") -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM liabilities WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_liability(user_id: str, data: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if data.get("id"):
        cursor.execute("""
        UPDATE liabilities SET
            name = ?, type = ?, balance_idr = ?, interest_rate_pct = ?, monthly_payment_idr = ?,
            remaining_term_months = ?, notes = ?
        WHERE id = ? AND user_id = ?
        """, (
            data.get("name"), data.get("type", "MORTGAGE"), float(data.get("balance_idr") or 0.0),
            float(data.get("interest_rate_pct") or 0.0), float(data.get("monthly_payment_idr") or 0.0),
            int(data.get("remaining_term_months") or 0), data.get("notes", ""), data.get("id"), user_id
        ))
    else:
        cursor.execute("""
        INSERT INTO liabilities (user_id, name, type, balance_idr, interest_rate_pct, monthly_payment_idr, remaining_term_months, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, data.get("name"), data.get("type", "MORTGAGE"), float(data.get("balance_idr") or 0.0),
            float(data.get("interest_rate_pct") or 0.0), float(data.get("monthly_payment_idr") or 0.0),
            int(data.get("remaining_term_months") or 0), data.get("notes", "")
        ))
    conn.commit()
    conn.close()


def delete_liability(user_id: str, item_id: int):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM liabilities WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()


# Investment Theses Management
def get_user_theses(user_id: str = "default_user") -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM investment_theses WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_thesis(user_id: str, data: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if data.get("id"):
        cursor.execute("""
        UPDATE investment_theses SET
            ticker = ?, thesis = ?, catalysts = ?, risks = ?, invalidation = ?, status = ?, review_date = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """, (
            data.get("ticker"), data.get("thesis"), data.get("catalysts"), data.get("risks"),
            data.get("invalidation"), data.get("status", "INTACT"), data.get("review_date"),
            data.get("id"), user_id
        ))
    else:
        cursor.execute("""
        INSERT INTO investment_theses (user_id, ticker, thesis, catalysts, risks, invalidation, status, review_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, data.get("ticker"), data.get("thesis"), data.get("catalysts"),
            data.get("risks"), data.get("invalidation"), data.get("status", "INTACT"), data.get("review_date")
        ))
    conn.commit()
    conn.close()


def delete_thesis(user_id: str, thesis_id: int):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM investment_theses WHERE id = ? AND user_id = ?", (thesis_id, user_id))
    conn.commit()
    conn.close()


# Tax Rules
def get_tax_rules() -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tax_rules ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
