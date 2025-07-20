import asyncio
import json
import websockets
from termcolor import cprint
from app.services.managers import regular_liquidations_manager # Uses the REGULAR manager

# --- Configuration ---
USE_FUTURES = True
WEBSOCKET_URL_BASE = 'wss://fstream.binance.com/ws/' if USE_FUTURES else 'wss://stream.binance.com:9443/ws/'
TARGET_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT'] 
USD_THRESHOLD_DISPLAY = 1000

async def run_liquidations_feed():
    """Connects to Binance and broadcasts all liquidations above a small threshold."""
    full_websocket_url = f'{WEBSOCKET_URL_BASE}!forceOrder@arr'
    cprint("BACKGROUND TASK: Starting Regular Liquidations feed...", "cyan")

    while True:
        try:
            async with websockets.connect(full_websocket_url) as websocket:
                cprint("BACKGROUND TASK: ✅ Regular Liquidations feed connected.", "green")
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    if data.get('e') != 'forceOrder' or 'o' not in data: continue
                    order_data = data['o']
                    if order_data['s'] not in TARGET_SYMBOLS: continue
                    price = float(order_data['p'])
                    filled_quantity = float(order_data['z'])
                    usd_size = filled_quantity * price
                    if usd_size >= USD_THRESHOLD_DISPLAY:
                        packet = {"symbol": order_data['s'], "side": order_data['S'], "usd_size": usd_size}
                        await regular_liquidations_manager.broadcast_json(packet)
                        cprint(f"BROADCAST: REG LIQ | {packet['symbol']} | ${packet['usd_size']:,.0f}", "yellow")
        except Exception as e:
            cprint(f"BACKGROUND TASK ERROR (Regular Liqs): {e}. Reconnecting...", "red")
            await asyncio.sleep(5)
