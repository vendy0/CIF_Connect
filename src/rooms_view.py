import flet as ft

# class Room_Description()


def RoomsView(page: ft.Page, rooms):
	# 	# Simulation de données (à remplacer par la BDD plus tard)

	room_list = ft.ListView(expand=True, spacing=10)

	for r in rooms:
		room_list.controls.append(r.controls)

	return ft.View(
		route="/rooms",
		appbar=ft.AppBar(
			title=ft.Text("Mes Salons"),
			actions=[
				ft.IconButton(ft.Icons.SETTINGS, on_click=lambda _: page.go("/settings")),
			],
		),
		floating_action_button=ft.FloatingActionButton(
			icon=ft.Icons.ADD,
			tooltip="Créer ou rejoindre",
			on_click=lambda _: page.go("/new_room"),
		),
		controls=[
			ft.Text("Sélectionnez un espace de discussion", size=12, color=ft.Colors.GREY_500),
			room_list,
		],
	)
