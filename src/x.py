import flet as ft

def main(page: ft.Page):
    # Avatar avec une image distante
    avatar1 = ft.CircleAvatar(
        foreground_image_src="https://picsum.photos/200/200",
        content=ft.Text("ID"), # Affiché si l'image ne charge pas
    )

    # Avatar avec des initiales (parfait pour l'anonymat)
    avatar2 = ft.CircleAvatar(
        content=ft.Text("GA"),
        bgcolor=ft.Colors.BLUE_GREY_400,
        radius=20, # Taille du cercle
    )

    page.add(avatar1, avatar2)

ft.app(target=main)

