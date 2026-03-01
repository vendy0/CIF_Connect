import flet as ft
from login_view import LoginView
from chat_view import ChatView
from settings_view import SettingsView
from rooms_view import RoomsView
from create_room_view import CreateRoomView
from utils import generer_pseudo, view_pop, decode_token
# import asyncio


async def main(page: ft.Page):
	storage = ft.SharedPreferences()
	page.title = "CIF Connect"
	page.theme_mode = ft.ThemeMode.SYSTEM

	# ---- ROUTE CHANGE ----
	async def route_change():  # e : ft.RouteChangeEvent):
		if page.route in ["/login", "/", "/rooms"]:
			page.views.clear()
		
		# e.route (ou page.route) contient la route active
		if page.route == "/login" or page.route == "/":
			page.views.append(await LoginView(page))
		elif page.route == "/rooms":
			page.views.append(await RoomsView(page))
		elif page.route == "/chat":
			page.views.append(await ChatView(page))
		elif page.route == "/settings":
			page.views.append(await SettingsView(page))
		elif page.route == "/new_room":
			page.views.append(await CreateRoomView(page))
		else:
			page.views.append(await LoginView(page))
		page.update()

	# ---- BACK NAVIGATION ----

	page.on_route_change = route_change
	page.on_view_pop = lambda e: view_pop(e.view, page)

	if await storage.contains_key("cif_token"):

		# On récupère le token
		token = await storage.get("cif_token")

		# Décodage
		user_info = await decode_token(token)

		# Stockage des infos utiles via SharedPreferences
		if "pseudo" in user_info:
			await storage.set("user_pseudo", user_info["pseudo"])
		if "role" in user_info:
			await storage.set("user_role", user_info["role"])
		if "email" in user_info:
			await storage.set("user_email", user_info["email"])
		await page.push_route("/rooms")
	else:
		await page.push_route("/login")

	await route_change()


if __name__ == "__main__":
	# ft.run est le bon standard pour 0.80.5
	ft.run(main, assets_dir="../assets", port=8550)
