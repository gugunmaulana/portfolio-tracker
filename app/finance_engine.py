import time
import datetime
from dateutil.relativedelta import relativedelta
import math
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("finance_engine")
logger.setLevel(logging.INFO)

# Robust HTTP Session with desktop browser headers to prevent 401 Invalid Crumb
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
})

# In-memory cache for market data with ultra-fast TTL for live stream
MARKET_CACHE: Dict[str, Any] = {}
CACHE_TTL_SECONDS = 15

# Persistent long-term cache for heavy multi-year historical data & yearly returns (1-day TTL)
# This avoids re-downloading 15 years of charts when user simply adds capital or edits P/E ratio
HISTORICAL_PNL_CACHE: Dict[str, Dict[str, Any]] = {}
HISTORICAL_CACHE_TTL = 86400

# Vetted high-resolution asset logo repository
ASSET_LOGOS = {
    # Cryptocurrencies & Commodities
    "BTC-USD": "https://assets.coingecko.com/coins/images/1/small/bitcoin.png",
    "BTC": "https://assets.coingecko.com/coins/images/1/small/bitcoin.png",
    "ETH-USD": "https://assets.coingecko.com/coins/images/279/small/ethereum.png",
    "ETH": "https://assets.coingecko.com/coins/images/279/small/ethereum.png",
    "SOL-USD": "https://assets.coingecko.com/coins/images/4128/small/solana.png",
    "SOL": "https://assets.coingecko.com/coins/images/4128/small/solana.png",
    "GC=F": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/paxg.png", # Gold bullion
    "XAUUSD": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/paxg.png",
    # ETFs & Major Indices
    "VOO": "https://assets.parqet.com/logos/symbol/VOO?format=png",
    "QQQ": "https://assets.parqet.com/logos/symbol/QQQ?format=png",
    "SMH": "https://assets.parqet.com/logos/symbol/SMH?format=png",
    "^GSPC": "https://assets.parqet.com/logos/symbol/SPY?format=png",
    "^JKSE": "https://assets.parqet.com/logos/symbol/EIDO?format=png",
    # US & Global Equities
    "NVDA": "https://assets.parqet.com/logos/symbol/NVDA?format=png",
    "MSFT": "https://assets.parqet.com/logos/symbol/MSFT?format=png",
    "AAPL": "https://assets.parqet.com/logos/symbol/AAPL?format=png",
    "GOOGL": "https://assets.parqet.com/logos/symbol/GOOGL?format=png",
    "AMZN": "https://assets.parqet.com/logos/symbol/AMZN?format=png",
    "META": "https://assets.parqet.com/logos/symbol/META?format=png",
    "BRK-B": "https://assets.parqet.com/logos/symbol/BRK-B?format=png",
    "TSM": "https://assets.parqet.com/logos/symbol/TSM?format=png",
    "ASML": "https://assets.parqet.com/logos/symbol/ASML?format=png",
    "AVGO": "https://assets.parqet.com/logos/symbol/AVGO?format=png",
    "COST": "https://assets.parqet.com/logos/symbol/COST?format=png",
    "JPM": "https://assets.parqet.com/logos/symbol/JPM?format=png",
    "V": "https://assets.parqet.com/logos/symbol/V?format=png",
    "LLY": "https://assets.parqet.com/logos/symbol/LLY?format=png",
    "PLTR": "https://assets.parqet.com/logos/symbol/PLTR?format=png",
    "MSTR": "https://assets.parqet.com/logos/symbol/MSTR?format=png",
    "KLAC": "https://assets.parqet.com/logos/symbol/KLAC?format=png",
    "AMAT": "https://assets.parqet.com/logos/symbol/AMAT?format=png",
    "LRCX": "https://assets.parqet.com/logos/symbol/LRCX?format=png",
    "ETN": "https://assets.parqet.com/logos/symbol/ETN?format=png",
    "RTX": "https://assets.parqet.com/logos/symbol/RTX?format=png",
    "SNPS": "https://assets.parqet.com/logos/symbol/SNPS?format=png",
    "CEG": "https://assets.parqet.com/logos/symbol/CEG?format=png",
    "PWR": "https://assets.parqet.com/logos/symbol/PWR?format=png",
    "CCJ": "https://assets.parqet.com/logos/symbol/CCJ?format=png",
    "VRT": "https://assets.parqet.com/logos/symbol/VRT?format=png",
    "CRWD": "https://assets.parqet.com/logos/symbol/CRWD?format=png",
    "SPGI": "https://assets.parqet.com/logos/symbol/SPGI?format=png",
    "ISRG": "https://assets.parqet.com/logos/symbol/ISRG?format=png",
    "TMO": "https://assets.parqet.com/logos/symbol/TMO?format=png",
    "PANW": "https://assets.parqet.com/logos/symbol/PANW?format=png",
    "NET": "https://assets.parqet.com/logos/symbol/NET?format=png",
    "MCO": "https://assets.parqet.com/logos/symbol/MCO?format=png",
    "RACE": "https://assets.parqet.com/logos/symbol/RACE?format=png",
    "LVMUY": "https://assets.parqet.com/logos/symbol/LVMUY?format=png",
    "FCX": "https://assets.parqet.com/logos/symbol/FCX?format=png",
    "NVO": "https://assets.parqet.com/logos/symbol/NVO?format=png",
    "UNP": "https://assets.parqet.com/logos/symbol/UNP?format=png",
    "WM": "https://assets.parqet.com/logos/symbol/WM?format=png",
    # Indonesian Stocks
    "BBCA.JK": "https://assets.parqet.com/logos/symbol/BBCA.JK?format=png",
    "BBRI.JK": "https://assets.parqet.com/logos/symbol/BBRI.JK?format=png",
    "BMRI.JK": "https://assets.parqet.com/logos/symbol/BMRI.JK?format=png",
    "BBNI.JK": "https://assets.parqet.com/logos/symbol/BBNI.JK?format=png",
    "UNTR.JK": "https://assets.parqet.com/logos/symbol/UNTR.JK?format=png",
    "BREN.JK": "https://assets.parqet.com/logos/symbol/BREN.JK?format=png",
    "AMMN.JK": "https://assets.parqet.com/logos/symbol/AMMN.JK?format=png",
    "TLKM.JK": "https://assets.parqet.com/logos/symbol/TLKM.JK?format=png",
    "ASII.JK": "https://assets.parqet.com/logos/symbol/ASII.JK?format=png",
}


def get_asset_logo_url(ticker: str) -> str:
    clean = ticker.strip().upper()
    if clean in ASSET_LOGOS:
        return ASSET_LOGOS[clean]
    if "-USD" in clean:
        coin = clean.split("-")[0].lower()
        return f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/{coin}.png"
    return f"https://assets.parqet.com/logos/symbol/{clean}?format=png"


