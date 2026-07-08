import asyncio
import uuid
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[uuid.UUID, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: uuid.UUID):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def arena_websocket(websocket: WebSocket, user_id: uuid.UUID):
    """
    WebSocket endpoint for real-time PvP Battles.
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle attack, defense, combo logic here
            # For Phase 3 MVP, just echo the attack globally
            if data.get("action") == "attack":
                await manager.broadcast({
                    "event": "hero_attack",
                    "player_id": str(user_id),
                    "damage": 15
                })
    except WebSocketDisconnect:
        manager.disconnect(user_id)
