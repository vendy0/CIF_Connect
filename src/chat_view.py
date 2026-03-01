import flet as ft
from dataclasses import dataclass, field
from typing import List, Optional
import httpx
from utils import get_initials, get_avatar_color, get_colors, host, port


# =============================================================================
# 1. MODÈLES DE DONNÉES
# =============================================================================


@dataclass
class Message:
	id: int
	pseudo: str
	content: str
	message_type: str
	parent_id: Optional[int] = None
	parent_content: Optional[str] = None
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


# (Votre dataclass Message et vos fonctions get_colors, get_initials, etc. restent inchangés)


class ChatMessage(ft.Column):
	def __init__(self, message: Message, page: ft.Page, on_reply, on_report, on_react):
		super().__init__()
		self.message = message
		self._page_ref = page
		self.on_reply = on_reply
		self.on_report = on_report
		self.on_react = on_react
		self.spacing = 2

		# --- Création du BottomSheet ---
		self.bottom_sheet = ft.BottomSheet(
			content=ft.Container(
				padding=10,
				# open=False,
				content=ft.Column(
					tight=True,
					controls=[
						ft.ListTile(
							leading=ft.Icon(ft.Icons.FAVORITE_BORDER),
							title=ft.Text("Liker"),
							on_click=lambda e: self.action_react(
								e, "❤️"
							),  # Ajout de l'emoji par défaut
						),
						ft.ListTile(
							leading=ft.Icon(ft.Icons.REPLY),
							title=ft.Text("Répondre"),
							on_click=self.action_reply,
						),
						ft.ListTile(
							leading=ft.Icon(ft.Icons.REPORT_GMAILERRORRED, color=ft.Colors.ERROR),
							title=ft.Text("Signaler", color=ft.Colors.ERROR),
							on_click=self.action_report,
						),
					],
				),
			),
		)

		# --- Construction du contenu de la bulle ---
		bubble_content = []

		# 1. Indicateur de réponse (ajouté uniquement si parent_id existe)
		if self.message.parent_id is not None:
			bubble_content.append(
				ft.Container(
					content=ft.Row(
						[
							ft.Icon(ft.Icons.REPLY_ALL_ROUNDED, size=14, color=ft.Colors.OUTLINE),
							ft.Text("Réponse", size=12, italic=True, color=ft.Colors.OUTLINE),
						],
						tight=True,
						spacing=4,
					),
					padding=ft.padding.only(left=8, bottom=2),
					border=ft.border.only(left=ft.border.BorderSide(2, ft.Colors.OUTLINE)),
					margin=ft.margin.only(bottom=4),
				)
			)

		# 2. Ajout du pseudo et du message
		bubble_content.extend(
			[
				ft.Text(self.message.pseudo, weight="bold"),
				ft.Text(self.message.content),
			]
		)

		# --- Assemblage final ---
		self.controls = [
			ft.Row(
				[
					ft.CircleAvatar(
						content=ft.Text(get_initials(self.message.pseudo)),
						bgcolor=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
					),
					ft.GestureDetector(
						on_long_press=self.open_menu,
						content=ft.Container(
							content=ft.Column(bubble_content, spacing=2),
							bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,  # Syntaxe 0.80.5
							padding=10,
							border_radius=10,
						),
					),
				]
			)
		]

	async def open_menu(self, e):
		page = getattr(e, "page", None) or getattr(e.control, "page", None)
		if not page:
			return
		#
		if not self.bottom_sheet.open:
			# page.overlay.append(self.bottom_sheet)
			self.page.show_dialog(self.bottom_sheet)
			page.update()

	async def action_reply(self, e):
		self.bottom_sheet.open = False
		self.page.update()

		await self.on_reply(self.message)  # Ajout du await ici pour la fonction async

	async def action_report(self, e):
		# self.page.show_dialog(self.bottom_sheet)
		# self.page.update()

		self.on_report(self.message)
		self.bottom_sheet.open = False

	async def action_react(self, e, emoji):
		self.bottom_sheet.open = False
		self.page.update()
		await self.on_react(self.message, emoji)


# class ChatMessage(ft.Column):
# 	def __init__(self, message: Message, page: ft.Page, on_reply, on_report, on_react):
# 		super().__init__()
# 		self.message = message
# 		self._page_ref = page
# 		self.on_reply = on_reply
# 		self.on_report = on_report
# 		self.on_react = on_react
# 		self.spacing = 2

