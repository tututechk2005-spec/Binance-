from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import asyncio
import json
from loguru import logger
from core.security import decode_token

router = APIRouter()

active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active:
            self.active[user_id] = set()
        self.active[user_id].add(websocket)
        logger.info(f"WebSocket connected: {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active:
            self.active[user_id].discard(websocket)
            if not self.active[user_id]:
                del self.active[user_id]
        logger.info(f"WebSocket disconnected: {user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active:
            dead = set()
            for ws in self.active[user_id]:
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    dead.add(ws)
            for ws in dead:
                self.active[user_id].discard(ws)

    async def broadcast(self, message: dict):
        for user_id, connections in list(self.active.items()):
            await self.send_to_user(user_id, message)


manager = ConnectionManager()


@router.websocket("/signals")
async def signal_websocket(websocket: WebSocket, token: str = Query(...)):
    try:
        data = decode_token(token)
        user_id = data.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
    except Exception:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            msg = await websocket.receive_text()
            parsed = json.loads(msg)
            if parsed.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


@router.websocket("/trades")
async def trades_websocket(websocket: WebSocket, token: str = Query(...)):
    try:
        data = decode_token(token)
        user_id = data.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
    except Exception:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, f"trades:{user_id}")
    try:
        while True:
            await asyncio.sleep(5)
            await websocket.send_text(json.dumps({"type": "heartbeat", "status": "ok"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"trades:{user_id}")
