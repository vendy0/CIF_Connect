"""
# - Connexion avec email et vérification
# - Boite de dialogue de bienvenue
# - Quand qlq'un change de pseudo faut l'avertir que ça se verra dans les rooms créés.
# - Mot de passe oublié
# - Quand il y a une nouvelle version
# - Mot de passe oublié
# - Reprendre une Room la où l'on s'est arrêté
# - Rechercher un message
# - Taguer
# - Émoji
# - Modifier et supprimer un salon
# - Interface Administrateur
# - Les marqueurs de dates visibles
# - Annonces

# Analyse attentivement la chat_view. Maintenant voila ce dont j'ai besoin :
# - Un fond d'écran simple et doux qui s'adapte au thème à la manière de whatsapp
# - Glisser un message vers la droite pour y répondre (comme la plupart des applications de chat)
# - Le bouton qui affiche les émojis à gauche de la new_message_input (Je ne sais pas si flet possède des émojis préfabriqués)
# - Reprendre une Room là où l'on l'a quittée (Je n'ai absolument aucune idée de comment faire ça)
# - Puis une view quand on clique sur L'app bar qui affiche les infos du Salon (Nom, code invitation, description, Changer les informarions du salon (nom, description), Je ne sais pas si je peux afficher les utilisateurs même si c'est un adm pour l'anonymat, tu me donneras ton avis, avec les options qui vont suivre (Je ne sais pas si les répéter est une bonne chose))

# * Remplacer le bouton pour sortir de la Room par un menu (3 points) avec des options:
# - Rechercher un message
# - Quitter le Salon
# - Modifier et supprimer un salon (Si on est adm du salon)
# - Et d'autres truc interessants

# - Puis un bouton à gauche de l'app bar pour retourner à la rooms_view

"""
# - Glisser pour répondre
# - Fond d'écran
# - Avant d'envoyer vers bdd, vérifier si il y a changement
# - Generate secure code
# - Changer la couleur du pseudo
# - Premiere lettre en majuscule
# - Supprimer le selected
# - Copier un message (ft.Clipboard().set(message))
# - Je devrait peut-être faire un soft delete. Quand on repond a un message supprimé, le parent_bubble disparait.
# - Sauvegarder le pseudo changé en bdd
# - Changer les print pour utiliser des barres d'infos
# - Délimiteur parent message dans le front
# - Informer par snack bar ou qlq chose de plus stylé
# - Page de connexion
# - Le jwt à la place des id dans les requetes.

# Un dictionnaire pour tout centraliser
utilisateurs_actifs = {
	websocket_A: {"pseudo": "Lion Courageux", "email": "eleve1@interfamilia.com"},
	websocket_B: {"pseudo": "Chat Malicieux", "email": "eleve2@interfamilia.com"},
}


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
