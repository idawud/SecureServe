'''
Docstring for reference-data.reference_data_api
This module implements a FastAPI application that provides endpoints for
retrieving African forex rates. It includes logging configuration, health check,
and data processing functionalities.
'''
import json
from pathlib import Path
import time
from typing import Dict, Any, List, Set
from data.africa_fx_details import africa_fx_details
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import logging
import os
import asyncio
import random

###############################################################################
# Setup Logging and App
###############################################################################

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

## Initialize FastAPI app
app = FastAPI()
FX_DATA_PATH = Path(__file__).parent / "data" / "forex_rate_api_response.json"

## load data from a JSON file at startup
with open(FX_DATA_PATH, "r") as file:
        FX_DATA: Dict[str, Any] = json.load(file)
        logger.info("Loaded forex data....")

###############################################################################
# WebSocket Connection Manager
###############################################################################

class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""
    
    def __init__(self):
        self.active_connections: Dict[WebSocket, Set[str]] = {}
    
    async def broadcast_to_all(self, currency:str, message: str):
        """Broadcast message to all connected clients that have subscriptions."""
        for connection in self.active_connections:
            if self.active_connections[connection] and currency in self.active_connections[connection]:  # Only send if client has active subscriptions
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error("Error broadcasting to client: %s", str(e))

    async def connect(self, websocket: WebSocket):
        """Accept and track a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[websocket] = set()
        logger.info("WebSocket client connected. Total connections: %d", len(self.active_connections))
        
    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket."""
        if websocket in self.active_connections:
            del self.active_connections[websocket]
        logger.info("WebSocket client disconnected. Total connections: %d", len(self.active_connections))
        
    def subscribe(self, websocket: WebSocket, currencies: Set[str] = None):
        """Subscribe to currency updates."""
        if websocket in self.active_connections:
            if currencies:
                self.active_connections[websocket].update(currencies)
                logger.info("Client subscribed to currencies: %s", currencies)
            else:
                # Subscribe to all currencies
                self.active_connections[websocket] = set(africa_fx_details.keys())
                logger.info("Client subscribed to all currencies")
                
    def unsubscribe(self, websocket: WebSocket, currencies: Set[str] = None):
        """Unsubscribe from currency updates."""
        if websocket in self.active_connections:
            if currencies:
                self.active_connections[websocket].difference_update(currencies)
                logger.info("Client unsubscribed from currencies: %s", currencies)
            else:
                # Unsubscribe from all
                self.active_connections[websocket].clear()
                logger.info("Client unsubscribed from all currencies")
                
    def get_subscriptions(self, websocket: WebSocket) -> Set[str]:
        """Get the current subscriptions for a client."""
        return self.active_connections.get(websocket, set()).copy()

manager = ConnectionManager()

###############################################################################
# Background Tasks
###############################################################################

async def price_tick_simulator():
    """
    Simulate price tick updates every 5 seconds.
    Broadcasts updated forex rates to all subscribed WebSocket clients.
    """
    while True:
        try:
            await asyncio.sleep(5)
            logger.info("Simulating price tick update...")
            # Get all supported currencies and latest rates
            all_currencies = list(africa_fx_details.keys())
            rate_data = process_fx_data(all_currencies)
            for currency,detail in rate_data['rates'].items():
                # Simulate a small random fluctuation in rates
                if detail['rate'] is None:
                    continue
                fluctuation = random.uniform(-0.005, 0.005)  # +/-0.5%
                detail['rate'] = round(detail['rate'] * (1 + fluctuation), 6) # new rate; round to 6 decimal places
                data = {
                    "success": True,
                    "base": "USD",
                    "timestamp": int(time.time() * 1000),
                    "rates": {currency: detail },
                    "date": time.strftime("%Y-%m-%d"),
                }
                await manager.broadcast_to_all(currency, json.dumps(data))
                logger.debug("[%s] Price tick broadcast sent to all subscribed clients", currency)
            
        except Exception as e:
            logger.error("Error in price tick simulator: %s", str(e))
            await asyncio.sleep(5)  # Continue on error

@app.on_event("startup")
async def startup_event():
    """Start background price tick simulator on app startup."""
    logger.info("Starting price tick simulator...")
    asyncio.create_task(price_tick_simulator())

###############################################################################
# API Endpoints
###############################################################################

# redirect /swagger to /docs
@app.get("/swagger")
async def redirect_to_swagger():
    logger.info("Redirecting /swagger to /docs")
    return JSONResponse(status_code=302, headers={"Location": "/docs"}, content={})
        
# health check endpoint
@app.get("/health")
async def health_check() -> JSONResponse:
    '''
    Docstring for health_check
    
    :return: Description
    :rtype: Any
    '''
    logger.info("Health check endpoint called")
    return JSONResponse(content={"status": "ok"})

