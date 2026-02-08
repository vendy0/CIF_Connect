import flet as ft


def main(page: ft.Page):
	# C'est ici qu'on configure notre "tableau blanc"
	page.title = "CIF Connect"
	page.vertical_alignment = ft.MainAxisAlignment.CENTER  # Centre le contenu

	# On crée un composant texte
	texte_bienvenue = ft.Text("Bienvenue sur InterPam !", size=30, color="blue")

	# On l'ajoute à la page
	page.add(texte_bienvenue)


# On lance l'application
ft.app(target=main, view=ft.AppView.WEB_BROWSER)
