"""
BloodReach BD — WebSocket Connection Manager
Maintains active WebSocket connections per authenticated user and enables instant real-time pushes.
"""

from typing import Dict, List, Any
from uuid import UUID
from fastapi import WebSocket
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections for online users"""

    def __init__(self):
        # Maps user_id -> List of active WebSocket connections (e.g. multi-tab/devices)
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept WebSocket connection and store reference"""
        await websocket.accept()
        async with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections for user: {len(self.active_connections[user_id])}")

    async def disconnect(self, user_id: str, websocket: WebSocket):
        """Remove disconnected WebSocket"""
        async with self._lock:
            if user_id in self.active_connections:
                if websocket in self.active_connections[user_id]:
                    self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send JSON payload to all active connections of a specific user"""
        user_key = str(user_id)
        connections = self.active_connections.get(user_key, [])
        if not connections:
            return

        payload = json.dumps(message, default=str)
        dead_connections = []
        for connection in connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket for user {user_key}: {e}")
                dead_connections.append(connection)

        if dead_connections:
            async with self._lock:
                for dead in dead_connections:
                    if dead in self.active_connections.get(user_key, []):
                        self.active_connections[user_key].remove(dead)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast event to all connected users in real time"""
        payload = json.dumps(message, default=str)
        tasks = []
        for user_id, conns in list(self.active_connections.items()):
            for ws in conns:
                tasks.append(ws.send_text(payload))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Global singleton instance
ws_manager = ConnectionManager()