FALLBACK_PRICES = {
    "USDIDR=X": 17688.0,
    "CNYIDR=X": 2632.0,
    "^JKSE": 6499.07,
    "^GSPC": 5924.37,
    "VOO": 703.71,
    "QQQ": 491.15,
    "SMH": 248.50,
    "BTC-USD": 77482.0,
    "GC=F": 2930.50,
    "BRK-B": 495.82,
    "COST": 971.84,
    "JPM": 247.38,
    "V": 315.60,
    "MSFT": 412.30,
    "AAPL": 228.45,
    "META": 654.80,
    "AMZN": 218.60,
    "GOOGL": 184.25,
    "AVGO": 218.40,
    "TSM": 194.50,
    "NVDA": 214.72,
    "ASML": 715.40,
    "LLY": 845.20,
    "BBCA.JK": 6375.0,
    "BBRI.JK": 4450.0,
    "BMRI.JK": 6800.0,
    "BBNI.JK": 5300.0,
    "UNTR.JK": 26800.0,
    "BREN.JK": 6250.0,
    "TLKM.JK": 2850.0,
    "ASII.JK": 4950.0,
    "ETH-USD": 2750.0,
    "MSTR": 345.50,
    "KLAC": 710.0,
    "AMAT": 195.0,
    "LRCX": 78.50,
    "ETN": 355.0,
    "RTX": 125.0,
    "SNPS": 515.0,
    "CEG": 285.0,
    "PWR": 295.0,
    "CCJ": 58.0,
    "VRT": 115.0,
    "CRWD": 310.40,
    "SPGI": 542.07,
    "ISRG": 492.60,
    "PLTR": 36.29,
    "TMO": 582.18,
    "PANW": 365.0,
    "NET": 85.0,
    "MCO": 460.0,
    "RACE": 420.0,
    "LVMUY": 155.0,
    "FCX": 45.0,
    "NVO": 130.0,
    "UNP": 245.0,
    "WM": 210.0
}

FALLBACK_PE_RATIOS = {
    "VOO": 26.5,
    "QQQ": 32.1,
    "SMH": 34.0,
    "BRK-B": 15.0,
    "COST": 45.67,
    "JPM": 12.06,
    "V": 31.57,
    "MSFT": 31.57,
    "AAPL": 35.84,
    "META": 28.71,
    "AMZN": 38.80,
    "GOOGL": 20.82,
    "AVGO": 61.34,
    "TSM": 30.52,
    "NVDA": 42.88,
    "ASML": 54.83,
    "LLY": 42.13,
    "BBCA.JK": 21.5,
    "BBRI.JK": 11.27,
    "BMRI.JK": 10.8,
    "BBNI.JK": 8.5,
    "UNTR.JK": 5.4,
    "BREN.JK": 169.6,
    "TLKM.JK": 14.2,
    "ASII.JK": 6.8,
    "KLAC": 50.26,
    "AMAT": 42.46,
    "LRCX": 42.66,
    "ETN": 42.66,
    "RTX": 39.5,
    "SNPS": 92.21,
    "CEG": 26.59,
    "PWR": 73.23,
    "CCJ": 117.29,
    "VRT": 59.28,
    "CRWD": 80.50,
    "SPGI": 38.40,
    "ISRG": 78.20,
    "PLTR": 115.0,
    "TMO": 34.80,
    "PANW": 55.40,
    "NET": 72.0,
    "MCO": 42.10,
    "RACE": 48.50,
    "LVMUY": 24.50,
    "FCX": 18.20,
    "NVO": 38.50,
    "UNP": 21.80,
    "WM": 32.40
}

SHARES_OUTSTANDING = {
    "NVDA": 24.5e9,
    "AAPL": 15.2e9,
    "MSFT": 7.44e9,
    "AMZN": 10.5e9,
    "GOOGL": 12.3e9,
    "META": 2.54e9,
    "BRK-B": 2.18e9,
    "TSM": 5.18e9,
    "AVGO": 4.70e9,
    "COST": 4.43e8,
    "JPM": 2.84e9,
    "V": 1.99e9,
    "ASML": 3.91e8,
    "LLY": 9.48e8,
    "KLAC": 1.34e8,
    "AMAT": 8.16e8,
    "LRCX": 1.29e8,
    "ETN": 3.96e8,
    "RTX": 1.33e9,
    "SNPS": 1.54e8,
    "CEG": 3.14e8,
    "PWR": 1.51e8,
    "CCJ": 4.36e8,
    "VRT": 3.78e8,
    "CRWD": 2.44e8,
    "SPGI": 3.12e8,
    "ISRG": 3.56e8,
    "PLTR": 2.26e9,
    "TMO": 3.82e8,
    "PANW": 3.25e8,
    "NET": 3.38e8,
    "MCO": 1.83e8,
    "RACE": 1.81e8,
    "LVMUY": 5.0e8,
    "FCX": 1.44e9,
    "NVO": 4.47e9,
    "UNP": 6.08e8,
    "WM": 4.02e8,
    "MSTR": 2.45e8,
    "BBCA.JK": 123.28e9,
    "BBRI.JK": 151.56e9,
    "BMRI.JK": 93.33e9,
    "BBNI.JK": 37.3e9,
    "UNTR.JK": 3.73e9,
    "BREN.JK": 133.79e9,
    "TLKM.JK": 99.06e9,
    "ASII.JK": 40.48e9,
    "BTC-USD": 19.8e6,
    "ETH-USD": 120.4e6,
    "VOO": 8.2e8,
    "QQQ": 4.4e8,
    "SMH": 5.2e7
}


def format_mcap_str(val: Optional[float], curr: str = "USD") -> str:
    """Format market cap into concise human-readable representation."""
    if not val or val <= 0:
        return "N/A"
    if curr == "IDR":
        if val >= 1e12:
            return f"Rp {val/1e12:.1f}T"
        elif val >= 1e9:
            return f"Rp {val/1e9:.1f}M"
        return f"Rp {val:,.0f}"
    else:
        if val >= 1e12:
            return f"${val/1e12:.2f}T"
        elif val >= 1e9:
            return f"${val/1e9:.1f}B"
        elif val >= 1e6:
            return f"${val/1e6:.1f}M"
        return f"${val:,.0f}"


def format_volume_str(val: Optional[int]) -> str:
    """Format trading volume into concise human-readable representation."""
    if not val or val <= 0:
        return "N/A"
    if val >= 1e9:
        return f"{val/1e9:.2f}B"
    elif val >= 1e6:
        return f"{val/1e6:.2f}M"
    elif val >= 1e3:
        return f"{val/1e3:.1f}K"
    return f"{val:,}"


