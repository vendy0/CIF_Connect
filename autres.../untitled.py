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
# - Mettre les messages en fil d'attente




# - Mettre les options de message dans le swipe


# - Rechercher un message ne l'affiche pas mais swipe jusqu'à lui. Je pensais plutôt faire une requête api si l'utilisateur demande plus parce que le chat ne contient que les 100 derniers messages. Cette requête retournerais tous les messages jusqu'à celui qu'on cherche.



# Maintenant je veux :
# Analyse attentivement ma chat_view
# - Quand on scroll ça doit afficher la dernière date (style whatsapp). Quand on arrive à l'endroit où cette date délimite elle s'arrete et la date precedente prend le relai
# - Et puis je n'arrive pas à ajouter Scroll btn à la page
# - Pour le dernier message lu je comptais plutot utiliser la date pour reprendre la room où on l'a laissée
# - Afficher le nombre de messages non lus dans la room view (pour chaque room, style whatsapp). J'optimiserai plus tard avec les websocket pour chaque nouveau message reçu


# =========== LES WEBSOCKETS ========== #






Pour les messages non lus :
La meilleure approche (hybride) :
 * Ajoute une colonne last_read_at dans models.py sur ta table de liaison user_room (c'est la BDD qui fait foi).
 * Quand l'élève quitte ChatView, tu envoies une requête PUT /user/rooms/{id}/read avec l'heure actuelle.
 * Le badge dans utils.py sera conditionné par le calcul fait par le backend (total_messages - messages_before_last_read), renvoyé lors du /user/rooms. Ne te casse pas la tête à le calculer en front-end, le back-end est fait pour ça !
3. Logique de ChatView (Scroll, Recherche et Menu)
Désactiver l'auto-scroll si on remonte :
La détection de scroll dans Flet est capricieuse si on ne laisse pas une marge (tolérance).
# Dans chat_view.py, avant de définir chat_list :
    def on_chat_scroll(e: ft.OnScrollEvent):
        # Si on est à moins de 30 pixels du bas, on réactive l'autoscroll
        is_at_bottom = e.pixels >= (e.max_scroll_extent - 30)
        chat_list.auto_scroll = is_at_bottom
        page.update()

    chat_list = ft.ListView(expand=True, spacing=15, auto_scroll=True, padding=10, on_scroll=on_chat_scroll)

Recherche de message par Scroll :
Au lieu de cacher les messages, on défile jusqu'à eux grâce à la propriété key.
# Remplacer ta fonction filter_messages dans chat_view.py par :
    async def filter_messages(query: str):
        if not query:
            return
        query = query.lower()

        # On cherche d'abord dans les messages déjà chargés localement
        for ctrl in chat_list.controls:
            if hasattr(ctrl, "message") and query in ctrl.message.content.lower():
                await chat_list.scroll_to(key=str(ctrl.message.id), duration=300)
                await show_top_toast(page, "Message trouvé ! (En local)")
                return

        # TODO plus tard : Si on n'a pas trouvé, faire une requête API pour récupérer l'historique plus ancien.
        await show_top_toast(page, "Message non trouvé dans l'historique récent.", True)

Unifier le rendu des messages :
Créer deux classes distinctes (MyChatMessage, OtherChatMessage) te fait dupliquer du code. Crée une fonction générique pour centraliser :
# Dans chat_view.py, remplace les appels if message.pseudo != current_pseudo par :
    def render_single_message(message: Message, is_me: bool):
        # Assigne l'id comme clé pour le scroll_to()
        key_str = str(message.id)

        if is_me:
            return MyChatMessage(key=key_str, message=message, page=page, ...) # Passe les callbacks
        else:
            return OtherChatMessage(key=key_str, message=message, page=page, ...)

# Et dans def on_message(message: Message):
    if message.message_type == "chat":
        is_me = (message.pseudo == current_pseudo)
        chat_list.controls.append(render_single_message(message, is_me))

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


# On crée l'objet qui va gérer le tuyau
ws = ft.WebSocketClient(url="ws://ton-serveur.com/ws", on_message=ma_fonction_qui_traite_le_message)

# On l'ajoute à la page pour qu'il commence à écouter
page.overlay.append(ws)
page.update()
ws.connect()


class ConnectionManager:
	def __init__(self):
		# Un dictionnaire pour lier un room_id à une liste de connexions
		self.active_connections: dict[int, list[WebSocket]] = {}

	async def connect(self, websocket: WebSocket, room_id: int):
		# Logique pour accepter et stocker la connexion
		pass

	async def broadcast(self, message: dict, room_id: int):
		# Logique pour envoyer le message à tous ceux qui sont dans ce salon
		pass


class ConnectionManager:
	def __init__(self):
		# Dictionnaire : { room_id: [liste_des_websockets_connectés] }
		self.active_connections: dict[int, list[WebSocket]] = {}

	async def connect(self, websocket: WebSocket, room_id: int):
		await websocket.accept()
		# Si le salon n'existe pas encore dans notre dictionnaire, on le crée
		if room_id not in self.active_connections:
			self.active_connections[room_id] = []
		self.active_connections[room_id].append(websocket)

	def disconnect(self, websocket: WebSocket, room_id: int):
		# On retire le tuyau du salon spécifique
		if room_id in self.active_connections:
			self.active_connections[room_id].remove(websocket)


from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
	def __init__(self):
		# Structure : { room_id: [websocket1, websocket2, ...] }
		self.active_connections: Dict[int, List[WebSocket]] = {}

	async def connect(self, websocket: WebSocket, room_id: int):
		await websocket.accept()
		if room_id not in self.active_connections:
			self.active_connections[room_id] = []
		self.active_connections[room_id].append(websocket)

	def disconnect(self, websocket: WebSocket, room_id: int):
		if room_id in self.active_connections:
			self.active_connections[room_id].remove(websocket)
			# Nettoyage si le salon est vide
			if not self.active_connections[room_id]:
				del self.active_connections[room_id]

	async def broadcast_to_room(self, room_id: int, message_data: dict):
		"""Envoie le message uniquement aux membres du salon spécifié."""
		if room_id in self.active_connections:
			for connection in self.active_connections[room_id]:
				await connection.send_json(message_data)


manager = ConnectionManager()


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
	# 1. Connexion et stockage
	await manager.connect(websocket, room_id)
	try:
		while True:
			# 2. Attente de réception (si l'élève envoie via WS)
			data = await websocket.receive_json()

			# 3. Diffusion à tout le salon
			# Note : On peut ajouter ici la sauvegarde en BDD via tes fonctions CRUD
			await manager.broadcast_to_room(room_id, data)
	except Exception:
		# 4. Déconnexion automatique en cas de fermeture d'app ou erreur
		manager.disconnect(websocket, room_id)


# Exemple dans ta route POST message
@app.post("/room/{room_id}/messages")
async def create_message(room_id: int, payload: dict):
	# ... ta logique CRUD actuelle pour sauver le message ...
	new_msg = await crud.save_message(payload)

	# On prévient tout le monde dans le salon via le tuyau
	await manager.broadcast_to_room(room_id, new_msg)

	return new_msg


async def ChatView(page: ft.Page):
	# ... ton code actuel (récupération du token, room_id, etc.) ...

	async def on_ws_message(e):
		# 1. On reçoit les données (souvent en JSON)
		# 2. On les transforme en objet Message (ton modèle)
		# 3. On ajoute le message à la liste visuelle (chat_list)
		# 4. On fait page.update()
		pass

	# Création du client WebSocket
	ws = ft.WebSocketClient(url=f"ws://localhost:8000/ws/{current_room_id}", on_message=on_ws_message)

	# On l'ajoute à la page pour qu'il s'active
	page.overlay.append(ws)
	page.update()

	# On lance la connexion
	await ws.connect()


# Dans ton ChatView
async def on_ws_message(data_brute):
	# Le serveur nous envoie du JSON
	import json

	data = json.loads(data_brute)

	# On crée l'objet Message à partir du JSON
	new_msg = Message(**data)

	# On choisit le bon composant (Moi ou un Autre)
	# user_id est celui stocké dans tes SharedPreferences
	if new_msg.user_id == current_user_id:
		chat_list.controls.append(MyChatMessage(new_msg, ...))
	else:
		chat_list.controls.append(OtherChatMessage(new_msg, ...))

	# LA commande magique !
	await page.update_async()


from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
	def __init__(self):
		# On stocke les connexions par salon : { room_id: [liste_des_websockets] }
		self.active_connections: Dict[int, List[WebSocket]] = {}

	async def connect(self, websocket: WebSocket, room_id: int):
		"""Branche un élève dans un salon spécifique."""
		await websocket.accept()
		if room_id not in self.active_connections:
			self.active_connections[room_id] = []
		self.active_connections[room_id].append(websocket)

	def disconnect(self, websocket: WebSocket, room_id: int):
		"""Débranche l'élève et nettoie le salon si vide."""
		if room_id in self.active_connections:
			self.active_connections[room_id].remove(websocket)
			if not self.active_connections[room_id]:
				del self.active_connections[room_id]

	async def broadcast_to_room(self, room_id: int, message_data: dict):
		"""Envoie l'info à tout le monde dans le salon visé."""
		if room_id in self.active_connections:
			for connection in self.active_connections[room_id]:
				# On utilise send_json pour envoyer le dictionnaire directement
				await connection.send_json(message_data)


manager = ConnectionManager()

from fastapi import WebSocket, WebSocketDisconnect


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
	# 1. On accepte la connexion et on enregistre le "tuyau" dans le manager
	await manager.connect(websocket, room_id)

	try:
		while True:
			# On reste en attente de messages envoyés par le client via WS
			# (Même si on utilise le mode mixte, il faut garder la boucle ouverte)
			data = await websocket.receive_json()

			# Si tu veux que le WS serve aussi à envoyer, on diffuse ici :
			# await manager.broadcast_to_room(room_id, data)

	except WebSocketDisconnect:
		# 2. Nettoyage automatique si l'élève ferme l'app ou perd le réseau
		manager.disconnect(websocket, room_id)

import json
import flet as ft

async def ChatView(page: ft.Page):
    # ... tes récupérations de token et room_id ...
    
    # 1. La fonction qui traite les messages arrivant du serveur
    async def on_ws_message(e):
        msg_data = json.loads(e.data)
        new_msg = Message(**msg_data)
        
        # Éviter le doublon si c'est notre propre message (déjà ajouté localement)
        # ou l'ajouter ici si tu as choisi d'attendre le retour du serveur
        if new_msg.id not in [m.id for m in chat_list.controls if hasattr(m, 'id')]:
            if new_msg.pseudo == mon_pseudo:
                chat_list.controls.append(MyChatMessage(new_msg, page))
            else:
                chat_list.controls.append(OtherChatMessage(new_msg, page))
            
            await chat_list.update_async()
            # Scroll automatique vers le bas
            chat_list.scroll_to(offset=-1, duration=300)

    # 2. Création et configuration du client WebSocket
    # Remplace par ton IP de serveur (ex: 10.0.2.2 pour l'émulateur Android)
    ws_url = f"ws://127.0.0.1:8000/ws/{current_room_id}"
    ws = ft.WebSocketClient(
        url=ws_url,
        on_message=on_ws_message
    )

    # 3. Ajout à la page et connexion
    page.overlay.append(ws)
    await page.update_async()
    await ws.connect()
