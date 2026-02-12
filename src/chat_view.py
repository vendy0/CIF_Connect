import flet as ft
from dataclasses import dataclass
from utils import generer_pseudo, get_initials, get_avatar_color, get_colors


@dataclass
class Message:
	user: str
	text: str
	message_type: str


COLORS_LOOKUP = get_colors()


class ChatMessage(ft.Row):
	def __init__(self, message: Message):
		super().__init__()
		self.message = message
		self.vertical_alignment = ft.CrossAxisAlignment.START
		self.user_initials = get_initials(self.message.user)
		self.avatar_color = get_avatar_color(self.message.user, COLORS_LOOKUP)
		self.controls = [
			ft.CircleAvatar(content=ft.Text(get_initials(message.user)), bgcolor=self.avatar_color),
			ft.GestureDetector(
				on_long_press_start=lambda _: self.show_options(),  # Pour mobile
				content=ft.Container(
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
				),
			),
			# Menu d'options (Réagir / Signaler)
			ft.PopupMenuButton(
				icon=ft.Icons.MORE_VERT,
				items=[
					ft.PopupMenuItem(
						icon=ft.Icons.FAVORITE_BORDER,
						content="Liker",
						on_click=lambda _: on_react(message),
					),
					ft.PopupMenuItem(
						icon=ft.Icons.REPORT_GMAILERRORRED,
						content="Signaler",
						on_click=lambda _: on_report(message),
					),
					ft.PopupMenuItem(
						icon=ft.Icons.REPLY_SHARP,
						content="Répondre",
						on_click=lambda _: on_response(message),
					),
				],
			),
		]


def ChatView(page: ft.Page, current_user):
	# Simuler un chargement
	loading_screen = ft.Column(
		[
			ft.ProgressBar(width=400, color="blue"),
			ft.Text("Chargement des messages...", italic=True),
		],
		horizontal_alignment="center",
	)

	container = ft.Container(
		content=loading_screen,
		expand=True,
		alignment=ft.Alignment.CENTER,
	)

	# Fonction pour "charger" réellement
	def load_history():
		import time

		time.sleep(1.5)  # Simule le réseau
		container.content = chat_list
		page.update()

	# Fallback si pas de user
	if not current_user:
		current_user = pseudo

	chat_list = ft.ListView(
		expand=True,
		spacing=10,
		auto_scroll=True,
	)

	def send_click(e):
		if not new_message.value:
			return

		page.pubsub.send_all(
			Message(
				user=current_user,
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

	def on_message(message: Message):
		if message.message_type == "chat_message":
			m = ChatMessage(message)
			chat_list.controls.append(m)
		page.update()

	# Abonnement au PubSub
	page.pubsub.subscribe(on_message)

	# AppBar avec bouton de déconnexion
	app_bar = ft.AppBar(
		leading=ft.Icon(ft.Icons.FORUM_ROUNDED),
		leading_width=40,
		title=ft.Text("Salon Général"),
		center_title=True,
		bgcolor=ft.Colors.DEEP_PURPLE_700,
		actions=[
			ft.IconButton(
				ft.Icons.LOGOUT,
				tooltip="Déconnexion",
				on_click=lambda e: page.go("/rooms"),
			)
		],
	)

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