def fetch_direct_yahoo_chart(ticker: str, range_str: str = "10y", interval: str = "1d") -> Optional[Dict[str, Any]]:
    """Directly fetch chart data from Yahoo Finance API with robust browser headers."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={interval}&range={range_str}"
    try:
        r = session.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
                return data["chart"]["result"][0]
    except Exception as e:
        logger.debug(f"Direct yahoo fetch error for {ticker}: {e}")
    return None


def fetch_direct_yahoo_quote(ticker: str) -> Optional[Dict[str, Any]]:
    """Directly fetch live quote metrics (trailingPE, forwardPE, marketCap, eps, volume) from Yahoo Finance API."""
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
    try:
        r = session.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if "quoteResponse" in data and "result" in data["quoteResponse"] and data["quoteResponse"]["result"]:
                return data["quoteResponse"]["result"][0]
    except Exception as e:
        logger.debug(f"Direct yahoo quote fetch error for {ticker}: {e}")
    return None


def get_macro_and_fx() -> Dict[str, Any]:
    """Fetch live USD/IDR, CNY/IDR, IHSG, S&P500 and their complete multi-period returns (24h, 1w, 1m, 6m, 1y, 5y)."""
    tickers = ["USDIDR=X", "CNYIDR=X", "^JKSE", "^GSPC"]
    raw_data = {}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_ticker_market_data, t): t for t in tickers}
        for future in as_completed(futures):
            t = futures[future]
            try:
                raw_data[t] = future.result()
            except Exception as e:
                logger.debug(f"Error fetching macro {t}: {e}")
                raw_data[t] = {}

    usd_data = raw_data.get("USDIDR=X", {})
    cny_data = raw_data.get("CNYIDR=X", {})
    ihsg_data = raw_data.get("^JKSE", {})
    sp500_data = raw_data.get("^GSPC", {})

    # Robust fallback sanity
    usd_price = usd_data.get("price") or 17688.0
    cny_price = cny_data.get("price") or 2632.0
    ihsg_price = ihsg_data.get("price") or 6518.12
    sp500_price = sp500_data.get("price") or 7711.76

    usd_perf = usd_data.get("perf") or {"24h": -0.36, "1w": 0.17, "1m": -2.18, "6m": 5.59, "1y": 8.20, "5y": 22.72}
    cny_perf = cny_data.get("perf") or {"24h": 0.0, "1w": 0.12, "1m": -1.85, "6m": 4.80, "1y": 7.65, "5y": 18.40}
    ihsg_perf = ihsg_data.get("perf") or {"24h": 1.76, "1w": 1.94, "1m": 5.37, "6m": -20.85, "1y": -17.87, "5y": 7.89}
    sp500_perf = sp500_data.get("perf") or {"24h": 0.47, "1w": 0.92, "1m": 4.03, "6m": 11.62, "1y": 18.98, "5y": 71.02}

    return {
        "usd_idr": usd_price,
        "usd_idr_chg": usd_perf.get("24h", 0.0),
        "usd_idr_perf": usd_perf,
        "cny_idr": cny_price,
        "cny_idr_chg": cny_perf.get("24h", 0.0),
        "cny_idr_perf": cny_perf,
        "ihsg": ihsg_price,
        "ihsg_chg": ihsg_perf.get("24h", 0.0),
        "ihsg_perf": ihsg_perf,
        "sp500": sp500_price,
        "sp500_chg": sp500_perf.get("24h", 0.0),
        "sp500_perf": sp500_perf,
        "benchmarks": {
            "usdidr": {
                "name": "USD / IDR",
                "symbol": "USDIDR=X",
                "tradingview_url": "https://www.tradingview.com/symbols/USDIDR/",
                "price": usd_price,
                "perf": usd_perf
            },
            "cnyidr": {
                "name": "CNY / IDR",
                "symbol": "CNYIDR=X",
                "tradingview_url": "https://www.tradingview.com/symbols/CNYIDR/",
                "price": cny_price,
                "perf": cny_perf
            },
            "ihsg": {
                "name": "IHSG (IDX COMPOSITE)",
                "symbol": "^JKSE",
                "tradingview_url": "https://www.tradingview.com/symbols/IDX-COMPOSITE/",
                "price": ihsg_price,
                "perf": ihsg_perf
            },
            "sp500": {
                "name": "S&P 500 (INDEXSP:.INX)",
                "symbol": "^GSPC",
                "tradingview_url": "https://www.tradingview.com/symbols/SPX/",
                "price": sp500_price,
                "perf": sp500_perf
            }
        }
    }


def calculate_yearly_returns(chart_max: Optional[Dict[str, Any]], ticker_symbol: str, cur_price: float) -> Dict[str, Optional[float]]:
    """
    Extract calendar yearly returns (% profit from year to year) for 2011 through current year.
    Returns a dictionary mapping string years "2011", "2012", ..., "2026" to float percentage or None.
    """
    cur_year = datetime.datetime.now().year
    yearly: Dict[str, Optional[float]] = {str(y): None for y in range(2011, cur_year + 1)}
    
    # Pre-Yahoo / historical curated baseline for revolutionary early assets
    t_clean = (ticker_symbol or "").upper()
    if "BTC" in t_clean:
        yearly["2011"] = 1460.0
        yearly["2012"] = 186.0
        yearly["2013"] = 5500.0
    elif "ETH" in t_clean:
        yearly["2016"] = 9384.15

    if not chart_max:
        return yearly

    timestamps = chart_max.get("timestamp", [])
    quotes = chart_max.get("indicators", {}).get("quote", [{}])[0]
    closes = quotes.get("close", [])
    
    if not timestamps or not closes:
        return yearly

    year_closes: Dict[int, List[float]] = {}
    for ts, c in zip(timestamps, closes):
        if c is not None and not math.isnan(c) and c > 0:
            try:
                dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
                year_closes.setdefault(dt.year, []).append(c)
            except Exception:
                pass

    for y in range(2011, cur_year + 1):
        y_str = str(y)
        if y in year_closes and year_closes[y]:
            if (y - 1) in year_closes and year_closes[y - 1]:
                prev_c = year_closes[y - 1][-1]
                cur_c = year_closes[y][-1] if (y != cur_year or len(year_closes[y]) > 0) else cur_price
                if prev_c > 0 and cur_c > 0:
                    ret = ((cur_c - prev_c) / prev_c) * 100.0
                    yearly[y_str] = round(ret, 2)
            elif yearly.get(y_str) is None:
                # First recorded listing year for this asset
                first_c = year_closes[y][0]
                cur_c = year_closes[y][-1] if y != cur_year else cur_price
                if first_c > 0 and cur_c > 0:
                    ret = ((cur_c - first_c) / first_c) * 100.0
                    yearly[y_str] = round(ret, 2)

    return yearly


def fetch_ticker_market_data(ticker_symbol: str) -> Dict[str, Any]:
    """Fetch realtime quote, ATH, PE ratio, high-precision multi-period performance (24h to 20y), and yearly returns (2011-now)."""
    cached = MARKET_CACHE.get(ticker_symbol)
    now = time.time()
    if cached and (now - cached.get("_timestamp", 0) < CACHE_TTL_SECONDS):
        return cached

    # If long-term historical PnL & yearly returns are already cached, reuse them instantly!
    # This ensures adding capital or editing PE/quantity takes < 10ms with zero heavy network downloads.
    hist = HISTORICAL_PNL_CACHE.get(ticker_symbol)
    if hist and (now - hist.get("_cached_at", 0) < HISTORICAL_CACHE_TTL):
        quick_chart = fetch_direct_yahoo_chart(ticker_symbol, "5d", "1d")
        quick_price = None
        chg_24h = 0.0
        if quick_chart:
            q_meta = quick_chart.get("meta", {})
            q_quotes = quick_chart.get("indicators", {}).get("quote", [{}])[0]
            q_closes = [c for c in q_quotes.get("close", []) if c is not None and not math.isnan(c) and c > 0]
            quick_price = q_meta.get("regularMarketPrice") or (q_closes[-1] if q_closes else None)
            prev_c = q_meta.get("regularMarketPreviousClose") or (q_closes[-2] if len(q_closes) >= 2 else None)
            if quick_price and prev_c and prev_c > 0:
                chg_24h = round(((quick_price - prev_c) / prev_c) * 100.0, 2)

        cur_price = quick_price or hist.get("price", 100.0)
        result = dict(hist)
        result["price"] = cur_price
        result["perf"] = dict(hist.get("perf", {}))
        result["perf"]["24h"] = chg_24h
        
        # Ensure PE is present if available in fallback or quote
        is_crypto_or_commodity = "-USD" in ticker_symbol or ticker_symbol in ["BTC-USD", "ETH-USD", "SOL-USD", "GC=F"] or ticker_symbol.startswith("^")
        if not is_crypto_or_commodity and result.get("pe") is None:
            result["pe"] = FALLBACK_PE_RATIOS.get(ticker_symbol)
            if result["pe"] is None:
                prof_tmp = detect_volatility_profile(ticker_symbol)
                if prof_tmp.get("default_pe") and prof_tmp["default_pe"].get("good"):
                    result["pe"] = float(prof_tmp["default_pe"]["good"])

        dec2025_c = hist.get("_dec2025_close")
        if dec2025_c and dec2025_c > 0:
            result["yearly_returns"] = dict(hist.get("yearly_returns", {}))
            result["yearly_returns"]["2026"] = round(((cur_price - dec2025_c) / dec2025_c) * 100.0, 2)
            
        result["_timestamp"] = now
        MARKET_CACHE[ticker_symbol] = result
        return result

    result = {
        "ticker": ticker_symbol,
        "price": FALLBACK_PRICES.get(ticker_symbol, 100.0),
        "ath": FALLBACK_PRICES.get(ticker_symbol, 100.0) * 1.15,
        "pe": FALLBACK_PE_RATIOS.get(ticker_symbol, None),
        "perf": {
            "24h": 0.0,
            "5h": 0.0,
            "1w": 0.0,
            "1m": 0.0,
            "6m": 0.0,
            "1y": 0.0,
            "5y": None,
            "10y": None,
            "15y": None,
            "20y": None,
            "5y_cagr": None,
            "10y_cagr": None,
            "15y_cagr": None,
            "20y_cagr": None
        },
        "yearly_returns": {str(y): None for y in range(2011, datetime.datetime.now().year + 1)},
        "_timestamp": now
    }

    try:
        # Tier 1: High-precision daily bars for up to 10 years
        if ticker_symbol == "CNYIDR=X":
            usd_chart = fetch_direct_yahoo_chart("USDIDR=X", "10y", "1d")
            cny_chart = fetch_direct_yahoo_chart("CNY=X", "10y", "1d")
            chart_daily = None
            if usd_chart and cny_chart:
                u_ts = usd_chart.get("timestamp", [])
                u_quotes = usd_chart.get("indicators", {}).get("quote", [{}])[0]
                u_closes = u_quotes.get("close", [])
                
                c_ts = cny_chart.get("timestamp", [])
                c_quotes = cny_chart.get("indicators", {}).get("quote", [{}])[0]
                c_closes = c_quotes.get("close", [])
                
                c_dict = {}
                for t, cl in zip(c_ts, c_closes):
                    if cl and cl > 0:
                        dt_str = datetime.datetime.fromtimestamp(t, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
                        c_dict[dt_str] = cl
                        
                syn_ts, syn_closes = [], []
                for t, u_cl in zip(u_ts, u_closes):
                    if u_cl and u_cl > 0:
                        dt_str = datetime.datetime.fromtimestamp(t, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
                        c_cl = c_dict.get(dt_str)
                        if c_cl and c_cl > 0:
                            syn_val = round(u_cl / c_cl, 2)
                            syn_ts.append(t)
                            syn_closes.append(syn_val)
                            
                chart_daily = {
                    "timestamp": syn_ts,
                    "indicators": {
                        "quote": [{
                            "close": syn_closes,
                            "high": syn_closes,
                            "low": syn_closes,
                            "open": syn_closes
                        }]
                    },
                    "meta": {
                        "regularMarketPrice": syn_closes[-1] if syn_closes else 2632.0,
                        "regularMarketPreviousClose": syn_closes[-2] if len(syn_closes) >= 2 else 2632.0
                    }
                }
        else:
            chart_daily = fetch_direct_yahoo_chart(ticker_symbol, "10y", "1d")
        
        # Tier 2: Monthly max bars for >10y history (15y, 20y) and true lifetime ATH
        if ticker_symbol == "CNYIDR=X":
            chart_max = chart_daily
        else:
            chart_max = fetch_direct_yahoo_chart(ticker_symbol, "max", "1mo")
        
        daily_pts = []
        highs_daily = []
        meta = {}
        if chart_daily:
            meta = chart_daily.get("meta", {})
            ts_d = chart_daily.get("timestamp", [])
            q_d = chart_daily.get("indicators", {}).get("quote", [{}])[0]
            raw_c_d = q_d.get("close", [])
            raw_o_d = q_d.get("open", [])
            highs_daily = [h for h in q_d.get("high", []) if h is not None and not math.isnan(h) and h > 0]
            for t, o, c in zip(ts_d, raw_o_d, raw_c_d):
                if c is not None and not math.isnan(c) and c > 0:
                    dt = datetime.datetime.fromtimestamp(t, datetime.timezone.utc)
                    daily_pts.append({
                        "dt": dt,
                        "ts": t,
                        "open": o if (o is not None and not math.isnan(o) and o > 0) else c,
                        "close": c
                    })

        max_pts = []
        highs_max = []
        if chart_max:
            ts_m = chart_max.get("timestamp", [])
            q_m = chart_max.get("indicators", {}).get("quote", [{}])[0]
            raw_c_m = q_m.get("close", [])
            raw_o_m = q_m.get("open", [])
            highs_max = [h for h in q_m.get("high", []) if h is not None and not math.isnan(h) and h > 0]
            for t, o, c in zip(ts_m, raw_o_m, raw_c_m):
                if c is not None and not math.isnan(c) and c > 0:
                    dt = datetime.datetime.fromtimestamp(t, datetime.timezone.utc)
                    max_pts.append({
                        "dt": dt,
                        "ts": t,
                        "open": o if (o is not None and not math.isnan(o) and o > 0) else c,
                        "close": c
                    })

        # Determine true realtime market price
        price = meta.get("regularMarketPrice")
        if (not price or math.isnan(price)) and daily_pts:
            price = daily_pts[-1]["close"]
        elif (not price or math.isnan(price)) and max_pts:
            price = max_pts[-1]["close"]
            
        if price and not math.isnan(price):
            result["price"] = round(price, 2)

        cur_price = result["price"]

        # Determine Rolling 2-Year Daily Close ATH (Pilihan 1: Daily Close High dalam 2 Tahun Terakhir)
        # Menghindari false intraday wick spikes dan bubble anomali masa lalu
        cur_dt = daily_pts[-1]["dt"] if daily_pts else datetime.datetime.now(datetime.timezone.utc)
        two_years_ago_dt = cur_dt - datetime.timedelta(days=730)
        
        # Ambil seluruh harga penutupan harian (Daily Close) dalam rentang 2 tahun terakhir
        closes_2y = [
            p["close"] for p in daily_pts 
            if p["dt"] >= two_years_ago_dt and p["close"] is not None and not math.isnan(p["close"]) and p["close"] > 0
        ]
        
        if closes_2y:
            high_point = max(closes_2y)
        elif daily_pts:
            high_point = max([p["close"] for p in daily_pts if p["close"] is not None and not math.isnan(p["close"]) and p["close"] > 0])
        else:
            ath_meta = meta.get("fiftyTwoWeekHigh") or (cur_price * 1.1)
            high_point = ath_meta

        result["ath"] = round(max(high_point, cur_price), 2)

        # Calculate high-precision performance returns
        if daily_pts:
            cur_dt = daily_pts[-1]["dt"]
            cur_ts = daily_pts[-1]["ts"]
            
            # 24H (1 trading day return vs previous close)
            prev_close = meta.get("regularMarketPreviousClose") or meta.get("previousClose")
            if not prev_close and len(daily_pts) >= 2:
                prev_close = daily_pts[-2]["close"]
            if prev_close and prev_close > 0:
                result["perf"]["24h"] = round(((cur_price - prev_close) / prev_close) * 100.0, 2)

            def get_window_return(delta) -> Optional[float]:
                target_dt = cur_dt - delta
                earliest_dt = max_pts[0]["dt"] if max_pts else (daily_pts[0]["dt"] if daily_pts else None)
                if earliest_dt and (target_dt < (earliest_dt - relativedelta(days=45))):
                    return None
                    
                # 1. TradingView & Bloomberg standard: Close price on or before target date
                before_cands = [b for b in daily_pts if b["dt"] <= target_dt]
                if before_cands:
                    base_price = before_cands[-1]["close"]
                    if base_price > 0:
                        return round(((cur_price - base_price) / base_price) * 100.0, 2)

                # 2. Start candle on or after target_dt (if target_dt is near the very beginning of the series)
                cands = [b for b in daily_pts if b["dt"] >= target_dt]
                if cands and cands[0]["ts"] != cur_ts:
                    base_price = cands[0]["close"] or cands[0]["open"]
                    if base_price > 0:
                        return round(((cur_price - base_price) / base_price) * 100.0, 2)
                        
                # 3. Monthly max series for >10y timeframes
                if max_pts:
                    m_before = [b for b in max_pts if b["dt"] <= target_dt]
                    if m_before:
                        base_price = m_before[-1]["close"]
                        if base_price > 0:
                            return round(((cur_price - base_price) / base_price) * 100.0, 2)
                    m_cands = [b for b in max_pts if b["dt"] >= target_dt]
                    if m_cands:
                        base_price = m_cands[0]["close"] or m_cands[0]["open"]
                        if base_price > 0:
                            return round(((cur_price - base_price) / base_price) * 100.0, 2)
                            
                return None

            def get_cagr_pct(p_ret: Optional[float], years: float) -> Optional[float]:
                if p_ret is None:
                    return None
                growth_factor = 1.0 + (p_ret / 100.0)
                if growth_factor <= 0:
                    return None
                return round(((growth_factor ** (1.0 / years)) - 1.0) * 100.0, 2)

            # Accurate 5H / 1W Return (1 full trading week: 5 trading sessions for equities, 7 daily bars for crypto)
            is_crypto = "-USD" in ticker_symbol or ticker_symbol in ["BTC-USD", "ETH-USD", "SOL-USD"]
            n_bars = 7 if is_crypto else 5
            if len(daily_pts) > n_bars:
                base_5h = daily_pts[-1 - n_bars]["close"]
                if base_5h > 0:
                    result["perf"]["5h"] = round(((cur_price - base_5h) / base_5h) * 100.0, 2)
            else:
                target_5h_dt = cur_dt - datetime.timedelta(days=7)
                cands_5h = [b for b in daily_pts if b["dt"] <= target_5h_dt]
                if cands_5h:
                    base_5h = cands_5h[-1]["close"]
                    if base_5h > 0:
                        result["perf"]["5h"] = round(((cur_price - base_5h) / base_5h) * 100.0, 2)
                else:
                    result["perf"]["5h"] = get_window_return(datetime.timedelta(days=7))
                
            result["perf"]["1w"] = result["perf"]["5h"]
            result["perf"]["1m"] = get_window_return(relativedelta(months=1))
            result["perf"]["6m"] = get_window_return(relativedelta(months=6))
            result["perf"]["1y"] = get_window_return(relativedelta(years=1))
            
            # Cumulative Total Profit %
            result["perf"]["5y"] = get_window_return(relativedelta(years=5))
            result["perf"]["10y"] = get_window_return(relativedelta(years=10))
            result["perf"]["15y"] = get_window_return(relativedelta(years=15))
            result["perf"]["20y"] = get_window_return(relativedelta(years=20))

            # Annualized Compound Growth Rate (CAGR %)
            result["perf"]["5y_cagr"] = get_cagr_pct(result["perf"]["5y"], 5.0)
            result["perf"]["10y_cagr"] = get_cagr_pct(result["perf"]["10y"], 10.0)
            result["perf"]["15y_cagr"] = get_cagr_pct(result["perf"]["15y"], 15.0)
            result["perf"]["20y_cagr"] = get_cagr_pct(result["perf"]["20y"], 20.0)

            # Inception / Lifetime CAGR Calculation (from asset's earliest release/issuance data)
            earliest_pt = max_pts[0] if max_pts else (daily_pts[0] if daily_pts else None)
            inception_cagr = None
            inception_years = None
            inception_date_str = None
            inception_return = None
            if earliest_pt and daily_pts:
                earliest_dt = earliest_pt["dt"]
                cur_dt = daily_pts[-1]["dt"]
                years_diff = (cur_dt - earliest_dt).total_seconds() / (365.25 * 86400)
                base_price = earliest_pt["open"] or earliest_pt["close"]
                if years_diff >= 0.1 and base_price and base_price > 0 and cur_price > 0:
                    inception_return = round(((cur_price - base_price) / base_price) * 100.0, 2)
                    growth_f = 1.0 + (inception_return / 100.0)
                    if growth_f > 0:
                        inception_cagr = round(((growth_f ** (1.0 / years_diff)) - 1.0) * 100.0, 2)
                        inception_years = round(years_diff, 1)
                        inception_date_str = earliest_dt.strftime("%Y-%m-%d")

            result["perf"]["inception_cagr"] = inception_cagr
            result["perf"]["inception_years"] = inception_years
            result["perf"]["inception_date"] = inception_date_str
            result["perf"]["inception_return"] = inception_return

            # Requirement 4: If 15y or 20y CAGR is None (asset history < 15y/20y), pull CAGR from inception
            if result["perf"]["15y_cagr"] is None and inception_cagr is not None:
                result["perf"]["15y_cagr"] = inception_cagr
                result["perf"]["15y_cagr_is_inception"] = True
            else:
                result["perf"]["15y_cagr_is_inception"] = False

            if result["perf"]["20y_cagr"] is None and inception_cagr is not None:
                result["perf"]["20y_cagr"] = inception_cagr
                result["perf"]["20y_cagr_is_inception"] = True
            else:
                result["perf"]["20y_cagr_is_inception"] = False

            if result["perf"]["15y"] is None and inception_return is not None:
                result["perf"]["15y"] = inception_return

            if result["perf"]["20y"] is None and inception_return is not None:
                result["perf"]["20y"] = inception_return

            # Volume
            vol = meta.get("regularMarketVolume")
            if not vol and chart_daily:
                vol_list = chart_daily.get("indicators", {}).get("quote", [{}])[0].get("volume", [])
                valid_vols = [v for v in vol_list if v is not None and not math.isnan(v) and v > 0]
                if valid_vols:
                    vol = valid_vols[-1]
            result["volume"] = int(vol) if vol else 0

            # Market Cap
            shares = SHARES_OUTSTANDING.get(ticker_symbol)
            if shares:
                result["market_cap"] = round(cur_price * shares, 2)
            else:
                result["market_cap"] = meta.get("marketCap", None)

            # Live Quote metrics for PE, Forward PE, and Market Statistics
            is_crypto_or_commodity = "-USD" in ticker_symbol or ticker_symbol in ["BTC-USD", "ETH-USD", "SOL-USD", "GC=F"] or ticker_symbol.startswith("^")
            if not is_crypto_or_commodity:
                try:
                    q_data = fetch_direct_yahoo_quote(ticker_symbol)
                    if q_data:
                        live_pe = q_data.get("trailingPE") or q_data.get("forwardPE")
                        if not live_pe and q_data.get("epsTrailingTwelveMonths") and q_data["epsTrailingTwelveMonths"] > 0 and cur_price > 0:
                            live_pe = cur_price / q_data["epsTrailingTwelveMonths"]
                        if live_pe and not math.isnan(live_pe) and live_pe > 0:
                            result["pe"] = round(float(live_pe), 2)
                        
                        if not result.get("market_cap") and q_data.get("marketCap"):
                            result["market_cap"] = q_data["marketCap"]
                        if (not result.get("volume") or result["volume"] == 0) and q_data.get("regularMarketVolume"):
                            result["volume"] = int(q_data["regularMarketVolume"])
                except Exception as e:
                    logger.debug(f"Live quote fetch error for {ticker_symbol}: {e}")

            # Yearly Calendar Returns (2011 to Current Year)
            result["yearly_returns"] = calculate_yearly_returns(chart_max, ticker_symbol, cur_price)

    except Exception as e:
        logger.debug(f"Fetch error for {ticker_symbol}: {e}")

    # Fallback sanity
    if result["price"] <= 0:
        result["price"] = FALLBACK_PRICES.get(ticker_symbol, 100.0)
    if result["ath"] <= result["price"]:
        result["ath"] = round(result["price"] * 1.1, 2)

    is_crypto_or_commodity = "-USD" in ticker_symbol or ticker_symbol in ["BTC-USD", "ETH-USD", "SOL-USD", "GC=F"] or ticker_symbol.startswith("^")
    if not is_crypto_or_commodity:
        if result["pe"] is None:
            result["pe"] = FALLBACK_PE_RATIOS.get(ticker_symbol, None)
        if result["pe"] is None:
            prof_tmp = detect_volatility_profile(ticker_symbol)
            if prof_tmp.get("default_pe") and prof_tmp["default_pe"].get("good"):
                result["pe"] = float(prof_tmp["default_pe"]["good"])
    else:
        result["pe"] = None

    if result.get("market_cap") is None:
        shares = SHARES_OUTSTANDING.get(ticker_symbol)
        if shares:
            result["market_cap"] = round(result["price"] * shares, 2)
    if not result.get("yearly_returns") or all(v is None for v in result.get("yearly_returns", {}).values()):
        result["yearly_returns"] = calculate_yearly_returns(None, ticker_symbol, result["price"])

    prof = detect_volatility_profile(ticker_symbol)
    result["volatility_profile"] = prof["profile"]
    result["volatility_label"] = prof["label"]
    result["volatility_bg"] = prof["badge_bg"]
    result["smart_pe_thresholds"] = prof["default_pe"]

    # Store in persistent long-term historical cache
    hist_copy = dict(result)
    hist_copy["_cached_at"] = now
    HISTORICAL_PNL_CACHE[ticker_symbol] = hist_copy

    MARKET_CACHE[ticker_symbol] = result
    return result


def fetch_all_tickers_parallel(tickers: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch multiple tickers concurrently in parallel."""
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_ticker_market_data, t): t for t in set(tickers)}
        for future in futures:
            t = futures[future]
            try:
                results[t] = future.result()
            except Exception as e:
                logger.debug(f"Failed to fetch {t}: {e}")
                results[t] = {
                    "ticker": t,
                    "price": FALLBACK_PRICES.get(t, 100.0),
                    "ath": FALLBACK_PRICES.get(t, 100.0) * 1.1,
                    "pe": FALLBACK_PE_RATIOS.get(t, None),
                    "volume": 0,
                    "market_cap": None,
                    "perf": {"24h": 0.0, "5h": 0.0, "1w": 0.0, "1m": 0.0, "6m": 0.0, "1y": 0.0, "5y": None, "10y": None, "15y": None, "20y": None}
                }
    return results


