import flet as ft


def main(page: ft.Page):
	page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
	page.vertical_alignment = ft.MainAxisAlignment.CENTER

	# 1. Nos composants
	titre = ft.Text("Connexion CIF Connect", size=25, weight="bold")
	champ_email = ft.TextField(label="Email @interfamilia.com", width=300)

	# C'est notre nouveau messager !
	message_retour = ft.Text("", size=14)

	# ... (tes autres composants)

	# 1. Le champ pour le code (caché par défaut)
	champ_code = ft.TextField(
		label="Code reçu par email",
		visible=False,  # <-- Il est là mais invisible
		width=300,
		password=True,
		can_reveal_password=True,
	)

	def valider_connexion(e):
		if not champ_code.visible:
			email = champ_email.value.lower()
			if email.endswith("@interfamilia.com"):
				# L'email est bon !
				message_retour.value = "✅ Code envoyé ! Vérifie ta boîte mail."
				message_retour.color = "green"

				# --- LA TRANSITION ---
				champ_email.disabled = True  # On verrouille l'email
				champ_code.visible = True  # On montre le champ code
				bouton.text = "Vérifier le code"  # On change le texte du bouton
				champ_code.focus()
				page.update()
			else:
				message_retour.value = "❌ Email invalide."
				message_retour.color = "red"
				champ_email.focus()
				page.update()
		else:
			if champ_code.value == "1234":  # On imagine que le code est 1234
				message_retour.value = "✅ Connexion réussie !"
				message_retour.color = "blue"
				page.controls.clear()
				
				# 2. On ajoute le message de bienvenue ou l'interface de chat
				page.add(ft.Text("Bienvenue sur CIF Connect !", size=30, color="blue"))
				
				# 3. On rafraîchit
				page.update()
			else:
				message_retour.value = "❌ Code incorrect."
				message_retour.color = "red"
				champ_code.focus()
		page.update()

	bouton = ft.Button("Recevoir le code", on_click=valider_connexion)
	page.add(
		titre,
		champ_email,
		champ_code,
		message_retour,  # On l'ajoute entre le champ et le bouton
		bouton,
	)


ft.run(main, port=8550, view=ft.AppView.WEB_BROWSER)
