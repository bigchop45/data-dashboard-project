from fastapi import WebSocket
from typing import List

class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.last_known_data: Optional[Dict[str, Any]] = None # To store state

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        if self.last_known_data:
            await websocket.send_json(self.last_known_data)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_json(self, data: dict):
        """Broadcasts a JSON message and updates the last known state."""
        self.last_known_data = data
        for connection in self.active_connections:
            await connection.send_json(data)

# --- Create a manager instance for EACH of your data feeds ---
regular_liquidations_manager = ConnectionManager()
whale_liquidations_manager = ConnectionManager()
recent_trades_manager = ConnectionManager()
recent_trades_halfmil_manager = ConnectionManager()
funding_rates_manager = ConnectionManager()
price_ticker_manager = ConnectionManager()
fear_and_greed_manager = ConnectionManager()
