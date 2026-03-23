import flet as ft
from utils import api, show_top_toast, format_date
from datetime import datetime
import httpx


async def AdminView(page: ft.Page):
    storage = ft.SharedPreferences()

    # Redirection sécurité si non admin (à adapter selon ta logique d'authentification)
    current_role = await storage.get("user_role")
    # if current_role != "admin":
    #     await show_top_toast(page, "Accès refusé. Vous n'êtes pas administrateur.", True)
    # Décommente la ligne ci-dessous pour forcer la redirection
    # await page.push_route("/rooms")

    # ==========================================================
    #                 COMPOSANTS DE L'INTERFACE
    # ==========================================================

    reports_list = ft.ListView(expand=True, spacing=10, padding=20)
    users_list = ft.ListView(expand=True, spacing=10, padding=20)

    # Loader global
    loading_ring = ft.Container(content=ft.ProgressRing(), alignment=ft.Alignment.CENTER, expand=True, visible=False)

    # ==========================================================
    #                 LOGIQUE DES SIGNALEMENTS
    # ==========================================================

    async def load_reports():
        loading_ring.visible = True
        reports_list.visible = False
        page.update()

        try:
            response = await api.get("/reports")
            if response.status_code == 200:
                reports = response.json()
                reports_list.controls.clear()

                if not reports:
                    reports_list.controls.append(ft.Container(content=ft.Text("Aucun signalement à traiter.", color=ft.Colors.GREY, italic=True), alignment=ft.Alignment.CENTER, padding=50))
                else:
                    for report in reports:
                        status_color = ft.Colors.ORANGE if report["status"] == "pending" else (ft.Colors.GREEN if report["status"] == "resolved" else ft.Colors.RED)
                        status_text = "En attente" if report["status"] == "pending" else ("Résolu" if report["status"] == "resolved" else "Rejeté")

                        reported_pseudo = report["reported"]["pseudo"] if report.get("reported") else "Utilisateur inconnu"
                        reporter_pseudo = report["reporter"]["pseudo"] if report.get("reporter") else "Anonyme"
                        date_str = format_date(datetime.fromisoformat(report["created_at"]))

                        # Extraction sécurisée (évite un crash si le message a été supprimé de la BDD)
                        message_content = report.get("message", {}).get("content", "Message introuvable") if report.get("message") else "Message introuvable"

                        reports_list.controls.append(
                            ft.Card(
                                content=ft.ListTile(
                                    leading=ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED_400),
                                    title=ft.Text(f"Signalé : {reported_pseudo}", weight="bold"),
                                    subtitle=ft.Column(
                [
                    ft.Text(f"Motif : {report['raison']}", weight="bold"),
                    ft.Text(f"« {message_content} »", italic=True, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(f"Par : {reporter_pseudo} le {date_str}", size=11, color=ft.Colors.OUTLINE)
                ], 
                spacing=2
            ),
                                    trailing=ft.Container(
                                        content=ft.Text(status_text, size=12, weight="bold", color=status_color),
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        bgcolor=ft.Colors.with_opacity(0.1, status_color),
                                        border_radius=10,
                                    ),
                                    # Désactive le clic si ce n'est plus en attente
                                    on_click=lambda e, r=report: page.run_task(open_resolve_dialog, r) if r["status"] == "pending" else None,
                                )
                            )
                        )
            elif response.status_code == 401:
                await page.push_route("/login")
        except httpx.RequestError:
            await show_top_toast(page, "Erreur réseau lors du chargement des signalements.", True)
        finally:
            loading_ring.visible = False
            reports_list.visible = True
            page.update()

    async def open_resolve_dialog(report):
        print("Cliqué")
        action_dropdown = ft.Dropdown(
            label="Action à prendre",
            options=[
                ft.dropdown.Option(key="dismissed", text="Rejeter (Faux signalement)"),
                ft.dropdown.Option(key="resolved_warn", text="Avertissement (Sans bannissement)"),
                ft.dropdown.Option(key="resolved_ban", text="Bannir l'utilisateur"),
            ],
            width=400,
            value="resolved_warn",
        )

        ban_duration_dropdown = ft.Dropdown(
            label="Durée du bannissement",
            options=[
                ft.dropdown.Option(key="1", text="1 Heure"),
                ft.dropdown.Option(key="24", text="24 Heures"),
                ft.dropdown.Option(key="168", text="7 Jours"),
                ft.dropdown.Option(key="0", text="Définitif"),
            ],
            width=400,
            value="24",
            visible=False,
        )

        ban_reason_input = ft.TextField(label="Motif du bannissement (Optionnel)", width=400, visible=False, value=report["raison"])

        def on_action_change(e):
            is_ban = action_dropdown.value == "resolved_ban"
            ban_duration_dropdown.visible = is_ban
            ban_reason_input.visible = is_ban
            page.update()

        action_dropdown.on_change = on_action_change

        async def submit_resolution(e):
            submit_btn.disabled = True
            page.update()

            status_val = "resolved" if action_dropdown.value in ["resolved_warn", "resolved_ban"] else "dismissed"
            ban_user = action_dropdown.value == "resolved_ban"
            duration = int(ban_duration_dropdown.value) if ban_user and ban_duration_dropdown.value != "0" else None

            payload = {"status": status_val, "ban_user": ban_user, "ban_duration_hours": duration, "ban_reason": ban_reason_input.value if ban_user else None}

            try:
                response = await api.post(f"/reports/{report['id']}/resolve", data=payload)
                if response.status_code == 200:
                    page.pop_dialog()
                    await show_top_toast(page, "Signalement traité avec succès.")
                    await load_reports()
                    await load_users()  # Rafraîchir la liste des utilisateurs si un ban a eu lieu
                else:
                    await show_top_toast(page, "Erreur lors du traitement.", True)
            except httpx.RequestError:
                await show_top_toast(page, "Erreur réseau.", True)
            finally:
                submit_btn.disabled = False
                page.update()

        submit_btn = ft.ElevatedButton("Valider", on_click=submit_resolution, icon=ft.Icons.CHECK)

        dlg = ft.AlertDialog(
            title=ft.Text("Traiter le signalement"),
            content=ft.Column(
                [
                    ft.Text(f"Utilisateur signalé : {report['reported']['pseudo'] if report.get('reported') else 'Inconnu'}", weight="bold"),
                    ft.Text(f"Message ID : {report['message_id']}", size=12, color=ft.Colors.OUTLINE),
                    ft.Divider(),
                    action_dropdown,
                    ban_duration_dropdown,
                    ban_reason_input,
                ],
                tight=True,
                spacing=15,
            ),
            actions=[ft.TextButton("Annuler", on_click=lambda _: page.pop_dialog()), submit_btn],
        )
        await page.show_dialog(dlg)
        page.update()

    # ==========================================================
    #                 LOGIQUE DES UTILISATEURS
    # ==========================================================

    async def load_users():
        try:
            response = await api.get("/users")
            if response.status_code == 200:
                users = response.json()
                users_list.controls.clear()

                for user in users:
                    is_banned = user.get("is_banned", False)
                    badge_color = ft.Colors.RED if is_banned else ft.Colors.GREEN
                    badge_text = "Banni" if is_banned else "Actif"
                    role_icon = ft.Icons.ADMIN_PANEL_SETTINGS if user["role"] == "admin" else ft.Icons.PERSON

                    users_list.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(role_icon, color=ft.Colors.BLUE_400),
                            title=ft.Text(user["pseudo"], weight="bold"),
                            subtitle=ft.Text(user["email"], size=12),
                            trailing=ft.Container(
                                content=ft.Text(badge_text, size=11, color=badge_color, weight="bold"),
                                border=ft.border.all(1, badge_color),
                                border_radius=5,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            ),
                        )
                    )
                page.update()
        except httpx.RequestError:
            pass  # Erreur silencieuse gérée globalement

    # ==========================================================
    #                 CHARGEMENT INITIAL ET VUE
    # ==========================================================

    def handle_tab_change(e):
        if e.control.selected_index == 0:
            page.run_task(load_reports)
        elif e.control.selected_index == 1:
            page.run_task(load_users)

    tabs = ft.Tabs(
        selected_index=0,
        length=2,
        animation_duration=300,
        on_change=handle_tab_change,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                # ==========================
                #        BARRE D’ONGLETS
                # ==========================
                ft.TabBar(
                    tabs=[
                        ft.Tab(
                            label="Signalements",
                            icon=ft.Icons.REPORT_PROBLEM_ROUNDED,
                        ),
                        ft.Tab(
                            label="Utilisateurs",
                            icon=ft.Icons.PEOPLE_ALT_ROUNDED,
                        ),
                    ],
                    tab_alignment=ft.TabAlignment.CENTER,
                ),
                # ==========================
                #        CONTENU ONGLET
                # ==========================
                ft.TabBarView(
                    expand=True,
                    controls=[
                        # -------- ONGLET SIGNALMENTS --------
                        ft.Stack(
                            expand=True,
                            controls=[ft.Container(expand=True, content=reports_list), loading_ring],
                        ),
                        # -------- ONGLET UTILISATEURS --------
                        users_list,
                    ],
                ),
            ],
        ),
    )

    # Lancement initial
    page.run_task(load_reports)

    return ft.View(
        route="/admin",
        appbar=ft.AppBar(
            title=ft.Text("Administration", weight="bold"),
            center_title=True,
            bgcolor=ft.Colors.SURFACE,
            elevation=2,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda _: page.run_task(page.push_route, "/rooms")),
        ),
        controls=[tabs],
    )
