"""WebSocket connection manager and message handlers."""
import json
import logging
from typing import Dict, Set, List
from fastapi import WebSocket
from data.africa_fx_details import africa_fx_details
from utils import process_fx_data
from logging_config import logger

class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""

    def __init__(self):
        self.active_connections: Dict[WebSocket, Set[str]] = {}

    async def broadcast_to_all(self, currency: str, message: str):
        """Broadcast message to all connected clients that have subscriptions."""
        for connection in list(self.active_connections.keys()):
            # Only send if the client is subscribed to the currency
            if self.active_connections.get(connection) and currency in self.active_connections[connection]:
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

    def get_subscriptions(self, websocket: WebSocket):
        """Get the current subscriptions for a client."""
        return self.active_connections.get(websocket, set()).copy()


# single shared manager instance
manager = ConnectionManager()


async def handle_subscribe(websocket: WebSocket, currencies: List[str] = None) -> None:
    """
    Handle subscribe request from WebSocket client.
    """
    if currencies:
        # Validate currencies exist
        currencies = set([c.upper() for c in currencies])
        invalid = currencies - set(africa_fx_details.keys())
        if invalid:
            await websocket.send_text(json.dumps({"error": f"Invalid currencies: {invalid}"}))
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
    """
    if currencies:
        currencies = set([c.upper() for c in currencies])
        manager.unsubscribe(websocket, currencies)
    else:
        manager.unsubscribe(websocket)  # Unsubscribe from all
    await websocket.send_text(json.dumps({"status": "unsubscribed"}))


async def process_websocket_message(websocket: WebSocket, client_id: str, data: str) -> None:
    """
    Process incoming WebSocket message and route to appropriate handler.
    """
    try:
        message = json.loads(data)
    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
        return

    mode = message.get("mode")
    currencies = message.get("currencies")
    logger.info("[%s] Processing WebSocket message: mode=%s, currencies=%s", client_id, mode, currencies)

    if mode == "subscribe":
        await handle_subscribe(websocket, currencies)
    elif mode == "unsubscribe":
        await handle_unsubscribe(websocket, currencies)
    else:
        await websocket.send_text(json.dumps({"error": "Invalid mode. Use 'subscribe' or 'unsubscribe'"}))
