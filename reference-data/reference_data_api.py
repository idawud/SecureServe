'''
Docstring for reference-data.reference_data_api
This module implements a FastAPI application that provides endpoints for
retrieving African forex rates. It wires the WebSocket handlers and starts
background tasks (price tick simulator).
'''
import json
import time
import asyncio
import random
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from data.africa_fx_details import africa_fx_details
from ws import manager, process_websocket_message
from utils import process_fx_data
from logging_config import logger
app = FastAPI()

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

            # For each currency simulate a tiny fluctuation and broadcast
            for currency, detail in rate_data["rates"].items():
                if detail.get("rate") is None:
                    continue
                fluctuation = random.uniform(-0.005, 0.005)  # +/-0.5%
                detail["rate"] = round(detail["rate"] * (1 + fluctuation), 6)

                payload = {
                    "success": True,
                    "base": "USD",
                    "timestamp": int(time.time() * 1000),
                    "rates": {currency: detail},
                    "date": time.strftime("%Y-%m-%d"),
                }

                # broadcast the tick to all subscribed clients
                await manager.broadcast_to_all(currency, json.dumps(payload))
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
    logger.info("Health check endpoint called")
    return JSONResponse(content={"status": "ok"})


@app.get("/v1/fx/rate")
async def get_forex_rates(currency: str = None) -> JSONResponse:
    logger.info("get_forex_rates called with currency: %s", currency)
    ccy = set(africa_fx_details.keys())
    if currency:
        logger.info("Processing forex rates for currency: %s", currency)
        if currency.upper() not in ccy:
            logger.debug("Requested currency %s not supported", currency)
            return JSONResponse(content={"error": f"Currency {currency} not supported"}, status_code=404)
        ccy = [currency.upper()]
    else:
        logger.info("Processing forex rates for all supported African currencies")
        ccy = list(ccy)

    return JSONResponse(content=process_fx_data(ccy))


@app.websocket("/subscribe/fx/rate/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint that delegates message processing to `ws` module.
    """
    logger.info("WebSocket connection request received from client_id: %s", client_id)
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info("[{}] WebSocket received data: %s", client_id, data)
            await process_websocket_message(websocket, client_id, data)
    except Exception as e:
        logger.error("WebSocket error: %s", str(e))
    finally:
        manager.disconnect(websocket)