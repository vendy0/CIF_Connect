import flet as ft
from dataclasses import dataclass
from utils import generer_pseudo, get_initials, get_avatar_color, get_colors
import asyncio


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
		initials = get_initials(self.message.user)
		avatar_color = get_avatar_color(self.message.user, COLORS_LOOKUP)

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
			ft.CircleAvatar(content=ft.Text(initials), bgcolor=avatar_color),
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

	def send_click(e):
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
		new_message.focus()
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
		actions=[
			ft.IconButton(ft.Icons.LOGOUT, tooltip="Retour", on_click= go_to_rooms)
		],
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
				padding=ft.padding.only(left=10, right=10, bottom=10),
			),
		],
	)


# import flet as ft
# from dataclasses import dataclass
# from utils import generer_pseudo, get_initials, get_avatar_color, get_colors


# @dataclass
# class Message:
# 	user: str
# 	text: str
# 	message_type: str


# COLORS_LOOKUP = get_colors()

# import flet as ft
# from dataclasses import dataclass

# # ... (tes imports et dataclass Message restent identiques) ...


# class ChatMessage(ft.Row):
# 	def __init__(self, message: Message):
# 		super().__init__()
# 		self.message = message
# 		self.vertical_alignment = ft.CrossAxisAlignment.START

# 		# On prépare le BottomSheet (le menu qui s'ouvrira en bas)
# 		self.bottom_sheet = ft.BottomSheet(
# 			content=ft.Container(
# 				padding=10,
# 				content=ft.Column(
# 					tight=True,
# 					controls=[
# 						ft.ListTile(
# 							leading=ft.Icon(ft.Icons.FAVORITE_BORDER),
# 							title=ft.Text("Liker"),
# 							on_click=lambda e: self.close_sheet_and_act(e, "react"),
# 						),
# 						ft.ListTile(
# 							leading=ft.Icon(ft.Icons.REPLY),
# 							title=ft.Text("Répondre"),
# 							on_click=lambda e: self.close_sheet_and_act(e, "reply"),
# 						),
# 						ft.ListTile(
# 							leading=ft.Icon(ft.Icons.REPORT_GMAILERRORRED, color=ft.Colors.RED),
# 							title=ft.Text("Signaler", color=ft.Colors.RED),
# 							on_click=lambda e: self.close_sheet_and_act(e, "report"),
# 						),
# 					],
# 				),
# 			),
# 		)

# 		# Contenu visuel du message
# 		msg_content = ft.Container(
# 			content=ft.Column(
# 				[
# 					ft.Text(message.user, size=12, weight="bold"),
# 					ft.Text(message.text),
# 				],
# 				spacing=2,
# 			),
# 			padding=10,
# 			bgcolor=ft.Colors.SURFACE_CONTAINER,
# 			border_radius=15,
# 		)

# 		self.controls = [
# 			ft.CircleAvatar(content=ft.Text("AB"), bgcolor="blue"),  # Remplacer par tes fonctions
# 			ft.GestureDetector(
# 				content=msg_content,
# 				# C'est ici que la magie opère pour le Mobile
# 				on_long_press_start=self.open_menu,
# 				# Et pour le Desktop (Clic droit)
# 				on_secondary_tap=self.open_menu,
# 			),
# 		]

# 	def open_menu(self, e):
# 		print(f"Ouverture du menu pour : {self.message.text}")

# 		# 1. On attache le bottom_sheet à la page
# 		# Note: on utilise e.page ou e.control.page pour être sûr d'avoir la réf
# 		page = e.control.page
# 		page.bottom_sheet = self.bottom_sheet

# 		# 2. On déclare qu'il est ouvert
# 		self.bottom_sheet.open = True

# 		# 3. On met à jour la page pour afficher le changement
# 		page.update()

# 	def close_sheet_and_act(self, e, action):
# 		# 1. On ferme
# 		self.bottom_sheet.open = False
# 		e.control.page.update()
# 		# 2. On log l'action
# 		print(f"Action: {action} sur le message {self.message.text}")
# 		# Ici tu mettras ta logique (ex: if action == 'reply': ...)

# 	# if action == "react": on_react(self.message)...


# # class ChatMessage(ft.Row):
# # 	def __init__(self, message: Message):
# # 		super().__init__()
# # 		self.message = message
# # 		self.vertical_alignment = ft.CrossAxisAlignment.START
# # 		self.user_initials = get_initials(self.message.user)
# # 		self.avatar_color = get_avatar_color(self.message.user, COLORS_LOOKUP)

