import flet as ft
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, date, time, timedelta
import httpx
from utils import (
	get_initials,
	get_avatar_color,
	get_colors,
	host,
	port,
	show_top_toast,
	format_date,
	api,
)
import asyncio


# =============================================================================
# 1. MODÈLES DE DONNÉES
# =============================================================================


@dataclass
class Message:
	id: int
	pseudo: str
	content: str
	message_type: str
	modified: bool
	message_datetime: datetime
	message_date: date
	message_time: time
	parent_id: Optional[int] = None
	parent_content: Optional[str] = None
	parent_author: Optional[str] = None
	reactions: dict = field(default_factory=dict)


COLORS_LOOKUP = get_colors()

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


# class ChatMessage(ft.Row):  # On repasse en Row pour mettre l'Avatar à gauche
#     def __init__(
#         self,
#         message: Message,
#         current_pseudo: str,
#         page: ft.Page,
#         on_reply,
#         on_edit,
#         on_report,
#         on_react,
#     ):
#         super().__init__()
#         self.message = message
#         self.current_pseudo = current_pseudo
#         self._page_ref = page
#         self.on_reply = on_reply
#         self.on_edit = on_edit
#         self.on_react = on_react
#         self.on_report = on_report
#         self.vertical_alignment = ft.CrossAxisAlignment.START  # Aligne l'avatar en haut

#         # --- Création du BottomSheet (Standard 0.80.5) ---
#         self.bottom_sheet = ft.BottomSheet(
#             content=ft.Container(
#                 padding=10,
#                 content=ft.Column(
#                     tight=True,
#                     controls=[
#                         ft.ListTile(
#                             leading=ft.Icon(ft.Icons.REPLY),
#                             title=ft.Text("Répondre"),
#                             on_click=self.action_reply,
#                         ),
#                         ft.ListTile(
#                             leading=ft.Icon(ft.Icons.EDIT),
#                             title=ft.Text("Modifier"),
#                             on_click=self.action_edit,
#                         )
#                         if self.message.pseudo == self.current_pseudo and (datetime.now() - timedelta(minutes=15)) < message.message_datetime
#                         else ft.Container(),
#                         ft.ListTile(
#                             leading=ft.Icon(ft.Icons.FAVORITE_BORDER),
#                             title=ft.Text("Réagir"),
#                             on_click=self.action_react,
#                         ),
#                         ft.ListTile(
#                             leading=ft.Icon(ft.Icons.REPORT_GMAILERRORRED, color=ft.Colors.ERROR),
#                             title=ft.Text("Signaler", color=ft.Colors.ERROR),
#                             on_click=self.action_report,
#                         ),
#                     ],
#                 ),
#             ),
#         )

#         # --- Construction du contenu de la bulle ---
#         parent_bubble = []

#         # 1. Message Parent (Reply) - Full Width (Style WhatsApp)
#         if self.message.parent_content and self.message.parent_author:
#             parent_bubble.append(
#                 ft.Container(
#                     content=ft.Column(
#                         [
#                             ft.Text(
#                                 self.message.parent_author,
#                                 size=11,
#                                 weight="bold",
#                                 color=ft.Colors.PRIMARY,
#                             ),
#                             ft.Text(
#                                 self.message.parent_content,
#                                 size=12,
#                                 max_lines=1,
#                                 overflow=ft.TextOverflow.ELLIPSIS,
#                                 italic=True,
#                                 selectable=True,
#                             ),
#                         ],
#                         spacing=1,
#                     ),
#                     padding=ft.padding.all(8),
#                     # Marge en bas pour espacer du vrai message
#                     margin=ft.margin.only(bottom=5),
#                     bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE_VARIANT),
#                     border=ft.border.only(left=ft.BorderSide(4, ft.Colors.PRIMARY)),
#                     border_radius=5,
#                 )
#             )

#         # 2. Pseudo et Contenu
#         parent_bubble.extend(
#             [
#                 ft.Text(
#                     self.message.pseudo,
#                     size=12,
#                     weight="bold",
#                     color=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
#                 ),
#                 ft.Text(self.message.content, size=15, selectable=True),
#             ]
#         )

