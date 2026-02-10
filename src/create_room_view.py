import flet as ft

def CreateRoomView(page: ft.Page):
    return ft.View(
        route = "/create_room",
        appbar=ft.AppBar(title=ft.Text("Nouveau Salon")),
        controls=[
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Rejoindre", content=ft.Column([
                        ft.TextField(label="Code d'invitation", placeholder="Ex: AX-77-Z"),
                        ft.ElevatedButton("Entrer dans le salon", icon=ft.Icons.LOGIN)
                    ], spacing=20, padding=20)),
                    ft.Tab(text="Créer", content=ft.Column([
                        ft.TextField(label="Nom du salon"),
                        ft.TextField(label="Description", multiline=True),
                        ft.ElevatedButton("Générer le salon", icon=ft.Icons.ADD_HOME_WORK)
                    ], spacing=20, padding=20)),
                ]
            )
        ]
    )
