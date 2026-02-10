import flet as ft
from dataclasses import dataclass
from utils import get_initials, get_avatar_color, get_colors


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
			ft.CircleAvatar(
				content=ft.Text(self.user_initials),
				color=ft.Colors.WHITE,
				bgcolor=self.avatar_color,
			),
			ft.Column(
				tight=True,
				spacing=5,
				controls=[
					ft.Text(self.message.user, weight=ft.FontWeight.BOLD),
					ft.Text(self.message.text, selectable=True),
				],
			),
		]


def ChatView(page: ft.Page, current_user):
	# Fallback si pas de user
	if not current_user:
		current_user = "Anonyme"

	chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

	def send_click(e):
		if not new_message.value:
			return

		page.pubsub.send_all(
			Message(
				user=current_user,
				text=new_message.value,
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
		center_title=False,
		bgcolor=ft.Colors.DEEP_PURPLE_700,
		actions=[
			ft.IconButton(ft.Icons.LOGOUT, tooltip="Déconnexion", on_click=lambda e: page.go("/"))
		],
	)

	return ft.View(
		route="/chat",
		controls=[
			app_bar,
			ft.Container(
				content=chat_list,
				padding=10,
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
