import flet as ft
from utils import Room, rooms, generate_secure_code


async def CreateRoomView(page: ft.Page):
	async def verifier_code(e):
		code = code_input.value
		if not code:
			code_input.error = "Tous les champs sont obligatoires !"
			page.update()
		else:
			if code in [room.code for room in rooms]:
				await page.push_route("/chat")
			else:
				code_input.error = "Salon introuvable !"
				page.update()

	async def new_room(e):
		await page.push_route("/new_room")

	async def creer_room(e):
		name = room_name_input.value
		desc = room_description_input.value

		if not name:
			room_name_input.error = "Tous les champs sont obligatoires."
			page.update()
		if not desc:
			room_description_input.error = "Tous les champs sont obligatoires."
			page.update()
		if name and desc:
			room_id = len(rooms)
			room = Room(page, room_id, name, desc, code =generate_secure_code())
			rooms.append(room)
			await page.push_route("/rooms")

	room_name_input = ft.TextField(label="Nom de salon")

	room_description_input = ft.TextField(
		label="Description",
		multiline=True,
		on_submit=creer_room,
	)

	code_input = ft.TextField(
		label="Code d'invitation",
		hint_text="Ex: AX-77-Z",
		on_submit=verifier_code,
	)

	return ft.View(
		route="/new_room",
		appbar=ft.AppBar(title=ft.Text("Nouveau Salon")),
		controls=[
			ft.Tabs(
				selected_index=0,
				length=2,
				expand=True,
				# Le 'content' contient une Column qui sépare les onglets du contenu
				content=ft.Column(
					expand=True,
					controls=[
						# 1. La barre de navigation en haut
						ft.TabBar(
							tabs=[
								ft.Tab(label="Rejoindre", icon=ft.Icons.LOGIN),
								ft.Tab(label="Créer", icon=ft.Icons.ADD_HOME_WORK),
							],
							tab_alignment=ft.TabAlignment.CENTER,
						),
						# 2. La vue qui change selon l'onglet sélectionné
						ft.TabBarView(
							expand=True,
							# align=ft.Alignment.CENTER,
							controls=[
								# Contenu de l'onglet "Rejoindre"
								ft.Container(
									padding=20,
									content=ft.Column(
										[
											code_input,
											ft.ElevatedButton(
												"Entrer dans le salon",
												icon=ft.Icons.LOGIN,
												on_click=verifier_code,
											),
										],
										spacing=20,
									),
								),
								# Contenu de l'onglet "Créer"
								ft.Container(
									padding=20,
									content=ft.Column(
										[
											room_name_input,
											room_description_input,
											ft.ElevatedButton(
												"Générer le salon",
												icon=ft.Icons.ADD_HOME_WORK,
												on_click=creer_room,
											),
										],
										spacing=20,
									),
								),
							],
						),
					],
				),
			)
		],
	)
