import flet as ft
import time
import asyncio
from utils import generer_pseudo
# from utils import shake


async def LoginView(page: ft.Page):

    def update_fields(*fields):
        for f in fields:
            f.update()
        page.update()

    async def login_click(e):
        email = email_input.value.strip()
        mdp = password_input.value
        if not email:
            email_input.error = "Veuillez remplir tous les champs"
        else:
            email_input.error = None
        if not mdp:
            password_input.error = "Veuillez remplir tous les champs"
        else:
            password_input.error = None
            password_input.update()
        page.update()
        if mdp and email:
            if email != "aaaa":
                email_input.error = "Email incorrect !"
            elif mdp != "1234":
                email_input.error = None
                # await shake(password_input, page)
                password_input.error = "Mot de passe incorrect !"
                await page.push_route("/login")

            # Simulation de chargement
            else:
                login_btn.content = ft.ProgressRing(width=20, height=20, stroke_width=2, color="white")
                login_btn.disabled = True
                login_btn.icon = None
                page.update()

                # time.sleep(10)  # Juste pour l'effet visuel

                # --- ICI : Connecter plus tard à ta BDD (gestion_bdd.db) ---
                # Pour l'instant, on stocke le pseudo dans la session et on navigue
                # On prend la partie avant le @ comme pseudo temporaire
                page.session.store.set("pseudo", generer_pseudo())
                await page.push_route("/rooms")
            update_fields(email_input, password_input)
        page.update()

    # Lopush_route
    lopush_route = ft.Image(
        src="lopush_route.png",  # Flet cherche automatiquement dans 'assets'
        width=120,
        height=120,
        fit=ft.BoxFit.CONTAIN,
    )

    # Champs de saisie
    email_input = ft.TextField(
        label="Email personnel",
        prefix_icon=ft.Icons.EMAIL,
        border_radius=10,
        keyboard_type=ft.KeyboardType.EMAIL,
        on_submit=lambda e: password_input.focus(),
    )

    password_input = ft.TextField(
        label="Mot de passe",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        border_radius=10,
        on_submit=login_click,  # Permet de valider avec "Entrée"
    )

    login_btn = ft.ElevatedButton(
        content="Se connecter",
        icon=ft.Icons.LOGIN,
        width=200,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=ft.Colors.BLUE_600,
            color="white",
        ),
        on_click=login_click,
    )

    # Structure de la page (View)
    return ft.View(
        route="/",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(height=20),  # Espace vide
                        lopush_route,
                        ft.Text(
                            "CIF Connect",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_900,
                        ),
                        ft.Text("Chat anonyme du campus", size=16, color=ft.Colors.GREY_500),
                        ft.Container(height=30),
                        email_input,
                        ft.Container(height=10),
                        password_input,
                        ft.Container(height=20),
                        login_btn,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=30,
                alignment=ft.Alignment.CENTER,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