def detect_volatility_profile(ticker: str) -> Dict[str, Any]:
    """Classify asset into Stabil, Moderat Growth, or Volatil Kripto and return adaptive thresholds & PE bounds."""
    t_upper = (ticker or "").upper()

    # 1. Crypto & Ultra-High Beta
    if "-USD" in t_upper or "BTC" in t_upper or "ETH" in t_upper or "SOL" in t_upper or t_upper in ["MSTR", "BREN.JK"]:
        return {
            "profile": "VOLATIL_CRYPTO",
            "label": "⚡ Volatil Kripto",
            "badge_bg": "bg-purple-500/15 text-purple-600 dark:text-purple-400 border-purple-500/30",
            "thresholds": {
                "z1": -25.0,
                "z2": -45.0,
                "z3": -65.0
            },
            "default_pe": None
        }

    # 2. Stable Broad Indices, Mega-cap Defensives, Commodities, Indo Big Banks
    if t_upper in ["VOO", "SPY", "IVV", "BRK-B", "COST", "JPM", "V", "PG", "GC=F", "UNP", "WM", "LVMUY"] or (t_upper.endswith(".JK") and any(t_upper.startswith(p) for p in ["BBCA", "BMRI", "BBNI", "UNTR", "TLKM", "ASII"])):
        if ".JK" in t_upper and ("BBCA" in t_upper or "BMRI" in t_upper or "BBNI" in t_upper):
            pe_bounds = {"great": 12.0, "good": 17.0, "expensive": 23.0}
        elif ".JK" in t_upper and ("UNTR" in t_upper or "ADRO" in t_upper or "PTBA" in t_upper):
            pe_bounds = {"great": 5.0, "good": 8.0, "expensive": 12.0}
        elif ".JK" in t_upper and ("TLKM" in t_upper or "ASII" in t_upper):
            pe_bounds = {"great": 10.0, "good": 15.0, "expensive": 20.0}
        elif t_upper == "GC=F":
            pe_bounds = None
        elif t_upper in ["COST"]:
            pe_bounds = {"great": 32.0, "good": 42.0, "expensive": 54.0}
        elif t_upper in ["JPM"]:
            pe_bounds = {"great": 10.0, "good": 12.5, "expensive": 16.0}
        elif t_upper in ["V"]:
            pe_bounds = {"great": 24.0, "good": 30.0, "expensive": 38.0}
        else: # VOO, BRK-B, UNP, WM, LVMUY
            pe_bounds = {"great": 18.0, "good": 24.0, "expensive": 32.0}

        return {
            "profile": "STABIL",
            "label": "🛡️ Stabil",
            "badge_bg": "bg-sky-500/15 text-sky-600 dark:text-sky-400 border-sky-500/30",
            "thresholds": {
                "z1": -8.0,
                "z2": -15.0,
                "z3": -25.0
            },
            "default_pe": pe_bounds
        }

    # 3. Specialized Moat & High Growth Categories
    if any(k in t_upper for k in ["SPGI", "MCO"]):
        pe_bounds = {"great": 26.0, "good": 34.0, "expensive": 44.0}
    elif any(k in t_upper for k in ["TMO"]):
        pe_bounds = {"great": 24.0, "good": 30.0, "expensive": 38.0}
    elif any(k in t_upper for k in ["ISRG"]):
        pe_bounds = {"great": 45.0, "good": 60.0, "expensive": 82.0}
    elif any(k in t_upper for k in ["CRWD", "PLTR", "PANW", "NET"]):
        pe_bounds = {"great": 50.0, "good": 75.0, "expensive": 110.0}
    elif any(k in t_upper for k in ["LLY", "NVO"]):
        pe_bounds = {"great": 28.0, "good": 38.0, "expensive": 50.0}
    elif any(k in t_upper for k in ["SMH", "NVDA", "TSM", "AVGO", "ASML", "KLAC", "AMAT", "LRCX", "VRT", "SNPS", "CEG", "PWR", "CCJ"]):
        pe_bounds = {"great": 28.0, "good": 38.0, "expensive": 52.0}
    elif any(k in t_upper for k in ["QQQ", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "ETN", "RTX"]):
        pe_bounds = {"great": 24.0, "good": 32.0, "expensive": 42.0}
    else:
        pe_bounds = {"great": 20.0, "good": 28.0, "expensive": 38.0}

    return {
        "profile": "MODERAT_GROWTH",
        "label": "🚀 Growth",
        "badge_bg": "bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 border-indigo-500/30",
        "thresholds": {
            "z1": -15.0,
            "z2": -25.0,
            "z3": -35.0
        },
        "default_pe": pe_bounds
    }