#         # 1. Prépare tes réactions à part (ne les ajoute PAS à bubble_items)
#         reactions_row = ft.Row(spacing=4, tight=True)
#         if self.message.reactions:
#             for emoji, count in self.message.reactions.items():
#                 reactions_row.controls.append(
#                     ft.Container(
#                         content=ft.Text(f"{emoji} {count}", size=11),
#                         bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
#                         border_radius=10,
#                         padding=ft.padding.symmetric(horizontal=6, vertical=2),
#                         border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
#                     )
#                 )

#         # 4. Heure (Conservée selon ton code)
#         parent_bubble.extend(
#             [
#                 ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
#                 ft.Row(
#                     controls=[
#                         ft.Text(
#                             self.message.message_time.strftime("%H:%M"),
#                             size=10,
#                             color=ft.Colors.ON_SURFACE_VARIANT,
#                             weight="bold",
#                         ),
#                     ],
#                     alignment=ft.MainAxisAlignment.END,
#                 ),
#             ]
#         )

#         # --- Assemblage final ---
#         main_bubble = ft.GestureDetector(
#             on_long_press=self.open_menu,
#             content=ft.Container(
#                 # L'ASTUCE ICI : CrossAxisAlignment.STRETCH force le message parent à prendre toute la largeur !
#                 content=ft.Column(
#                     parent_bubble,
#                     spacing=2,
#                     tight=True,
#                     horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
#                 ),
#                 bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
#                 padding=10,
#                 border_radius=10,
#                 width=200,  # Largeur fixée pour un rendu propre type mobile
#             ),
#         )

#         self.controls = [
#             ft.CircleAvatar(
#                 content=ft.Text(get_initials(self.message.pseudo)),
#                 bgcolor=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
#             ),
#             ft.Stack(
#                 [
#                     ft.Column(
#                         [
#                             main_bubble,
#                             ft.Container(height=10) if self.message.reactions else ft.Container(),  # Espace pour pas que ça chevauche le msg suivant
#                         ],
#                         tight=True,
#                     ),
#                     # Le badge flottant
#                     ft.Container(
#                         content=reactions_row,
#                         bottom=0,  # Aligné sur le bas
#                         right=10,  # Un peu décalé du bord droit
#                         # offset=ft.Offset(0, -0.5),  # DÉPLACE le container de moitié vers le bas (flottant)
#                     )
#                     if self.message.reactions
#                     else ft.Container(),
#                 ]
#             ),
#         ]

#     # --- Méthodes d'action 0.80.5 ---
#     async def open_menu(self, e):
#         self._page_ref.show_dialog(self.bottom_sheet)

#     async def action_reply(self, e):
#         self._page_ref.pop_dialog()
#         await self.on_reply(self.message)

#     async def action_edit(self, e):
#         self._page_ref.pop_dialog()
#         await self.on_edit(e, self.message)

#     async def action_react(self, e):
#         self._page_ref.pop_dialog()
#         await self.on_react(e, self.message)

#     async def action_report(self, e):
#         self._page_ref.pop_dialog()
#         await self.on_report(self.message)


class BaseChatMessage(ft.Row):
	def __init__(
		self,
		message: Message,
		page: ft.Page,
		on_copy,
		on_reply,
		on_edit,
		on_report,
		on_react,
		on_delete,
	):
		super().__init__()
		self.message = message
		self._page_ref = page
		self.on_copy = on_copy
		self.on_reply = on_reply
		self.on_edit = on_edit
		self.on_react = on_react
		self.on_report = on_report
		self.on_delete = on_delete
		self.vertical_alignment = ft.CrossAxisAlignment.START
		self.parent_bubble = ft.Container()

		# 1. Message Parent (Reply) - Full Width (Style WhatsApp)
		if self.message.parent_content and self.message.parent_author:
			self.parent_bubble = ft.Container(
				content=ft.Column(
					[
						ft.Text(
							self.message.parent_author,
							size=11,
							weight="bold",
							color=ft.Colors.PRIMARY,
						),
						ft.Text(
							self.message.parent_content,
							size=12,
							max_lines=1,
							overflow=ft.TextOverflow.ELLIPSIS,
							italic=True,
						),
					],
					spacing=1,
				),
				padding=ft.padding.all(8),
				# Marge en bas pour espacer du vrai message
				margin=ft.margin.only(bottom=5),
				bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE_VARIANT),
				border=ft.border.only(left=ft.BorderSide(4, ft.Colors.PRIMARY)),
				border_radius=5,
			)

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

	def action_react(self, e):
		self._page_ref.show_dialog(self._page_ref.bottom_sheet)
		self._page_ref.update()
		self.on_react(e, self.message)

	async def pass_func(self, e):
		pass


