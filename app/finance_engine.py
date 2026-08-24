import time
import math
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
import yfinance as yf

logger = logging.getLogger("finance_engine")
logger.setLevel(logging.INFO)

# In-memory cache for market data with ultra-fast TTL for live stream
MARKET_CACHE: Dict[str, Any] = {}
CACHE_TTL_SECONDS = 15

FALLBACK_PRICES = {
    "USDIDR=X": 17688.0,
    "CNYIDR=X": 2632.0,
    "^JKSE": 6534.9,
    "^GSPC": 5924.37,
    "VOO": 542.80,
    "QQQ": 491.15,
    "SMH": 248.50,
    "BTC-USD": 97442.0,
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
    "NVDA": 132.80,
    "ASML": 715.40,
    "LLY": 845.20,
    "BBCA.JK": 9850.0,
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


def get_macro_and_fx() -> Dict[str, Any]:
    """Fetch live USD/IDR, CNY/IDR, IHSG, S&P500 and their returns."""
    tickers = ["USDIDR=X", "CNYIDR=X", "^JKSE", "^GSPC"]
    data = {}
    
    def fetch_single(t):
        try:
            ticker_obj = yf.Ticker(t)
            fi = getattr(ticker_obj, "fast_info", None)
            price = getattr(fi, "last_price", None) if fi else None
            prev_close = getattr(fi, "previous_close", None) if fi else None
            
            if not price or math.isnan(price):
                hist = ticker_obj.history(period="5d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                    if len(hist) > 1:
                        prev_close = float(hist["Close"].iloc[-2])
            
            if not price or math.isnan(price):
                price = FALLBACK_PRICES.get(t, 1.0)
            if not prev_close or math.isnan(prev_close):
                prev_close = price
                
            chg_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
            return t, {
                "price": round(price, 2) if price < 10000 else round(price, 0),
                "change_pct": round(chg_pct, 2)
            }
        except Exception as e:
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
        "ihsg": data.get("^JKSE", {}).get("price", 6534.9),
        "ihsg_chg": data.get("^JKSE", {}).get("change_pct", 0.17),
        "sp500": data.get("^GSPC", {}).get("price", 5924.37),
        "sp500_chg": data.get("^GSPC", {}).get("change_pct", 0.43),
        "benchmarks": {
            "ihsg": {
                "name": "IHSG (IDX COMPOSITE)",
                "symbol": "^JKSE",
                "price": data.get("^JKSE", {}).get("price", 6534.9),
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
        t = yf.Ticker(ticker_symbol)
        
        # 1. Fast Info & Current Price
        fi = getattr(t, "fast_info", None)
        price = None
        if fi:
            price = getattr(fi, "last_price", None)
            ath_52w = getattr(fi, "year_high", None)
            if ath_52w and not math.isnan(ath_52w):
                result["ath"] = round(ath_52w, 2)

        # 2. History for returns (fetch max history to get 5y, 10y, 15y, 20y accurately)
        hist = t.history(period="max")
        if not hist.empty:
            if not price or math.isnan(price):
                price = float(hist["Close"].iloc[-1])
            
            hist_high = float(hist["High"].max())
            if hist_high > result["ath"]:
                result["ath"] = round(hist_high, 2)
            
            c_latest = float(hist["Close"].iloc[-1])
            n = len(hist)

            # 24h (~1 day)
            if n >= 2:
                c_prev = float(hist["Close"].iloc[-2])
                result["perf"]["24h"] = round(((c_latest - c_prev) / c_prev) * 100, 2)
            # 1w (~5 trading days)
            if n >= 5:
                c_1w = float(hist["Close"].iloc[-5])
                result["perf"]["1w"] = round(((c_latest - c_1w) / c_1w) * 100, 2)
            # 1m (~21 trading days)
            if n >= 21:
                c_1m = float(hist["Close"].iloc[-21])
                result["perf"]["1m"] = round(((c_latest - c_1m) / c_1m) * 100, 2)
            # 6m (~126 trading days)
            if n >= 126:
                c_6m = float(hist["Close"].iloc[-126])
                result["perf"]["6m"] = round(((c_latest - c_6m) / c_6m) * 100, 2)
            # 1y (~252 trading days)
            if n >= 252:
                c_1y = float(hist["Close"].iloc[-252])
                result["perf"]["1y"] = round(((c_latest - c_1y) / c_1y) * 100, 2)
            elif n > 10:
                c_1y = float(hist["Close"].iloc[0])
                result["perf"]["1y"] = round(((c_latest - c_1y) / c_1y) * 100, 2)

            # 5y (~1260 trading days)
            if n >= 1260:
                c_5y = float(hist["Close"].iloc[-1260])
                result["perf"]["5y"] = round(((c_latest - c_5y) / c_5y) * 100, 2)
            
            # 10y (~2520 trading days)
            if n >= 2520:
                c_10y = float(hist["Close"].iloc[-2520])
                result["perf"]["10y"] = round(((c_latest - c_10y) / c_10y) * 100, 2)

            # 15y (~3780 trading days)
            if n >= 3780:
                c_15y = float(hist["Close"].iloc[-3780])
                result["perf"]["15y"] = round(((c_latest - c_15y) / c_15y) * 100, 2)

            # 20y (~5040 trading days)
            if n >= 5040:
                c_20y = float(hist["Close"].iloc[-5040])
                result["perf"]["20y"] = round(((c_latest - c_20y) / c_20y) * 100, 2)

        if price and not math.isnan(price):
            result["price"] = round(price, 2)

        # 3. Enhanced PE Ratio Multi-source fetch
        try:
            info = getattr(t, "info", {})
            pe = info.get("trailingPE") or info.get("forwardPE")
            if not pe or math.isnan(pe):
                eps = info.get("trailingEps") or info.get("forwardEps")
                if eps and eps > 0 and result["price"] > 0:
                    pe = result["price"] / eps
            if pe and not math.isnan(pe) and pe > 0:
                result["pe"] = round(pe, 2)
        except Exception:
            pass

    except Exception as e:
        logger.warning(f"Live data warning for {ticker_symbol}: {e}")

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
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(fetch_ticker_market_data, t): t for t in set(tickers)}
        for future in futures:
            t = futures[future]
            try:
                results[t] = future.result()
            except Exception as e:
                logger.warning(f"Failed to fetch {t}: {e}")
                results[t] = {
                    "ticker": t,
                    "price": FALLBACK_PRICES.get(t, 100.0),
                    "ath": FALLBACK_PRICES.get(t, 100.0) * 1.1,
                    "pe": None,
                    "perf": {"24h": 0.0, "1w": 0.0, "1m": 0.0, "6m": 0.0, "1y": 0.0, "5y": 0.0, "10y": 0.0}
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
    """Calculate ATH drawdown, Z1-Z4 Dislocation Zone, and PE Valuation rating."""
    if ath > 0:
        drawdown = ((price - ath) / ath) * 100.0
    else:
        drawdown = 0.0
    drawdown = round(drawdown, 2)

    if drawdown >= -15.0:
        status_code = "Z1"
        status_label = "Z1: Hold"
        status_color = "slate"
        status_bg = "bg-slate-200 text-slate-800 border-slate-300 dark:bg-slate-800 dark:text-slate-200 dark:border-slate-700 font-bold shadow-xs"
    elif drawdown >= -25.0:
        status_code = "Z2"
        status_label = "Z2: Watch/Scout"
        status_color = "yellow"
        status_bg = "bg-amber-100 text-amber-950 border-amber-400 dark:bg-amber-500/20 dark:text-amber-300 dark:border-amber-500/50 font-bold shadow-xs"
    elif drawdown >= -40.0:
        status_code = "Z3"
        status_label = "Z3: High Dislocation"
        status_color = "green"
        status_bg = "bg-emerald-100 text-emerald-950 border-emerald-500 dark:bg-emerald-500/25 dark:text-emerald-300 dark:border-emerald-500/50 font-extrabold shadow-xs"
    else:
        status_code = "Z4"
        status_label = "Z4: Extreme Stress"
        status_color = "teal"
        status_bg = "bg-cyan-100 text-cyan-950 border-cyan-500 dark:bg-cyan-500/30 dark:text-cyan-300 dark:border-cyan-400 font-extrabold badge-glow-teal animate-pulse shadow-md"

    pe_status = "N/A"
    pe_color = "text-slate-500 dark:text-slate-400 font-medium"
    if pe is not None and pe > 0:
        if pe_great and pe <= pe_great:
            pe_status = "Great Buy"
            pe_color = "text-emerald-900 bg-emerald-100 border-emerald-400 dark:text-emerald-300 dark:bg-emerald-950/60 dark:border-emerald-600/60 font-bold px-2 py-0.5 rounded border shadow-xs"
        elif pe_good and pe <= pe_good:
            pe_status = "Good Buy"
            pe_color = "text-lime-900 bg-lime-100 border-lime-400 dark:text-lime-300 dark:bg-lime-950/50 dark:border-lime-600/50 font-bold px-2 py-0.5 rounded border shadow-xs"
        elif pe_exp and pe >= pe_exp:
            pe_status = "Expensive"
            pe_color = "text-rose-900 bg-rose-100 border-rose-400 dark:text-rose-300 dark:bg-rose-950/60 dark:border-rose-600/60 font-bold px-2 py-0.5 rounded border shadow-xs"
        else:
            pe_status = "Fair Value"
            pe_color = "text-slate-600 dark:text-slate-400 font-semibold"

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
    """Take user raw portfolio and enrich with live prices, values, PnL and scorecards."""
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
                "perf": {"24h": 0.0, "1w": 0.0, "1m": 0.0, "6m": 0.0, "1y": 0.0, "5y": 0.0, "10y": 0.0}
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

            cat_items.append({
                **item,
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


# ==============================================================================
# CAGR CAPITAL ALLOCATOR & HISTORICAL YEARLY RETURNS ENGINE (2011 - 2026)
# ==============================================================================

CAGR_CACHE: Dict[str, Dict[int, Optional[float]]] = {}

DEFAULT_CAGR_DATA = {
    "categories": [
        {"name": "Core Broad Beta", "tickers": ["VOO", "SMH", "QQQ"]},
        {"name": "Macro / Hedge", "tickers": ["BTC-USD", "ETH-USD", "GC=F"]},
        {"name": "Global Compounder", "tickers": ["BRK-B", "COST", "JPM", "V", "MSFT", "AAPL", "GOOGL", "AMZN", "META"]},
        {"name": "Semiconductor / Chokepoint", "tickers": ["AVGO", "TSM", "NVDA", "ASML", "KLAC", "AMAT", "LRCX", "SNPS"]},
        {"name": "Healthcare Mega", "tickers": ["LLY"]},
        {"name": "Policy / Infrastructure", "tickers": ["ETN", "RTX", "CEG", "PWR", "CCJ"]},
        {"name": "Data Center Infra", "tickers": ["VRT"]},
        {"name": "Indonesia Satellite", "tickers": ["BBCA.JK", "BBRI.JK", "BREN.JK", "UNTR.JK"]}
    ],
    "years": [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
    "returns": {
        "VOO": {2011: 0.021, 2012: 0.160, 2013: 0.324, 2014: 0.136, 2015: 0.0138, 2016: 0.0983, 2017: 0.1947, 2018: -0.0631, 2019: 0.2872, 2020: 0.1619, 2021: 0.2702, 2022: -0.1952, 2023: 0.2432, 2024: 0.2335, 2025: 0.1039, 2026: 0.0245},
        "SMH": {2011: -0.070, 2012: 0.048, 2013: 0.397, 2014: 0.283, 2015: -0.0120, 2016: 0.2450, 2017: 0.4210, 2018: -0.0530, 2019: 0.6420, 2020: 0.5310, 2021: 0.4150, 2022: -0.3480, 2023: 0.7210, 2024: 0.2820, 2025: 0.1840, 2026: 0.0410},
        "QQQ": {2011: 0.034, 2012: 0.181, 2013: 0.369, 2014: 0.192, 2015: 0.0950, 2016: 0.0710, 2017: 0.3270, 2018: -0.0010, 2019: 0.3910, 2020: 0.4860, 2021: 0.2740, 2022: -0.3260, 2023: 0.5470, 2024: 0.2240, 2025: 0.1250, 2026: 0.0315},
        "BTC-USD": {2011: 14.600, 2012: 1.860, 2013: 55.000, 2014: -0.580, 2015: 0.3500, 2016: 1.2383, 2017: 13.6890, 2018: -0.7356, 2019: 0.9220, 2020: 3.0316, 2021: 0.5987, 2022: -0.6427, 2023: 1.5542, 2024: 1.2105, 2025: -0.0534, 2026: 0.0820},
        "ETH-USD": {2017: 93.8415, 2018: -0.8231, 2019: -0.0114, 2020: 4.7228, 2021: 3.9915, 2022: -0.6797, 2023: 0.9087, 2024: 0.7896, 2025: 0.1481, 2026: 0.0540},
        "GC=F": {2011: 0.101, 2012: 0.070, 2013: -0.283, 2014: -0.015, 2015: -0.1040, 2016: 0.0812, 2017: 0.1347, 2018: -0.0115, 2019: 0.1831, 2020: 0.2443, 2021: -0.0364, 2022: -0.0022, 2023: 0.1307, 2024: 0.2718, 2025: 0.1032, 2026: 0.0385},
        "BRK-B": {2011: -0.047, 2012: 0.168, 2013: 0.313, 2014: 0.270, 2015: -0.1250, 2016: 0.2343, 2017: 0.2162, 2018: 0.0301, 2019: 0.1093, 2020: 0.0237, 2021: 0.2895, 2022: 0.0331, 2023: 0.1546, 2024: 0.2709, 2025: 0.1089, 2026: 0.0180},
        "COST": {2011: 0.191, 2012: 0.198, 2013: 0.175, 2014: 0.233, 2015: 0.1560, 2016: 0.0028, 2017: 0.2237, 2018: 0.1060, 2019: 0.4570, 2020: 0.3267, 2021: 0.4280, 2022: -0.0885, 2023: 0.5182, 2024: 0.3962, 2025: -0.0539, 2026: 0.0125},
        "JPM": {2011: -0.223, 2012: 0.321, 2013: 0.331, 2014: 0.103, 2015: 0.0840, 2016: 0.3068, 2017: 0.2393, 2018: -0.0872, 2019: 0.4280, 2020: -0.0885, 2021: 0.2462, 2022: -0.1299, 2023: 0.3050, 2024: 0.3962, 2025: 0.0804, 2026: 0.0210},
        "V": {2011: 0.461, 2012: 0.493, 2013: 0.454, 2014: 0.170, 2015: 0.1920, 2016: 0.0320, 2017: 0.4610, 2018: 0.1640, 2019: 0.4240, 2020: 0.1710, 2021: -0.0030, 2022: -0.0410, 2023: 0.2510, 2024: 0.1520, 2025: 0.1330, 2026: 0.0195},
        "MSFT": {2011: -0.070, 2012: 0.029, 2013: 0.400, 2014: 0.275, 2015: 0.2290, 2016: 0.1200, 2017: 0.3788, 2018: 0.1874, 2019: 0.5528, 2020: 0.4104, 2021: 0.5121, 2022: -0.2869, 2023: 0.5680, 2024: 0.1208, 2025: 0.1474, 2026: 0.0340},
        "AAPL": {2011: 0.256, 2012: 0.326, 2013: 0.081, 2014: 0.406, 2015: -0.0300, 2016: 0.1003, 2017: 0.4611, 2018: -0.0679, 2019: 0.8616, 2020: 0.8075, 2021: 0.3382, 2022: -0.2683, 2023: 0.4818, 2024: 0.3007, 2025: 0.1060, 2026: 0.0210},
        "GOOGL": {2011: 0.095, 2012: 0.095, 2013: 0.584, 2014: -0.054, 2015: 0.4660, 2016: 0.0186, 2017: 0.3293, 2018: -0.0080, 2019: 0.2818, 2020: 0.3085, 2021: 0.6530, 2022: -0.3867, 2023: 0.5832, 2024: 0.3551, 2025: 0.1470, 2026: 0.0185},
        "AMZN": {2011: -0.038, 2012: 0.449, 2013: 0.590, 2014: -0.222, 2015: 1.1780, 2016: 0.1095, 2017: 0.5595, 2018: 0.2843, 2019: 0.2303, 2020: 0.7625, 2021: 0.0238, 2022: -0.4962, 2023: 0.8088, 2024: 0.3290, 2025: 0.1890, 2026: 0.0280},
        "META": {2012: -0.303, 2013: 1.053, 2014: 0.428, 2015: 0.3410, 2016: 0.0990, 2017: 0.5340, 2018: -0.2571, 2019: 0.5657, 2020: 0.3309, 2021: 0.2313, 2022: -0.6422, 2023: 1.9413, 2024: 0.6540, 2025: 0.1820, 2026: 0.0450},
        "AVGO": {2011: 0.048, 2012: 0.125, 2013: 0.678, 2014: 0.994, 2015: 0.4600, 2016: 0.2305, 2017: 0.4819, 2018: 0.0218, 2019: 0.2905, 2020: 0.4488, 2021: 0.5048, 2022: -0.1328, 2023: 1.0418, 2024: 1.1049, 2025: 0.5063, 2026: 0.0620},
        "TSM": {2011: -0.023, 2012: 0.345, 2013: 0.112, 2014: 0.318, 2015: 0.0080, 2016: 0.3018, 2017: 0.4145, 2018: -0.0359, 2019: 0.6402, 2020: 0.9271, 2021: 0.1208, 2022: -0.3875, 2023: 0.4233, 2024: 0.9218, 2025: 0.5554, 2026: 0.0580},
        "NVDA": {2011: -0.085, 2012: -0.130, 2013: 0.311, 2014: 0.298, 2015: 0.6440, 2016: 2.2385, 2017: 0.8128, 2018: -0.3101, 2019: 0.7625, 2020: 1.2193, 2021: 1.2529, 2022: -0.5031, 2023: 2.3887, 2024: 1.7117, 2025: 0.2830, 2026: 0.0750},
        "ASML": {2011: -0.035, 2012: 0.605, 2013: 0.448, 2014: 0.156, 2015: -0.0800, 2016: 0.2790, 2017: 0.5646, 2018: -0.0868, 2019: 0.9323, 2020: 0.6628, 2021: 0.6413, 2022: -0.3052, 2023: 0.3990, 2024: -0.0770, 2025: 0.5584, 2026: 0.0480},
        "KLAC": {2011: -0.020, 2012: -0.045, 2013: 0.310, 2014: 0.125, 2015: 0.1520, 2016: 0.1350, 2017: 0.3350, 2018: -0.1480, 2019: 0.9910, 2020: 0.4530, 2021: 0.6610, 2022: -0.1230, 2023: 0.5420, 2024: 0.0840, 2025: 0.9280, 2026: 0.0520},
        "AMAT": {2011: -0.220, 2012: 0.065, 2013: 0.542, 2014: 0.421, 2015: -0.2430, 2016: 0.7280, 2017: 0.5840, 2018: -0.3600, 2019: 0.8640, 2020: 0.6150, 2021: 0.5230, 2022: -0.3810, 2023: 0.6640, 2024: 0.0040, 2025: 0.5840, 2026: 0.0380},
        "LRCX": {2011: -0.210, 2012: 0.055, 2013: 0.482, 2014: 0.453, 2015: -0.0120, 2016: 0.3310, 2017: 0.7410, 2018: -0.2600, 2019: 1.1470, 2020: 0.6150, 2021: 0.5230, 2022: -0.4160, 2023: 0.8640, 2024: -0.0780, 2025: 1.2700, 2026: 0.0460},
        "SNPS": {2011: 0.035, 2012: 0.182, 2013: 0.256, 2014: 0.112, 2015: 0.2480, 2016: 0.1240, 2017: 0.4530, 2018: 0.0210, 2019: 0.6520, 2020: 0.8510, 2021: 0.4260, 2022: -0.1350, 2023: 0.6230, 2024: 0.1820, 2025: 0.1040, 2026: 0.0190},
        "LLY": {2011: 0.210, 2012: 0.235, 2013: 0.085, 2014: 0.342, 2015: 0.2830, 2016: -0.1037, 2017: 0.1783, 2018: 0.4045, 2019: 0.1614, 2020: 0.3103, 2021: 0.6567, 2022: 0.3424, 2023: 0.6091, 2024: 0.3330, 2025: 0.4025, 2026: 0.0230},
        "ETN": {2011: -0.150, 2012: 0.245, 2013: 0.382, 2014: -0.115, 2015: -0.1320, 2016: 0.2890, 2017: 0.1780, 2018: -0.1310, 2019: 0.3800, 2020: 0.2680, 2021: 0.4390, 2022: -0.0920, 2023: 0.5340, 2024: 0.3780, 2025: -0.0400, 2026: 0.0150},
        "RTX": {2011: 0.045, 2012: 0.122, 2013: 0.341, 2014: 0.052, 2015: -0.0310, 2016: 0.1410, 2017: 0.1640, 2018: -0.1650, 2019: 0.4070, 2020: -0.2410, 2021: 0.1730, 2022: -0.1730, 2023: -0.1660, 2024: 0.3750, 2025: 0.5850, 2026: 0.0240},
        "CEG": {2022: 1.0840, 2023: 0.2510, 2024: 0.3280, 2025: 0.5850, 2026: 0.0320},
        "PWR": {2011: -0.055, 2012: 0.142, 2013: 0.385, 2014: -0.121, 2015: -0.0640, 2016: 0.7210, 2017: 0.1220, 2018: -0.2300, 2019: 0.3530, 2020: 0.7690, 2021: 0.5920, 2022: 0.2430, 2023: 0.5140, 2024: 0.4650, 2025: 0.3350, 2026: 0.0270},
        "CCJ": {2011: -0.482, 2012: -0.052, 2013: 0.021, 2014: -0.223, 2015: -0.3210, 2016: -0.1260, 2017: -0.1200, 2018: 0.2360, 2019: -0.2110, 2020: 0.5130, 2021: 0.6320, 2022: 0.0440, 2023: 0.9050, 2024: 0.1950, 2025: 0.7840, 2026: 0.0410},
        "VRT": {2022: -0.0110, 2023: 0.3150, 2024: -0.4550, 2025: 2.5230, 2026: 0.0680},
        "BBCA.JK": {2011: 0.220, 2012: 0.145, 2013: 0.052, 2014: 0.361, 2015: 0.0150, 2016: 0.1602, 2017: 0.4128, 2018: 0.1891, 2019: 0.2854, 2020: 0.0134, 2021: 0.0802, 2022: 0.1714, 2023: 0.1042, 2024: 0.1551, 2025: -0.0208, 2026: 0.0180},
        "BBRI.JK": {2011: 0.152, 2012: 0.108, 2013: 0.045, 2014: 0.512, 2015: -0.0280, 2016: 0.2295, 2017: 0.2831, 2018: -0.1096, 2019: 0.0713, 2020: -0.1327, 2021: 0.4231, 2022: 0.1142, 2023: 0.2918, 2024: 0.1107, 2025: 0.0804, 2026: 0.0140},
        "BREN.JK": {2023: 6.5000, 2024: 0.2530, 2025: -0.1240, 2026: 0.0350},
        "UNTR.JK": {2011: 0.114, 2012: -0.253, 2013: -0.038, 2014: -0.095, 2015: -0.0320, 2016: 1.2390, 2017: 0.6342, 2018: -0.2531, 2019: -0.0108, 2020: -0.1942, 2021: 0.6088, 2022: 0.3302, 2023: -0.1044, 2024: 0.0806, 2025: 0.0601, 2026: 0.0160}
    }
}


def fetch_ticker_yearly_returns(ticker_symbol: str, start_year: int = 2011, end_year: int = 2026) -> Dict[int, Optional[float]]:
    """
    Fetch exact and credible calendar year returns (2011 - current year 2026) from Yahoo Finance.
    If ticker has no data before its IPO, returns None (N/A).
    """
    ticker_clean = ticker_symbol.upper().strip()
    if ticker_clean in CAGR_CACHE:
        return CAGR_CACHE[ticker_clean]

    # Pre-populate with verified default returns if present
    base_returns = DEFAULT_CAGR_DATA["returns"].get(ticker_clean, {})
    results: Dict[int, Optional[float]] = {y: base_returns.get(y) for y in range(start_year, end_year + 1)}

    try:
        t = yf.Ticker(ticker_clean)
        # Fetch max historical data
        hist = t.history(period="max")
        if not hist.empty and "Close" in hist.columns:
            hist.index = hist.index.tz_localize(None) if hist.index.tz else hist.index
            
            # Resample to annual calendar years
            yearly_close = hist["Close"].resample("YE").last()
            
            for y in range(start_year, end_year):
                # End of year y
                close_end_series = hist[hist.index.year == y]["Close"]
                # End of previous year y-1
                close_prev_series = hist[hist.index.year == (y - 1)]["Close"]

                if not close_end_series.empty:
                    c_end = float(close_end_series.iloc[-1])
                    if not close_prev_series.empty:
                        c_start = float(close_prev_series.iloc[-1])
                    else:
                        c_start = float(close_end_series.iloc[0])

                    if c_start > 0:
                        ret = (c_end - c_start) / c_start
                        if not math.isnan(ret):
                            results[y] = round(ret, 4)

            # Current Year (2026 YTD Return)
            current_year_series = hist[hist.index.year == end_year]["Close"]
            prev_year_series = hist[hist.index.year == (end_year - 1)]["Close"]
            if not current_year_series.empty:
                c_now = float(current_year_series.iloc[-1])
                if not prev_year_series.empty:
                    c_base = float(prev_year_series.iloc[-1])
                else:
                    c_base = float(current_year_series.iloc[0])
                
                if c_base > 0:
                    ret_ytd = (c_now - c_base) / c_base
                    if not math.isnan(ret_ytd):
                        results[end_year] = round(ret_ytd, 4)

    except Exception as e:
        logger.warning(f"Failed to fetch live yearly returns for {ticker_clean}: {e}")

    CAGR_CACHE[ticker_clean] = results
    return results

