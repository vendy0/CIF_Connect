import flet as ft
from utils import api, show_top_toast, get_avatar_color, COLORS_LOOKUP, get_initials, copy_message, refresh_rooms, select_icon_dialog, generate_secure_code
import httpx
import json


async def RoomInfoView(page: ft.Page):
	storage = ft.SharedPreferences()
	room_id = page.session.store.get("current_room_id")
	current_user_id = await storage.get("user_id")  # Assure-toi de stocker ça au login

	if not room_id:
		await page.push_route("/rooms")
		return ft.View(route="/room_info")

	# Variable pour stocker l'icône sélectionnée (état local)
	state = {"selected_icon": ft.Icons.GROUPS}

	input_change = False

	# Avant le return, définissez l'icône d'en-tête
	room_icon_display = ft.Icon(icon=ft.Icons.GROUPS, size=40, color=ft.Colors.ON_PRIMARY_CONTAINER)
	room_name_display = ft.Text("Chargement...", size=24, weight="bold")
	room_code_display = ft.Text("Public", size=12, color=ft.Colors.OUTLINE)

	is_admin = False

	btn_refresh = ft.IconButton(icon=ft.Icons.REFRESH, visible=False)
	btn_copy = ft.IconButton(icon=ft.Icons.COPY, visible=False)  # On l'activera dans load_room_info

	room_avatar_container = ft.GestureDetector(content=ft.CircleAvatar(radius=50, content=room_icon_display, bgcolor=ft.Colors.PRIMARY_CONTAINER), on_tap=lambda e: page.run_task(handle_change_icon, e, is_admin))

	# Mettre le change input sur True
	def change_input(e):
		nonlocal input_change
		if input_change:
			return
		input_change = True
		name_field.on_change = None
		desc_field.on_change = None
		code_field.on_change = None

	# Champs éditables
	name_field = ft.TextField(label="Nom du salon", value="Chargement...", read_only=True, expand=True, border=ft.InputBorder.UNDERLINE, on_change=change_input)
	desc_field = ft.TextField(label="Description", value="Chargement...", read_only=True, expand=True, multiline=True, border=ft.InputBorder.UNDERLINE, on_change=change_input)
	code_field = ft.TextField(label="Code d'invitation", value="Chargement...", read_only=True, expand=True, border=ft.InputBorder.UNDERLINE, suffix=ft.Row([btn_refresh, btn_copy], tight=True), on_change=change_input)
	# Ajouter un bouton de rafraîchissement au code_field

	# --- FONCTION POUR GÉNÉRER UN NOUVEAU CODE ---
	async def handle_refresh_code(e):
		nonlocal input_change
		input_change = True
		new_code = generate_secure_code()
		code_field.value = new_code
		page.update()
		await show_top_toast(page, "Nouveau code généré (n'oubliez pas d'enregistrer)")

	# Bouton de sauvegarde (Caché par défaut)
	save_btn = ft.ElevatedButton("Enregistrer les modifications", icon=ft.Icons.SAVE, visible=False)

	# À définir avant le return du ft.View
	delete_btn = ft.TextButton(
		"Supprimer le salon",
		icon=ft.Icons.DELETE_FOREVER,
		style=ft.ButtonStyle(color=ft.Colors.ERROR),
		visible=False,  # Caché par défaut
		on_click=lambda e: open_delete_dialog(),
	)

	async def handle_delete_room(e):
		try:
			# On ferme le dialogue d'abord

			response = await api.delete(endpoint=f"/rooms/{room_id}")

			if response.status_code == 204:
				page.pop_dialog()
				await page.push_route("/rooms")
				await show_top_toast(page, "Salon supprimé avec succès")
				await refresh_rooms(page, storage)
			else:
				error_msg = response.json().get("detail", "Erreur lors de la suppression")
				await show_top_toast(page, error_msg, True)
		except httpx.RequestError:
			await show_top_toast(page, "Erreur réseau", True)
			page.update()

	def open_delete_dialog():
		confirm_dialog = ft.AlertDialog(
			title=ft.Text("Supprimer le salon ?"),
			content=ft.Text("Cette action est irréversible. Tous les messages seront perdus."),
			actions=[ft.TextButton("Annuler", on_click=page.pop_dialog), ft.FilledButton("Supprimer", bgcolor=ft.Colors.ERROR, color=ft.Colors.ON_ERROR, on_click=handle_delete_room)],
		)
		page.show_dialog(confirm_dialog)
		page.update()

	# Au lieu de la ListView, on crée un Row horizontal
	members_info_row = ft.Row(
		controls=[
			ft.Icon(ft.Icons.PEOPLE_ALT_ROUNDED, color=ft.Colors.PRIMARY, size=20),
			ft.Text(
				"0 / 0 membres en ligne",  # On mettra à jour ce texte dynamiquement
				size=16,
				weight=ft.FontWeight.W_500,
				color=ft.Colors.ON_SURFACE_VARIANT,
			),
		],
		alignment=ft.MainAxisAlignment.CENTER,
		spacing=10,
	)

	# On l'enveloppe dans un container pour le centrer et lui donner du style
	members_container = ft.Container(
		content=members_info_row,
		bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
		padding=ft.padding.symmetric(horizontal=20, vertical=15),
		border_radius=15,
		margin=ft.margin.only(top=10),
	)

	async def load_room_info():
		nonlocal is_admin
		try:
			cached_rooms_str = await storage.get("rooms_cache")
			if cached_rooms_str:
				rooms = json.loads(cached_rooms_str)

			room_data = {}
			for r in rooms:
				if r["id"] == room_id:
					room_data = r
					break

			if not room_data:
				await show_top_toast(page, "Salon introuvable", True)
				await page.push_route("/chat")
				return

			room_data = r

			state["selected_icon"] = room_data.get("icon", ft.Icons.GROUPS)
			room_icon_display.icon = state["selected_icon"]

			room_name_display.value = room_data["name"]
			if room_data["access_key"]:
				room_code_display.value = f"Code : {room_data['access_key']}"

			# Vérification Admin
			if room_data["creator"]:
				is_admin = str(room_data["creator"]["id"]) == str(current_user_id)

			try:
				online_res = await api.get(f"/rooms/{room_id}/online")
				if online_res.status_code == 200:
					online_members = online_res.json().get("online_members", 0)
					total_members = online_res.json().get("total_members", "?")  # Si tu as le total via l'API

					# Mise à jour du composant texte
					members_info_row.controls[1].value = f"{online_members} / {total_members} membres en ligne"
					page.update()
			except Exception as e:
				await show_top_toast(page, "Erreur chargement membres en ligne", True)
				print(f"Erreur chargement membres en ligne: {e}")

			# Remplissage de l'UI
			name_field.value = room_data["name"]
			desc_field.value = room_data["description"]
			if room_data["access_key"]:
				code_field.value = room_data["access_key"]
				# code_field.on_click = lambda e: page.run_task(copy_message, e, page, room_data["access_key"], "Clé d'accès copiée !")
			else:
				code_field.value = "Salon Public"

			if is_admin:
				name_field.read_only = False
				desc_field.read_only = False
				save_btn.visible = True
				btn_refresh.visible = True
				btn_refresh.on_click = handle_refresh_code
				btn_copy.visible = True
				btn_copy.on_click = lambda e: page.run_task(copy_message, e, page, code_field.value, "Code copié !")
				delete_btn.visible = True

			page.update()

		except httpx.RequestError:
			await show_top_toast(page, "Erreur réseau !", True)

	# --- FONCTION POUR CHANGER L'ICÔNE ---
	def update_icon_state(icon_name):
		state["selected_icon"] = icon_name

	async def handle_change_icon(e, is_admin):
		nonlocal input_change
		if is_admin:
			await select_icon_dialog(page, room_icon_display, update_icon_state)
			input_change = True

	async def save_changes(e):
		nonlocal input_change
		if not input_change:
			await show_top_toast(page, "Aucune modification à enregistrer")
			return
		try:
			payload = {"name": name_field.value, "description": desc_field.value, "icon": state["selected_icon"], "access_key": code_field.value}
			# Appel API selon ton main.py: PUT /rooms/{room_id}?user_id={id}
			response = await api.put(f"/rooms/{room_id}", data=payload)

			if response.status_code == 200:
				await show_top_toast(page, "Modifications enregistrées !")
				page.session.store.set("current_room_name", name_field.value)
				room_name_display = name_field.value
				await refresh_rooms(page, storage)
				page.run_task(load_room_info)

				# On réinitialise la variable input_change
				input_change = False
				name_field.on_change = change_input
				desc_field.on_change = change_input
				code_field.on_change = change_input
			else:
				await show_top_toast(page, response.json().get("detail", "Erreur lors de la modification"), True)
		except Exception as ex:
			await show_top_toast(page, "Erreur réseau", True)

	save_btn.on_click = save_changes

	# Déclenchement du chargement
	page.run_task(load_room_info)

	return ft.View(
		route=f"/room_info/{room_id}",
		appbar=ft.AppBar(
			leading=ft.IconButton(
				ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
				on_click=lambda _: page.run_task(page.push_route, "/chat"),
			),
			title=ft.Text("Détails du salon", weight="bold"),
			bgcolor="surface",
			center_title=True,
		),
		controls=[
			ft.Container(
				content=ft.Column(
					horizontal_alignment=ft.CrossAxisAlignment.CENTER,
					controls=[
						# En-tête avec Avatar et Nom
						ft.Container(height=20),
						room_avatar_container,
						room_name_display,
						room_code_display,
						ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
						# Formulaire (dans un Container pour limiter la largeur sur PC/Tablette)
						ft.Container(
							content=ft.Column(
								[
									name_field,
									desc_field,
									code_field,
									ft.Container(
										content=save_btn,
										alignment=ft.Alignment.CENTER,
										margin=ft.margin.only(top=15, bottom=15),
									),
								],
								# horizontal_alignment=ft.CrossAxisAlignment.CENTER,
							),
							padding=ft.padding.symmetric(horizontal=20),
						),
						# Section Membres
						ft.Container(
							content=ft.Column(
								[
									ft.Row(
										[
											ft.Text("Membres", size=18, weight="bold"),
											ft.Text("En ligne", size=12, color=ft.Colors.GREEN_500),
										],
										alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
									),
									members_container,
								]
							),
							padding=ft.padding.symmetric(horizontal=20),
						),  # ... dans le Column principal
						ft.Container(
							content=delete_btn,
							alignment=ft.Alignment.CENTER,
							margin=ft.margin.only(top=30, bottom=20),
						),
						# ...
					],
					scroll=ft.ScrollMode.AUTO,
				),
				expand=True,
			)
		],
	)