# 		# --- Création du BottomSheet ---
# 		# self.bottom_sheet = ft.BottomSheet(
# 		#     content=ft.Container(
# 		#         padding=20,
# 		#         content=ft.Column(
# 		#             tight=True,
# 		#             controls=[
# 		#                 ft.Text("Actions", weight="bold"),
# 		#                 ft.Row(
# 		#                     [
# 		#                         # CORRECTION: Utilisation de TextButton pour les emojis
# 		#                         ft.TextButton(content="👍", on_click=lambda e: self.action_react(e, "👍")),
# 		#                         ft.TextButton(content="❤️", on_click=lambda e: self.action_react(e, "❤️")),
# 		#                     ],
# 		#                     alignment=ft.MainAxisAlignment.CENTER,
# 		#                 ),
# 		#                 ft.ListTile(leading=ft.Icon(ft.Icons.REPLY), title=ft.Text("Répondre"), on_click=self.action_reply),
# 		#                 ft.ListTile(leading=ft.Icon(ft.Icons.REPORT, color="error"), title=ft.Text("Signaler"), on_click=self.action_report),
# 		#             ],
# 		#         ),
# 		#     )
# 		# )

# 		# BottomSheet (menu)
# 		self.bottom_sheet = ft.BottomSheet(
# 			content=ft.Container(
# 				padding=10,
# 				content=ft.Column(
# 					tight=True,
# 					controls=[
# 						ft.ListTile(
# 							leading=ft.Icon(ft.Icons.FAVORITE_BORDER),
# 							title=ft.Text("Liker"),
# 							on_click=lambda e: self.action_react(e),
# 						),
# 						ft.ListTile(
# 							leading=ft.Icon(ft.Icons.REPLY),
# 							title=ft.Text("Répondre"),
# 							on_click=self.action_reply,
# 						),
# 						ft.ListTile(
# 							leading=ft.Icon(ft.Icons.REPORT_GMAILERRORRED, color=ft.Colors.RED),
# 							title=ft.Text("Signaler", color=ft.Colors.RED),
# 							on_click=lambda e: self.action_report(e),
# 						),
# 					],
# 				),
# 			),
# 		)

# 		# Avatar et bulles
# 		self.controls = [
# 			ft.Row(
# 				[
# 					ft.CircleAvatar(content=ft.Text(get_initials(self.message.pseudo)), bgcolor=get_avatar_color(self.message.pseudo, COLORS_LOOKUP)),
# 					ft.GestureDetector(
# 						on_long_press=self.open_menu,
# 						content=ft.Container(
# 							content=ft.Column(
# 								[
# 									ft.Text(self.message.pseudo, weight="bold"),
# 									ft.Text(self.message.content),
# 								],
# 								spacing=2,
# 							),
# 							bgcolor="surfacevariant",
# 							padding=10,
# 							border_radius=10,
# 						),
# 					),
# 				]
# 			)
# 		]

# 	async def open_menu(self, e):
# 		page = getattr(e, "page", None) or getattr(e.control, "page", None)
# 		if not page:
# 			return
# #
# 		if self.bottom_sheet not in page.overlay:
# 			page.overlay.append(self.bottom_sheet)
# 			self.page.show_dialog(bottom_sheet)
# 			page.update()

# 	async def action_reply(self, e):
# 		self.bottom_sheet.open = False
# 		self.page.update()

# 		await self.on_reply(self.message)  # Ajout du await ici pour la fonction async

# 	async def action_report(self, e):
# 		await self._page_ref.close(self.bottom_sheet)
# 		await self.on_report(self.message)

# 	async def action_react(self, e, emoji):
# 		await self._page_ref.close(self.bottom_sheet)
# 		await self.on_react(self.message, emoji)


# =============================================================================
# 3. VUE PRINCIPALE DU CHAT
# =============================================================================


