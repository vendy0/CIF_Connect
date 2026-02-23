import flet as ft
from login_view import LoginView
from chat_view import ChatView
from settings_view import SettingsView
from rooms_view import RoomsView
from create_room_view import CreateRoomView
from utils import generer_pseudo, rooms, Room, generate_secure_code
# import asyncio


async def main(page: ft.Page):

    page.title = "CIF Connect"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Création des rooms
    room_1, room_2 = (
        Room(
            page,
            1,
            "Salon Général",
            "Discussion libre pour tous",
            ft.Icons.PUBLIC,
            generate_secure_code(),
        ),
        Room(
            page,
            2,
            "Projet Python",
            "Groupe de travail dév",
            ft.Icons.CODE,
            generate_secure_code(),
        ),
    )

    rooms.clear()
    rooms.extend([room_1, room_2])
    page.session.store.set("rooms", rooms)

    # pseudo = generer_pseudo()
    # fixer_pseudo = lambda ps, actuel: ps if ps else actuel

    # ---- ROUTE CHANGE ----
    async def route_change():  # e : ft.RouteChangeEvent):
        # e.route (ou page.route) contient la route active
        if page.route == "/login" or page.route == "/":
            if page.session.store.contains_key("pseudo"):
                page.views.append(await RoomsView(page))
            else:
                page.views.append(await LoginView(page))
        elif page.route == "/rooms":
            page.views.append(await RoomsView(page))
        elif page.route == "/chat":
            page.views.append(await ChatView(page))
        elif page.route == "/settings":
            page.views.append(await SettingsView(page))
        elif page.route == "/new_room":
            page.views.append(await CreateRoomView(page))
        else:
            page.views.append(await LoginView(page))
        page.update()

    # ---- BACK NAVIGATION ----
    async def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            previous = page.views[-1]
            await page.push_route(previous.route)
        else:
            print("Aucune vue précédente.")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Lancement initial
    # async def verify_pseudo(pseudo=None):
    if page.session.store.contains_key("pseudo"):
        await page.push_route("/rooms")
    else:
        await page.push_route("/login")

    # verify_pseudo(pseudo if pseudo else None)
    await route_change()


if __name__ == "__main__":
    # ft.run est le bon standard pour 0.80.5
    ft.run(main, assets_dir="../assets", port=8550)
