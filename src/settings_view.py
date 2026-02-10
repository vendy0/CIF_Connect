import flet as ft
from utils import generer_pseudo

def SettingsView(page: ft.Page, pseudo):
	def toggle_theme(e):
		page.theme_mode = (
			ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
		)
		theme_icon.icon = (
			ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
		)
		page.update()

	theme_icon = ft.IconButton(ft.Icons.DARK_MODE, on_click=toggle_theme)
	
	def changer_pseudo():
		pass
	
	
	return ft.View(
		route="/settings",
		appbar=ft.AppBar(title=ft.Text("Paramètres")),
		controls=[
			ft.ListTile(
				leading=ft.Icon(ft.Icons.PERSON),
				title=ft.Text("Modifier le pseudo"),
				subtitle=ft.Text(pseudo),
				on_click=changer_pseudo,
			),
			ft.ListTile(
				leading=ft.Icon(ft.Icons.PALETTE),
				title=ft.Text("Thème de l'application"),
				trailing=theme_icon,
			),
			ft.ListTile(
				leading=ft.Icon(ft.Icons.CALENDAR_MONTH),
				title=ft.Text("Membre depuis"),
				subtitle=ft.Text("10 Février 2026"),
			),
			ft.Divider(),
			ft.TextButton(
				"Déconnexion", icon=ft.Icons.LOGOUT, on_click=lambda _: page.go("/login")
			),
		],
	), pseudo
