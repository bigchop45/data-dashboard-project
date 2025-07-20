import asyncio
import json
import websockets
from termcolor import cprint
from app.services.managers import price_ticker_manager

# --- Configuration ---
SYMBOLS = ['btcusdt', 'ethusdt', 'solusdt', 'xrpusdt', 'dogeusdt', 'xlmusdt', 'virtualusdt']
WEBSOCKET_URL_BASE = 'wss://fstream.binance.com/ws/'

async def _price_stream_for_symbol(symbol: str):
    """Connects to a symbol's 24hr ticker stream."""
    url = f'{WEBSOCKET_URL_BASE}{symbol}@ticker'
    while True:
        try:
            async with websockets.connect(url) as ws:
                cprint(f"BACKGROUND TASK: ✅ Connected to {symbol.upper()} ticker stream", "green")
                while True:
                    data = json.loads(await ws.recv())
                    if data.get('e') != '24hrTicker': continue
                    
                    packet = {
                        "symbol": data['s'],
                        "price": float(data['c']),
                        "change_percent": float(data['P'])
                    }
                    
                    await price_ticker_manager.broadcast_json(packet)
        except Exception as e:
            cprint(f"BACKGROUND TASK ERROR (Ticker - {symbol.upper()}): {e}. Reconnecting...", "red")
            await asyncio.sleep(5)

async def run_price_ticker_feed():
    """The main background task that runs a price ticker stream for each symbol concurrently."""
    cprint("BACKGROUND TASK: Starting all Price Ticker feeds...", "blue")
    tasks = [_price_stream_for_symbol(s) for s in SYMBOLS]
    await asyncio.gather(*tasks)