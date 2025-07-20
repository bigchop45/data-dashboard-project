from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.managers import (
    ConnectionManager, 
    regular_liquidations_manager,
    whale_liquidations_manager,
    recent_trades_manager,
    recent_trades_halfmil_manager,
    funding_rates_manager,
    price_ticker_manager,
    fear_and_greed_manager
)
from termcolor import cprint

router = APIRouter(prefix="/ws", tags=["WebSockets"])

async def websocket_handler(websocket: WebSocket, manager: ConnectionManager, feed_name: str):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        cprint(f"CLIENT DISCONNECT: A client disconnected from the {feed_name} feed.", "yellow")

@router.websocket("/regular-liquidations")
async def websocket_regular_liquidations_endpoint(websocket: WebSocket):
    await websocket_handler(websocket, regular_liquidations_manager, "Regular Liquidations")

@router.websocket("/whale-liquidations")
async def websocket_whale_liquidations_endpoint(websocket: WebSocket):
    await websocket_handler(websocket, whale_liquidations_manager, "Whale Liquidations")

@router.websocket("/recent-trades")
async def websocket_recent_trades_endpoint(websocket: WebSocket):
    await websocket_handler(websocket, recent_trades_manager, "Recent Trades")

@router.websocket("/recent-trades-halfmil")
async def websocket_recent_trades_halfmil_endpoint(websocket: WebSocket):
    await websocket_handler(websocket, recent_trades_halfmil_manager, "Large Trades")

@router.websocket("/funding-rates")
async def websocket_funding_rates_endpoint(websocket: WebSocket):
    await websocket_handler(websocket, funding_rates_manager, "Funding Rates")

@router.websocket("/price-ticker")
async def websocket_price_ticker_endpoint(websocket: WebSocket):
    await websocket_handler(websocket, price_ticker_manager, "Price Ticker")

@router.websocket("/fear-and-greed")
async def websocket_fear_and_greed_endpoint(websocket: WebSocket):
    await websocket_handler(websocket, fear_and_greed_manager, "Fear & Greed")