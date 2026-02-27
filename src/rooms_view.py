import flet as ft
import httpx
# import asyncio
# class Room_Description()


host = "127.0.0.1"
port = "8000"


async def RoomsView(page: ft.Page):


    # 1. On récupère le badge de sécurité (le token)
    sp = ft.SharedPreferences()
    token = await sp.get("cif_token")

    # 2. On prépare l'enveloppe (le header)
    headers = {"Authorization": f"Bearer {token}"}

    # 3. On demande la liste fraîche au serveur
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{host}:{port}/rooms", headers=headers)

            # Si le jeton est expiré ou invalide (401)
            if response.status_code == 401:
                await sp.remove("cif_token")  # On nettoie
                await page.push_route("/login")  # On redirige
                return

            rooms_data = response.json()
    except Exception as e:
        # En cas de problème réseau par exemple
        print(f"Erreur de connexion : {e}")
        await page.push_route("/login")
        return

    # 	# Simulation de données (à remplacer par la BDD plus tard)
    async def go_to_new_room(e):
        await page.push_route("/new_room")
        page.update()

    async def go_to_settings(e):
        await page.push_route("/settings")
        # page.views.append("/settings")
        page.update()

    room_list = ft.ListView(expand=True, spacing=10, padding=10)

    for r in rooms:
        # Création de l'objet Room à partir du dictionnaire 'r'
        new_room_obj = Room(page=page, room_id=r["id"], name=r["name"], desc=r["description"], icon=r["icon"])
        # Ajout du composant visuel à la ListView
        room_list.controls.append(new_room_obj.controls)

    if not rooms:
        info_text = ft.Text(
            "Aucun salon disponible pour le moment",
            size=12,
            color=ft.Colors.GREY_500,
        )
    else:
        info_text = ft.Text(
            "Sélectionnez un espace de discussion",
            size=12,
            color=ft.Colors.GREY_500,
        )

    return ft.View(
        route="/rooms",
        appbar=ft.AppBar(
            title=ft.Text("Mes Salons"),
            actions=[
                ft.IconButton(ft.Icons.SETTINGS, on_click=go_to_settings),
            ],
        ),
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Créer ou rejoindre",
            on_click=go_to_new_room,
        ),
        controls=[
            ft.Text("Sélectionnez un espace de discussion", size=12, color=ft.Colors.GREY_500),
            room_list,
        ],
    )