# # 		# Menu d'options (Réagir / Signaler / Répondre)
# # 		self.popup = ft.PopupMenuButton(
# # 			icon=ft.Icons.MORE_VERT,
# # 			visible=False,
# # 			items=[
# # 				ft.PopupMenuItem(
# # 					icon=ft.Icons.FAVORITE_BORDER,
# # 					content="Liker",
# # 					on_click=lambda _: on_react(message),
# # 				),
# # 				ft.PopupMenuItem(
# # 					icon=ft.Icons.REPORT_GMAILERRORRED,
# # 					content="Signaler",
# # 					on_click=lambda _: on_report(message),
# # 				),
# # 				ft.PopupMenuItem(
# # 					icon=ft.Icons.REPLY_SHARP,
# # 					content="Répondre",
# # 					on_click=lambda _: on_response(message),
# # 				),
# # 			],
# # 		)
# # 		self.controls = [
# # 			ft.CircleAvatar(content=ft.Text(get_initials(message.user)), bgcolor=self.avatar_color),
# # 			ft.GestureDetector(
# # 				on_long_press_start=self.handle_long_press,  # Pour mobile
# # 				content=ft.Container(
# # 					content=ft.Column(
# # 						[
# # 							ft.Text(message.user, size=12, weight="bold"),
# # 							ft.Text(message.text),
# # 						],
# # 						spacing=2,
# # 					),
# # 					padding=10,
# # 					bgcolor=ft.Colors.SURFACE_CONTAINER,
# # 					border_radius=15,
# # 				),
# # 			),
# # 			self.popup,
# # 		]

# # 	# Ta méthode modifiée
# # 	def handle_long_press(self, e: ft.Event[ft.PopupMenuButton]):
# # 		# On peut même récupérer la position si on voulait
# # 		# ouvrir un menu flottant personnalisé plus tard
# # 		self.popup.open = True
# # 		self.update()  # Plus performant que page.update() si tu changes juste ce composant

# # 	def show_options(self, e):
# # 		self.popup.open = True
# # 		self.page.update()


# def ChatView(page: ft.Page, current_user):
# 	# Simuler un chargement
# 	loading_screen = ft.Column(
# 		[
# 			ft.ProgressBar(width=400, color="blue"),
# 			ft.Text("Chargement des messages...", italic=True),
# 		],
# 		horizontal_alignment="center",
# 	)

# 	container = ft.Container(
# 		content=loading_screen,
# 		expand=True,
# 		alignment=ft.Alignment.CENTER,
# 	)

# 	# Fonction pour "charger" réellement
# 	def load_history():
# 		import time

# 		time.sleep(1.5)  # Simule le réseau
# 		container.content = chat_list
# 		page.update()

# 	# Fallback si pas de user
# 	if not current_user:
# 		current_user = pseudo

# 	chat_list = ft.ListView(
# 		expand=True,
# 		spacing=10,
# 		auto_scroll=True,
# 	)

# 	def send_click(e):
# 		if not new_message.value:
# 			return

# 		page.pubsub.send_all(
# 			Message(
# 				user=current_user,
# 				text=new_message.value.strip(),
# 				message_type="chat_message",
# 			)
# 		)
# 		new_message.value = ""
# 		new_message.focus()
# 		page.update()

# 	new_message = ft.TextField(
# 		hint_text="Écrivez un message...",
# 		filled=True,
# 		expand=True,
# 		min_lines=1,
# 		border_radius=20,
# 		shift_enter=True,
# 		on_submit=send_click,
# 	)

# 	def on_message(message: Message):
# 		if message.message_type == "chat_message":
# 			m = ChatMessage(message)
# 			chat_list.controls.append(m)
# 		page.update()

# 	# Abonnement au PubSub
# 	page.pubsub.subscribe(on_message)

# 	# AppBar avec bouton de déconnexion
# 	app_bar = ft.AppBar(
# 		leading=ft.Icon(ft.Icons.FORUM_ROUNDED),
# 		leading_width=40,
# 		title=ft.Text("Salon Général"),
# 		center_title=True,
# 		bgcolor=ft.Colors.DEEP_PURPLE_700,
# 		actions=[
# 			ft.IconButton(ft.Icons.LOGOUT, tooltip="Retour", on_click=lambda e: page.push_route("/rooms"))
# 		],
# 	)

# 	return ft.View(
# 		route="/chat",
# 		controls=[
# 			app_bar,
# 			ft.Container(
# 				content=chat_list,
# 				padding=0,
# 				expand=True,
# 			),
# 			ft.Container(
# 				content=ft.Row(
# 					[
# 						new_message,
# 						ft.IconButton(
# 							icon=ft.Icons.SEND_ROUNDED,
# 							icon_color=ft.Colors.BLUE_600,
# 							tooltip="Envoyer",
# 							on_click=send_click,
# 						),
# 					]
# 				),
# 				padding=ft.padding.only(left=10, right=10, bottom=10),
# 			),
# 		],
# 	)
