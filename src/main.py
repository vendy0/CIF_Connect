import flet as ft
from login_view import LoginView
from chat_view import ChatView
from settings_view import SettingsView
from rooms_view import RoomsView
from create_room_view import CreateRoomView
from utils import generer_pseudo, rooms, Room, generate_secure_code

pseudo = ""


def main(page: ft.Page):
	global pseudo

	page.title = "CIF Connect"
	page.theme_mode = ft.ThemeMode.LIGHT

	# Création des rooms
	room_1 = Room(
		page,
		1,
		"Salon Général",
		"Discussion libre pour tous",
		ft.Icons.PUBLIC,
		generate_secure_code(),
	)

	room_2 = Room(
		page,
		2,
		"Projet Python",
		"Groupe de travail dév",
		ft.Icons.CODE,
		generate_secure_code(),
	)

	rooms.clear()
	rooms.extend([room_1, room_2])

	pseudo = generer_pseudo()
	fixer_pseudo = lambda ps, actuel: ps if ps else actuel

	# ---- ROUTE CHANGE ----
	def route_change(e: ft.RouteChangeEvent):
		global pseudo
		page.views.clear()

		# e.route (ou page.route) contient la route active
		if page.route == "/login":
			page.views.append(LoginView(page))
		elif page.route == "/rooms":
			page.views.append(RoomsView(page, rooms))
		elif page.route == "/chat":
			page.views.append(ChatView(page, pseudo))
		elif page.route == "/settings":
			cont, ps = SettingsView(page, pseudo)
			pseudo = fixer_pseudo(ps, pseudo)
			page.views.append(cont)
		elif page.route == "/new_room":
			page.views.append(CreateRoomView(page))

		page.update()

	# ---- BACK NAVIGATION ----
	def view_pop(e: ft.ViewPopEvent):
		# page.pop_route() n'existe pas en Flet.
		# L'approche native consiste à retirer la dernière vue de la pile et à naviguer vers la précédente.
		if len(page.views) > 1:
			page.views.pop()
			top_view = page.views[-1]
			page.push_route(top_view.route)

	page.on_route_change = route_change
	page.on_view_pop = view_pop

	# Lancement initial
	if pseudo:
		page.route = "/rooms"
	else:
		page.route = "/login"
	


if __name__ == "__main__":
	# ft.run est le bon standard pour 0.80.5
	ft.run(main, assets_dir="../assets", port=8550)
