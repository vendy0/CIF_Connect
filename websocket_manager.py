from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

# On crée un routeur dédié
router = APIRouter()


# --- GESTIONNAIRE WEBSOCKET ---
# class ConnectionManager:
#     def __init__(self):
#         # self.user_connections: Dict[int, List[WebSocket]] = {}
#         # Pour le chat dans les salons
#         self.room_connections: Dict[int, List[WebSocket]] = {}
#         # Pour les notifications globales (nouveaux messages, salons, etc.)
#         self.user_connections: Dict[int, List[WebSocket]] = {}

#     async def connect(self, websocket: WebSocket, room_id: int):
#         await websocket.accept()
#         if room_id not in self.user_connections:
#             self.user_connections[room_id] = []
#         self.user_connections[room_id].append(websocket)

#     def disconnect(self, websocket: WebSocket, room_id: int):
#         if room_id in self.user_connections:
#             self.user_connections[room_id].remove(websocket)
#             if not self.user_connections[room_id]:
#                 del self.user_connections[room_id]

#     async def broadcast_to_room(self, room_id: int, message_data: dict):
#         if room_id in self.user_connections:
#             for connection in self.user_connections[room_id]:
#                 await connection.send_json(message_data)


class ConnectionManager:
    def __init__(self):
        # Pour le chat dans les salons
        self.room_connections: Dict[int, List[WebSocket]] = {}
        # Pour les notifications globales (nouveaux messages, salons, etc.)
        self.user_connections: Dict[int, List[WebSocket]] = {}

    async def connect_user(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)

    def disconnect_user(self, websocket: WebSocket, user_id: int):
        if user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)

    async def notify_user(self, user_id: int, message: dict):
        """Envoie un signal à un utilisateur spécifique"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_json(message)

    async def broadcast_global(self, message: dict):
        """Envoie un signal à TOUT le monde (ex: nouveau salon créé)"""
        for connections in self.user_connections.values():
            for connection in connections:
                await connection.send_json(message)

    # --- Garde tes méthodes existantes pour les rooms ---
    async def connect_room(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        self.room_connections[room_id].append(websocket)

    def disconnect_room(self, websocket: WebSocket, room_id: int):
        if room_id in self.room_connections:
            self.room_connections[room_id].remove(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]

    # ... (reste de tes méthodes broadcast_to_room)

    async def broadcast_to_room(self, room_id: int, message_data: dict):
        if room_id in self.room_connections:
            for connection in self.room_connections[room_id]:
                await connection.send_json(message_data)


manager = ConnectionManager()


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await manager.connect_room(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect_room(websocket, room_id)


@router.websocket("/ws/user/{user_id}")
async def user_websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect_user(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()  # Maintient la connexion ouverte
    except WebSocketDisconnect:
        manager.disconnect_user(websocket, user_id)
