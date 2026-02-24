import flet as ft

async def main(page: ft.Page):
    # utiliser SharedPreferences sans 'page='
    sp = ft.SharedPreferences()

    # stocker
    await sp.set("key", "value")

    # lire
    data = await sp.get("key")
    print("stored value:", data)

    # vérifier
    exists = await sp.contains_key("key")
    print("exists?", exists)

    # supprimer
    await sp.remove("key")

    # lister
    keys = await sp.get_keys("")
    print("remaining keys:", keys)

ft.run(main, port=8550)
