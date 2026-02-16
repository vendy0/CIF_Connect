"""
- Page de connexion
- Boite de dialogue de bienvenue
"""

# Un dictionnaire pour tout centraliser
utilisateurs_actifs = {websocket_A: {"pseudo": "Lion Courageux", "email": "eleve1@interfamilia.com"}, websocket_B: {"pseudo": "Chat Malicieux", "email": "eleve2@interfamilia.com"}}


# On récupère le pseudo de celui qui parle
expediteur_pseudo = utilisateurs_actifs[websocket_actuel]["pseudo"]
message_complet = f"{expediteur_pseudo} : {message_recu}"

# On boucle sur tout le monde pour diffuser
for client_socket, infos in utilisateurs_actifs.items():
    if client_socket != websocket_actuel:
        await client_socket.send_text(message_complet)

"""
class ConnectionManager:
    def __init__(self):
        # Notre dictionnaire "tuyau" -> "infos"
        self.active_connections = {}

    async def connect(self, websocket, user_info):
        await websocket.accept()
        self.active_connections[websocket] = user_info

    def disconnect(self, websocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    async def broadcast(self, message: str, sender_socket: WebSocket):
        # Vérification du Shadowban avant de diffuser
        user_info = self.active_connections.get(sender_socket)
        if user_info and user_info.get("is_shadowbanned"):
            return  # On s'arrête ici : le message meurt dans le silence

        # Si tout va bien, on diffuse
        for client_socket in self.active_connections.keys():
            if client_socket == sender_socket:
                continue

            try:
                pseudo = user_info["pseudo"]
                await client_socket.send_text(f"{pseudo} : {message}")
            except:
                self.disconnect(client_socket)
"""


class ConnectionManager:
    def __init__(self):
        # Le dictionnaire principal : {websocket: {"pseudo": "...", "is_shadowbanned": ...}}
        self.active_connections = {}

    async def connect(self, websocket, user_info):
        """Appelé quand un élève ouvre l'application."""
        await websocket.accept()
        self.active_connections[websocket] = user_info

    def disconnect(self, websocket):
        """Appelé quand l'élève ferme l'application ou perd internet."""
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    async def broadcast(self, sender_socket):
        # Si l'expéditeur est shadowbanned, on arrête tout
        if user_info.get("is_shadowbanned"):
            return

        for connection in self.active_connections:
            if connection == sender_socket:
                continue
            try:
                # On tente l'envoi
                await connection.send_text(f"{pseudo} : {message}")
            except:
                # Si ça échoue, c'est que l'élève est parti
                self.disconnect(connection)
