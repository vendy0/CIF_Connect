import flet as ft
from login_view import LoginView
from chat_view import ChatView
from settings_view import SettingsView
from rooms_view import RoomsView
from create_room_view import CreateRoomView
from utils import generer_pseudo

pseudo = ""


def main(page: ft.Page):
	global pseudo
	pseudo = generer_pseudo()
	# Syntaxe : valeur_si_vrai if condition else valeur_si_faux
	fixer_pseudo = lambda ps, actuel: ps if ps else actuel

	# if page.route == "/":
	# 	view_pop(e)
	if pseudo:
		page.go("/rooms")
	else:
		page.go("/login")

	page.title = "CIF Connect"
	page.theme_mode = ft.ThemeMode.LIGHT

	# Configuration initiale
	# page.window.width = 400
	# page.window.height = 700
	def route_change(route):
		global pseudo
		page.views.clear()
		if page.route == "/login":
			page.views.append(LoginView(page))
		elif page.route == "/rooms":
			page.views.append(RoomsView(page))
		elif page.route == "/chat":
			page.views.append(ChatView(page, pseudo))
		elif page.route == "/settings":
			cont, ps = SettingsView(page, pseudo)
			pseudo = fixer_pseudo(ps, pseudo)
			page.views.append(cont)
		elif page.route == "/create_room":
			page.views.append(CreateRoomView(page))
		page.update()

	def view_pop(view):
		page.views.pop()
		top_view = page.views[-1]
		page.go(top_view.route)

	page.on_route_change = route_change
	page.on_view_pop = view_pop

	# Lancement sur la page de login
	page.go("/login")


# Important: assets_dir indique où chercher le logo
ft.app(target=main, assets_dir="../assets", port=8550)
