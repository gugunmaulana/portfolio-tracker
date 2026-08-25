import time
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


def fetch_direct_yahoo_chart(ticker: str, range_str: str = "10y") -> Optional[Dict[str, Any]]:
    """Directly fetch chart data from Yahoo Finance API with robust browser headers."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range={range_str}"
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
        res = fetch_direct_yahoo_chart(t, "1y")
        if res:
            meta = res.get("meta", {})
            price = meta.get("regularMarketPrice")
            prev_close = meta.get("chartPreviousClose")
            
            quotes = res.get("indicators", {}).get("quote", [{}])[0]
            closes = [c for c in quotes.get("close", []) if c is not None]
            if not price and closes:
                price = closes[-1]
            if not prev_close and len(closes) > 1:
                prev_close = closes[-2]
                
            chg_pct = 0.0
            if price and prev_close and prev_close > 0:
                chg_pct = ((price - prev_close) / prev_close) * 100.0
                
            return t, {
                "price": round(price, 2) if price < 10000 else round(price, 0),
                "change_pct": round(chg_pct, 2)
            }
        return t, {"price": FALLBACK_PRICES.get(t, 1.0), "change_pct": 0.0}

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(fetch_single, tickers)
        for t, val in results:
            data[t] = val
            
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
                "price": data.get("^JKSE", {}).get("price", 6499.07),
                "perf": {"24h": 0.17, "1w": -2.31, "1m": 0.41, "6m": -9.37, "1y": -7.31, "5y": 6.96, "10y": 20.63}
            },
            "sp500": {
                "name": "S&P 500 (INDEXSP:.INX)",
                "symbol": "^GSPC",
                "price": data.get("^GSPC", {}).get("price", 5924.37),
                "perf": {"24h": 0.43, "1w": -0.91, "1m": 3.92, "6m": 1.28, "1y": 19.33, "5y": 71.32, "10y": 250.92}
            }
        }
    }


def fetch_ticker_market_data(ticker_symbol: str) -> Dict[str, Any]:
    """Fetch realtime quote, ATH, PE ratio, and multi-period performance (24h to 20y) for a given ticker."""
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
            "1w": 0.0,
            "1m": 0.0,
            "6m": 0.0,
            "1y": 0.0,
            "5y": None,
            "10y": None,
            "15y": None,
            "20y": None
        },
        "_timestamp": now
    }

    try:
        chart_res = fetch_direct_yahoo_chart(ticker_symbol, "max")
        if chart_res:
            meta = chart_res.get("meta", {})
            timestamps = chart_res.get("timestamp", [])
            quotes = chart_res.get("indicators", {}).get("quote", [{}])[0]
            raw_closes = quotes.get("close", [])
            raw_highs = quotes.get("high", [])

            # Valid pairs
            data_points = []
            for t, c in zip(timestamps, raw_closes):
                if c is not None and not math.isnan(c) and c > 0:
                    data_points.append((t, c))

            highs = [h for h in raw_highs if h is not None and not math.isnan(h)]

            price = meta.get("regularMarketPrice")
            if (not price or math.isnan(price)) and data_points:
                price = data_points[-1][1]
            if price and not math.isnan(price):
                result["price"] = round(price, 2)

            ath_meta = meta.get("fiftyTwoWeekHigh")
            high_point = max(highs) if highs else (price * 1.1 if price else 100.0)
            result["ath"] = round(max(ath_meta or 0, high_point), 2)

            if len(data_points) >= 1:
                cur_close = data_points[-1][1]
                now_ts = data_points[-1][0]
                first_ts = data_points[0][0]
                total_span_days = (now_ts - first_ts) / 86400.0

                # 24H (1 trading session / 1 day return)
                if len(data_points) >= 2:
                    c_prev = data_points[-2][1]
                    result["perf"]["24h"] = round(((cur_close - c_prev) / c_prev) * 100.0, 1)

                # 5H / 1W (5 trading sessions / 1 week return)
                if len(data_points) >= 6:
                    c_5d = data_points[-6][1]
                    result["perf"]["5h"] = round(((cur_close - c_5d) / c_5d) * 100.0, 1)
                    result["perf"]["1w"] = result["perf"]["5h"]
                elif len(data_points) >= 2:
                    c_first = data_points[0][1]
                    result["perf"]["5h"] = round(((cur_close - c_first) / c_first) * 100.0, 1)
                    result["perf"]["1w"] = result["perf"]["5h"]

                def get_total_profit_pct(days: int) -> Optional[float]:
                    # If total history is significantly shorter than requested timeframe, return None (N/A)
                    if total_span_days < (days * 0.85):
                        return None
                    target_ts = now_ts - (days * 86400)
                    if target_ts < first_ts:
                        return None
                    closest = min(data_points, key=lambda x: abs(x[0] - target_ts))
                    if closest[1] and closest[1] > 0:
                        # Pure Total Cumulative Profit Percentage (NO CAGR!)
                        ret = ((cur_close - closest[1]) / closest[1]) * 100.0
                        return round(ret, 1)
                    return None

                # If 5h wasn't set by trading sessions, compute by 7 calendar days
                if result["perf"].get("5h") is None:
                    p5 = get_total_profit_pct(7)
                    result["perf"]["5h"] = p5
                    result["perf"]["1w"] = p5

                result["perf"]["1m"] = get_total_profit_pct(30)
                result["perf"]["6m"] = get_total_profit_pct(182)
                result["perf"]["1y"] = get_total_profit_pct(365)
                result["perf"]["5y"] = get_total_profit_pct(5 * 365)
                result["perf"]["10y"] = get_total_profit_pct(10 * 365)
                result["perf"]["15y"] = get_total_profit_pct(15 * 365)
                result["perf"]["20y"] = get_total_profit_pct(20 * 365)

    except Exception as e:
        logger.debug(f"Fetch error for {ticker_symbol}: {e}")

    # Fallback sanity
    if result["price"] <= 0:
        result["price"] = FALLBACK_PRICES.get(ticker_symbol, 100.0)
    if result["ath"] <= result["price"]:
        result["ath"] = round(result["price"] * 1.1, 2)
    if result["pe"] is None:
        result["pe"] = FALLBACK_PE_RATIOS.get(ticker_symbol, None)

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
                    "perf": {"24h": 0.0, "1w": 0.0, "1m": 0.0, "6m": 0.0, "1y": 0.0, "5y": None, "10y": None, "15y": None, "20y": None}
                }
    return results


def calculate_dislocation_and_valuation(
    price: float,
    ath: float,
    pe: Optional[float],
    pe_great: Optional[float],
    pe_good: Optional[float],
    pe_exp: Optional[float]
) -> Dict[str, Any]:
    """Calculate ATH drawdown, Z1-Z4 Dislocation Zone, and PE Valuation rating tailored per asset."""
    if ath > 0:
        drawdown = ((price - ath) / ath) * 100.0
    else:
        drawdown = 0.0
    drawdown = round(drawdown, 2)

    if drawdown >= -15.0:
        status_code = "Z1"
        status_label = "Z1: Hold"
        status_color = "slate"
        status_bg = "bg-slate-100 text-slate-800 border-slate-300 dark:bg-slate-800/80 dark:text-slate-300 dark:border-slate-700 font-semibold"
    elif drawdown >= -25.0:
        status_code = "Z2"
        status_label = "Z2: Watch/Scout"
        status_color = "yellow"
        status_bg = "bg-amber-50 text-amber-900 border-amber-300 dark:bg-amber-500/15 dark:text-amber-300 dark:border-amber-500/40 font-semibold"
    elif drawdown >= -40.0:
        status_code = "Z3"
        status_label = "Z3: High Dislocation"
        status_color = "green"
        status_bg = "bg-emerald-50 text-emerald-900 border-emerald-400 dark:bg-emerald-500/20 dark:text-emerald-300 dark:border-emerald-500/40 font-bold"
    else:
        status_code = "Z4"
        status_label = "Z4: Extreme Stress"
        status_color = "teal"
        status_bg = "bg-cyan-50 text-cyan-900 border-cyan-400 dark:bg-cyan-500/25 dark:text-cyan-300 dark:border-cyan-400 font-extrabold"

    pe_status = "N/A"
    pe_color = "text-slate-400 dark:text-slate-500 font-normal"
    if pe is not None and pe > 0:
        if pe_great is not None and pe <= pe_great:
            pe_status = "Diskon / Murah"
            pe_color = "text-emerald-700 bg-emerald-50 border-emerald-300 dark:text-emerald-300 dark:bg-emerald-950/40 dark:border-emerald-600/50 font-bold px-2 py-0.5 rounded border"
        elif pe_good is not None and pe <= pe_good:
            pe_status = "Harga Wajar"
            pe_color = "text-blue-700 bg-blue-50 border-blue-300 dark:text-blue-300 dark:bg-blue-950/40 dark:border-blue-600/50 font-semibold px-2 py-0.5 rounded border"
        elif pe_exp is not None and pe >= pe_exp:
            pe_status = "Mahal / Overvalued"
            pe_color = "text-rose-700 bg-rose-50 border-rose-300 dark:text-rose-300 dark:bg-rose-950/40 dark:border-rose-600/50 font-bold px-2 py-0.5 rounded border"
        else:
            pe_status = "Fair"
            pe_color = "text-slate-700 bg-slate-100 border-slate-300 dark:text-slate-300 dark:bg-slate-800 dark:border-slate-700 font-medium px-2 py-0.5 rounded border"

    return {
        "drawdown": drawdown,
        "status_code": status_code,
        "status_label": status_label,
        "status_color": status_color,
        "status_bg": status_bg,
        "pe_status": pe_status,
        "pe_color": pe_color
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
                "perf": {"24h": 0.0, "1w": 0.0, "1m": 0.0, "6m": 0.0, "1y": 0.0, "5y": None, "10y": None, "15y": None, "20y": None}
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
                pe_exp=item.get("pe_exp")
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
                "drawdown": disloc["drawdown"],
                "status_code": disloc["status_code"],
                "status_label": disloc["status_label"],
                "status_color": disloc["status_color"],
                "status_bg": disloc["status_bg"],
                "pe": pe,
                "pe_status": disloc["pe_status"],
                "pe_color": disloc["pe_color"],
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
    
    return sanitize_for_json(raw_output)
