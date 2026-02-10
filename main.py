import flet as ft
from views.login_view import LoginView
from views.chat_view import ChatView


def main(page: ft.Page):
	print(page.route)
	page.title = "CIF Connect"
	page.theme_mode = ft.ThemeMode.LIGHT

	# Configuration initiale
	# page.window.width = 400
	# page.window.height = 700

	def route_change(route):
		page.views.clear()

		# Route: Page de Connexion (Accueil)
		if page.route == "/":
			page.views.append(LoginView(page))

		# Route: Chat principal
		elif page.route == "/chat":
			# On récupère le nom d'utilisateur passé en argument (s'il existe)
			# Dans une vraie app, on utiliserait page.session
			user_name = "CliCli"
			page.views.append(ChatView(page, user_name))

		page.update()

	def view_pop(view):
		page.views.pop()
		top_view = page.views[-1]
		page.go(top_view.route)

	page.on_route_change = route_change
	page.on_view_pop = view_pop

	# Lancement sur la page de login
	page.go("/chat")


# Important: assets_dir indique où chercher le logo
ft.app(target=main, assets_dir="assets", port=8550)
