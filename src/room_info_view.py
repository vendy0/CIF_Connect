import flet as ft
from utils import api, show_top_toast, get_avatar_color, COLORS_LOOKUP, get_initials
import httpx
import json


async def RoomInfoView(page: ft.Page):
    storage = ft.SharedPreferences()
    room_id = page.session.store.get("current_room_id")
    current_user_id = page.session.store.get("user_id")  # Assure-toi de stocker ça au login

    if not room_id:
        await page.push_route("/rooms")
        return ft.View(route="/room_info")

    # Variables d'état
    # room_data = # Remplacer room_data = {} par :

    # Avant le return, définissez l'icône d'en-tête
    room_icon_display = ft.Icon(icon=ft.Icons.GROUPS, size=40, color=ft.Colors.ON_PRIMARY_CONTAINER)
    room_name_display = ft.Text("", size=24, weight="bold")
    room_code_display = ft.Text("Public", size=12, color=ft.Colors.OUTLINE)

    is_admin = False

    # Champs éditables
    name_field = ft.TextField(label="Nom du salon", read_only=True, border=ft.InputBorder.UNDERLINE)
    desc_field = ft.TextField(label="Description", read_only=True, multiline=True, border=ft.InputBorder.UNDERLINE)
    code_field = ft.TextField(label="Code d'invitation", value="Salon public", read_only=True, border=ft.InputBorder.UNDERLINE)

    # Bouton de sauvegarde (Caché par défaut)
    save_btn = ft.ElevatedButton("Enregistrer les modifications", icon=ft.Icons.SAVE, visible=False)

    members_list = ft.ListView(spacing=5, padding=10, height=300)

    async def load_room_info():
        nonlocal is_admin
        try:
            cached_rooms_str = await storage.get("rooms_cache")
            if cached_rooms_str:
                rooms = json.loads(cached_rooms_str)

            for r in rooms:
                if r["id"] == room_id:
                    room_data = r
                    break

            if not room_data:
                await show_top_toast(page, "Salon introuvable", True)
                await page.views.pop()
                return

            room_data = r
            room_icon_display.icon = room_data.get("icon", ft.Icons.GROUPS)  # Utilise get par sécurité
            room_name_display.value = room_data["name"]
            if room_data["access_key"]:
                room_code_display.value = f"Code : {room_data['access_key']}"

            # Vérification Admin
            if room_data["creator"]:
                is_admin = room_data["creator"]["id"] == current_user_id

            # Remplissage de l'UI
            name_field.value = room_data["name"]
            desc_field.value = room_data["description"]
            if room_data["access_key"]:
                code_field.value = room_data["access_key"]

            if is_admin:
                name_field.read_only = False
                desc_field.read_only = False
                save_btn.visible = True

            # Simulation d'affichage des membres (À relier à une route API qui liste les membres de la room)
            members = [{"pseudo": "RapideRenard5"}, {"pseudo": "CalmeHibou42"}]  # Exemple

            members_list.controls.clear()
            for m in members:
                members_list.controls.append(
                    ft.ListTile(
                        leading=ft.CircleAvatar(content=ft.Text(get_initials(m["pseudo"])), bgcolor=get_avatar_color(m["pseudo"], COLORS_LOOKUP)),
                        title=ft.Text(m["pseudo"], weight="bold"),
                    )
                )
            page.update()

        except httpx.RequestError:
            await show_top_toast(page, "Erreur réseau !", True)

    async def save_changes(e):
        try:
            payload = {
                "name": name_field.value,
                "description": desc_field.value,
            }
            # Appel API selon ton main.py: PUT /rooms/{room_id}?user_id={id}
            response = await api.put(f"/rooms/{room_id}?user_id={current_user_id}", data=payload)

            if response.status_code == 200:
                await show_top_toast(page, "Modifications enregistrées !")
                page.session.store.set("current_room_name", name_field.value)
            else:
                await show_top_toast(page, "Erreur lors de la modification", True)
        except Exception as ex:
            await show_top_toast(page, "Erreur réseau", True)

    save_btn.on_click = save_changes

    # Déclenchement du chargement
    page.run_task(load_room_info)

    return ft.View(
        route=f"/room_info/{room_id}",
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda _: page.views.pop()),
            title=ft.Text("Détails du salon", weight="bold"),
            bgcolor="surface",
            center_title=True,
        ),
        controls=[
            ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        # En-tête avec Avatar et Nom
                        ft.Container(height=20),
                        ft.CircleAvatar(radius=50, content=room_icon_display, bgcolor=ft.Colors.PRIMARY_CONTAINER),
                        room_name_display,
                        room_code_display,
                        ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                        # Formulaire (dans un Container pour limiter la largeur sur PC/Tablette)
                        ft.Container(
                            content=ft.Column(
                                [
                                    name_field,
                                    desc_field,
                                    code_field,
                                    ft.Container(content=save_btn, alignment=ft.Alignment.CENTER, margin=ft.margin.only(top=15, bottom=15)),
                                ]
                            ),
                            padding=ft.padding.symmetric(horizontal=20),
                        ),
                        # Section Membres
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("Membres", size=18, weight="bold"),
                                            ft.Text("En ligne", size=12, color=ft.Colors.GREEN_500),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Container(content=members_list, bgcolor=ft.Colors.SURFACE_CONTAINER_LOW, border_radius=15, padding=5),
                                ]
                            ),
                            padding=ft.padding.symmetric(horizontal=20),
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
            )
        ],
    )
