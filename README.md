# Real-Time Crypto Data Dashboard

This project is a comprehensive, real-time cryptocurrency data dashboard. It features a Python backend powered by FastAPI that streams live market data from various sources via WebSockets. The frontend is a dynamic, single-page application built with HTML, Tailwind CSS, and vanilla JavaScript, featuring a customizable grid layout for displaying multiple data feeds simultaneously.

---

## Features

* **Live Data Feeds:** Real-time updates for prices, trades, liquidations, and funding rates.
* **Multiple Panels:** A multi-panel display showing:
    * Regular & Whale-Sized Liquidations
    * Recent & Large Aggregated Trades
    * Live Prices & 24h Change
    * Funding Rates
    * Fear & Greed Index
    * Global Trading Session Clock
* **Interactive UI:** Draggable and resizable panels powered by GridStack.js.
* **High-Performance Backend:** Built with modern, asynchronous Python using FastAPI.

---

## Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, WebSockets
* **Frontend:** HTML, JavaScript, Tailwind CSS, GridStack.js
* **Data Sources:** Binance WebSockets, various public APIs (CryptoCompare, etc.)
* **Environment:** Conda

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd data-dashboard-project

2. Create the Conda EnvironmentEnsure you have Anaconda or Miniconda installed. Then, create the environment from the environment.yml file:conda env create -f environment.yml

3. Set Up Environment VariablesCreate a .env file in the root of the project directory. This file is used to store your secret API keys and is ignored by Git. Add your keys to this file:
# Example for CryptoCompare API Key
CRYPTOCOMPARE_API_KEY="YOUR_API_KEY_HERE"

Running the Application

Activate the Conda Environment:conda activate data-dashboard
Start the Backend Server:
Run the Uvicorn server from the project's root directory. The --reload flag will automatically restart the server when you make code changes.uvicorn app.main:app --reload
The API will be running at http://127.0.0.1:8000.Launch the Frontend:Open the frontend.html or dashboard.html file directly in your web browser (e.g., by double-clicking it or using the "Open File" menu in your browser).

Adding New Data FeedsThe project is designed to be easily extensible.
To add a new live data feed, follow these five steps:Step 1: Create a Connection ManagerFile: app/services/managers.pyAction:

Add a newConnectionManager instance for your new feed.

Example:# In app/services/managers.py
new_feature_manager = ConnectionManager()

Step 2: Create the Background TaskFile: Create a new file in the app/background_tasks/ directory (e.g., new_feature_feed.py).Action: Write the Python logic to fetch your data in a continuous loop.

Import the new manager you created and use await new_feature_manager.broadcast_json(data_packet) to send data to the frontend.Example:# In app/background_tasks/new_feature_feed.py

from app.services.managers import new_feature_manager

async def run_new_feature_feed():
    # Your logic to get data...
    # await new_feature_manager.broadcast_json(packet)
    pass # Placeholder
Step 3: Add a WebSocket EndpointFile: app/routers/websockets.pyAction: Import your new manager and create a new WebSocket endpoint that connects it to a URL path.Example:# In app/routers/websockets.py
# Add new_feature_manager to the import list

@router.websocket("/new-feature")
async def websocket_new_feature_endpoint(websocket: WebSocket):
    await websocket_handler(websocket, new_feature_manager, "New Feature")
Step 4: Launch the New TaskFile: app/main.pyAction: Import your new background task function and add it to the startup_event function.Example:# In app/main.py
from app.background_tasks.new_feature_feed import run_new_feature_feed

# Inside the startup_event function:
asyncio.create_task(run_new_feature_feed())
Step 5: Add the Panel to the FrontendFile: frontend.html or dashboard.htmlAction:Copy and paste an existing grid-stack-item <div> to create a new panel. Change the title and id attributes.In the <script> tag at the bottom, add a new setupWebSocket() call to connect your new panel to the WebSocket endpoint you created.Example:<!-- In the HTML body -->
<div class="grid-stack-item" gs-x="0" gs-y="18" gs-w="4" gs-h="4">
    <div class="grid-stack-item-content">
        <header class="p-3 border-b border-gray-800">
            <h2 class="text-base font-bold text-pink-400">New Feature</h2>
            <div id="status-new-feature" class="mt-1">...</div>
        </header>
        <div id="feed-new-feature" class="p-3"></div>
    </div>
</div>

<!-- In the script tag -->
<script>
    // ...
    setupWebSocket('new-feature', 'new-feature');
</script>
