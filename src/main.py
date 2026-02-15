import flet as ft
from login_view import LoginView
from chat_view import ChatView
from settings_view import SettingsView
from rooms_view import RoomsView
from create_room_view import CreateRoomView
from utils import generer_pseudo, rooms, Room, generate_secure_code
# import asyncio

pseudo = ""


async def main(page: ft.Page):
	global pseudo

	page.title = "CIF Connect"
	page.theme_mode = ft.ThemeMode.LIGHT

	# Création des rooms
	room_1, room_2 = (
		Room(
			page,
			1,
			"Salon Général",
			"Discussion libre pour tous",
			ft.Icons.PUBLIC,
			generate_secure_code(),
		),
		Room(
			page,
			2,
			"Projet Python",
			"Groupe de travail dév",
			ft.Icons.CODE,
			generate_secure_code(),
		),
	)

	rooms.clear()
	rooms.extend([room_1, room_2])

	# pseudo = generer_pseudo()
	# fixer_pseudo = lambda ps, actuel: ps if ps else actuel

	# ---- ROUTE CHANGE ----
	async def route_change():  # e : ft.RouteChangeEvent):
		global pseudo
		page.views.clear()

		# e.route (ou page.route) contient la route active
		if page.route == "/login":
			page.views.append(await LoginView(page))
		elif page.route == "/rooms":
			page.views.append(await RoomsView(page, rooms))
		elif page.route == "/chat":
			page.views.append(await ChatView(page, pseudo))
		elif page.route == "/settings":
			cont, ps = await SettingsView(page, pseudo)
			pseudo = ps if ps else pseudo
			page.views.append(cont)
		elif page.route == "/new_room":
			page.views.append(await CreateRoomView(page))

		page.update()

	# ---- BACK NAVIGATION ----
	async def view_pop(e):
		if e.view is not None:
			print("View pop:", e.view)
			page.views.remove(e.view)
			top_view = page.views[-1]
			await page.push_route(top_view.route)

	page.on_route_change = route_change
	page.on_view_pop = view_pop

	# Lancement initial
	# async def verify_pseudo(pseudo=None):
	if pseudo:
		await page.push_route("/rooms")
	else:
		await page.push_route("/login")

	# verify_pseudo(pseudo if pseudo else None)
	await route_change()


if __name__ == "__main__":
	# ft.run est le bon standard pour 0.80.5
	ft.run(main, assets_dir="../assets", port=8550)
