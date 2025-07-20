import asyncio
import json
import websockets
from datetime import datetime, timezone
from termcolor import cprint
from app.services.managers import recent_trades_halfmil_manager

# --- Configuration ---
USE_FUTURES = True
USD_THRESHOLD = 500000
SYMBOLS = ['btcusdt', 'ethusdt', 'solusdt', 'xrpusdt', 'dogeusdt']
WEBSOCKET_URL_BASE = 'wss://fstream.binance.com/ws/' if USE_FUTURES else 'wss://stream.binance.com:9443/ws/'

# --- Trade Aggregator Class ---
class TradeAggregator:
    def __init__(self):
        # Buckets to hold aggregated USD size per symbol, per second, per side
        self.trade_buckets = {}

    def add_trade(self, data):
        """Adds a new trade to the appropriate bucket."""
        try:
            price = float(data['p'])
            quantity = float(data['q'])
            usd_size = price * quantity
            
            # Key: (symbol, second_of_the_minute, side)
            trade_time = datetime.fromtimestamp(data['T'] / 1000, tz=timezone.utc)
            second = trade_time.strftime('%H:%M:%S')
            side = "SELL" if data['m'] else "BUY"
            symbol = data['s']
            
            trade_key = (symbol, second, side)
            
            # Add the trade's USD size to the bucket
            self.trade_buckets[trade_key] = self.trade_buckets.get(trade_key, 0) + usd_size
        except (KeyError, ValueError) as e:
            cprint(f"AGGREGATOR ERROR: Could not process trade data: {e}", "yellow")

    async def check_and_broadcast(self):
        """Checks buckets for aggregated trades exceeding the threshold and broadcasts them."""
        # Use a copy of keys to allow modification during iteration
        for trade_key in list(self.trade_buckets.keys()):
            usd_size = self.trade_buckets[trade_key]
            
            if usd_size >= USD_THRESHOLD:
                symbol, second, side = trade_key
                
                # Prepare data packet for the frontend
                aggregated_trade_packet = {
                    "symbol": symbol,
                    "side": side,
                    "usd_size": usd_size,
                    "time_bucket": second
                }
                
                await recent_trades_halfmil_manager.broadcast_json(aggregated_trade_packet)
                
                cprint(f"BROADCAST: LARGE AGG TRADE | {symbol} | {side} | ${usd_size:,.0f}", "magenta")
                
                # Remove the bucket after broadcasting
                del self.trade_buckets[trade_key]
                
    def clear_old_buckets(self):
        """Periodically clears out old buckets to prevent memory leaks."""
        current_minute = datetime.now(timezone.utc).minute
        # Clear buckets that are more than 2 minutes old
        for key in list(self.trade_buckets.keys()):
            try:
                bucket_time_str = key[1]
                bucket_minute = int(bucket_time_str.split(':')[1])
                if (current_minute - bucket_minute) % 60 > 2:
                    del self.trade_buckets[key]
            except (IndexError, ValueError):
                # If key is malformed, remove it
                del self.trade_buckets[key]


# --- WebSocket Connection Logic ---
async def _trade_stream_for_aggregator(symbol: str, aggregator: TradeAggregator):
    """Connects to a symbol's stream and passes data to the aggregator."""
    stream_url = f"{WEBSOCKET_URL_BASE}{symbol}@aggTrade"
    while True:
        try:
            async with websockets.connect(stream_url) as websocket:
                cprint(f"BACKGROUND TASK: ✅ Connected to {symbol.upper()} for Large Trade Aggregation", "green")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    aggregator.add_trade(data)
        except Exception as e:
            cprint(f"BACKGROUND TASK ERROR (Large Trades - {symbol.upper()}): {e}. Reconnecting...", "red")
            await asyncio.sleep(5)

async def _aggregator_processor(aggregator: TradeAggregator):
    """Task that runs every second to process and broadcast aggregated trades."""
    clear_interval = 0
    while True:
        await asyncio.sleep(1)
        await aggregator.check_and_broadcast()
        
        clear_interval += 1
        if clear_interval >= 60: # Clear old buckets every minute
            aggregator.clear_old_buckets()
            clear_interval = 0


# --- Main Background Task Entry Point ---
async def run_recent_trades_halfmil_feed():
    """The main background task that sets up the aggregator and all symbol streams."""
    cprint("BACKGROUND TASK: Starting Large Aggregated Trades feed...", "blue")
    
    trade_aggregator = TradeAggregator()
    
    # Create a listener task for each symbol
    listener_tasks = [_trade_stream_for_aggregator(symbol, trade_aggregator) for symbol in SYMBOLS]
    
    # Create a single processor task
    processor_task = asyncio.create_task(_aggregator_processor(trade_aggregator))
    
    # Run all listener tasks and the processor task concurrently
    await asyncio.gather(*listener_tasks, processor_task)