def calculate_dislocation_and_valuation(
    price: float,
    ath: float,
    pe: Optional[float],
    pe_great: Optional[float],
    pe_good: Optional[float],
    pe_exp: Optional[float],
    ticker: str = ""
) -> Dict[str, Any]:
    """Calculate ATH drawdown, adaptive Z1-Z4 Dislocation Zone, smart PE Valuation rating, and AI Dip Buying Signal."""
    prof = detect_volatility_profile(ticker)
    th = prof["thresholds"]

    if ath > 0:
        drawdown = ((price - ath) / ath) * 100.0
    else:
        drawdown = 0.0
    drawdown = round(drawdown, 2)

    # 1. Adaptive Drawdown Dislocation Z1-Z4
    if drawdown >= th["z1"]:
        status_code = "Z1"
        status_label = "Z1: Hold (Normal)"
        status_color = "slate"
        status_bg = "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-300 dark:border-slate-700 font-semibold"
    elif drawdown >= th["z2"]:
        status_code = "Z2"
        status_label = "Z2: Watch/Scout"
        status_color = "yellow"
        status_bg = "bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/30 font-semibold"
    elif drawdown >= th["z3"]:
        status_code = "Z3"
        status_label = "Z3: High Dislocation"
        status_color = "green"
        status_bg = "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/40 font-bold"
    else:
        status_code = "Z4"
        status_label = "Z4: Extreme Stress"
        status_color = "teal"
        status_bg = "bg-cyan-500/25 text-cyan-800 dark:text-cyan-300 border border-cyan-500/40 font-extrabold"

    # 2. Sectoral Smart PE Valuation
    def_pe = prof["default_pe"] or {}
    g_great = pe_great if (pe_great is not None and pe_great > 0) else def_pe.get("great")
    g_good = pe_good if (pe_good is not None and pe_good > 0) else def_pe.get("good")
    g_exp = pe_exp if (pe_exp is not None and pe_exp > 0) else def_pe.get("expensive")

    pe_state = "NA" # 'GREAT', 'GOOD', 'FAIR', 'EXPENSIVE', 'NA'
    pe_status = "N/A"
    pe_color = "text-slate-400 dark:text-slate-500 font-normal"

    if pe is not None and pe > 0:
        if g_great is not None and pe <= g_great:
            pe_state = "GREAT"
            pe_status = "Diskon / Murah"
            pe_color = "text-emerald-700 bg-emerald-50 border-emerald-300 dark:text-emerald-300 dark:bg-emerald-950/40 dark:border-emerald-600/50 font-bold px-2 py-0.5 rounded border"
        elif g_good is not None and pe <= g_good:
            pe_state = "GOOD"
            pe_status = "Harga Wajar"
            pe_color = "text-blue-700 bg-blue-50 border-blue-300 dark:text-blue-300 dark:bg-blue-950/40 dark:border-blue-600/50 font-semibold px-2 py-0.5 rounded border"
        elif g_exp is not None and pe >= g_exp:
            pe_state = "EXPENSIVE"
            pe_status = "Mahal / Overvalued"
            pe_color = "text-rose-700 bg-rose-50 border-rose-300 dark:text-rose-300 dark:bg-rose-950/40 dark:border-rose-600/50 font-bold px-2 py-0.5 rounded border"
        else:
            pe_state = "FAIR"
            pe_status = "Wajar"
            pe_color = "text-slate-700 bg-slate-100 border-slate-300 dark:text-slate-300 dark:bg-slate-800 dark:border-slate-700 font-medium px-2 py-0.5 rounded border"

    # 3. Composite Smart Dip-Buying Signal
    if status_code in ["Z3", "Z4"]:
        if pe_state in ["GREAT", "GOOD"] or pe_state == "NA":
            signal_code = "PRIME_BUY"
            signal_label = "🟢 PRIME BUY"
            signal_bg = "bg-emerald-500 text-white font-black shadow-[0_0_14px_rgba(16,185,129,0.85)] ring-2 ring-emerald-400/60 animate-pulse border border-emerald-300 dark:border-emerald-400"
            signal_desc = "Diskon ATH dalam & Valuasi Murah/Wajar (Double Discount)"
        elif pe_state == "EXPENSIVE":
            signal_code = "ACCUMULATE"
            signal_label = "🟡 Cicil DCA"
            signal_bg = "bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/40 font-semibold"
            signal_desc = "Diskon harga bagus tapi P/E masih agak premium"
        else:
            signal_code = "PRIME_BUY"
            signal_label = "🟢 PRIME BUY"
            signal_bg = "bg-emerald-500 text-white font-black shadow-[0_0_14px_rgba(16,185,129,0.85)] ring-2 ring-emerald-400/60 animate-pulse border border-emerald-300 dark:border-emerald-400"
            signal_desc = "Penurunan tajam dari ATH (Peluang Akumulasi Besar)"
    elif status_code == "Z2":
        if pe_state == "EXPENSIVE":
            signal_code = "HOLD"
            signal_label = "⚪ Hold"
            signal_bg = "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-medium"
            signal_desc = "Koreksi wajar namun valuasi masih tinggi"
        else:
            signal_code = "ACCUMULATE"
            signal_label = "🟡 Cicil DCA"
            signal_bg = "bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30 font-semibold"
            signal_desc = "Pullback sehat & valuasi bersahabat"
    else:  # Z1 (Near ATH)
        if pe_state == "EXPENSIVE":
            signal_code = "WAIT"
            signal_label = "⚪ Wait / Mahal"
            signal_bg = "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-medium"
            signal_desc = "Harga di puncak ATH dan P/E overvalued"
        elif pe_state == "GREAT":
            signal_code = "ACCUMULATE"
            signal_label = "🟡 Cicil DCA"
            signal_bg = "bg-sky-500/15 text-sky-600 dark:text-sky-400 border border-sky-500/30 font-semibold"
            signal_desc = "Meskipun dekat ATH, pertumbuhan laba membuat P/E murah"
        else:
            signal_code = "HOLD"
            signal_label = "⚪ Hold"
            signal_bg = "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-medium"
            signal_desc = "Harga stabil di zona normal"

    return {
        "drawdown": drawdown,
        "status_code": status_code,
        "status_label": status_label,
        "status_color": status_color,
        "status_bg": status_bg,
        "pe_status": pe_status,
        "pe_color": pe_color,
        "pe_state": pe_state,
        "volatility_profile": prof["profile"],
        "volatility_label": prof["label"],
        "volatility_bg": prof["badge_bg"],
        "smart_pe_thresholds": {
            "great": g_great,
            "good": g_good,
            "expensive": g_exp
        },
        "signal_code": signal_code,
        "signal_label": signal_label,
        "signal_bg": signal_bg,
        "signal_desc": signal_desc
    }


