import asyncio
import httpx
from termcolor import cprint
from app.services.managers import fear_and_greed_manager

# --- Configuration ---
API_URL = "https://api.alternative.me/fng/"
FETCH_INTERVAL = 180 # Updated to 3 minutes

async def run_fear_and_greed_feed():
    """Periodically fetches and broadcasts the Crypto Fear & Greed Index."""
    cprint("BACKGROUND TASK: Starting Fear & Greed Index feed...", "blue")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(API_URL)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and 'data' in data and len(data['data']) > 0:
                        index_data = data['data'][0]
                        
                        packet = {
                            "value": int(index_data['value']),
                            "classification": index_data['value_classification']
                        }
                        
                        await fear_and_greed_manager.broadcast_json(packet)
                        cprint(f"BROADCAST: F&G Index | {packet['value']} ({packet['classification']})", "yellow")
                else:
                    cprint(f"BACKGROUND TASK ERROR (F&G): API returned status {response.status_code}", "red")

            except Exception as e:
                cprint(f"BACKGROUND TASK ERROR (F&G): An unexpected error occurred: {e}", "red")
            
            await asyncio.sleep(FETCH_INTERVAL)