import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .database import (
    init_db,
    get_user_portfolio,
    update_user_settings,
    upsert_portfolio_item,
    delete_portfolio_item,
    move_portfolio_item,
    reorder_portfolio_items,
    get_monthly_records,
    get_available_years,
    create_year_records,
    upsert_monthly_record,
    get_user_categories,
    upsert_category,
    delete_category,
    reorder_categories,
    DEFAULT_PORTFOLIO_CONFIG
)
from .finance_engine import (
    compute_full_portfolio,
    get_macro_and_fx,
    fetch_ticker_market_data,
    get_asset_logo_url,
    MARKET_CACHE
)

app = FastAPI(title="Core-Satellite Portfolio & Financial Freedom Tracker")

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


# Pydantic Schemas for API
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


class CategoryPayload(BaseModel):
    id: str
    name: str
    subtitle: Optional[str] = ""
    color: Optional[str] = "blue"
    sort_order: Optional[int] = 0


class SettingsPayload(BaseModel):
    target_financial_freedom: float
    total_outgoings: float
    cash_balance: float


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


# Web Pages
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: str = "default_user", year: int = 2026):
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    years = get_available_years(user_id)
    if year not in years:
        year = years[-1] if years else 2026
    monthly = get_monthly_records(user_id, year=year)
    categories = get_user_categories(user_id)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "portfolio": portfolio,
            "monthly": monthly,
            "available_years": years,
            "current_year": year,
            "categories": categories,
            "user_id": user_id
        }
    )


# API Endpoints for Realtime Interaction
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


# Category Management APIs
@app.get("/api/categories")
async def api_get_categories(user_id: str = "default_user"):
    categories = get_user_categories(user_id)
    return JSONResponse(content=categories)


@app.post("/api/categories/upsert")
async def api_upsert_category(payload: CategoryPayload, user_id: str = "default_user"):
    upsert_category(user_id, payload.dict())
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    categories = get_user_categories(user_id)
    return JSONResponse(content={"status": "success", "portfolio": portfolio, "categories": categories})


@app.delete("/api/categories/{category_id}")
async def api_delete_category(category_id: str, user_id: str = "default_user"):
    delete_category(user_id, category_id)
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    categories = get_user_categories(user_id)
    return JSONResponse(content={"status": "success", "portfolio": portfolio, "categories": categories})


class ReorderCategoriesPayload(BaseModel):
    categories: List[Dict[str, Any]]


@app.post("/api/categories/reorder")
async def api_reorder_categories(payload: ReorderCategoriesPayload, user_id: str = "default_user"):
    reorder_categories(user_id, payload.categories)
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    categories = get_user_categories(user_id)
    return JSONResponse(content={"status": "success", "portfolio": portfolio, "categories": categories})


class MoveAssetPayload(BaseModel):
    item_id: int
    target_category: str
    target_sort_order: Optional[int] = 0


class ReorderAssetsPayload(BaseModel):
    items: List[Dict[str, Any]]


# Asset Management APIs
@app.post("/api/assets/upsert")
async def api_upsert_asset(payload: AssetPayload, user_id: str = "default_user"):
    p_dict = payload.dict()
    p_dict["ticker"] = (p_dict.get("ticker") or "").strip().upper()
    upsert_portfolio_item(user_id, p_dict)
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


@app.post("/api/assets/move")
async def api_move_asset(payload: MoveAssetPayload, user_id: str = "default_user"):
    move_portfolio_item(user_id, payload.item_id, payload.target_category, payload.target_sort_order or 0)
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


@app.post("/api/assets/reorder")
async def api_reorder_assets(payload: ReorderAssetsPayload, user_id: str = "default_user"):
    reorder_portfolio_items(user_id, payload.items)
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
        cash_balance=payload.cash_balance
    )
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


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


@app.get("/api/ticker/lookup/{ticker}")
async def api_lookup_ticker(ticker: str):
    data = fetch_ticker_market_data(ticker.upper())
    return JSONResponse(content=data)