def sanitize_for_json(obj: Any) -> Any:
    """Recursively replace NaN and Inf with None or 0.0 for clean JSON serialization."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    return obj


def compute_full_portfolio(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """Take user raw portfolio and enrich with live prices, values, PnL, logos, and custom valuations."""
    macro = get_macro_and_fx()
    usd_idr = macro["usd_idr"]
    
    # Collect all unique tickers
    all_tickers = []
    for cat in portfolio_data.get("categories", []):
        for item in cat.get("items", []):
            all_tickers.append(item["ticker"])
            
    # Fetch all concurrently
    market_data_map = fetch_all_tickers_parallel(all_tickers)

    total_invested_idr = 0.0
    current_value_investment_idr = 0.0
    enriched_categories = []
    allocation_breakdown = {}
    
    for cat in portfolio_data.get("categories", []):
        cat_items = []
        cat_invested = 0.0
        cat_value = 0.0
        
        for item in cat.get("items", []):
            ticker = item["ticker"]
            currency = item.get("currency", "USD")
            quantity = float(item.get("quantity", 0.0))
            invested_idr = float(item.get("invested_idr", 0.0))
            avg_price = float(item.get("avg_price", 0.0))
            is_lot = bool(item.get("is_lot", False))
            
            mkt = market_data_map.get(ticker, {
                "price": FALLBACK_PRICES.get(ticker, 100.0),
                "ath": FALLBACK_PRICES.get(ticker, 100.0) * 1.1,
                "pe": None,
                "volume": 0,
                "market_cap": None,
                "perf": {"24h": 0.0, "5h": 0.0, "1w": 0.0, "1m": 0.0, "6m": 0.0, "1y": 0.0, "5y": None, "10y": None, "15y": None, "20y": None}
            })
            
            current_price = mkt["price"]
            ath = mkt["ath"]
            pe = mkt["pe"]
            perf = mkt["perf"]
            
            disloc = calculate_dislocation_and_valuation(
                price=current_price,
                ath=ath,
                pe=pe,
                pe_great=item.get("pe_great"),
                pe_good=item.get("pe_good"),
                pe_exp=item.get("pe_exp"),
                ticker=ticker
            )
            
            units = quantity * 100.0 if is_lot else quantity
            
            if currency == "IDR":
                cur_val_idr = units * current_price if units > 0 else (invested_idr if invested_idr > 0 else 0.0)
                cur_val_usd = cur_val_idr / usd_idr if usd_idr > 0 else 0.0
                invested_usd = invested_idr / usd_idr if usd_idr > 0 else 0.0
            else: # USD
                cur_val_usd = units * current_price if units > 0 else (invested_idr / usd_idr if invested_idr > 0 and usd_idr > 0 else 0.0)
                cur_val_idr = cur_val_usd * usd_idr
                invested_usd = invested_idr / usd_idr if usd_idr > 0 else 0.0

            if invested_idr > 0 and units > 0:
                pnl_idr = cur_val_idr - invested_idr
                pnl_usd = cur_val_usd - invested_usd
                pnl_pct = (pnl_idr / invested_idr) * 100.0
            else:
                pnl_idr = 0.0
                pnl_usd = 0.0
                pnl_pct = 0.0

            total_invested_idr += invested_idr
            current_value_investment_idr += cur_val_idr
            cat_invested += invested_idr
            cat_value += cur_val_idr

            logo_url = get_asset_logo_url(ticker)

            cat_items.append({
                **item,
                "logo_url": logo_url,
                "current_price": current_price,
                "ath": ath,
                "ath_price": ath,
                "drawdown": disloc["drawdown"],
                "ath_drawdown_pct": disloc["drawdown"],
                "status_code": disloc["status_code"],
                "status_label": disloc["status_label"],
                "status_color": disloc["status_color"],
                "status_bg": disloc["status_bg"],
                "ath_zone": disloc["status_label"],
                "volatility_profile": disloc["volatility_profile"],
                "volatility_label": disloc["volatility_label"],
                "volatility_bg": disloc["volatility_bg"],
                "pe": pe,
                "pe_ratio": pe,
                "pe_status": disloc["pe_status"],
                "pe_color": disloc["pe_color"],
                "pe_state": disloc["pe_state"],
                "smart_pe_thresholds": disloc["smart_pe_thresholds"],
                "signal_code": disloc["signal_code"],
                "signal_label": disloc["signal_label"],
                "signal_bg": disloc["signal_bg"],
                "signal_desc": disloc["signal_desc"],
                "market_cap": mkt.get("market_cap"),
                "market_cap_formatted": format_mcap_str(mkt.get("market_cap"), currency),
                "volume": mkt.get("volume", 0),
                "volume_formatted": format_volume_str(mkt.get("volume", 0)),
                "cur_val_idr": cur_val_idr,
                "cur_val_usd": cur_val_usd,
                "invested_usd": invested_usd,
                "pnl_idr": pnl_idr,
                "pnl_usd": pnl_usd,
                "pnl_pct": round(pnl_pct, 2) if not math.isnan(pnl_pct) else 0.0,
                "perf": perf,
                "yearly_returns": mkt.get("yearly_returns", {})
            })
            
        enriched_categories.append({
            **cat,
            "items": cat_items,
            "total_invested_idr": cat_invested,
            "total_value_idr": cat_value
        })
        
        allocation_breakdown[cat["name"]] = round(cat_value, 2)

    cash_balance = float(portfolio_data.get("cash_balance", 0.0))
    current_net_worth_idr = current_value_investment_idr + cash_balance
    current_net_worth_usd = current_net_worth_idr / usd_idr if usd_idr > 0 else 0.0
    
    total_outgoings_idr = float(portfolio_data.get("total_outgoings", 0.0))
    target_mode = str(portfolio_data.get("target_mode") or "USD").upper()
    if target_mode == "USD":
        target_ff_usd = float(portfolio_data.get("target_financial_freedom_usd", 500000.0))
        target_ff_idr = target_ff_usd * usd_idr if usd_idr > 0 else float(portfolio_data.get("target_financial_freedom", 8844000000.0))
    else:
        target_ff_idr = float(portfolio_data.get("target_financial_freedom", 8844000000.0))
        target_ff_usd = target_ff_idr / usd_idr if usd_idr > 0 else 500000.0
    
    ff_progress_pct = (current_net_worth_idr / target_ff_idr * 100.0) if target_ff_idr > 0 else 0.0
    
    total_pnl_idr = current_value_investment_idr - total_invested_idr
    total_pnl_usd = (current_value_investment_idr / usd_idr) - (total_invested_idr / usd_idr) if usd_idr > 0 else 0.0
    total_pnl_pct = (total_pnl_idr / total_invested_idr * 100.0) if total_invested_idr > 0 else 0.0

    raw_output = {
        "user_id": portfolio_data.get("user_id"),
        "user_name": portfolio_data.get("user_name", "Investor"),
        "target_mode": target_mode,
        "target_financial_freedom_usd": round(target_ff_usd, 2),
        "target_financial_freedom_idr": target_ff_idr,
        "ff_progress_pct": round(ff_progress_pct, 2) if not math.isnan(ff_progress_pct) else 0.0,
        "current_net_worth_idr": round(current_net_worth_idr, 0) if not math.isnan(current_net_worth_idr) else 0.0,
        "current_net_worth_usd": round(current_net_worth_usd, 2) if not math.isnan(current_net_worth_usd) else 0.0,
        "total_outgoings_idr": round(total_outgoings_idr, 0) if not math.isnan(total_outgoings_idr) else 0.0,
        "total_invested_idr": round(total_invested_idr, 0) if not math.isnan(total_invested_idr) else 0.0,
        "total_invested_usd": round(total_invested_idr / usd_idr, 2) if usd_idr > 0 and not math.isnan(usd_idr) else 0.0,
        "current_value_investment_idr": round(current_value_investment_idr, 0) if not math.isnan(current_value_investment_idr) else 0.0,
        "current_value_investment_usd": round(current_value_investment_idr / usd_idr, 2) if usd_idr > 0 and not math.isnan(usd_idr) else 0.0,
        "cash_balance_idr": round(cash_balance, 0) if not math.isnan(cash_balance) else 0.0,
        "total_pnl_idr": round(total_pnl_idr, 0) if not math.isnan(total_pnl_idr) else 0.0,
        "total_pnl_usd": round(total_pnl_usd, 2) if not math.isnan(total_pnl_usd) else 0.0,
        "total_pnl_pct": round(total_pnl_pct, 2) if not math.isnan(total_pnl_pct) else 0.0,
        "macro": macro,
        "categories": enriched_categories,
        "allocation_chart": allocation_breakdown
    }
    
    sanitized = sanitize_for_json(raw_output)
    try:
        from .database import sync_realtime_monthly_snapshot
        sync_realtime_monthly_snapshot(portfolio_data.get("user_id", "default_user"), sanitized)
    except Exception as e:
        logger.debug(f"Monthly snapshot sync: {e}")

    return sanitized
