"""Utility functions and data loading for reference-data service."""
import json
from pathlib import Path
import time
from typing import Dict, Any, List
from data.africa_fx_details import africa_fx_details
from logging_config import logger

FX_DATA_PATH = Path(__file__).parent / "data" / "forex_rate_api_response.json"

with open(FX_DATA_PATH, "r") as file:
    FX_DATA: Dict[str, Any] = json.load(file)
    logger.info("Loaded forex data from utils...")


def process_fx_data(currencies: List[str] = []) -> Dict[str, Any]:
    """
    Process forex data to filter by currencies.
    Returns a payload similar to the original implementation.
    """
    raw_rates = FX_DATA.get("rates", {})

    rates: Dict[str, Dict[str, Any]] = {}
    missing: List[str] = []
    for ccy in currencies:
        if ccy in raw_rates:
            rates[ccy] = {"rate": raw_rates[ccy]}
        else:
            rates[ccy] = {"rate": None}
            missing.append(ccy)
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
