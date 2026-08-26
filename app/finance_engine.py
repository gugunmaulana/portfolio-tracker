import time
import datetime
from dateutil.relativedelta import relativedelta
import math
import logging
from concurrent.futures import ThreadPoolExecutor
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
    # Indonesian Stocks
    "BBCA.JK": "https://assets.parqet.com/logos/symbol/BBCA.JK?format=png",
    "BBRI.JK": "https://assets.parqet.com/logos/symbol/BBRI.JK?format=png",
    "BMRI.JK": "https://assets.parqet.com/logos/symbol/BMRI.JK?format=png",
    "UNTR.JK": "https://assets.parqet.com/logos/symbol/UNTR.JK?format=png",
    "BREN.JK": "https://assets.parqet.com/logos/symbol/BREN.JK?format=png",
    "AMMN.JK": "https://assets.parqet.com/logos/symbol/AMMN.JK?format=png",
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
    "UNTR.JK": 26800.0,
    "BREN.JK": 6250.0,
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
    "VRT": 115.0
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
    "UNTR.JK": 5.4,
    "BREN.JK": 169.6,
    "KLAC": 50.26,
    "AMAT": 42.46,
    "LRCX": 42.66,
    "ETN": 42.66,
    "RTX": 39.5,
    "SNPS": 92.21,
    "CEG": 26.59,
    "PWR": 73.23,
    "CCJ": 117.29,
    "VRT": 59.28
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
    "MSTR": 2.45e8,
    "BBCA.JK": 123.28e9,
    "BBRI.JK": 151.56e9,
    "BMRI.JK": 93.33e9,
    "UNTR.JK": 3.73e9,
    "BREN.JK": 133.79e9,
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


def get_macro_and_fx() -> Dict[str, Any]:
    """Fetch live USD/IDR, CNY/IDR, IHSG, S&P500 and their multi-period returns."""
    tickers = ["USDIDR=X", "CNYIDR=X", "^JKSE", "^GSPC"]
    data = {}
    
    def fetch_single(t):
        res = fetch_direct_yahoo_chart(t, "5d", "1d")
        if res:
            meta = res.get("meta", {})
            quotes = res.get("indicators", {}).get("quote", [{}])[0]
            closes = [c for c in quotes.get("close", []) if c is not None and not math.isnan(c)]
            price = meta.get("regularMarketPrice") or (closes[-1] if closes else None)
            prev_close = meta.get("regularMarketPreviousClose") or meta.get("previousClose") or (closes[-2] if len(closes) >= 2 else None)
                
            chg_pct = 0.0
            if price and prev_close and prev_close > 0:
                chg_pct = ((price - prev_close) / prev_close) * 100.0
                
            if price:
                return t, {
                    "price": round(price, 2) if price < 10000 else round(price, 0),
                    "change_pct": round(chg_pct, 2)
                }
        return t, {"price": FALLBACK_PRICES.get(t, 1.0), "change_pct": 0.0}

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(fetch_single, tickers)
        for t, val in results:
            data[t] = val

    # Dynamic live benchmark data
    ihsg_data = fetch_ticker_market_data("^JKSE")
    sp500_data = fetch_ticker_market_data("^GSPC")
            
    return {
        "usd_idr": data.get("USDIDR=X", {}).get("price", 17688.0),
        "usd_idr_chg": data.get("USDIDR=X", {}).get("change_pct", 0.0),
        "cny_idr": data.get("CNYIDR=X", {}).get("price", 2632.0),
        "cny_idr_chg": data.get("CNYIDR=X", {}).get("change_pct", 0.0),
        "ihsg": data.get("^JKSE", {}).get("price", 6499.07),
        "ihsg_chg": data.get("^JKSE", {}).get("change_pct", 0.17),
        "sp500": data.get("^GSPC", {}).get("price", 5924.37),
        "sp500_chg": data.get("^GSPC", {}).get("change_pct", 0.43),
        "benchmarks": {
            "ihsg": {
                "name": "IHSG (IDX COMPOSITE)",
                "symbol": "^JKSE",
                "price": ihsg_data.get("price", 6501.67),
                "perf": ihsg_data.get("perf", {"24h": 0.17, "1w": -2.31, "1m": 0.41, "6m": -9.37, "1y": -7.31, "5y": 6.96, "10y": 20.63})
            },
            "sp500": {
                "name": "S&P 500 (INDEXSP:.INX)",
                "symbol": "^GSPC",
                "price": sp500_data.get("price", 5924.37),
                "perf": sp500_data.get("perf", {"24h": 0.43, "1w": -0.91, "1m": 3.92, "6m": 1.28, "1y": 19.33, "5y": 71.32, "10y": 250.92})
            }
        }
    }


