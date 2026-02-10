import flet as ft

def RoomsView(page: ft.Page):
    # Simulation de données (à remplacer par la BDD plus tard)
    rooms = [
        {"id": 1, "name": "Salon Général", "desc": "Discussion libre pour tous", "icon": ft.Icons.PUBLIC},
        {"id": 2, "name": "Projet Python", "desc": "Groupe de travail dév", "icon": ft.Icons.CODE},
    ]

    def join_room(e):
        # On pourrait stocker l'ID du salon en session
        page.go("/chat")

    room_list = ft.ListView(expand=True, spacing=10)

    for r in rooms:
        room_list.controls.append(
            ft.ListTile(
                leading=ft.Icon(r["icon"], color=ft.Colors.BLUE_600),
                title=ft.Text(r["name"], weight="bold"),
                subtitle=ft.Text(r["desc"]),
                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                data=r["id"],
                on_click=join_room,
            )
        )

    return ft.View(
        route = "/rooms",
        appbar=ft.AppBar(
            title=ft.Text("Mes Salons"),
            actions=[
                ft.IconButton(ft.Icons.SETTINGS, on_click=lambda _: page.go("/settings")),
            ]
        ),
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD, 
            tooltip="Créer ou rejoindre",
            on_click=lambda _: page.go("/create_room")
        ),
        controls=[
            ft.Text("Sélectionnez un espace de discussion", size=12, color=ft.Colors.GREY_500),
            room_list
        ]
    )