async def ChatView(page: ft.Page):
	storage = ft.SharedPreferences()
	token = await storage.get("cif_token")

	current_room_id = page.session.store.get("current_room_id") or 1
	current_room_name = page.session.store.get("current_room_name") or "Salon Inconnue..."
	current_pseudo = await storage.get("user_pseudo") or "Anonyme"

	replying_to_message: Optional[Message] = None

	if not current_room_id:
		print("Le salon est introuvable !")
		await page.push_route("/rooms")
		page.update()

	if not token:
		await page.push_route("/login")

	# On récupère tous les messages
	# 2. On prépare l'enveloppe (le header)
	headers = {"Authorization": f"Bearer {token}"}

	chat_list = ft.ListView(expand=True, spacing=15, auto_scroll=True, padding=10)

	# 3. On demande la liste fraîche au serveur
	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(
				f"http://{host}:{port}/room/{current_room_id}/messages", headers=headers
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
					ft.Icons.CLOSE, icon_size=16, on_click=lambda e: cancel_reply(e)
				),  # Sera awaité plus tard
			],
		),
	)

	new_message = ft.TextField(
		hint_text="Écrivez un message...",
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

	async def cancel_reply(e):  # Rendu async pour pouvoir être awaité
		nonlocal replying_to_message
		replying_to_message = None
		reply_banner.visible = False
		reply_banner.content.controls[0].controls[1].value = ""
		page.update()

	async def prepare_reply(msg: Message):  # Rendu async
		nonlocal replying_to_message
		replying_to_message = msg
		reply_banner.visible = True
		reply_banner.content.controls[0].controls[1].value = f"{msg.pseudo}: {msg.content[:30]}..."
		await new_message.focus()  # CORRECTION DU WARNING ICI
		page.update()

	async def react_to_message(msg: Message, emoji: str):
		if emoji in msg.reactions:
			msg.reactions[emoji] += 1
		else:
			msg.reactions[emoji] = 1
		# (La logique UI sera faite plus tard si tu veux l'afficher)

	def report_message(msg: Message):
		report_reason_input = ft.TextField(label="Raison du signalement", multiline=True)

		def submit_report(e):
			report_dialog.open = False
			snack_bar = ft.SnackBar(ft.Text("Signalement envoyé à la modération."))
			page.show_dialog(snack_bar)
			page.update()

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

	async def send_click(e):
		if not new_message.value:
			return

		text = new_message.value
		parent_id = replying_to_message.id if replying_to_message else None

		# 3. On demande la liste fraîche au serveur
		try:
			async with httpx.AsyncClient() as client:
				payload = {"content": new_message.value.strip()}
				if parent_id:
					payload["parent_id"] = parent_id
				response = await client.post(
					f"http://{host}:{port}/room/{current_room_id}/messages",
					headers=headers,
					json=payload,
				)

				# Si le jeton est expiré ou invalide (401)
				if response.status_code != 201:
					print("Erreur lors de l'envoi du message !")
					new_message.error = "Message non envoyé !"
					page.update()
					return

				new_message.value = ""
				await new_message.focus()
				page.update()

				# On envoie le pubsub
				page.pubsub.send_all(
					Message(
						id=1001,
						pseudo=current_pseudo,
						content=text,
						message_type="chat",
						parent_id=parent_id,
					)
				)
		# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
		except httpx.RequestError as ex:
			print(f"Erreur lors de l'envoi du message : {ex}")
			new_message.error = "Erreur, Message non envoyé !"
			page.update()
			return
		except Exception as e:
			# En cas de problème réseau par exemple
			print(f"Erreur de connexion : {e}")
			new_message.error = "Erreur connexion !"
			return

		new_message.value = ""
		await cancel_reply(None)
		await new_message.focus()  # CORRECTION DU WARNING ICI
		page.update()

	def on_message(message: Message):
		if message.message_type in ["join", "quit"]:
			chat_list.controls.append(SystemMessage(message))
		elif message.message_type == "chat":
			chat_list.controls.append(
				ChatMessage(
					message=message,
					page=page,
					on_reply=prepare_reply,
					on_report=report_message,
					on_react=react_to_message,
				)
			)
		page.update()  # Reste synchrone car c'est un callback PubSub

	# On affiche les messages
	if messages_received:
		for message_to_show in messages_received:
			me = Message(
				id=message_to_show["id"],
				pseudo=message_to_show["author_display_name"],
				content=message_to_show["content"],
				message_type=message_to_show["message_type"],
				parent_id=message_to_show["parent_id"],
			)
			on_message(me)
	else:
		pass

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