def fetch_ticker_market_data(ticker_symbol: str) -> Dict[str, Any]:
    """Fetch realtime quote, ATH, PE ratio, and high-precision multi-period performance (24h to 20y) for a given ticker."""
    cached = MARKET_CACHE.get(ticker_symbol)
    now = time.time()
    if cached and (now - cached.get("_timestamp", 0) < CACHE_TTL_SECONDS):
        return cached

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
        "_timestamp": now
    }

    try:
        # Tier 1: High-precision daily bars for up to 10 years
        chart_daily = fetch_direct_yahoo_chart(ticker_symbol, "10y", "1d")
        
        # Tier 2: Monthly max bars for >10y history (15y, 20y) and true lifetime ATH
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

        # Determine All-Time High across both daily and max series
        all_highs = highs_daily + highs_max
        ath_meta = meta.get("fiftyTwoWeekHigh")
        high_point = max(all_highs) if all_highs else (ath_meta or (cur_price * 1.1))
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
                    
                # 1. TradingView window: start candle open on or after target_dt
                cands = [b for b in daily_pts if b["dt"] >= target_dt]
                if cands and cands[0]["ts"] != cur_ts:
                    base_price = cands[0]["open"] or cands[0]["close"]
                    if base_price > 0:
                        return round(((cur_price - base_price) / base_price) * 100.0, 2)
                        
                # 2. Daily candle on or before target_dt
                before_cands = [b for b in daily_pts if b["dt"] <= target_dt]
                if before_cands:
                    base_price = before_cands[-1]["close"]
                    if base_price > 0:
                        return round(((cur_price - base_price) / base_price) * 100.0, 2)
                        
                # 3. Monthly max series for >10y timeframes
                if max_pts:
                    m_cands = [b for b in max_pts if b["dt"] >= target_dt]
                    if m_cands:
                        base_price = m_cands[0]["open"] or m_cands[0]["close"]
                        if base_price > 0:
                            return round(((cur_price - base_price) / base_price) * 100.0, 2)
                    m_before = [b for b in max_pts if b["dt"] <= target_dt]
                    if m_before:
                        base_price = m_before[-1]["close"]
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

            # Accurate 5H / 1W Return (1 full trading week: 5 trading sessions for equities, 7 for crypto)
            is_crypto = "-USD" in ticker_symbol or ticker_symbol in ["BTC-USD", "ETH-USD", "SOL-USD"]
            target_5h_dt = cur_dt - datetime.timedelta(days=7)
            cands_5h = [b for b in daily_pts if b["dt"] <= target_5h_dt]
            if cands_5h:
                base_5h = cands_5h[-1]["close"]
                if base_5h > 0:
                    result["perf"]["5h"] = round(((cur_price - base_5h) / base_5h) * 100.0, 2)
            elif len(daily_pts) >= (8 if is_crypto else 6):
                n_bars = 7 if is_crypto else 5
                base_5h = daily_pts[-1 - n_bars]["close"]
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

    except Exception as e:
        logger.debug(f"Fetch error for {ticker_symbol}: {e}")

    # Fallback sanity
    if result["price"] <= 0:
        result["price"] = FALLBACK_PRICES.get(ticker_symbol, 100.0)
    if result["ath"] <= result["price"]:
        result["ath"] = round(result["price"] * 1.1, 2)
    if result["pe"] is None:
        result["pe"] = FALLBACK_PE_RATIOS.get(ticker_symbol, None)
    if result.get("market_cap") is None:
        shares = SHARES_OUTSTANDING.get(ticker_symbol)
        if shares:
            result["market_cap"] = round(result["price"] * shares, 2)

    prof = detect_volatility_profile(ticker_symbol)
    result["volatility_profile"] = prof["profile"]
    result["volatility_label"] = prof["label"]
    result["volatility_bg"] = prof["badge_bg"]
    result["smart_pe_thresholds"] = prof["default_pe"]

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
    if t_upper in ["VOO", "SPY", "IVV", "BRK-B", "COST", "JPM", "V", "PG", "GC=F"] or (t_upper.endswith(".JK") and any(t_upper.startswith(p) for p in ["BBCA", "BMRI", "UNTR", "TLKM"])):
        if ".JK" in t_upper and ("BBCA" in t_upper or "BMRI" in t_upper):
            pe_bounds = {"great": 13.0, "good": 18.0, "expensive": 23.0}
        elif ".JK" in t_upper and "UNTR" in t_upper:
            pe_bounds = {"great": 5.0, "good": 8.0, "expensive": 12.0}
        elif t_upper == "GC=F":
            pe_bounds = None
        else: # VOO, BRK-B, COST, JPM, V
            pe_bounds = {"great": 19.0, "good": 24.0, "expensive": 30.0}

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

    # 3. Moderate / High-Growth Tech & Semiconductor Stocks
    if any(k in t_upper for k in ["SMH", "NVDA", "TSM", "AVGO", "ASML", "KLAC", "AMAT", "LRCX", "VRT", "SNPS", "CEG", "PWR", "CCJ"]):
        pe_bounds = {"great": 28.0, "good": 38.0, "expensive": 50.0}
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
            signal_label = "🟢 Prime Buy"
            signal_bg = "bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/40 font-bold shadow-sm"
            signal_desc = "Diskon ATH dalam & Valuasi Murah/Wajar (Double Discount)"
        elif pe_state == "EXPENSIVE":
            signal_code = "ACCUMULATE"
            signal_label = "🟡 Cicil DCA"
            signal_bg = "bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/40 font-semibold"
            signal_desc = "Diskon harga bagus tapi P/E masih agak premium"
        else:
            signal_code = "PRIME_BUY"
            signal_label = "🟢 Prime Buy"
            signal_bg = "bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/40 font-bold"
            signal_desc = "Penurunan tajam dari ATH (Peluang Akumulasi Besar)"
    elif status_code == "Z2":
        if pe_state == "EXPENSIVE":
            signal_code = "HOLD"
            signal_label = "⚪ Hold"
            signal_bg = "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 border border-slate-300 dark:border-slate-700 font-medium"
            signal_desc = "Koreksi wajar namun valuasi masih tinggi"
        else:
            signal_code = "ACCUMULATE"
            signal_label = "🟡 Cicil DCA"
            signal_bg = "bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30 font-semibold"
            signal_desc = "Pullback sehat & valuasi bersahabat"
    else:  # Z1 (Near ATH)
        if pe_state == "EXPENSIVE":
            signal_code = "WAIT"
            signal_label = "🔴 Wait / Mahal"
            signal_bg = "bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/30 font-semibold"
            signal_desc = "Harga di puncak ATH dan P/E overvalued"
        elif pe_state == "GREAT":
            signal_code = "ACCUMULATE"
            signal_label = "🟡 Cicil DCA"
            signal_bg = "bg-sky-500/15 text-sky-600 dark:text-sky-400 border border-sky-500/30 font-semibold"
            signal_desc = "Meskipun dekat ATH, pertumbuhan laba membuat P/E murah"
        else:
            signal_code = "HOLD"
            signal_label = "⚪ Hold"
            signal_bg = "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 border border-slate-300 dark:border-slate-700 font-medium"
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
                cur_val_idr = units * current_price if units > 0 else 0.0
                cur_val_usd = cur_val_idr / usd_idr if usd_idr > 0 else 0.0
                invested_usd = invested_idr / usd_idr if usd_idr > 0 else 0.0
            else: # USD
                cur_val_usd = units * current_price if units > 0 else 0.0
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
                "perf": perf
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
    target_ff_idr = float(portfolio_data.get("target_financial_freedom", 8844000000.0))
    
    ff_progress_pct = (current_net_worth_idr / target_ff_idr * 100.0) if target_ff_idr > 0 else 0.0
    
    total_pnl_idr = current_value_investment_idr - total_invested_idr
    total_pnl_usd = (current_value_investment_idr / usd_idr) - (total_invested_idr / usd_idr) if usd_idr > 0 else 0.0
    total_pnl_pct = (total_pnl_idr / total_invested_idr * 100.0) if total_invested_idr > 0 else 0.0

    raw_output = {
        "user_id": portfolio_data.get("user_id"),
        "user_name": portfolio_data.get("user_name", "Investor"),
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
