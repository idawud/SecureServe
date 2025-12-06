'''
Docstring for reference-data.reference_data_api
This module implements a FastAPI application that provides endpoints for
retrieving African forex rates. It includes logging configuration, health check,
and data processing functionalities.
'''
import json
from pathlib import Path
import time
from typing import Dict, Any, List
from data.africa_fx_details import africa_fx_details
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
import os

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
            logger.warning("Requested currency %s not supported", currency)
            return JSONResponse(content={"error": f"Currency {currency} not supported"}, status_code=404)
        ccy = [currency.upper()]
    else:
        logger.info("Processing forex rates for all supported African currencies")
    return JSONResponse(content=process_fx_data(ccy))

###############################################################################
# Helper Functions
###############################################################################
    
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