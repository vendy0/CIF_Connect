import flet as ft


def afficher_chat(page: ft.Page):
    # --- CORRECTION DU BUG D'AFFICHAGE ---
    # On remet l'alignement à "START" (en haut à gauche) pour que le chat prenne tout l'espace
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = (
        ft.CrossAxisAlignment.STRETCH
    )  # Important pour remplir la largeur

    page.controls.clear()

    # 1. Les composants du chat
    chat_messages = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    nouveau_message = ft.TextField(
        hint_text="Message...",
        expand=True,
        on_submit=lambda e: envoyer_clic(e),  # Permet d'envoyer avec "Entrée"
    )

    def envoyer_clic(e):
        if nouveau_message.value:
            chat_messages.controls.append(ft.Text(f"Anonyme: {nouveau_message.value}"))
            nouveau_message.value = ""
            nouveau_message.focus()
            page.update()

    barre_envoi = ft.Row(
        controls=[
            nouveau_message,
            ft.IconButton(icon=ft.icons.Icons.SEND, on_click=envoyer_clic),
        ]
    )

    # 2. La mise en page principale
    ecran_chat = ft.Column(
        controls=[
            ft.Text("Bienvenue sur CIF Connect !", size=30, color="blue"),
            chat_messages,
            barre_envoi,
        ],
        expand=True,  # La colonne prend toute la hauteur disponible
    )

    page.add(ecran_chat)
    page.update()


def afficher_login(page: ft.Page):
    # Configuration pour le Login (Centré)
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.controls.clear()

    titre = ft.Text("Connexion CIF Connect", size=25, weight="bold")
    champ_email = ft.TextField(label="Email @interfamilia.com", width=300)
    message_retour = ft.Text("", size=14)

    champ_code = ft.TextField(
        label="Code reçu",
        visible=False,
        width=300,
        password=True,
        can_reveal_password=True,
    )

    def action_bouton(e):
        # Étape 1 : Vérification Email
        if not champ_code.visible:
            email = champ_email.value.lower()
            if email.endswith("@interfamilia.com"):
                message_retour.value = "✅ Code envoyé !"
                message_retour.color = "green"
                champ_email.disabled = True
                champ_code.visible = True
                bouton.text = "Vérifier le code"
                champ_code.focus()
            else:
                message_retour.value = "❌ Email invalide."
                message_retour.color = "red"
            page.update()

        # Étape 2 : Vérification Code
        else:
            if champ_code.value == "1234":
                # C'est ici qu'on change de monde ! 🌍
                afficher_chat(page)
            else:
                message_retour.value = "❌ Code incorrect."
                message_retour.color = "red"
                page.update()

    bouton = ft.ElevatedButton("Recevoir le code", on_click=action_bouton)

    page.add(titre, champ_email, message_retour, champ_code, bouton)
    page.update()


def main(page: ft.Page):
    page.title = "CIF Connect"
    # On lance directement l'écran de login au démarrage
    afficher_login(page)


ft.run(main, port=8550, view=ft.AppView.WEB_BROWSER)
