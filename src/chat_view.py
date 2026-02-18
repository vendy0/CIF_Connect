import flet as ft
from dataclasses import dataclass
from utils import generer_pseudo, get_initials, get_avatar_color, get_colors
import asyncio
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
	user: str
	text: str
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
		self.initials = get_initials(self.message.user)
		self.avatar_color = get_avatar_color(self.message.user, COLORS_LOOKUP)

		msg_content = ft.Container(
			content=ft.Column(
				[
					ft.Text(message.user, size=12, weight="bold"),
					ft.Text(message.text),
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
		print(f"[ChatMessage] open_menu appelé pour : {self.message.text!r}")

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
		print(f"[ChatMessage] Action: {action} sur le message {self.message.text!r}")


# Vue principale du chat
async def ChatView(page: ft.Page):
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
	async def load_history():
		import time

		await time.sleep(1.0)
		container.content = chat_list
		page.update()

	async def send_click(e):
		if not new_message.value:
			return

		page.pubsub.send_all(
			Message(
				user=page.session.store.get("pseudo"),
				text=new_message.value.strip(),
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
		await page.push_route(
			"/rooms"
		)  # Note: push_route est souvent remplacé par go_async dans les versions récentes

	# Réception d'un message via pubsub
	def on_message(message: Message):
		if message.message_type == "chat_message":
			m = ChatMessage(message)
			chat_list.controls.append(m)
		page.update()

	page.pubsub.subscribe(on_message)

	# AppBar
	app_bar = ft.AppBar(
		leading=ft.Icon(ft.Icons.FORUM_ROUNDED),
		leading_width=40,
		title=ft.Text("Salon Général"),
		center_title=True,
		bgcolor=ft.Colors.DEEP_PURPLE_700,
		actions=[ft.IconButton(ft.Icons.LOGOUT, tooltip="Retour", on_click=go_to_rooms)],
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
