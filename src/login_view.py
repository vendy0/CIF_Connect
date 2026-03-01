import flet as ft
import httpx
from utils import generer_pseudo, decode_token
from math import pi

async def LoginView(page: ft.Page):
	host = "127.0.0.1"
	port = "8000"

	is_register_mode = False

	# Dans ton LoginView (Flet 0.80.5)
	storage = ft.SharedPreferences()

	email_input = ft.TextField(
		label="Email", prefix_icon=ft.Icons.EMAIL, border_radius=10, multiline=False
	)
	password_input = ft.TextField(
		label="Mot de passe",
		prefix_icon=ft.Icons.LOCK,
		password=True,
		can_reveal_password=True,
		border_radius=10,
		multiline=False,
	)
	confirm_password_input = ft.TextField(
		label="Confirmer le mot de passe",
		prefix_icon=ft.Icons.LOCK_OUTLINE,
		password=True,
		can_reveal_password=True,
		border_radius=10,
	)

	async def login_success(token_data):
		# On stocke le jeton pour les prochaines fois
		await storage.set("cif_token", token_data["access_token"])

		# On peut aussi stocker le pseudo pour l'affichage rapide
		# page.session.store reste utile pour les données temporaires de session
		page.session.store.set("token", token_data["access_token"])
		token = token_data["access_token"]

		# Décodage
		user_info = await decode_token(token)

		# Stockage des infos utiles via SharedPreferences
		if "pseudo" in user_info:
			await storage.set("user_pseudo", user_info["pseudo"])
		if "role" in user_info:
			await storage.set("user_role", user_info["role"])
		if "email" in user_info:
			await storage.set("user_email", user_info["email"])

	async def handle_submit(e):
		email = email_input.value.strip()
		password = password_input.value.strip()
		confirm = confirm_password_input.value.strip()

		if is_register_mode and len(password) < 8:
			password_input.error = "Le mot de passe est trop court !"
			page.update()
			return

		email_input.error = password_input.error = confirm_password_input.error = None

		if not email:
			email_input.error = "Champ requis"
		if not password:
			password_input.error = "Champ requis"
		if is_register_mode:
			if not confirm:
				confirm_password_input.error = "Confirmation requise"
			elif confirm != password:
				confirm_password_input.error = "Les mots ne correspondent pas"

		page.update()

		if email and password and (not is_register_mode or password == confirm):
			# ... validation locale (champs vides, etc.) ...
			payload = {"email": email_input.value, "password": password_input.value}

			endpoint = ""
			if is_register_mode:
				payload["pseudo"] = generer_pseudo()
				endpoint = "/register"
			else:
				endpoint = "/login"

			async with httpx.AsyncClient() as client:
				try:
					response = await client.post(f"http://{host}:{port}{endpoint}", json=payload)
					# if len(response) == 0:
					# 	email_input.error = "Rien n'a été reçu du serveur !"
					# 	page.update()
					# 	return
					if response.status_code in [200, 201]:
						data = response.json()
						await login_success(data)
						await page.push_route("/rooms")
					else:
						error_detail = response.json().get("detail", "Erreur inconnue")
						email_input.error = error_detail
						page.update()

				# VRAIE erreur réseau (serveur éteint, pas de wifi, etc.)
				except httpx.RequestError as ex:
					print(f"Erreur réseau : {ex}")
					email_input.error = "Serveur injoignable"
					page.update()

				# Erreur dans ton code Python (ex: faute de frappe, variable manquante)
				except Exception as ex:
					print(f"BINGO ! Erreur Python interceptée : {ex}")
					email_input.error = f"Erreur interne au code"
					page.update()

	main_button = ft.Button(width=220, height=50, on_click=handle_submit)
	toggle_button = ft.TextButton()

	def build_form():
		if is_register_mode:
			title = "Créer un compte"
			subtitle = "Entre dans l’espace"
			main_button.content = "S'inscrire"
			main_button.icon = ft.Icons.PERSON_ADD
			toggle_button.content = "Déjà inscrit ? Se connecter"
			fields = [email_input, password_input, confirm_password_input]
			email_input.error = None
			password_input.error = None
			confirm_password_input.error = None
		else:
			title = "Connexion"
			subtitle = "Bon retour"
			main_button.content = "Se connecter"
			main_button.icon = ft.Icons.LOGIN
			toggle_button.content = "Pas encore inscrit ? S'inscrire"
			fields = [email_input, password_input]
			email_input.error = None
			password_input.error = None

		return ft.Container(
			width=400,
			padding=30,
			border_radius=20,
			bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
			animate_rotation=400,
			animate_scale=400,
			rotate=0,
			scale=1,
			content=ft.Column(
				spacing=15,
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				controls=[
					ft.Text(title, size=28, weight=ft.FontWeight.BOLD),
					ft.Text(subtitle, size=14, color=ft.Colors.GREY_500),
					ft.Divider(),
					*fields,
					main_button,
					toggle_button,
				],
			),
		)

	switcher = ft.AnimatedSwitcher(
		content=build_form(),
		transition=ft.AnimatedSwitcherTransition.SCALE,
		duration=400,
		switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
		switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
	)

	def toggle_mode(e):
		nonlocal is_register_mode
		is_register_mode = not is_register_mode

		# L'AnimatedSwitcher s'occupe déjà de l'effet de transition (SCALE)
		switcher.content = build_form()
		page.update()

	toggle_button.on_click = toggle_mode

	return ft.View(
		route="/login",
		vertical_alignment=ft.MainAxisAlignment.CENTER,
		horizontal_alignment=ft.CrossAxisAlignment.CENTER,
		controls=[switcher],
	)
