import os
import io
import csv
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .database import (
    init_db,
    get_user_portfolio,
    update_user_settings,
    upsert_portfolio_item,
    delete_portfolio_item,
    get_monthly_records,
    get_available_years,
    create_year_records,
    upsert_monthly_record,
    get_user_liabilities,
    upsert_liability,
    delete_liability,
    get_user_theses,
    upsert_thesis,
    delete_thesis,
    get_tax_rules,
    get_user_appearance,
    update_user_appearance,
    get_user_watchlists,
    upsert_watchlist_item,
    delete_watchlist_item,
    get_saved_screens,
    upsert_saved_screen,
    delete_saved_screen,
    DEFAULT_PORTFOLIO_CONFIG
)
from .finance_engine import (
    compute_full_portfolio,
    get_macro_and_fx,
    fetch_ticker_market_data,
    compute_monte_carlo_simulation,
    compute_stress_test_scenarios,
    MARKET_CACHE
)
from .discover_engine import (
    scan_global_universe,
    get_thematic_discovery_data,
    get_single_asset_research,
    get_yahoo_finance_url
)

app = FastAPI(title="RADAR ASET 4.0 — Global Asset Scanner & Investment Intelligence Terminal")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup_event():
    init_db()


# Pydantic Schemas for API Validation
class AssetPayload(BaseModel):
    id: Optional[int] = None
    category: str
    ticker: str
    name: str
    currency: str = "USD"
    invested_idr: float = 0.0
    quantity: float = 0.0
    avg_price: float = 0.0
    is_lot: bool = False
    pe_great: Optional[float] = None
    pe_good: Optional[float] = None
    pe_exp: Optional[float] = None
    target_weight: Optional[float] = 0.0
    asset_class: Optional[str] = "EQUITY"
    geography: Optional[str] = "GLOBAL"
    sector: Optional[str] = "General"
    tax_category: Optional[str] = "FOREIGN_SECURITIES"


class SettingsPayload(BaseModel):
    target_financial_freedom: float
    total_outgoings: float
    cash_balance: float
    birth_year: Optional[int] = 1999
    target_retirement_age: Optional[int] = 45
    monthly_contribution: Optional[float] = 5000000.0
    contribution_growth: Optional[float] = 5.0
    inflation_rate: Optional[float] = 3.5
    expected_return: Optional[float] = 15.0
    volatility_assump: Optional[float] = 18.0
    withdrawal_rate: Optional[float] = 4.0
    risk_tolerance: Optional[str] = "MODERATE_AGGRESSIVE"


class AppearancePayload(BaseModel):
    selected_theme: Optional[str] = "terminal_dark"
    appearance_mode: Optional[str] = "dark"
    density: Optional[str] = "compact"
    investor_persona: Optional[str] = "BALANCED"


class MonthlyPayload(BaseModel):
    id: Optional[int] = None
    year: int = 2026
    month_index: int
    month_name: str
    total_outgoings: float = 0.0
    current_networth: float = 0.0
    investing_power: float = 0.0
    growth_pct: float = 0.0
    notes: Optional[str] = ""


class LiabilityPayload(BaseModel):
    id: Optional[int] = None
    name: str
    type: str = "MORTGAGE"
    balance_idr: float = 0.0
    interest_rate_pct: float = 0.0
    monthly_payment_idr: float = 0.0
    remaining_term_months: int = 0
    notes: Optional[str] = ""


class ThesisPayload(BaseModel):
    id: Optional[int] = None
    ticker: str
    thesis: str
    catalysts: str
    risks: str
    invalidation: Optional[str] = ""
    status: str = "INTACT"
    review_date: Optional[str] = ""


class WatchlistPayload(BaseModel):
    id: Optional[int] = None
    ticker: str
    name: str
    target_price: float = 0.0
    alert_conditions_json: Optional[str] = "{}"
    notes: Optional[str] = ""


class SavedScreenPayload(BaseModel):
    id: Optional[int] = None
    name: str
    filters_json: str = "{}"
    description: Optional[str] = ""


# Web Pages
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: str = "default_user", year: int = 2026):
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    years = get_available_years(user_id)
    if year not in years:
        year = years[-1] if years else 2026
    monthly = get_monthly_records(user_id, year=year)
    theses = get_user_theses(user_id)
    liabilities = get_user_liabilities(user_id)
    tax_rules = get_tax_rules()
    appearance = get_user_appearance(user_id)
    watchlists = get_user_watchlists(user_id)
    saved_screens = get_saved_screens(user_id)

    # Discovered assets & themes for Discover Workspace
    discovered_universe = scan_global_universe(
        user_holdings=portfolio.get("all_holdings", []),
        total_val_idr=portfolio.get("current_value_investment_idr", 0.0)
    )
    themes_data = get_thematic_discovery_data()

    # Net Worth calculation: Total Investable + Cash + Property - Liabilities
    total_liabilities_idr = sum(float(l.get("balance_idr", 0.0)) for l in liabilities)
    true_net_worth_idr = portfolio["current_net_worth_idr"] - total_liabilities_idr

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "portfolio": portfolio,
            "monthly": monthly,
            "available_years": years,
            "current_year": year,
            "theses": theses,
            "liabilities": liabilities,
            "tax_rules": tax_rules,
            "appearance": appearance,
            "watchlists": watchlists,
            "saved_screens": saved_screens,
            "discovered_universe": discovered_universe,
            "themes_data": themes_data,
            "total_liabilities_idr": total_liabilities_idr,
            "true_net_worth_idr": true_net_worth_idr,
            "user_id": user_id
        }
    )


