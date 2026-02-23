import flet as ft
from utils import Room, rooms, generate_secure_code


async def CreateRoomView(page: ft.Page):
	# ==========================================================
	#                         STATE
	# ==========================================================
	# Stocke l’icône sélectionnée
	state = {"selected_icon": ft.Icons.MESSAGE}

	# ==========================================================
	#                 LISTE DES ICÔNES DISPONIBLES
	# ==========================================================
	AVAILABLE_ICONS = [
		ft.Icons.MESSAGE,
		ft.Icons.GROUPS,
		ft.Icons.SCHOOL,
		ft.Icons.SPORTS_SOCCER,
		ft.Icons.SPORTS_BASKETBALL,
		ft.Icons.MUSIC_NOTE,
		ft.Icons.GAMEPAD,
		ft.Icons.COMPUTER,
		ft.Icons.SCIENCE,
		ft.Icons.BOOK,
		ft.Icons.COFFEE,
		ft.Icons.LOCAL_PIZZA,
		ft.Icons.LOCK,
		ft.Icons.STAR,
		ft.Icons.FAVORITE,
	]

	# ==========================================================
	#                   ICÔNE VISUELLE ACTUELLE
	# ==========================================================
	icon_display = ft.Icon(
		icon=state["selected_icon"],
		size=32,
		color=ft.Colors.PRIMARY,
	)

	# ==========================================================
	#                   DIALOGUE SÉLECTION ICÔNE
	# ==========================================================
	def close_icon_picker(e):
		icon_picker_dialog.open = False
		page.update()

	def select_icon_action(icon_name):
		state["selected_icon"] = icon_name
		icon_display.icon = icon_name
		icon_picker_dialog.open = False
		page.update()

	icon_grid = ft.GridView(
		expand=True,
		runs_count=4,
		max_extent=70,
		spacing=12,
		run_spacing=12,
		controls=[
			ft.IconButton(
				icon=i,
				icon_size=28,
				on_click=lambda e, i=i: select_icon_action(i),
			)
			for i in AVAILABLE_ICONS
		],
	)

	icon_picker_dialog = ft.AlertDialog(
		modal=True,
		title=ft.Text("Choisir une icône"),
		content=ft.Container(
			width=320,
			height=320,
			padding=10,
			content=icon_grid,
		),
		actions=[ft.TextButton("Annuler", on_click=close_icon_picker)],
		actions_alignment=ft.MainAxisAlignment.END,
	)

	def open_icon_picker(e):
		page.show_dialog(icon_picker_dialog)
		page.update()

	# ==========================================================
	#                    VALIDATION FORMULAIRE
	# ==========================================================
	async def verifier_code(e):
		code = code_input.value.strip()
		code_input.error = None

		if not code:
			code_input.error = "Champ obligatoire."
		elif code not in [r.code for r in rooms]:
			code_input.error = "Salon introuvable."
		else:
			await page.push_route("/chat")

		page.update()

	async def creer_room(e):
		name = room_name_input.value.strip()
		desc = room_description_input.value.strip()

		room_name_input.error = None
		room_description_input.error = None

		if not name:
			room_name_input.error = "Champ obligatoire."
		if not desc:
			room_description_input.error = "Champ obligatoire."

		if name and desc:
			new_room = Room(
				page,
				len(rooms),
				name,
				desc,
				icon=state["selected_icon"],
				code=generate_secure_code(),
			)
			rooms.append(new_room)
			await page.push_route("/rooms")

		page.update()

	# ==========================================================
	#                      CHAMPS INPUT
	# ==========================================================
	room_name_input = ft.TextField(
		label="Nom du salon",
		width=400,
	)

	room_description_input = ft.TextField(
		label="Description",
		multiline=True,
		min_lines=3,
		width=400,
	)

	code_input = ft.TextField(
		label="Code d’invitation",
		hint_text="Ex : AX-77-Z",
		width=350,
		on_submit=verifier_code,
	)

	# ==========================================================
	#                  SECTION CRÉATION (STYLISÉE)
	# ==========================================================
	create_section = ft.Container(
		alignment=ft.Alignment.CENTER,
		content=ft.Container(
			width=520,
			padding=30,
			border_radius=20,
			bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
			content=ft.Column(
				scroll=ft.ScrollMode.HIDDEN,
				tight=true,
				spacing=20,
				controls=[
					# Titre
					ft.Text(
						"Créer un nouveau salon",
						size=26,
						weight=ft.FontWeight.BOLD,
					),
					ft.Text(
						"Organise tes discussions en quelques secondes.",
						size=14,
						color=ft.Colors.ON_SURFACE_VARIANT,
					),
					ft.Divider(),
					room_name_input,
					room_description_input,
					# Sélection icône redesign
					ft.Column(
						spacing=10,
						controls=[
							ft.Text("Icône du salon", weight=ft.FontWeight.W_500),
							ft.Container(
								width=70,
								height=70,
								border_radius=35,
								alignment=ft.Alignment.CENTER,
								bgcolor=ft.Colors.PRIMARY_CONTAINER,
								content=icon_display,
							),
							ft.TextButton(
								"Changer l’icône",
								icon=ft.Icons.IMAGE_SEARCH,
								on_click=open_icon_picker,
							),
						],
					),
					ft.Divider(),
					ft.ElevatedButton(
						"Créer le salon",
						width=400,
						height=50,
						icon=ft.Icons.ADD_HOME_WORK,
						on_click=creer_room,
					),
				],
			),
		),
	)

	# ==========================================================
	#                  SECTION REJOINDRE
	# ==========================================================
	join_section = ft.Container(
		alignment=ft.Alignment.CENTER,
		content=ft.Container(
			width=500,
			padding=30,
			border_radius=20,
			bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
			content=ft.Column(
				spacing=20,
				controls=[
					ft.Text(
						"Rejoindre un salon",
						size=24,
						weight=ft.FontWeight.BOLD,
					),
					ft.Text(
						"Entre le code d’invitation fourni.",
						size=14,
						color=ft.Colors.ON_SURFACE_VARIANT,
					),
					ft.Divider(),
					code_input,
					ft.ElevatedButton(
						"Entrer dans le salon",
						width=350,
						height=50,
						icon=ft.Icons.LOGIN,
						on_click=verifier_code,
					),
				],
			),
		),
	)

	# ==========================================================
	#                         VIEW
	# ==========================================================
	return ft.View(
		route="/new_room",
		appbar=ft.AppBar(
			title=ft.Text("Nouveau Salon"),
			bgcolor=ft.Colors.SURFACE,
		),
		controls=[
			ft.Tabs(
				selected_index=0,
				length=2,
				expand=True,
				content=ft.Column(
					expand=True,
					controls=[
						# ==========================
						#        BARRE D’ONGLETS
						# ==========================
						ft.TabBar(
							tabs=[
								ft.Tab(
									label="Rejoindre",
									icon=ft.Icons.LOGIN,
								),
								ft.Tab(
									label="Créer",
									icon=ft.Icons.ADD_HOME_WORK,
								),
							],
							tab_alignment=ft.TabAlignment.CENTER,
						),
						# ==========================
						#        CONTENU ONGLET
						# ==========================
						ft.TabBarView(
							expand=True,
							controls=[
								# -------- ONGLET REJOINDRE --------
								join_section,
								# -------- ONGLET CRÉER --------
								create_section,
							],
						),
					],
				),
			)
		],
	)
