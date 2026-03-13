import flet as ft
from chat.models import Message
from utils import get_avatar_color, get_initials, COLORS_LOOKUP
from datetime import datetime, timedelta

# =============================================================================
# 2. COMPOSANTS VISUELS DES MESSAGES
# =============================================================================


class SystemMessage(ft.Row):
	def __init__(self, message: Message):
		super().__init__()
		self.alignment = ft.MainAxisAlignment.CENTER

		color = ft.Colors.GREEN_600 if message.message_type == "join" else ft.Colors.ERROR
		icon = ft.Icons.LOGIN_ROUNDED if message.message_type == "join" else ft.Icons.LOGOUT_ROUNDED

		self.controls = [
			ft.Container(
				content=ft.Row(
					[
						ft.Icon(icon, size=14, color=color),
						ft.Text(
							message.content,
							italic=True,
							size=12,
							color=ft.Colors.ON_SURFACE_VARIANT,
						),
					],
					tight=True,
					spacing=5,
				),
				bgcolor="surfacecontainerhighest",  # Syntaxe sécurisée
				padding=ft.padding.symmetric(horizontal=12, vertical=6),
				border_radius=15,
			)
		]


class BaseChatMessage(ft.Row):
	def __init__(self, message: Message, page: ft.Page, on_copy, on_reply, on_edit, on_report, on_react, on_delete):
		super().__init__()
		self.message = message
		key = str(self.message.id)
		self._page_ref = page
		self.on_copy = on_copy
		self.on_reply = on_reply
		self.on_edit = on_edit
		self.on_react = on_react
		self.on_report = on_report
		self.on_delete = on_delete
		# self.scroll_to_parent = scroll_to_parent
		self.vertical_alignment = ft.CrossAxisAlignment.START
		self.parent_bubble = ft.Container()
		self.content_text = ft.Text(self.message.content, size=15)
		self.modified_text = ft.Text("Modifié •", size=9, italic=True, visible=self.message.modified)
		self.reactions_container = ft.Container(content=self.get_reactions_row(), bottom=0)

		# Dans components.py, à l'intérieur de MyChatMessage et OtherChatMessage
		# On prépare le texte du timestamp
		self.timestamp = self.message.message_time.strftime("%H:%M")
		# Si le message n'est pas d'aujourd'hui, on ajoute la date
		if self.message.message_date != datetime.now().date():
			self.timestamp = f"{self.message.message_date.strftime('%d/%m')}  \t\t  {self.timestamp}"

		# 1. Message Parent (Reply) - Full Width (Style WhatsApp)
		if self.message.parent_id and self.message.parent_content:
			self.parent_bubble = ft.Container(
				content=ft.Column(
					[
						ft.Text(self.message.parent_author, size=11, weight="bold", color=get_avatar_color(self.message.parent_author)),
						ft.Text(self.message.parent_content, size=12, italic=True, max_lines=1, overflow="ellipsis"),
					],
					spacing=2,
				),
				padding=ft.padding.all(8),
				bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
				border_radius=5,
				border=ft.border.only(left=ft.BorderSide(3, ft.Colors.BLUE_400)),
				margin=ft.margin.only(bottom=5),
				# on_click=lambda _: self._page_ref.run_task(self.scroll_to_parent, self.message.parent_id),  # <-- On commente ça pour l'instant pour éviter un crash !
			)

	def update_ui(self):
		"""Méthode pour rafraîchir uniquement les textes du message"""
		self.content_text.value = self.message.content
		self.modified_text.visible = self.message.modified
		self.update()  # On demande à Flet de redessiner CE contrôle uniquement

	def update_reactions(self):
		"""Met à jour visuellement les emojis du message"""
		self.reactions_container.content = self.get_reactions_row()
		self.reactions_container.update()

	def get_reactions_row(self):
		reactions_row = ft.Row(spacing=4, tight=True)
		if self.message.reactions:
			for emoji, count in self.message.reactions.items():
				reactions_row.controls.append(
					ft.Container(
						content=ft.Text(f"{emoji} {count}", size=11),
						bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
						border_radius=10,
						padding=ft.padding.symmetric(horizontal=6, vertical=2),
						border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
					)
				)
		return reactions_row

	# Méthodes d'actions communes
	async def action_reply(self, e):
		# self._page_ref.show_dialog(self._page_ref.bottom_sheet)
		# self._page_ref.bottom_sheet.open = False
		self._page_ref.pop_dialog()
		self._page_ref.update()
		await self.on_reply(self.message)

	async def action_react(self, e):
		self._page_ref.pop_dialog()
		# self._page_ref.show_dialog(self._page_ref.bottom_sheet)
		self._page_ref.update()
		await self.on_react(e, self.message)

	# Fonction à ajouter dans ta classe :
	async def handle_swipe_reply(self, e: ft.DismissibleDismissEvent):
		# On déclenche la réponse
		await self.on_reply(self.message)
		await e.control.confirm_dismiss(False)
		# On renvoie False pour que le message revienne à sa place (il n'est pas supprimé)
		return False

	async def pass_func(self, e):
		pass


