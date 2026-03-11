"""
# - Connexion avec email et vérification
# - Mot de passe oublié
# - Boite de dialogue de bienvenue
# - Quand qlq'un change de pseudo faut l'avertir que ça se verra dans les rooms créés.
# - Ne peut pas changer de pseudo si les 7 jours ne sont pas encore écoulés
# - Quand il y a une nouvelle version
# - Mot de passe oublié
# - Changer "/chat" par f"/room/{current_room_id}"
# - Interface Administrateur
# - Les marqueurs de dates visibles
# - Annonces
# - Actualiser un seul élément plutôt que de refaire toute la liste
# - Comment je conditionne ce unread messages
# - Quitter le Salon général
# - Afficher les salons à partir du dernier message reçu
# - Les notifs (Quand on se fait tag aussi)
# - Mettre à jour la page room_info pour changer le nombre de membres en ligne
# - Désactiver l'auto scroll quand on remonte
# - Ajouter la colonne last read dans la bdd




# - Mettre les options de message dans le swipe


# - Rechercher un message ne l'affiche pas mais swipe jusqu'à lui. Je pensais plutôt faire une requête api si l'utilisateur demande plus parce que le chat ne contient que les 100 derniers messages. Cette requête retournerais tous les messages jusqu'à celui qu'on cherche.



# Maintenant je veux :
# Analyse attentivement ma chat_view
# - Quand on scroll ça doit afficher la dernière date (style whatsapp). Quand on arrive à l'endroit où cette date délimite elle s'arrete et la date precedente prend le relai
# - Et puis je n'arrive pas à ajouter Scroll btn à la page
# - Pour le dernier message lu je comptais plutot utiliser la date pour reprendre la room où on l'a laissée
# - Afficher le nombre de messages non lus dans la room view (pour chaque room, style whatsapp). J'optimiserai plus tard avec les websocket pour chaque nouveau message reçu


# =========== LES WEBSOCKETS ========== #

"""
# // "ON_PRIMARY",
# // // "ON_PRIMARY_CONTAINER",
# // "ON_PRIMARY_FIXED",
# // "ON_PRIMARY_FIXED_VARIANT",
# // "ON_SECONDARY",
# // "ON_SECONDARY_CONTAINER",
# // "ON_SECONDARY_FIXED",
# // "ON_SECONDARY_FIXED_VARIANT",
# // "ON_SURFACE",
# // "ON_SURFACE_VARIANT",
# // "ON_TERTIARY",
# // "ON_TERTIARY_CONTAINER",
# // "ON_TERTIARY_FIXED",
# // "ON_TERTIARY_FIXED_VARIANT",


# // "SURFACE",
# // "SURFACE_BRIGHT",
# // "SURFACE_CONTAINER",
# // "SURFACE_CONTAINER_HIGH",
# // "SURFACE_CONTAINER_HIGHEST",


# - Afficher les membres
# - Swipe de l'autre coté affiche la date ou un truc du genre
# - Taguer (Un message) (Optionnel)
# - Les chargements
# * Je veux que tu me fournisses la page info du salon (room_info.py). Sur cette page l'adm va pouvoir modifier les infos du salons comme c'est indiqué dans le crud.py. On pourra voir le nombre de membres totaux et combien sont en ligne (ex: 30/126 online). Je crois que je pourrais aussi afficher ça dans l'AppBar.
# - Sur la page y aura aussi le nom du salon, l'icon flet du salon aussi et les autres détails que tu juges nécéssaire. Et aussi le code du salon
# * Remplacer le bouton pour sortir de la Room par un menu (3 points) avec des options:
# - Puis une view quand on clique sur L'app bar qui affiche les infos du Salon (Nom, code invitation, description, Changer les informarions du salon (nom, description), Je ne sais pas si je peux afficher les utilisateurs même si c'est un adm pour l'anonymat, tu me donneras ton avis, avec les options qui vont suivre (Je ne sais pas si les répéter est une bonne chose))
# - Le bouton qui affiche les émojis à gauche de la new_message_input (Je ne sais pas si flet possède des émojis préfabriqués)
# - Un fond d'écran simple et doux qui s'adapte au thème à la manière de whatsapp
# - Puis un bouton à gauche de l'app bar pour retourner à la rooms_view
# - Quitter le Salon
# - Glisser un message vers la droite pour y répondre (comme la plupart des applications de chat)
# - Modifier et supprimer un salon (Si on est adm du salon)
# - Afficher les salons en fonction du dernier message. On gerera peut-être avec les websockets
# - Faire un soft delete sur les rooms
# - Ajouter d'autres icones
# - Émoji
# - Modifier et supprimer un salon
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