# API Endpoints
@app.get("/api/portfolio")
async def api_get_portfolio(user_id: str = "default_user"):
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content=portfolio)


@app.post("/api/refresh")
async def api_refresh_data(user_id: str = "default_user"):
    MARKET_CACHE.clear()
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


# DISCOVER ENDPOINTS
@app.get("/api/discover/universe")
async def api_discover_universe(
    user_id: str = "default_user",
    market: str = "ALL",
    asset_type: str = "ALL",
    style: str = "ALL",
    q: str = ""
):
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    results = scan_global_universe(
        user_holdings=portfolio.get("all_holdings", []),
        total_val_idr=portfolio.get("current_value_investment_idr", 0.0),
        filter_market=market,
        filter_type=asset_type,
        filter_style=style,
        search_query=q
    )
    return JSONResponse(content={"status": "success", "count": len(results), "items": results})


@app.get("/api/discover/themes")
async def api_discover_themes():
    themes = get_thematic_discovery_data()
    return JSONResponse(content={"status": "success", "themes": themes})


@app.get("/api/discover/asset/{ticker}")
async def api_discover_single_asset(ticker: str, user_id: str = "default_user"):
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    asset_data = get_single_asset_research(
        ticker_symbol=ticker,
        user_holdings=portfolio.get("all_holdings", []),
        total_val_idr=portfolio.get("current_value_investment_idr", 0.0)
    )
    if not asset_data:
        raise HTTPException(status_code=404, detail="Asset not found in global universe")
    return JSONResponse(content={"status": "success", "asset": asset_data})


# Signature Feature: Full Portfolio Scan
@app.post("/api/radar/scan")
async def api_radar_scan(user_id: str = "default_user"):
    MARKET_CACHE.clear()
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    scan_result = {
        "timestamp": os.getenv("CURRENT_TIME", "2026-08-25"),
        "health": portfolio["health"],
        "ai_risk": portfolio["ai_risk"],
        "top_priorities": portfolio["top_priorities"],
        "lookthrough": portfolio["lookthrough"],
        "rebalancing": portfolio["rebalancing"],
        "stress_scenarios": portfolio["stress_scenarios"],
        "monte_carlo_prob": portfolio["monte_carlo"]["probability_reaching_target_pct"],
        "data_quality_score": portfolio["health"]["data_quality_score"]
    }
    return JSONResponse(content={"status": "success", "scan": scan_result, "portfolio": portfolio})


@app.post("/api/assets/upsert")
async def api_upsert_asset(payload: AssetPayload, user_id: str = "default_user"):
    upsert_portfolio_item(user_id, payload.dict())
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


@app.delete("/api/assets/{asset_id}")
async def api_delete_asset(asset_id: int, user_id: str = "default_user"):
    delete_portfolio_item(user_id, asset_id)
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


@app.post("/api/settings")
async def api_update_settings(payload: SettingsPayload, user_id: str = "default_user"):
    update_user_settings(
        user_id=user_id,
        target_ff=payload.target_financial_freedom,
        total_outgoings=payload.total_outgoings,
        cash_balance=payload.cash_balance,
        birth_year=payload.birth_year,
        target_retirement_age=payload.target_retirement_age,
        monthly_contribution=payload.monthly_contribution,
        contribution_growth=payload.contribution_growth,
        inflation_rate=payload.inflation_rate,
        expected_return=payload.expected_return,
        volatility_assump=payload.volatility_assump,
        withdrawal_rate=payload.withdrawal_rate,
        risk_tolerance=payload.risk_tolerance
    )
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


@app.post("/api/settings/appearance")
async def api_update_appearance(payload: AppearancePayload, user_id: str = "default_user"):
    update_user_appearance(
        user_id=user_id,
        selected_theme=payload.selected_theme,
        appearance_mode=payload.appearance_mode,
        density=payload.density,
        investor_persona=payload.investor_persona
    )
    appearance = get_user_appearance(user_id)
    return JSONResponse(content={"status": "success", "appearance": appearance})


# Monthly Tracking APIs
@app.get("/api/monthly")
async def api_get_monthly(user_id: str = "default_user", year: int = 2026):
    records = get_monthly_records(user_id, year)
    return JSONResponse(content=records)