class MyChatMessage(BaseChatMessage):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.alignment = ft.MainAxisAlignment.END  # Aligné à droite
		self.reactions_container.left = 10

		# Menu spécifique : Copier, Modifier, Supprimer, Répondre
		self.menu_items = [
			ft.ListTile(
				leading=ft.Icon(ft.Icons.CONTENT_COPY),
				title=ft.Text("Copier"),
				on_click=lambda e: self._page_ref.run_task(self.on_copy, e, self._page_ref, self.message.content, "Message copié !"),
			),
			ft.ListTile(
				leading=ft.Icon(ft.Icons.EDIT),
				title=ft.Text("Modifier"),
				on_click=lambda e: self._page_ref.run_task(self.on_edit, e, self.message),
			)
			if (datetime.now() - timedelta(minutes=15)) < self.message.message_datetime
			else ft.Container(),
			ft.ListTile(
				leading=ft.Icon(ft.Icons.DELETE_OUTLINE, color="error"),
				title=ft.Text("Supprimer"),
				on_click=lambda e: self._page_ref.run_task(self.on_delete, e, self.message),
			)
			if (datetime.now() - timedelta(days=3)) < self.message.message_datetime
			else ft.Container(),
			ft.ListTile(
				leading=ft.Icon(ft.Icons.REPLY),
				title=ft.Text("Répondre"),
				on_click=self.action_reply,
			),
		]

		bubble = ft.GestureDetector(
			on_tap=lambda _: self.show_menu(),
			content=ft.Container(
				content=ft.Column(
					[
						self.parent_bubble,
						ft.Text(
							self.message.pseudo,
							size=12,
							weight="bold",
							color=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
						),
						self.content_text,
						ft.Row(
							[self.modified_text, ft.Text(self.timestamp, size=10)],
							alignment="end",
							spacing=1,
						),
					],
					tight=True,
					horizontal_alignment="stretch",
				),
				bgcolor=ft.Colors.PRIMARY_CONTAINER,  # Couleur différente pour nos messages
				padding=10,
				border_radius=ft.border_radius.only(top_left=15, top_right=0, bottom_left=15, bottom_right=15),
				width=200,
				# on_click=lambda _: self.show_menu(),
			),
		)

		bulle_complet = ft.Row(
			[
				ft.Stack(
					[
						ft.Column(
							[bubble, ft.Container(height=10 if self.message.reactions else 0)],
							tight=True,
						),
						self.reactions_container,  # Réactions à gauche pour nos messages
					],
				),
				ft.CircleAvatar(
					content=ft.Text(get_initials(self.message.pseudo)),
					bgcolor=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
				),
			],
			vertical_alignment=ft.CrossAxisAlignment.START,  # Aligne le haut de l'avatar au haut de la bulle
			alignment=ft.MainAxisAlignment.END,  # Garde le tout collé à droite
		)

		message_avec_swipe = ft.Dismissible(
			content=bulle_complet,
			dismiss_thresholds={ft.DismissDirection.START_TO_END: 0.1},
			dismiss_direction=ft.DismissDirection.START_TO_END,  # Glisser vers la droite
			background=ft.Container(
				bgcolor=ft.Colors.TRANSPARENT,
				padding=10,
				alignment=ft.Alignment.CENTER_LEFT,
				content=ft.Icon(ft.Icons.REPLY_ROUNDED, color=ft.Colors.PRIMARY),
			),
			# C'est ici qu'est la magie : on bloque la disparition de l'élément !
			on_confirm_dismiss=self.handle_swipe_reply,
		)

		self.controls = [message_avec_swipe]

	def show_menu(self):
		self._page_ref.bottom_sheet = ft.BottomSheet(ft.Container(ft.Column(self.menu_items, tight=True), padding=10))
		self._page_ref.show_dialog(self._page_ref.bottom_sheet)
		self._page_ref.update()


