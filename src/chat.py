import flet as ft
from dataclasses import dataclass

# Assurez-vous que utils.py est dans le même dossier
from utils import generer_pseudo, get_initials, get_avatar_color, get_colors


@dataclass
class Message:
	user: str
	text: str
	message_type: str


# Chargement des couleurs
COLORS_LOOKUP = get_colors()


class ChatMessage(ft.Row):
	def __init__(self, message: Message):
		super().__init__()
		self.message = message
		self.vertical_alignment = ft.CrossAxisAlignment.START

		# On recalcule les initiales/couleurs à la volée pour l'affichage
		# (Plus sûr que de les stocker en session)
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


def main(page: ft.Page):
	page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
	page.title = "CIF Connect"

	# --- Gestion des Préférences (Via Session au lieu de ClientStorage) ---
	# def get_user_preferences():
	#     # page.session fonctionne comme un dictionnaire temporaire
	#     if not page.session.contains_key("user_name"):
	#         pseudo = generer_pseudo()
	#         page.session.set("user_name", pseudo)

	#     return page.session.get("user_name")

	# Récupération du pseudo actuel
	# current_user = get_user_preferences()
	current_user = generer_pseudo()

	# --- UI ---
	chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)

	def send_click(e):
		if not new_message.value:
			new_message.error = "Il n'y a rien à envoyer !"
			new_message.update()
			return

		new_message.error = None

		# On récupère le nom depuis la session
		user_name = current_user

		page.pubsub.send_all(
			Message(
				user=user_name,
				text=new_message.value,
				message_type="chat_message",
			)
		)
		new_message.value = ""
		new_message.focus()
		page.update()

	new_message = ft.TextField(
		autofocus=True,
		shift_enter=True,
		hint_text="Écrivez un message...",
		filled=True,
		expand=True,
		min_lines=1,
		on_submit=send_click,
	)

	# --- PubSub ---
	def on_message(message: Message):
		if message.message_type == "chat_message":
			m = ChatMessage(message)
			chat.controls.append(m)
		elif message.message_type == "login_message":
			chat.controls.append(
				ft.Text(
					message.text,
					italic=True,
					color=ft.Colors.ORANGE_500,
					size=12,
					text_align=ft.TextAlign.CENTER,
				)
			)
		page.update()

	page.pubsub.subscribe(on_message)

	def join_click(e):
		welcome_dialog.open = False
		page.update()

		user_name = current_user
		page.pubsub.send_all(
			Message(
				user=user_name,
				text=f"{user_name} a rejoint le chat.",
				message_type="login_message",
			)
		)

	# Note : Sur les vieilles versions, page.overlay n'existe pas toujours,
	# on utilise donc page.dialog pour être sûr.
	welcome_dialog = ft.AlertDialog(
		open=True,
		modal=True,
		title=ft.Text(f"Bienvenue {current_user} !"),
		content=ft.Text("Votre identité est anonymisée (Adjectif + Adjectif + Nombre)."),
		actions=[ft.Button(content="Rejoindre", on_click=join_click)],
		actions_alignment=ft.MainAxisAlignment.END,
	)

	page.show_dialog(welcome_dialog)

	page.add(
		ft.Container(
			content=chat,
			padding=10,
			expand=True,
		),
		ft.Row(
			[
				new_message,
				ft.IconButton(
					icon=ft.Icons.SEND_ROUNDED,
					tooltip="Envoyer message",
					on_click=send_click,
				),
			]
		),
	)


# Utilisation standard moderne :
ft.run(main)

# Si votre version vous oblige VRAIMENT à utiliser run, décommentez la ligne ci-dessous
# et commentez la ligne ft.app ci-dessus :
# ft.run(target=main)
