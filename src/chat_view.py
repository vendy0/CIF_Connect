import flet as ft
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, date, time, timedelta
import httpx
from chat.components import MyChatMessage, OtherChatMessage, SystemMessage
from chat.models import Message
from chat.api import fetch_room_messages, put_message, post_reaction, post_report, delete_message_bdd, post_message, post_quit_room
from chat.dialogs import show_edit_dialog, show_delete_dialog, show_report_dialog, show_quit_dialog
from utils import get_initials, get_avatar_color, get_colors, show_top_toast, format_date, copy_message
import json
import websockets
import asyncio


# =============================================================================
# 3. VUE PRINCIPALE DU CHAT
# =============================================================================


async def ChatView(page: ft.Page):
	storage = ft.SharedPreferences()
	token = await storage.get("cif_token")

	def build_empty_chat_view():
		return ft.Container(
			content=ft.Column(
				[
					ft.Icon(
						icon=ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED,
						size=80,
						color=ft.Colors.OUTLINE_VARIANT,
					),
					ft.Text(
						"Le silence est d'or...",
						size=20,
						weight="bold",
						color=ft.Colors.ON_SURFACE,
					),
					ft.Text(
						"Soyez le premier à briser la glace !\nEnvoyez un message pour commencer la discussion.",
						size=14,
						color=ft.Colors.OUTLINE,
						text_align=ft.TextAlign.CENTER,
					),
				],
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				spacing=10,
			),
			alignment=ft.Alignment.CENTER,
			expand=True,
			padding=ft.padding.only(top=200),
		)

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

	chat_list = ft.ListView(expand=True, spacing=15, auto_scroll=True, padding=10)

	# # 1. Création du container principal avec le Loader initial
	# chm = ft.Container(
	# 	content=ft.ProgressRing(),  # Ton loader
	# 	expand=True,
	# 	alignment=ft.Alignment.CENTER,
	# )

	async def refresh_ui():
		# 1. Récupérer les nouveaux messages via ton module API
		updated_messages = await fetch_room_messages(page, current_room_id)

		if updated_messages is not None:
			# 2. Vider la liste visuelle (ListView)
			chat_list.controls.clear()

			# 3. Relancer l'affichage (réutilise ta fonction show_messages existante)
			await show_messages(updated_messages, first_load=False)

			# 4. Mettre à jour l'interface
			page.update()

	chat_container = ft.Container(
		content=ft.ProgressRing(),
		alignment=ft.Alignment.CENTER,
		expand=True,
		image=ft.DecorationImage(
			# src="icon.png",
			src="pattern.png",
			repeat=ft.ImageRepeat.REPEAT,
			fit=ft.BoxFit.NONE,
			opacity=0.4,  # Ton réglage de douceur
		),
		bgcolor=ft.Colors.SURFACE,
	)

	# On récupère les messages
	messages_received = None

	# 2. On définit la fonction de chargement
	async def load_initial_data():
		nonlocal messages_received
		# Appel à ton nouveau fichier API
		messages_received = await fetch_room_messages(page, current_room_id)

		if messages_received is None:
			# Si erreur (401 ou réseau), api.py a déjà fait le toast
			# On redirige explicitement ici si ce n'est pas déjà fait
			await page.push_route("/rooms")
			return

		is_chat_message = False
		for m in messages_received:
			if m["message_type"] == "chat":
				is_chat_message = True
				break

		if not is_chat_message:
			# Cas où il n'y a aucun message
			chat_container.content = build_empty_chat_view()
			page.update()
		else:
			# Cas où il y a des messages
			await show_messages(messages_received, first_load=True)
			chat_container.content = chat_list
			# On retire l'alignement center pour que la liste commence en haut
			chat_container.alignment = None
			page.update()
		# Si tout est OK, on affiche

	# 3. On lance le chargement SANS bloquer l'affichage de la vue
	page.run_task(load_initial_data)

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
			],
		),
	)
	new_message = ft.TextField(hint_text="Écrivez un message...", capitalization=ft.TextCapitalization.SENTENCES, autofocus=False, expand=True, multiline=True, min_lines=1, max_lines=5, border_radius=20)

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

	async def edit_message(e, msg: Message):
		page.pop_dialog()
		await show_edit_dialog(page, msg, on_success=refresh_ui)

	async def react_to_message(e, msg: Message):
		# Liste de tes emojis supportés
		emojis = ["👍", "❤️", "😂", "😮", "😢", "😡"]
		emoji_selected = None

		async def on_emoji_click(click_event, emoji_char):
			# 1. Fermer le menu en priorité (Flet 0.80.5 style)
			page.pop_dialog()
			await post_reaction(page, msg.id, emoji_char)

		# Construction de la grille d'emojis
		emoji_row = ft.Row(
			controls=[ft.TextButton(em, on_click=lambda ce, em=em: ce.page.run_task(on_emoji_click, ce, em)) for em in emojis],
			alignment=ft.MainAxisAlignment.SPACE_EVENLY,
		)

		picker = ft.BottomSheet(content=ft.Container(content=emoji_row, padding=20, height=100))
		page.show_dialog(picker)

	async def report_message(e, msg: Message):
		page.pop_dialog()
		await show_report_dialog(page, msg.id)

	async def delete_message(e, msg: Message):
		page.pop_dialog()
		await show_delete_dialog(page, msg.id, on_success=refresh_ui)

	async def send_click(e):
		if not new_message.value.strip():
			return

		# await ft.Clipboard().set(value=new_message.value.strip())

		parent_id = replying_to_message.id if replying_to_message else None

		message = await post_message(page, current_room_id, parent_id, new_message)
		if not message:
			return

		# Dans send_click, juste après avoir reçu la réponse de post_message :
		if chat_container.content != chat_list:
			chat_container.content = chat_list
			chat_container.alignment = None
			page.update()

		# await storage.set(f"last_read_{current_room_id}", message["id"])

		await cancel_reply(None)
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
		# await refresh_ui()

	def on_message(message: Message, is_me):
		# if message.parent_author == current_pseudo:
		# 	print("VIBRATION")
		if message.message_type in ["join", "quit"]:
			chat_list.controls.append(SystemMessage(message))
		elif message.message_type == "chat":
			if is_me:
				chat_list.controls.append(MyChatMessage(message=message, page=page, on_copy=copy_message, on_reply=prepare_reply, on_edit=edit_message, on_report=report_message, on_react=react_to_message, on_delete=delete_message))
			else:
				chat_list.controls.append(OtherChatMessage(message=message, page=page, on_copy=copy_message, on_reply=prepare_reply, on_edit=edit_message, on_report=report_message, on_react=react_to_message, on_delete=delete_message))
		page.update()

	async def show_messages(messages_received, first_load=False):
		nonlocal chat_list
		last_date = None
		# On affiche les messages
		if messages_received:
			if isinstance(messages_received, dict):
				messages_received = [messages_received]

			for message_to_show in messages_received:
				# On cherche s'il y a parent et le message et l'author du parent
				parent_id = message_to_show["parent_id"]
				parent_content = None
				parent_author = None

				if parent_id:
					for m in messages_received:
						if m["id"] != parent_id:
							continue
						parent_content = m["content"]
						parent_author = m["author_display_name"]
						break
					if not parent_content:
						parent_content = "Message supprimé !"
					if not parent_author:
						parent_author = "Autheur supprimé !"

				message_datetime = datetime.strptime(message_to_show["created_at"], "%Y-%m-%dT%H:%M:%S")
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
					# date_divider = ft.Container(
					# 	content=ft.Text(format_date(message_date), size=12, weight="bold"),
					# 	alignment=ft.Alignment.CENTER,
					# 	padding=ft.padding.symmetric(vertical=10),
					# )

					# Dans ChatView, au moment de créer le date_divider
					date_divider = ft.Container(content=ft.Text(format_date(message_date).upper(), size=11, weight="bold", color=ft.Colors.OUTLINE), alignment=ft.Alignment.CENTER, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE_VARIANT), padding=ft.padding.symmetric(horizontal=12, vertical=4), border_radius=10, margin=ft.margin.symmetric(vertical=10))

					chat_list.controls.append(date_divider)
					last_date = message_date
				is_me = me.pseudo == current_pseudo
				on_message(me, is_me)
			page.update()
			# await chat_list.scroll_to(offset=-1, duration=100)
			# On affiche le message
			# if first_load:
			#     last_read = await storage.get(f"last_read_{current_room_id}")
			#     if last_read:
			#         # Flet permet de scroller vers une "key" spécifique
			#         # await chat_list.scroll_to(key=str(last_read), duration=300)
			#         pass
			#     else:
			#         pass
			# Sinon, on va tout en bas
			# await chat_list.scroll_to(offset=-1, duration=100)

	# page.pubsub.subscribe(on_message)

	async def left_room(e):
		await show_quit_dialog(page, current_room_id)

	search_input = ft.TextField(hint_text="Rechercher...", expand=True, autofocus=True, border=ft.InputBorder.NONE, on_change=lambda e: filter_messages(e.control.value))

	def filter_messages(query: str):
		query = query.lower()
		# On parcourt les éléments de la chat_list
		for ctrl in chat_list.controls:
			if isinstance(ctrl, (MyChatMessage, OtherChatMessage)):
				# Si le texte correspond, on affiche, sinon on cache
				ctrl.visible = query in ctrl.message.content.lower()
		page.update()

	def toggle_search(e):
		# On remplace le titre par l'input, et on change les boutons
		if app_bar.title == search_input:
			# Annuler la recherche
			app_bar.title = ft.Row(controls=ft.Text(current_room_name, size=20, weight="bold"))
			app_bar.actions = [default_menu]
			filter_messages("")  # On réaffiche tout
		else:
			# Activer la recherche
			app_bar.title = search_input
			app_bar.actions = [ft.IconButton(ft.Icons.CLOSE, on_click=toggle_search)]
		page.update()

	default_menu = ft.PopupMenuButton(
		items=[
			ft.PopupMenuItem(icon=ft.Icons.SEARCH, content=ft.Text("Rechercher un message"), on_click=toggle_search),
		]
	)

	if current_room_id != 1 and current_room_name != "Salon Général":
		default_menu.items.append(ft.PopupMenuItem())
		default_menu.items.append(ft.PopupMenuItem(icon=ft.Icons.LOGOUT_ROUNDED, content=ft.Text("Quitter le salon"), on_click=left_room))

	app_bar = ft.AppBar(
		# --- BOUTON RETOUR ---
		leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda _: page.run_task(page.push_route, "/rooms")),
		leading_width=40,
		# --- TITRE CLIQUABLE (Pour les infos du salon) ---
		title=ft.GestureDetector(
			on_long_press=toggle_search,
			content=ft.Text(current_room_name, size=20, weight="bold", color="onsurface"),
			on_tap=lambda _: page.run_task(page.push_route, f"/room_info/{current_room_id}"),  # On verra cette vue plus bas
		),
		center_title=False,
		bgcolor="surface",
		elevation=2,
		# --- MENU 3 POINTS ---
		actions=[default_menu],
	)

	# Variable pour garder la main sur la connexion
	ws_connection = None

	async def listen_ws():
		nonlocal ws_connection
		ws_url = f"ws://127.0.0.1:8000/ws/{current_room_id}"

		try:
			async with websockets.connect(ws_url) as ws:
				ws_connection = ws
				async for data in ws:
					msg_data = json.loads(data)

					# Formatage des réactions
					reactions_counts = {}
					for r in msg_data.get("reactions", []):
						emj = r["emoji"]
						reactions_counts[emj] = reactions_counts.get(emj, 0) + 1

					message_datetime = datetime.strptime(msg_data["created_at"], "%Y-%m-%dT%H:%M:%S")

					new_msg = Message(id=msg_data["id"], pseudo=msg_data["author_display_name"], content=msg_data["content"], message_type=msg_data["message_type"], modified=msg_data["modified"], parent_id=msg_data["parent_id"], message_datetime=message_datetime, message_date=message_datetime.date(), message_time=message_datetime.time(), reactions=reactions_counts)

					# Vérification doublon
				# 	existing_ids = [m.content[0].key for m in chat_list.controls if hasattr(m.content[0], "key")]
					existing_ids = [str(m.message.id) for m in chat_list.controls if hasattr(m, "message")]
					if str(new_msg.id) not in existing_ids:
						is_me = new_msg.pseudo == current_pseudo
						on_message(new_msg, is_me)

						page.update()
						await chat_list.scroll_to(offset=-1, duration=300)
						page.update()

		except websockets.exceptions.ConnectionClosed:
			# Comportement normal quand on force la fermeture
			print(f"Déconnexion du salon {current_room_id}")

	# Lancement en tâche de fond (ne bloque pas l'UI)
	page.run_task(listen_ws)

	return ft.View(
		route="/chat",
		controls=[
			app_bar,
			# Le Stack entoure la liste ET le bouton
			ft.Container(
				content=chat_container,
				expand=True,
				padding=0,
			),
			# La zone de saisie en bas (reply_banner + new_message)
			ft.Container(
				content=ft.Column(
					spacing=0,
					controls=[
						reply_banner,
						ft.Row([new_message, ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color="blue", on_click=send_click)]),
					],
				),
				padding=ft.padding.Padding(left=10, top=5, right=10, bottom=15),
			),
		],
	)
