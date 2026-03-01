import flet as ft
from dataclasses import dataclass
from utils import generer_pseudo, get_initials, get_avatar_color, get_colors, port, host
import asyncio
import httpx
# import websockets


# async def ChatView(page: ft.Page):
#     # L'URL de ton serveur FastAPI
#     uri = "ws://localhost:8000/chat"

#     # On tente de se connecter
#     try:
#         websocket = await websockets.connect(uri)
#         # Une fois connecté, on peut envoyer les infos de l'élève
#         # (pseudo, etc.) pour que le serveur l'enregistre dans son dict.
#     except Exception as e:
#         print(f"Erreur de connexion : {e}")


# --- Modèle simple pour un message
@dataclass
class Message:
	pseudo: str
	content: str
	message_type: str


# Couleurs / utilitaires
COLORS_LOOKUP = get_colors()


class ChatMessage(ft.Row):
	def __init__(self, message: Message):
		super().__init__()
		self.message = message
		self.vertical_alignment = ft.CrossAxisAlignment.START

		# BottomSheet (menu)
		self.bottom_sheet = ft.BottomSheet(
			content=ft.Container(
				padding=10,
				content=ft.Column(
					tight=True,
					controls=[
						ft.ListTile(
							leading=ft.Icon(ft.Icons.FAVORITE_BORDER),
							title=ft.Text("Liker"),
							on_click=lambda e: self.close_sheet_and_act(e, "react"),
						),
						ft.ListTile(
							leading=ft.Icon(ft.Icons.REPLY),
							title=ft.Text("Répondre"),
							on_click=lambda e: self.close_sheet_and_act(e, "reply"),
						),
						ft.ListTile(
							leading=ft.Icon(ft.Icons.REPORT_GMAILERRORRED, color=ft.Colors.RED),
							title=ft.Text("Signaler", color=ft.Colors.RED),
							on_click=lambda e: self.close_sheet_and_act(e, "report"),
						),
					],
				),
			),
		)

		# Avatar + contenu du message
		self.initials = get_initials(self.message.pseudo)
		self.avatar_color = get_avatar_color(self.message.pseudo, COLORS_LOOKUP)

		msg_content = ft.Container(
			content=ft.Column(
				[
					ft.Text(message.pseudo, size=12, weight="bold"),
					ft.Text(message.content),
				],
				spacing=2,
			),
			padding=10,
			bgcolor=ft.Colors.SURFACE_CONTAINER,
			border_radius=15,
		)

		# GestureDetector : on_long_press pour mobile, on_secondary_tap pour bureau
		self.controls = [
			ft.CircleAvatar(content=ft.Text(self.initials), bgcolor=self.avatar_color),
			ft.GestureDetector(
				content=msg_content,
				on_long_press=self.open_menu,  # <-- changement important
				on_secondary_tap=self.open_menu,  # clic droit / secondary tap (desktop)
			),
		]

	def _get_event_page(self, e):
		# récupération robuste de la page depuis l'événement
		return getattr(e, "page", None) or getattr(getattr(e, "control", None), "page", None)

	def open_menu(self, e):
		print(f"[ChatMessage] open_menu appelé pour : {self.message.content!r}")

		page = getattr(e, "page", None) or getattr(e.control, "page", None)
		if not page:
			return

		if self.bottom_sheet not in page.overlay:
			page.overlay.append(self.bottom_sheet)

		self.bottom_sheet.open = True
		page.update()

	def close_sheet_and_act(self, e, action):
		page = self._get_event_page(e)
		# fermer le sheet
		try:
			self.bottom_sheet.open = False
		except Exception:
			pass
		if page:
			page.update()

		# log action (ici à remplacer par ta logique métier)
		print(f"[ChatMessage] Action: {action} sur le message {self.message.content!r}")