class OtherChatMessage(BaseChatMessage):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.alignment = ft.MainAxisAlignment.START
		self.reactions_container.right = 10

		# Menu spécifique : Répondre, Réagir, Signaler
		self.menu_items = [
			ft.ListTile(
				leading=ft.Icon(ft.Icons.CONTENT_COPY),
				title=ft.Text("Copier"),
				on_click=lambda e: self._page_ref.run_task(self.on_copy, e, self._page_ref, self.message.content, "Message copié !"),
			),
			ft.ListTile(
				leading=ft.Icon(ft.Icons.REPLY),
				title=ft.Text("Répondre"),
				on_click=lambda e: self._page_ref.run_task(self.action_reply, e),
			),
			ft.ListTile(
				leading=ft.Icon(ft.Icons.FAVORITE_BORDER),
				title=ft.Text("Réagir"),
				on_click=self.action_react,
			),
			ft.ListTile(
				leading=ft.Icon(ft.Icons.REPORT, color="error"),
				title=ft.Text("Signaler"),
				on_click=lambda e: self._page_ref.run_task(self.on_report, e, self.message),
			),
		]

		# Construction UI (Bulle classique à gauche avec Avatar)
		bubble = self.build_bubble(ft.Colors.SURFACE_CONTAINER_HIGHEST)

		bulle_complet = ft.Row(
			[
				ft.CircleAvatar(
					content=ft.Text(get_initials(self.message.pseudo)),
					bgcolor=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
				),
				ft.Stack(
					[
						self.parent_bubble,
						ft.Column(
							[bubble, ft.Container(height=10 if self.message.reactions else 0)],
							tight=True,
						),
						self.reactions_container,
					]
				),
			],
			vertical_alignment=ft.CrossAxisAlignment.START,  # Aligne le haut de l'avatar au haut de la bulle
			alignment=ft.MainAxisAlignment.START,  # Garde le tout collé à droite
		)

		message_avec_swipe = ft.Dismissible(
			content=bulle_complet,
			dismiss_thresholds={ft.DismissDirection.START_TO_END: 0.1},
			dismiss_direction=ft.DismissDirection.START_TO_END,  # Glisser vers la droite
			background=ft.Container(
				bgcolor=ft.Colors.TRANSPARENT,
				padding=10,
				alignment=ft.Alignment.CENTER_LEFT,
				content=ft.Icon(ft.Icons.REPLY_ROUNDED, color=ft.Colors.PRIMARY),
			),
			# C'est ici qu'est la magie : on bloque la disparition de l'élément !
			on_confirm_dismiss=self.handle_swipe_reply,
		)
		self.controls = [message_avec_swipe]

	def build_bubble(self, color):
		# Code de ta bulle actuelle (avec max_width=200)
		return ft.GestureDetector(
			on_tap=lambda _: self.show_menu(),
			# on_long_press=lambda _: self.show_menu(),
			content=ft.Container(
				content=ft.Column(
					[
						self.parent_bubble,
						ft.Text(
							self.message.pseudo,
							size=12,
							weight="bold",
							color=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
						),
						self.content_text,
						ft.Row(
							[self.modified_text, ft.Text(self.timestamp, size=10)],
							alignment="end",
							spacing=2,
						),
					],
					tight=True,
					horizontal_alignment="stretch",
				),
				bgcolor=color,
				padding=10,
				border_radius=ft.border_radius.only(top_left=0, top_right=15, bottom_left=15, bottom_right=15),
				width=200,
				# on_click=lambda _: self.show_menu(),
			),
		)

	def show_menu(self):
		self._page_ref.bottom_sheet = ft.BottomSheet(ft.Container(ft.Column(self.menu_items, tight=True), padding=10))
		self._page_ref.show_dialog(self._page_ref.bottom_sheet)
		self._page_ref.update()
