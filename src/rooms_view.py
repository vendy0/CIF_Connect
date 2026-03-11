import flet as ft
import httpx
from utils import Room, api, show_top_toast
import json


async def RoomsView(page: ft.Page):
    # 1. On récupère le badge de sécurité (le token)
    storage = ft.SharedPreferences()

    async def go_to_new_room(e):
        await page.push_route("/new_room")
        page.update()

    async def go_to_settings(e):
        await page.push_route("/settings")
        # page.views.append("/settings")
        page.update()

    room_list = ft.ListView(expand=True, spacing=10, padding=10)

    info_text = ft.Text("Chargement des salons...", size=14, color=ft.Colors.GREY_500)

    async def load_rooms():
        nonlocal info_text
        # On supprime toute la partie 'loader' et 'page.overlay' ici

        try:
            response = await api.get("/user/rooms")

            if response.status_code == 401:
                await storage.remove("cif_token")
                await page.push_route("/login")
                return

            data = response.json()

            # Dans rooms_view.py, juste après "rooms = response.json()"
            await storage.set("rooms_cache", json.dumps(data))
            storage.update()

            if not data:
                info_text.value = "Aucun salon disponible pour le moment"
            else:
                info_text.value = "Sélectionnez un espace de discussion"

            room_list.controls.clear()

            for r in data:
                new_room_obj = Room(
                    page=page,
                    room_id=r["id"],
                    name=r["name"],
                    description=r["description"],
                    icon=r["icon"],
                )
                room_list.controls.append(new_room_obj.controls)

            page.update()

        except httpx.RequestError:
            await show_top_toast(page, "Erreur réseau !", True)

    page.run_task(load_rooms)

    return ft.View(
        route="/rooms",
        appbar=ft.AppBar(
            title=ft.Text("CIF Connect"),
            center_title=True,
            automatically_imply_leading=False,
            actions=[
                ft.IconButton(ft.Icons.SETTINGS, on_click=go_to_settings),
            ],
        ),
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Créer ou rejoindre",
            on_click=go_to_new_room,
        ),
        controls=[info_text, room_list],
    )
