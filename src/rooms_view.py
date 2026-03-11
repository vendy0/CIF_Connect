import flet as ft
import httpx
from utils import Room, api, show_top_toast
import json


async def RoomsView(page: ft.Page):
	# 1. On récupère le badge de sécurité (le token)
	storage = ft.SharedPreferences()

	def build_empty_rooms_view():
		return ft.Container(
			content=ft.Column(
				[
					ft.Icon(
						icon=ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED,
						size=80,
						color=ft.Colors.OUTLINE_VARIANT,
					),
					ft.Text(
						"Tout est calme ici...",
						size=20,
						weight="bold",
						color=ft.Colors.ON_SURFACE,
					),
					ft.Text(
						"Aucun salon actif pour le moment.\nReviens plus tard ou contacte un admin !",
						size=14,
						color=ft.Colors.OUTLINE,
						text_align=ft.TextAlign.CENTER,
					),
				],
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				spacing=10,
			),
			# horizontal_alignment=ft.CrossAxisAlignment.CENTER,
			# vertical_alignment=ft.MainAxisAlignment.CENTER,
			padding=ft.padding.only(top=200),
			alignment=ft.Alignment.CENTER,
			expand=True,
		)

	async def go_to_new_room(e):
		await page.push_route("/new_room")
		page.update()

	async def go_to_settings(e):
		await page.push_route("/settings")
		# page.views.append("/settings")
		page.update()

	room_list = ft.ListView(expand=True, spacing=2, padding=10)

	info_text = ft.Text("Chargement des salons...", size=14, margin=ft.margin.only(bottom=20), color=ft.Colors.GREY_500)
	container_principal = ft.Container(
		content=ft.ProgressRing(),  # Loader initial
		expand=True,
		alignment=ft.Alignment.CENTER,
	)

	async def load_rooms():
		nonlocal info_text, container_principal
		# On supprime toute la partie 'loader' et 'page.overlay' ici

		try:
			response = await api.get("/user/rooms")

			if response.status_code == 401:
				await storage.remove("cif_token")
				await page.push_route("/login")
				return

			data = response.json()

			# Dans rooms_view.py, juste après "rooms = response.json()"
			await storage.set("rooms_cache", json.dumps(data))
			storage.update()

			if not data:
				info_text.value = "Aucun salon disponible pour le moment"
				container_principal.content = build_empty_rooms_view()
				container_principal.alignment = ft.Alignment.CENTER
				return
			else:
				info_text.value = "Sélectionnez un espace de discussion"

			room_list.controls.clear()
			room_list.controls.append(info_text)

			for r in data:
				new_room_obj = Room(
					page=page,
					room_id=r["id"],
					name=r["name"],
					description=r["description"],
					icon=r["icon"],
				)
				room_list.controls.append(new_room_obj.controls)
				room_list.controls.append(ft.Divider(height=2))

			container_principal.content = room_list
			container_principal.alignment = None
			page.update()

		except httpx.RequestError:
			await show_top_toast(page, "Erreur réseau !", True)

	page.run_task(load_rooms)

	return ft.View(
		route="/rooms",
		appbar=ft.AppBar(
			title=ft.Text("CIF Connect"),
			center_title=True,
			automatically_imply_leading=False,
			actions=[
				ft.IconButton(ft.Icons.SETTINGS, on_click=go_to_settings),
			],
		),
		floating_action_button=ft.FloatingActionButton(
			icon=ft.Icons.ADD,
			tooltip="Créer ou rejoindre",
			on_click=go_to_new_room,
		),
		controls=[container_principal],
	)