class MyChatMessage(BaseChatMessage):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.alignment = ft.MainAxisAlignment.END  # Aligné à droite

		# Menu spécifique : Modifier, Supprimer, Répondre
		self.menu_items = [
			ft.ListTile(
				leading=ft.Icon(ft.Icons.CONTENT_COPY),
				title=ft.Text("Copier"),
				on_click=lambda e: self._page_ref.run_task(self.on_copy, e, self.message),
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
			on_long_press=self.pass_func,
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
						ft.Text(
							self.message.content,
							size=15,
							color=ft.Colors.ON_PRIMARY_CONTAINER,
						),
						ft.Row(
							[
								ft.Text("Modifié • ", size=9, italic=True)
								if self.message.modified
								else ft.Container(),
								ft.Text(self.message.message_time.strftime("%H:%M"), size=10),
							],
							alignment="end",
							spacing=1,
						),
					],
					tight=True,
					horizontal_alignment="stretch",
				),
				bgcolor=ft.Colors.PRIMARY_CONTAINER,  # Couleur différente pour nos messages
				padding=10,
				border_radius=ft.border_radius.only(
					top_left=15, top_right=0, bottom_left=15, bottom_right=15
				),
				width=200,
				on_click=lambda _: self.show_menu(),
			),
		)

		self.controls = [
			ft.Stack(
				[
					ft.Column(
						[bubble, ft.Container(height=10 if self.message.reactions else 0)],
						tight=True,
					),
					ft.Container(
						content=self.get_reactions_row(), bottom=0, left=10
					),  # Réactions à gauche pour nos messages
				]
			),
			ft.CircleAvatar(
				content=ft.Text(get_initials(self.message.pseudo)),
				bgcolor=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
			),
			# Pas d'avatar à droite (style moderne) ou tu peux le rajouter après le stack
		]

	def show_menu(self):
		self._page_ref.bottom_sheet = ft.BottomSheet(
			ft.Container(ft.Column(self.menu_items, tight=True), padding=10)
		)
		self._page_ref.show_dialog(self._page_ref.bottom_sheet)
		self._page_ref.update()


class OtherChatMessage(BaseChatMessage):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.alignment = ft.MainAxisAlignment.START

		# Menu spécifique : Répondre, Réagir, Signaler
		self.menu_items = [
			ft.ListTile(
				leading=ft.Icon(ft.Icons.CONTENT_COPY),
				title=ft.Text("Copier"),
				on_click=lambda e: self._page_ref.run_task(self.on_copy, e, self.message),
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
				on_click=lambda _: self.on_report(self.message),
			),
		]

		# Construction UI (Bulle classique à gauche avec Avatar)
		bubble = self.build_bubble(ft.Colors.SURFACE_CONTAINER_HIGHEST)

		self.controls = [
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
					ft.Container(content=self.get_reactions_row(), bottom=0, right=10),
				]
			),
		]

	def build_bubble(self, color):
		# Code de ta bulle actuelle (avec max_width=200)
		return ft.GestureDetector(
			on_long_press=self.pass_func,
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
						ft.Text(self.message.content, size=15),
						ft.Row(
							[
								ft.Text("Modifié •", size=9, italic=True)
								if self.message.modified
								else ft.Container(),
								ft.Text(self.message.message_time.strftime("%H:%M"), size=10),
							],
							alignment="end",
							spacing=2,
						),
					],
					tight=True,
					horizontal_alignment="stretch",
				),
				bgcolor=color,
				padding=10,
				border_radius=ft.border_radius.only(
					top_left=0, top_right=15, bottom_left=15, bottom_right=15
				),
				width=200,
				on_click=lambda _: self.show_menu(),
			),
		)

	def show_menu(self):
		self._page_ref.bottom_sheet = ft.BottomSheet(
			ft.Container(ft.Column(self.menu_items, tight=True), padding=10)
		)
		self._page_ref.show_dialog(self._page_ref.bottom_sheet)
		self._page_ref.update()


