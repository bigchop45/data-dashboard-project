from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from termcolor import cprint

from app.core.config import settings
from app.routers import websockets as websocket_router

# Import all background task functions
from app.background_tasks.liquidations_feed import run_liquidations_feed
from app.background_tasks.big_liquidations import run_big_liquidations_feed
from app.background_tasks.recent_trades import run_recent_trades_feed
from app.background_tasks.recent_trades_halfmil import run_recent_trades_halfmil_feed
from app.background_tasks.funding_rates_feed import run_funding_rates_feed
from app.background_tasks.price_ticker_feed import run_price_ticker_feed
from app.background_tasks.fear_and_greed_feed import run_fear_and_greed_feed

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """On server startup, launch all background tasks."""
    cprint("SERVER STARTUP: Launching all background tasks...", "blue")
    
    asyncio.create_task(run_liquidations_feed())
    asyncio.create_task(run_big_liquidations_feed())
    asyncio.create_task(run_recent_trades_feed())
    asyncio.create_task(run_recent_trades_halfmil_feed())
    asyncio.create_task(run_funding_rates_feed())
    asyncio.create_task(run_price_ticker_feed())
    asyncio.create_task(run_fear_and_greed_feed())

app.include_router(websocket_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "API is running. Connect to WebSocket endpoints under /ws."}