import flet as ft
from utils import generer_pseudo, host, port
import httpx
# from flet_storage import FletStorage

# storage = FletStorage("cif_connect_app")
# storage.set("pseudo", page.session.store.get("pseudo"))
# pseudo = storage.get("pseudo")


async def SettingsView(page: ft.Page):
	storage = ft.SharedPreferences()
	pseudo = await storage.get("user_pseudo")
	email = await storage.get("user_email")

	async def go_login(e):
		await storage.remove("cif_token")
		keys = await storage.get_keys("user")
		for key in keys:
			await storage.remove(key)
		await page.push_route("/login")

	async def go_back(e):
		page.views.pop()
		page.update()

	def toggle_theme(e):
		page.theme_mode = (
			ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
		)
		theme_icon.icon = (
			ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
		)
		page.update()

	theme_icon = ft.IconButton(
		icon=ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE,
		on_click=toggle_theme,
	)

	# Référence au texte affichant le pseudo pour mise à jour visuelle
	pseudo_display_text = ft.Text(value=pseudo)

	def changer_pseudo(e):
		# Champ de saisie affichant un nouveau pseudo généré
		nouveau_pseudo_input = ft.TextField(
			value=pseudo,
			read_only=True,
			label="Pseudo suggéré",
		)

		async def valider_changement(e):
			# Mise à jour de la variable globale
			actuel_pseudo = nouveau_pseudo_input.value
			if actuel_pseudo == pseudo:
				dlg.open = False
				page.update()
				return

			# # Mise à jour de l'affichage dans la liste sans recharger la page
			# pseudo_display_text.value = actuel_pseudo
			# await storage.set("user_pseudo", actuel_pseudo)
			# dlg.open = False
			# page.update()

			token = await storage.get("cif_token")
			if not token:
				await page.push_route("/login")

			# 2. On prépare l'enveloppe (le header)
			headers = {"Authorization": f"Bearer {token}"}

			# 3. On demande la liste fraîche au serveur
			try:
				async with httpx.AsyncClient() as client:
					response = await client.put(
						f"http://{host}:{port}/users/pseudo",
						json={"new_pseudo": actuel_pseudo},
						headers=headers,
					)

					if response.status_code != 200:
						nouveau_pseudo_input.error = response.json().get(
							"detail", "Erreur inconnue"
						)
						page.update()
						return

					pseudo_display_text.value = actuel_pseudo
					await storage.set("user_pseudo", actuel_pseudo)
					dlg.open = False
					page.update()

			# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
			except httpx.RequestError as ex:
				print(f"Erreur réseau : {ex}")
				nouveau_pseudo_input.error = "Serveur injoignable"
				page.update()
				return

			except Exception as e:
				# En cas de problème réseau par exemple
				print(f"Erreur de connexion : {e}")
				nouveau_pseudo_input.error = "Erreur inconnue"
				return

		def generer_un_autre(e):
			nouveau_pseudo_input.value = generer_pseudo()
			page.update()

		def fermer_dialogue(e):
			dlg.open = False
			page.update()

		dlg = ft.AlertDialog(
			title=ft.Text("Nouveau Pseudo"),
			modal=True,
			content=ft.Column(
				[
					nouveau_pseudo_input,
					ft.TextButton("Générer un autre", on_click=generer_un_autre),
				],
				tight=True,
			),
			actions=[
				ft.ElevatedButton("Valider", on_click=valider_changement),
				ft.TextButton("Annuler", on_click=fermer_dialogue),
			],
			actions_alignment=ft.MainAxisAlignment.CENTER,
		)

		page.show_dialog(dlg)
		# dlg.open = True
		page.update()

	# Construction de la vue complète avec les ListTiles
	return ft.View(
		route="/settings",
		appbar=ft.AppBar(title=ft.Text("Paramètres")),
		controls=[
			ft.ListTile(
				leading=ft.Icon(ft.Icons.PERSON),
				title=ft.Text("Modifier le pseudo"),
				subtitle=pseudo_display_text,  # Utilise la référence ici
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
			ft.ListTile(
				leading=ft.Icon(ft.Icons.EMAIL),
				title=ft.Text("Email"),
				subtitle=ft.Text(email),
			),
			ft.Divider(),
			ft.TextButton("Déconnexion", icon=ft.Icons.LOGOUT, on_click=go_login),
			ft.TextButton("Retour", icon=ft.Icons.ARROW_BACK, on_click=go_back),
		],
	)
