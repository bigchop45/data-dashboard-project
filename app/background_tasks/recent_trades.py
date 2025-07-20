import asyncio
import json
import websockets
from datetime import datetime
from termcolor import cprint
from app.services.managers import recent_trades_manager

# --- Configuration based on your script ---
USE_FUTURES = True
USD_THRESHOLD = 15000
SYMBOLS = ['btcusdt', 'ethusdt', 'solusdt', 'xrpusdt', 'dogeusdt']
WEBSOCKET_URL_BASE = 'wss://fstream.binance.com/ws/' if USE_FUTURES else 'wss://stream.binance.com:9443/ws/'

async def _trade_stream_for_symbol(symbol: str):
    """Private helper to handle the connection for a single symbol's trade stream."""
    stream_url = f"{WEBSOCKET_URL_BASE}{symbol}@aggTrade"

    while True:
        try:
            async with websockets.connect(stream_url) as websocket:
                cprint(f"BACKGROUND TASK: ✅ Connected to {symbol.upper()} trade stream", "green")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    price = float(data['p'])
                    quantity = float(data['q'])
                    usd_size = price * quantity

                    if usd_size >= USD_THRESHOLD:
                        is_buyer_maker = data['m']
                        
                        # Prepare the data packet for the frontend
                        trade_data_packet = {
                            "symbol": data['s'],
                            "side": "SELL" if is_buyer_maker else "BUY",
                            "price": price,
                            "quantity": quantity,
                            "usd_size": usd_size,
                            "trade_time_utc": datetime.fromtimestamp(int(data['T']) / 1000).isoformat(),
                        }
                        
                        # Broadcast the data
                        await recent_trades_manager.broadcast_json(trade_data_packet)
                        
                        # Log to server console
                        color = 'red' if trade_data_packet['side'] == 'SELL' else 'green'
                        cprint(f"BROADCAST: TRADE | {trade_data_packet['symbol']} | {trade_data_packet['side']} | ${trade_data_packet['usd_size']:,.0f}", color)

        except Exception as e:
            cprint(f"BACKGROUND TASK ERROR (Trades - {symbol.upper()}): {e}. Reconnecting...", "red")
            await asyncio.sleep(5)

async def run_recent_trades_feed():
    """The main background task that runs a trade stream for each symbol concurrently."""
    cprint("BACKGROUND TASK: Starting Recent Trades feeds...", "blue")
    
    tasks = [_trade_stream_for_symbol(symbol) for symbol in SYMBOLS]
    await asyncio.gather(*tasks)