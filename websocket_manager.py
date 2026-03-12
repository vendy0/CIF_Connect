from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

# On crée un routeur dédié
router = APIRouter()


# --- GESTIONNAIRE WEBSOCKET ---
class ConnectionManager:
	def __init__(self):
		self.active_connections: Dict[int, List[WebSocket]] = {}

	async def connect(self, websocket: WebSocket, room_id: int):
		await websocket.accept()
		if room_id not in self.active_connections:
			self.active_connections[room_id] = []
		self.active_connections[room_id].append(websocket)

	def disconnect(self, websocket: WebSocket, room_id: int):
		if room_id in self.active_connections:
			self.active_connections[room_id].remove(websocket)
			if not self.active_connections[room_id]:
				del self.active_connections[room_id]

	async def broadcast_to_room(self, room_id: int, message_data: dict):
		if room_id in self.active_connections:
			for connection in self.active_connections[room_id]:
				await connection.send_json(message_data)


manager = ConnectionManager()


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
	await manager.connect(websocket, room_id)
	try:
		while True:
			data = await websocket.receive_json()
	except WebSocketDisconnect:
		manager.disconnect(websocket, room_id)
