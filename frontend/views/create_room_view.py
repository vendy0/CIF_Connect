import flet as ft
from utils import Room, rooms, generate_secure_code


async def CreateRoomView(page: ft.Page):
    # --- Gestion de la sélection d'icône ---

    # 1. Variable pour stocker l'icône choisie (valeur par défaut)
    # On utilise une liste ou un objet mutable pour pouvoir le modifier dans les fonctions internes
    state = {"selected_icon": ft.Icons.MESSAGE}

    # 2. Liste d'icônes disponibles (Curated list pour le contexte scolaire/social)
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

    # Composant visuel qui montre l'icône actuelle
    icon_display = ft.Icon(icon=state["selected_icon"], size=40, color=ft.Colors.PRIMARY)

    def close_icon_picker(e):
        icon_picker_dialog.open = False
        page.update()

    def select_icon_action(icon_name):
        # Mettre à jour la variable
        state["selected_icon"] = icon_name
        # Mettre à jour l'aperçu visuel
        icon_display.icon = icon_name
        # Fermer la modale
        icon_picker_dialog.open = False
        page.update()

    # Création de la grille d'icônes pour la modale
    icon_grid = ft.GridView(
        expand=True,
        runs_count=4,  # 4 icônes par ligne
        max_extent=60,
        child_aspect_ratio=1.0,
        spacing=10,
        run_spacing=10,
        controls=[ft.IconButton(icon=icon_name, icon_size=30, on_click=lambda e, name=icon_name: select_icon_action(name)) for icon_name in AVAILABLE_ICONS],
    )

    # La boîte de dialogue (Modale)
    icon_picker_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Choisir une icône"),
        content=ft.Container(
            content=icon_grid,
            width=300,
            height=300,  # Hauteur fixe pour scroller si besoin
        ),
        actions=[
            ft.TextButton("Annuler", on_click=close_icon_picker),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_icon_picker(e):
        page.show_dialog(icon_picker_dialog)
        icon_picker_dialog.open = True
        page.update()

    # --- Fin gestion icône ---

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
        # Récupération de l'icône choisie
        chosen_icon = state["selected_icon"]

        if not name:
            room_name_input.error = "Tous les champs sont obligatoires."
            page.update()
        if not desc:
            room_description_input.error = "Tous les champs sont obligatoires."
            page.update()
        if name and desc:
            room_id = len(rooms)
            # NOTE: Tu pourras ajouter l'argument 'icon' à ta classe Room dans utils.py plus tard
            # Pour l'instant, l'icône est dans la variable 'chosen_icon'
            room = Room(page, room_id, name, desc, icon=chosen_icon, code=generate_secure_code())

            # Si ta classe Room a un attribut icon, tu peux l'assigner ici :
            # room.icon = chosen_icon

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
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.TabBar(
                            tabs=[
                                ft.Tab(label="Rejoindre", icon=ft.Icons.LOGIN),
                                ft.Tab(label="Créer", icon=ft.Icons.ADD_HOME_WORK),
                            ],
                            tab_alignment=ft.TabAlignment.CENTER,
                        ),
                        ft.TabBarView(
                            expand=True,
                            controls=[
                                # Contenu de l'onglet "Rejoindre"
                                ft.Container(
                                    padding=20,
                                    content=ft.Column(
                                        [
                                            code_input,
                                            ft.Button(
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
                                            # --- Section Choix de l'icône ---
                                            ft.Row(
                                                controls=[
                                                    icon_display,  # Affiche l'icône actuelle
                                                    ft.Button("Choisir une icône", icon=ft.Icons.IMAGE_SEARCH, on_click=open_icon_picker),
                                                ],
                                                alignment=ft.MainAxisAlignment.START,
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            # -------------------------------
                                            ft.Button(
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
