import flet as ft
# import asyncio
# class Room_Description()


async def RoomsView(page: ft.Page, rooms):
	# 	# Simulation de données (à remplacer par la BDD plus tard)
	async def go_to_new_room(e):
		await page.push_route("/new_room")
		page.update()

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
			on_click=go_to_new_room,
		),
		controls=[
			ft.Text("Sélectionnez un espace de discussion", size=12, color=ft.Colors.GREY_500),
			room_list,
		],
	)
