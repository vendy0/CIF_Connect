import flet as ft

async def main(page: ft.Page):
    # stocker une valeur
    await page.shared_preferences.set("key", "value")

    # lire la valeur
    value = await page.shared_preferences.get("key")
    print("stored:", value)

    # vérifier si existe
    exists = await page.shared_preferences.contains_key("key")
    print("exists:", exists)

    # supprimer
    await page.shared_preferences.remove("key")

    # lister les clés
    keys = await page.shared_preferences.get_keys("")
    print("keys left:", keys)

ft.run(main, port=8550)
