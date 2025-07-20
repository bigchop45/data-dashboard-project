import asyncio
import json
import websockets
import time
from termcolor import cprint
from app.services.managers import funding_rates_manager

# --- Configuration ---
SYMBOLS = ['btcusdt', 'ethusdt', 'solusdt', 'xrpusdt', 'dogeusdt', 'xlmusdt', 'virtualusdt']
WEBSOCKET_URL_BASE = 'wss://fstream.binance.com/ws/'
BROADCAST_INTERVAL = 60 # seconds

async def _funding_stream_for_symbol(symbol: str):
    """Connects to a symbol's markPrice stream and broadcasts the funding rate periodically."""
    url = f'{WEBSOCKET_URL_BASE}{symbol}@markPrice'
    last_broadcast_time = 0
    
    while True:
        try:
            async with websockets.connect(url) as ws:
                cprint(f"BACKGROUND TASK: ✅ Connected to {symbol.upper()} funding stream", "green")
                while True:
                    data = json.loads(await ws.recv())
                    if data.get('e') != 'markPriceUpdate':
                        continue
                    
                    current_time = time.time()
                    if (current_time - last_broadcast_time) > BROADCAST_INTERVAL:
                        rate_str = data.get('r')
                        if rate_str is not None:
                            rate = float(rate_str)
                            # Send the 8-hour funding rate as a percentage.
                            packet = {
                                "symbol": data.get('s'),
                                "daily_rate_percent": rate * 100 
                            }
                            await funding_rates_manager.broadcast_json(packet)
                            last_broadcast_time = current_time # Reset timer
                            # Optional: Log the broadcast to the server console
                            cprint(f"BROADCAST (60s): FR | {packet['symbol']} | 8-Hour Rate: {packet['daily_rate_percent']:.4f}%", "cyan")

        except Exception as e:
            cprint(f"BACKGROUND TASK ERROR (Funding - {symbol.upper()}): {e}. Reconnecting...", "red")
            await asyncio.sleep(5)

async def run_funding_rates_feed():
    """The main background task that runs a funding rate stream for each symbol concurrently."""
    cprint("BACKGROUND TASK: Starting all Funding Rate feeds (from Binance WebSocket)...", "blue")
    tasks = [_funding_stream_for_symbol(s) for s in SYMBOLS]
    await asyncio.gather(*tasks)
