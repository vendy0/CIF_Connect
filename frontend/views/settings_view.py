import flet as ft
from utils import generer_pseudo
from flet_storage import FletStorage

# def view_pop(page: ft.Page):
# 	if len(page.views) > 1:
# 		page.views.pop()
# 		top_view = page.views[-1]
# 		page.push_route(top_view.route)
# 	else:
# 		print("Impossible de revenir en arrière : une seule view restante.")
#


async def SettingsView(page: ft.Page):
    async def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            previous = page.views[-1]
            await page.push_route(previous.route)
        else:
            print("Aucune vue précédente.")

    storage = FletStorage("cif_connect_app")
    await storage.set("pseudo", page.session.store.get("pseudo"))

    # On déclare 'pseudo' comme global au début pour pouvoir le modifier
    async def back(e):
        pseudo = await storage.get("pseudo")
        page.session.store.set("pseudo", pseudo)
        await page.go_back()
        # page.views.pop()

    async def go_login(e):
        await page.push_route("/login")

    async def view_pop(e):
        await page.push_route("/rooms")

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        theme_icon.icon = ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
        page.update()

    theme_icon = ft.IconButton(
        icon=ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE,
        on_click=toggle_theme,
    )

    # Référence au texte affichant le pseudo pour mise à jour visuelle
    pseudo = await storage.get("pseudo")
    pseudo_display_text = ft.Text(pseudo)

    def changer_pseudo(e):
        # Champ de saisie affichant un nouveau pseudo généré
        nouveau_pseudo_input = ft.TextField(
            value=generer_pseudo(),
            read_only=True,
            label="Pseudo suggéré",
        )

        async def valider_changement(e):
            # Mise à jour de la variable globale
            actuel_pseudo = nouveau_pseudo_input.value
            # Mise à jour de l'affichage dans la liste sans recharger la page
            pseudo_display_text.value = actuel_pseudo
            await storage.set("pseudo", actuel_pseudo)
            dlg.open = False
            page.update()

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
                subtitle=ft.Text("aaaa@gmail.com"),
            ),
            ft.Divider(),
            ft.TextButton("Déconnexion", icon=ft.Icons.LOGOUT, on_click=go_login),
            ft.TextButton("Retour", icon=ft.Icons.ARROW_BACK, on_click=view_pop),
        ],
    )