# Vue principale du chat
async def ChatView(page: ft.Page):
	storage = ft.SharedPreferences()

	room_id = page.session.store.get("current_room_id")

	if not room_id:
		print("Le salon est introuvable !")
		await page.push_route("/rooms")
		page.update()

	# On récupère tous les messages
	token = await storage.get("cif_token")
	if not token:
		await page.push_route("/login")

	# 2. On prépare l'enveloppe (le header)
	headers = {"Authorization": f"Bearer {token}"}

	# 3. On demande la liste fraîche au serveur
	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(
				f"http://{host}:{port}/room/{room_id}/messages", headers=headers
			)

			# Si le jeton est expiré ou invalide (401)
			if response.status_code == 401:
				await storage.remove("cif_token")  # On nettoie
				print("Erreur lors de la récupération des messages !")
				await page.push_route("/rooms")  # On redirige
				return

			messages_received = response.json()
		# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
	except httpx.RequestError as ex:
		print(f"Erreur réseau : {ex}")
		room_name_input.error = "Serveur injoignable"
		room_description_input.error = "Serveur injoignable"
		page.update()
		return
	except Exception as e:
		# En cas de problème réseau par exemple
		print(f"Erreur de connexion : {e}")
		await page.push_route("/rooms")
		return

	# Loading screen
	loading_screen = ft.Column(
		[
			ft.ProgressBar(width=400),
			ft.Text("Chargement des messages...", italic=True),
		],
		horizontal_alignment="center",
	)

	container = ft.Container(
		content=loading_screen,
		expand=True,
		alignment=ft.Alignment.CENTER,
	)

	# ListView qui contiendra les messages
	chat_list = ft.ListView(
		expand=True,
		spacing=10,
		auto_scroll=True,
	)

	# Fonction pour "charger" l'historique (simulée)
	def load_history():
		container.content = chat_list
		page.update()

	async def send_click(e):
		if not new_message.value:
			return

		page.pubsub.send_all(
			Message(
				pseudo=await storage.get("user_pseudo"),
				content=new_message.value.strip(),
				message_type="chat_message",
			)
		)
		new_message.value = ""
		await new_message.focus()
		page.update()

	new_message = ft.TextField(
		hint_text="Écrivez un message...",
		filled=True,
		expand=True,
		min_lines=1,
		border_radius=20,
		shift_enter=True,
		on_submit=send_click,
	)

	async def go_to_rooms(e):
		await page.session.store.remove("current_room_id")
		await page.push_route("/rooms")
		page.update()

	# Réception d'un message via pubsub
	def on_message(message: Message):
		m = ChatMessage(message)
		if message.message_type == "chat_message":
			chat_list.controls.append(m)
		page.update()

	# On affiche les messages
	if messages_received:
		for message_to_show in messages_received:
			me = Message(
				pseudo=message_to_show["author_display_name"],
				content=message_to_show["content"],
				message_type=message_to_show["message_type"],
			)
			on_message(me)

	page.pubsub.subscribe(on_message)

	# AppBar
	app_bar = ft.AppBar(
		bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
		elevation=2,
		actions=[
			ft.IconButton(ft.Icons.LOGOUT_ROUNDED, tooltip="Retour", on_click=go_to_rooms),
			# ft.PopupMenuButton(  # Un petit menu "trois points" pour faire pro
			# 	items=[
			# 		ft.PopupMenuItem(icon=ft.Icons.INFO_OUTLINE, text="Infos du salon"),
			# 		ft.PopupMenuItem(icon=ft.Icons.NOTIFICATIONS_OFF_OUTLINED, text="Muer"),
			# 	]
			# ),
		],
		leading=ft.Icon(ft.Icons.FORUM_ROUNDED, color=ft.Colors.PRIMARY),
		leading_width=40,
		title=ft.Text(
			"Salon Général", size=20, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE
		),
		center_title=True,
	)

	# Lancer le chargement (non-bloquant depuis la page principale)
	# note: si tu déclenches load_history ici, attention au thread blocking dans ton app réelle
	# on peut l'appeler via page.session_future ou similaire si nécessaire.
	# Pour test rapide on l'appelle normalement (bloquant simulé)
	load_history()

	return ft.View(
		route="/chat",
		controls=[
			app_bar,
			ft.Container(
				content=chat_list,
				padding=0,
				expand=True,
			),
			ft.Container(
				content=ft.Row(
					[
						new_message,
						ft.IconButton(
							icon=ft.Icons.SEND_ROUNDED,
							icon_color=ft.Colors.BLUE_600,
							tooltip="Envoyer",
							on_click=send_click,
						),
					]
				),
				padding=ft.padding.Padding.only(left=10, right=10, bottom=10),
			),
		],
	)