@app.get("/v1/fx/rate")
async def get_forex_rates(
    currency: str = None
) -> JSONResponse:
    '''
    Endpoint to return African forex rates.
    
    :return: JSON response with African forex rates
    :rtype: JSONResponse
    '''
    logger.info("get_forex_rates called with currency: %s", currency)
    ccy = africa_fx_details.keys() 
    if currency:
        logger.info("Processing forex rates for currency: %s", currency)
        if not currency.upper() in ccy:
            logger.debug("Requested currency %s not supported", currency)
            return JSONResponse(content={"error": f"Currency {currency} not supported"}, status_code=404)
        ccy = [currency.upper()]
    else:
        logger.info("Processing forex rates for all supported African currencies")
    return JSONResponse(content=process_fx_data(ccy))

@app.websocket("/subscribe/fx/rate/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time forex rate updates.
    
    Expected client messages:
    - {"mode": "subscribe", "currencies": ["ZAR", "NGN"]} - Subscribe to specific currencies
    - {"mode": "subscribe"} - Subscribe to all currencies
    - {"mode": "unsubscribe", "currencies": ["ZAR"]} - Unsubscribe from specific currencies
    - {"mode": "unsubscribe"} - Unsubscribe from all currencies
    """
    logger.info("WebSocket connection request received from client_id: %s", client_id)
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info("WebSocket received data: %s", data)
            await process_websocket_message(websocket, data)
    except Exception as e:
        logger.error("WebSocket error: %s", str(e))
    finally:
        manager.disconnect(websocket)
        
###############################################################################
# Helper Functions
###############################################################################

async def handle_subscribe(websocket: WebSocket, currencies: List[str] = None) -> None:
    """
    Handle subscribe request from WebSocket client.
    
    :param websocket: WebSocket connection
    :param currencies: List of currency codes (None for all)
    """
    if currencies:
        # Validate currencies exist
        currencies = set([c.upper() for c in currencies])
        invalid = currencies - set(africa_fx_details.keys())
        if invalid:
            await websocket.send_text(
                json.dumps({"error": f"Invalid currencies: {invalid}"})
            )
            return
        manager.subscribe(websocket, currencies)
    else:
        manager.subscribe(websocket)  # Subscribe to all
        
    # Send immediate update
    subs = manager.get_subscriptions(websocket)
    data_to_send = process_fx_data(list(subs)) if subs else process_fx_data(list(africa_fx_details.keys()))
    await websocket.send_text(json.dumps(data_to_send))

async def handle_unsubscribe(websocket: WebSocket, currencies: List[str] = None) -> None:
    """
    Handle unsubscribe request from WebSocket client.
    
    :param websocket: WebSocket connection
    :param currencies: List of currency codes (None for all)
    """
    if currencies:
        currencies = set([c.upper() for c in currencies])
        manager.unsubscribe(websocket, currencies)
    else:
        manager.unsubscribe(websocket)  # Unsubscribe from all
    await websocket.send_text(json.dumps({"status": "unsubscribed"}))


async def process_websocket_message(websocket: WebSocket, data: str) -> None:
    """
    Process incoming WebSocket message and route to appropriate handler.
    
    :param websocket: WebSocket connection
    :param data: Raw message data
    """
    try:
        message = json.loads(data)
    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
        return
        
    mode = message.get("mode")
    currencies = message.get("currencies")
    
    if mode == "subscribe":
        await handle_subscribe(websocket, currencies)
    elif mode == "unsubscribe":
        await handle_unsubscribe(websocket, currencies)
    else:
        await websocket.send_text(json.dumps({"error": "Invalid mode. Use 'subscribe' or 'unsubscribe'"}))
    
def process_fx_data(currencies: List[str] = []) -> Dict[str, Any]:
    '''
    Process forex data to filter by currencies.
    
    :param currencies: Comma-separated list of currency codes
    :type currencies: str
    :return: Filtered forex data
    :rtype: Dict[str, Any]
    '''
    raw_rates = FX_DATA.get("rates", {})

    # Preserve requested order and return None for missing currencies
    rates: Dict[str, Dict[str, Any]] = {}
    missing: List[str] = []
    for ccy in currencies:
        if ccy in raw_rates:
            rates[ccy] = {"rate": raw_rates[ccy]}
        else:
            rates[ccy] = {"rate": None}
            missing.append(ccy)
        # update the currency details
        details = africa_fx_details.get(ccy, {})
        rates[ccy].update(details)
    if missing:
        logger.warning("Requested currencies not found in data: %s", missing)

    return {
        "success": True,
        "base": "USD",
        "timestamp": int(time.time() * 1000),
        "rates": rates,
        "date": time.strftime("%Y-%m-%d"),
    }