@app.get("/api/monthly/years")
async def api_get_monthly_years(user_id: str = "default_user"):
    years = get_available_years(user_id)
    return JSONResponse(content=years)


@app.post("/api/monthly/add-year/{year}")
async def api_add_monthly_year(year: int, user_id: str = "default_user"):
    create_year_records(user_id, year)
    years = get_available_years(user_id)
    records = get_monthly_records(user_id, year)
    return JSONResponse(content={"status": "success", "years": years, "records": records})


@app.post("/api/monthly/upsert")
async def api_upsert_monthly(payload: MonthlyPayload, user_id: str = "default_user"):
    upsert_monthly_record(user_id, payload.dict())
    records = get_monthly_records(user_id, payload.year)
    return JSONResponse(content={"status": "success", "data": records})


# Liabilities APIs
@app.get("/api/liabilities")
async def api_get_liabilities(user_id: str = "default_user"):
    liabilities = get_user_liabilities(user_id)
    return JSONResponse(content=liabilities)


@app.post("/api/liabilities/upsert")
async def api_upsert_liability(payload: LiabilityPayload, user_id: str = "default_user"):
    upsert_liability(user_id, payload.dict())
    liabilities = get_user_liabilities(user_id)
    return JSONResponse(content={"status": "success", "data": liabilities})


@app.delete("/api/liabilities/{item_id}")
async def api_delete_liability(item_id: int, user_id: str = "default_user"):
    delete_liability(user_id, item_id)
    liabilities = get_user_liabilities(user_id)
    return JSONResponse(content={"status": "success", "data": liabilities})


# Investment Theses APIs
@app.get("/api/theses")
async def api_get_theses(user_id: str = "default_user"):
    theses = get_user_theses(user_id)
    return JSONResponse(content=theses)


@app.post("/api/theses/upsert")
async def api_upsert_thesis(payload: ThesisPayload, user_id: str = "default_user"):
    upsert_thesis(user_id, payload.dict())
    theses = get_user_theses(user_id)
    return JSONResponse(content={"status": "success", "data": theses})


@app.delete("/api/theses/{thesis_id}")
async def api_delete_thesis(thesis_id: int, user_id: str = "default_user"):
    delete_thesis(user_id, thesis_id)
    theses = get_user_theses(user_id)
    return JSONResponse(content={"status": "success", "data": theses})


# Watchlist APIs
@app.get("/api/watchlists")
async def api_get_watchlists(user_id: str = "default_user"):
    watchlists = get_user_watchlists(user_id)
    return JSONResponse(content=watchlists)


@app.post("/api/watchlists/upsert")
async def api_upsert_watchlist(payload: WatchlistPayload, user_id: str = "default_user"):
    upsert_watchlist_item(user_id, payload.dict())
    watchlists = get_user_watchlists(user_id)
    return JSONResponse(content={"status": "success", "data": watchlists})


@app.delete("/api/watchlists/{item_id}")
async def api_delete_watchlist(item_id: int, user_id: str = "default_user"):
    delete_watchlist_item(user_id, item_id)
    watchlists = get_user_watchlists(user_id)
    return JSONResponse(content={"status": "success", "data": watchlists})


# Saved Screens APIs
@app.get("/api/screens")
async def api_get_saved_screens(user_id: str = "default_user"):
    screens = get_saved_screens(user_id)
    return JSONResponse(content=screens)


@app.post("/api/screens/upsert")
async def api_upsert_saved_screen(payload: SavedScreenPayload, user_id: str = "default_user"):
    upsert_saved_screen(user_id, payload.dict())
    screens = get_saved_screens(user_id)
    return JSONResponse(content={"status": "success", "data": screens})


@app.delete("/api/screens/{screen_id}")
async def api_delete_saved_screen(screen_id: int, user_id: str = "default_user"):
    delete_saved_screen(user_id, screen_id)
    screens = get_saved_screens(user_id)
    return JSONResponse(content={"status": "success", "data": screens})


# Tax Rules API
@app.get("/api/tax/rules")
async def api_get_tax_rules():
    rules = get_tax_rules()
    return JSONResponse(content=rules)


# CSV Data Export Endpoint
@app.get("/api/export/csv")
async def api_export_csv(user_id: str = "default_user"):
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Category", "Ticker", "Name", "Currency", "Quantity", "Avg Price", "Current Price", "Invested IDR", "Current Value IDR", "PnL IDR", "PnL %", "Dislocation Zone", "PE", "Yahoo Finance Link"])
    for cat in portfolio["categories"]:
        for item in cat["items"]:
            writer.writerow([
                cat["name"], item["ticker"], item["name"], item["currency"],
                item["quantity"], item["avg_price"], item["current_price"],
                item["invested_idr"], item["cur_val_idr"], item["pnl_idr"], item["pnl_pct"],
                item["status_label"], item.get("pe", "N/A"), get_yahoo_finance_url(item["ticker"])
            ])
            
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=radar_aset_portfolio.csv"}
    )