# =============================================================================
# 3. VUE PRINCIPALE DU CHAT
# =============================================================================


async def ChatView(page: ft.Page):
	# last_date Pour afficher une division si il y a changement de jour
	storage = ft.SharedPreferences()
	token = await storage.get("cif_token")

	current_room_id = page.session.store.get("current_room_id") or 1
	current_room_name = page.session.store.get("current_room_name") or "Salon Inconnue..."
	current_pseudo = await storage.get("user_pseudo") or "Anonyme"

	replying_to_message: Optional[Message] = None

	if not current_room_id:
		await show_top_toast(page, "Le salon est introuvable !", True)
		await page.push_route("/rooms")
		page.update()

	if not token:
		await page.push_route("/login")

	# On récupère tous les messages
	# 2. On prépare l'enveloppe (le header)

	# Le bouton (caché par défaut)
	scroll_btn = ft.FloatingActionButton(
		icon=ft.Icons.ARROW_DOWNWARD,
		visible=False,
		mini=True,
		on_click=lambda e: chat_list.scroll_to(offset=-1, duration=300),  # -1 scroll tout en bas
	)

	# Fonction déclenchée quand on défile
	def list_scrolled(e: ft.OnScrollEvent = None):
		# Si on est remonté de plus de 100 pixels depuis le bas
		if e.pixels < (e.max_scroll_extent - 100):
			if not scroll_btn.visible:
				scroll_btn.visible = True
				scroll_btn.update()
		else:
			if scroll_btn.visible:
				scroll_btn.visible = False
				scroll_btn.update()

	chat_list = ft.ListView(expand=True, spacing=15, auto_scroll=True, padding=10)
	# on_scroll=list_scrolled

	# 3. On demande la liste fraîche au serveur
	try:
		response = await api.get(f"/room/{current_room_id}/messages")

		# Si le jeton est expiré ou invalide (401)
		if response.status_code == 401:
			await show_top_toast(page, "La session a expiré !", True)
			await page.push_route("/login")  # On redirige
			return
		#
		messages_received = response.json()

	# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
	except httpx.RequestError as ex:
		await show_top_toast(page, "Erreur réseau !", True)
		return

	# except Exception as e:
	#     # En cas de problème réseau par exemple
	#     await show_top_toast(page, "Erreur de connexion !", True)
	#     await page.push_route("/rooms")
	#     return
	# finally:
	#     pass

	reply_banner = ft.Container(
		visible=False,
		bgcolor="surfacevariant",
		padding=10,
		border_radius=ft.border_radius.only(top_left=15, top_right=15),
		content=ft.Row(
			alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
			controls=[
				ft.Column(
					spacing=0,
					controls=[
						ft.Text("Réponse à", size=11, color="primary"),
						ft.Text("", size=13, italic=True, no_wrap=True),
					],
				),
				ft.IconButton(
					ft.Icons.CLOSE,
					icon_size=16,
					on_click=lambda e: e.page.run_task(cancel_reply, e),
				),
				# Sera awaité plus tard
			],
		),
	)

	new_message = ft.TextField(
		hint_text="Écrivez un message...",
		capitalization=ft.TextCapitalization.SENTENCES,
		autofocus=False,
		expand=True,
		min_lines=1,
		border_radius=20,
		shift_enter=True,
		on_submit=lambda e: send_click(e),  # Sera awaité via le framework Flet
	)

	async def go_to_rooms(e):
		page.session.store.remove("current_room_id")
		page.session.store.remove("current_room_name")
		await page.push_route("/rooms")

	async def cancel_reply(e):
		nonlocal replying_to_message
		replying_to_message = None
		reply_banner.visible = False
		reply_banner.content.controls[0].controls[1].value = ""
		page.update()

	async def prepare_reply(msg: Message):
		nonlocal replying_to_message
		replying_to_message = msg
		reply_banner.visible = True
		reply_banner.content.controls[0].controls[1].value = f"{msg.pseudo}: {msg.content[:30]}..."
		await new_message.focus()
		page.update()

	async def copy_message(e, msg: Message):
		await ft.Clipboard().set(msg.content)
		page.pop_dialog()
		await show_top_toast(page, "Message copié.")

	async def edit_message(e, msg: Message):
		async def valider_changement(e):
			page.pop_dialog()
			msg.content = edit_message_input.value.strip()

			try:
				response = await api.put(f"/message/{msg.id}", data={"content": msg.content})
				# Si le jeton est expiré ou invalide (401)
				if response.status_code not in [200, 201]:
					edit_message_input.error = response.json().get("detail", "Erreur inconnue")
					await show_top_toast(page, "La session a expiré !", True)
					return

				page.update()
				# print(f"Message modifié : {msg.content}")
			# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
			except httpx.RequestError as ex:
				await show_top_toast(page, "Erreur réseau !", True)
				await page.push_route("/rooms")
				return
			# except Exception as e:
			#     # En cas de problème réseau par exemple
			#     await show_top_toast(page, "Erreur server !", True)
			#     # print(e)
			#     await page.push_route("/rooms")
			#     return

		async def fermer_dialogue(e):
			page.pop_dialog()

		page.pop_dialog()

		edit_message_input = ft.TextField(
			value=msg.content, label="Message", multiline=True, autofocus=True
		)
		dlg = ft.AlertDialog(
			title=ft.Text("Modifier le message"),
			modal=True,
			content=ft.Column(edit_message_input, tight=True),
			actions=[
				ft.ElevatedButton("Valider", on_click=valider_changement),
				ft.TextButton("Annuler", on_click=fermer_dialogue),
			],
			actions_alignment=ft.MainAxisAlignment.CENTER,
		)

		page.show_dialog(dlg)

	async def react_to_message(e, msg: Message):
		# Liste de tes emojis supportés
		emojis = ["👍", "❤️", "😂", "😮", "😢", "😡"]
		emoji_selected = None

		async def on_emoji_click(click_event, emoji_char):
			# 1. Fermer le menu en priorité (Flet 0.80.5 style)
			page.pop_dialog()
			# 2. Appeler ton API pour envoyer la réaction
			try:
				response = await api.post(f"/message/{msg.id}/reaction", data={"emoji": emoji_char})
				# Si le jeton est expiré ou invalide (401)
				if response.status_code == 401:
					await show_top_toast(page, "La session a expiré !", True)
					await page.push_route("/login")  # On redirige
					return

			# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
			except httpx.RequestError as ex:
				await show_top_toast(page, "Erreur réseau !", True)
				await page.push_route("/rooms")
				return
			# except Exception as e:
			#     # En cas de problème réseau par exemple
			#     await show_top_toast("Erreur server !")
			#     await page.push_route("/rooms")
			#     return

		# Construction de la grille d'emojis
		emoji_row = ft.Row(
			controls=[
				ft.TextButton(
					em, on_click=lambda ce, em=em: ce.page.run_task(on_emoji_click, ce, em)
				)
				for em in emojis
			],
			alignment=ft.MainAxisAlignment.SPACE_EVENLY,
		)

		picker = ft.BottomSheet(content=ft.Container(content=emoji_row, padding=20, height=100))
		page.show_dialog(picker)

	async def report_message(msg: Message):
		report_reason_input = ft.TextField(label="Raison du signalement", multiline=True)

		async def submit_report(e):
			if not report_reason_input.value.strip():
				report_reason_input.error = "Le champ ne doit pas être vide !"
				return

			report_dialog.open = False

			# 3. On demande la liste fraîche au serveur
			try:
				payload = {"message_id": msg.id, "raison": report_reason_input.value.strip()}
				response = await api.post(f"/reports", data=payload)

				# Si le jeton est expiré ou invalide (401)
				if response.status_code != 201:
					await show_top_toast(page, "Erreur lors du signalement !", True)
					report_reason_input.error = "Il y a eu urreur lors du signalement !"
					return

				await show_top_toast(page, "Signalement envoyé à la modération.")

			# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
			except httpx.RequestError as ex:
				await show_top_toast(page, "Erreur réseau !", True)
				report_reason_input.error = "Serveur injoignable"
				page.update()
				return
			# except Exception as e:
			#     # En cas de problème réseau par exemple
			#     report_reason_input.error = "Erreur de connexion !"
			#     page.update()
			#     await show_top_toast(page, "Erreur de connexion !", True)
			#     return

		def cancel_report(e):
			report_dialog.open = False
			page.update()

		report_dialog = ft.AlertDialog(
			title=ft.Text("Signaler ce message"),
			content=ft.Column(
				tight=True,
				controls=[
					ft.Text(f"Message de {msg.pseudo} :"),
					ft.Text(f'"{msg.content}"', italic=True),
					report_reason_input,
				],
			),
			actions=[
				ft.TextButton(content="Annuler", on_click=cancel_report),
				ft.ElevatedButton(
					"Envoyer",
					bgcolor=ft.Colors.ERROR,
					color=ft.Colors.WHITE,
					on_click=submit_report,
				),
			],
		)
		page.show_dialog(report_dialog)

	async def delete_message(e, msg: Message):
		async def cancel_delete(e):
			page.pop_dialog()

		async def confirm_delete(e):
			try:
				response = await api.delete(endpoint=f"/message/{msg.id}")

				if response.status_code != 204:
					await show_top_toast(
						page, response.json().get("detail", "Erreur lors de la suppression !"), True
					)
					return

				page.pop_dialog()
				await show_top_toast(page, "Message supprimé !")

			except httpx.RequestError as ex:
				await show_top_toast(page, "Erreur lors de la suppression !", True)
				page.update()
				return

		page.pop_dialog()
		dlg = ft.AlertDialog(
			content=ft.Text("Voulez vous vraiment supprimer ce message ?"),
			actions=[
				ft.Button("Annuler", on_click=cancel_delete),
				ft.Button("Supprimer", on_click=confirm_delete),
			],
		)
		page.show_dialog(dlg)

		# except Exception as e:
		#     # En cas de problème réseau par exemple
		#     await show_top_toast(page, "Erreur de connexion !", True)
		#     print(f"Erreur connexion {e}")
		#     return

	async def send_click(e):
		if not new_message.value.strip():
			return

		# await ft.Clipboard().set(value=new_message.value.strip())

		parent_id = replying_to_message.id if replying_to_message else None
		# 3. On demande la liste fraîche au serveur
		try:
			payload = {"content": new_message.value.strip(), "parent_id": parent_id}
			response = await api.post(f"/room/{current_room_id}/messages", data=payload)

			# Si le jeton est expiré ou invalide (401)
			if response.status_code != 201:
				await show_top_toast(page, "Erreur lors de l'envoi du message !", True)
				new_message.error = "Message non envoyé !"
				page.update()
				return

			print(response)
			message = response.json()
			print(message)

			new_message.error = None
			new_message.value = ""
			await cancel_reply(None)
			await new_message.focus()
			page.update()

			message_datetime = datetime.strptime(message["created_at"], "%Y-%m-%dT%H:%M:%S")
			message_date = message_datetime.date()
			message_time = message_datetime.time()

			# On envoie le pubsub si le message est arrivé en bdd
			page.pubsub.send_all(
				Message(
					id=message["id"],
					pseudo=message["author_display_name"],
					content=message["content"],
					message_type=message["message_type"],
					modified=message["modified"],
					parent_id=message["parent_id"],
					message_datetime=message_datetime,
					message_date=message_date,
					message_time=message_time,
				)
			)
		# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
		except httpx.RequestError as ex:
			await show_top_toast(page, "Erreur lors de l'envoi du message !", True)
			new_message.error = "Erreur, Message non envoyé !"
			page.update()
			return
		# except Exception as e:
		#     # En cas de problème réseau par exemple
		#     await show_top_toast(page, "Erreur de connexion !", True)
		#     print(f"Erreur connexion {e}")
		#     new_message.error = "Erreur connexion !"
		#     return

	def on_message(message: Message):
		if message.message_type in ["join", "quit"]:
			chat_list.controls.append(SystemMessage(message))
		elif message.message_type == "chat":
			if message.pseudo != current_pseudo:
				chat_list.controls.append(
					OtherChatMessage(
						message=message,
						page=page,
						on_copy=copy_message,
						on_reply=prepare_reply,
						on_edit=edit_message,
						on_report=report_message,
						on_react=react_to_message,
						on_delete=delete_message,
					)
				)
			else:
				chat_list.controls.append(
					MyChatMessage(
						message=message,
						page=page,
						on_copy=copy_message,
						on_reply=prepare_reply,
						on_edit=edit_message,
						on_report=report_message,
						on_react=react_to_message,
						on_delete=delete_message,
					)
				)
		page.update()  # Reste synchrone car c'est un callback PubSub

	async def show_messages(messages_received):
		last_date = None
		# On affiche les messages
		if messages_received:
			if type(messages_received) == dict:
				messages_received_list = [None]
				messages_received_list[0] = messages_received
				messages_received = messages_received_list

			for message_to_show in messages_received:
				# On cherche s'il y a parent et le message et l'author du parent
				parent_id = message_to_show["parent_id"]
				parent_content = None
				parent_author = None

				if parent_id:
					for m in messages_received:
						if not m["id"] == parent_id:
							continue
						parent_content = m["content"]
						parent_author = m["author_display_name"]
						break
					if not parent_content:
						parent_content = "Message supprimé !"
					if not parent_author:
						parent_content = "Autheur supprimé !"

				message_datetime = datetime.strptime(
					message_to_show["created_at"], "%Y-%m-%dT%H:%M:%S"
				)
				message_date = message_datetime.date()

				# --- AJOUT: Agrégation des réactions ---
				raw_reactions = message_to_show.get("reactions", [])
				reactions_counts = {}
				for r in raw_reactions:
					emj = r["emoji"]
					reactions_counts[emj] = reactions_counts.get(emj, 0) + 1

				me = Message(
					id=message_to_show["id"],
					pseudo=message_to_show["author_display_name"],
					content=message_to_show["content"],
					message_type=message_to_show["message_type"],
					message_datetime=message_datetime,
					message_date=message_date,
					message_time=message_datetime.time(),
					parent_id=parent_id,
					modified=message_to_show["modified"],
					parent_content=parent_content,
					parent_author=parent_author,
					reactions=reactions_counts,  # <--- On passe notre dictionnaire ici
				)

				# Si le jour est différent du message précédent, on insère un badge de date
				if message_date != last_date:
					date_divider = ft.Container(
						content=ft.Text(format_date(message_date), size=12, weight="bold"),
						alignment=ft.Alignment.CENTER,
						padding=ft.padding.symmetric(vertical=10),
					)
					chat_list.controls.append(date_divider)
					last_date = message_date
				# On affiche le message
				on_message(me)
			# await asyncio.sleep(0.1)
			# chat_list.scroll_to(offset=-1)

	await show_messages(messages_received)

	page.pubsub.subscribe(on_message)

	app_bar = ft.AppBar(
		leading=ft.Icon(ft.Icons.FORUM_ROUNDED, color="primary"),
		leading_width=40,
		title=ft.Text(current_room_name, size=20, weight="bold", color="onsurface"),
		center_title=False,
		bgcolor="surface",
		elevation=2,
		actions=[
			ft.IconButton(
				icon=ft.Icons.LOGOUT_ROUNDED,
				icon_color="error",
				tooltip="Quitter le salon",
				on_click=go_to_rooms,
			),
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
			# ft.Stack(scroll_btn),
			ft.Container(
				content=ft.Column(
					spacing=0,
					controls=[
						reply_banner,
						ft.Row(
							[
								new_message,
								ft.IconButton(
									icon=ft.Icons.SEND_ROUNDED,
									icon_color="blue",
									tooltip="Envoyer",
									on_click=send_click,
								),
							]
						),
					],
				),
				padding=ft.padding.Padding(left=10, top=5, right=10, bottom=15),
			),
		],
	)
