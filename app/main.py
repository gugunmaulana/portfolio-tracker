import os
from typing import Dict, Any, Optional
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
    DEFAULT_PORTFOLIO_CONFIG
)
from .finance_engine import (
    compute_full_portfolio,
    get_macro_and_fx,
    fetch_ticker_market_data,
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


class SettingsPayload(BaseModel):
    target_financial_freedom: float
    total_outgoings: float
    cash_balance: float


# Web Pages
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: str = "default_user"):
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "portfolio": portfolio,
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
    # Clear cache to force fresh Yahoo Finance fetch
    MARKET_CACHE.clear()
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


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
        cash_balance=payload.cash_balance
    )
    user_raw = get_user_portfolio(user_id)
    portfolio = compute_full_portfolio(user_raw)
    return JSONResponse(content={"status": "success", "data": portfolio})


@app.get("/api/ticker/lookup/{ticker}")
async def api_lookup_ticker(ticker: str):
    data = fetch_ticker_market_data(ticker.upper())
    return JSONResponse(content=data)
