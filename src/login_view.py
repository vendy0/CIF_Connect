import flet as ft
from utils import generer_pseudo
from math import pi


async def LoginView(page: ft.Page):
    is_register_mode = False

    email_input = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL, border_radius=10)
    password_input = ft.TextField(label="Mot de passe", prefix_icon=ft.Icons.LOCK, password=True, can_reveal_password=True, border_radius=10)
    confirm_password_input = ft.TextField(label="Confirmer le mot de passe", prefix_icon=ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True, border_radius=10)

    async def handle_submit(e):
        email = email_input.value.strip()
        password = password_input.value.strip()
        confirm = confirm_password_input.value.strip()

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
            page.session.store.set("pseudo", generer_pseudo())
            await page.push_route("/rooms")

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
        else:
            title = "Connexion"
            subtitle = "Bon retour"
            main_button.content = "Se connecter"
            main_button.icon = ft.Icons.LOGIN
            toggle_button.content = "Pas encore inscrit ? S'inscrire"
            fields = [email_input, password_input]

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
