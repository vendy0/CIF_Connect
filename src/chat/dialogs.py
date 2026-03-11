import flet as ft
from chat.api import put_message, post_report, delete_message_bdd, post_quit_room


async def show_edit_dialog(page, msg, on_success):
    edit_input = ft.TextField(value=msg.content, multiline=True, expand=True)

    async def save_click(e):
        if msg.content == edit_input.value.strip():
            page.pop_dialog()
            return
        msg.content = edit_input.value.strip()
        await put_message(page, edit_input, msg)
        page.pop_dialog()
        await on_success()

    dialog = ft.AlertDialog(
        title=ft.Text("Modifier le message"),
        content=edit_input,
        actions=[
            ft.TextButton("Annuler", on_click=lambda _: page.close(dialog)),
            ft.FilledButton("Enregistrer", on_click=save_click),
        ],
    )
    await page.show_dialog(dialog)


async def show_delete_dialog(page, msg_id, on_success):
    async def confirm_delete(e):
        await delete_message_bdd(page, msg_id)
        page.pop_dialog()
        await on_success()

    dialog = ft.AlertDialog(
        title=ft.Text("Supprimer ?"),
        content=ft.Text("Voulez-vous vraiment supprimer ce message ?"),
        actions=[
            ft.TextButton("Non", on_click=lambda _: page.pop_dialog()),
            ft.FilledButton("Oui, supprimer", on_click=confirm_delete, icon=ft.Icons.DELETE_FOREVER, icon_color="red"),
        ],
    )
    page.show_dialog(dialog)


async def show_report_dialog(page, msg_id):
    reason_input = ft.TextField(label="Raison du signalement", hint_text="Expliquez pourquoi...")

    async def send_report(e):
        if not reason_input.value.strip():
            return
        page.pop_dialog()
        payload = {"message_id": msg_id, "reason": reason_input.value.strip()}
        await post_report(page, msg_id, reason_input)

    dialog = ft.AlertDialog(
        title=ft.Text("Signaler le message"),
        content=reason_input,
        actions=[
            ft.TextButton("Annuler", on_click=lambda _: page.close(dialog)),
            ft.FilledButton("Signaler", on_click=send_report),
        ],
    )
    page.show_dialog(dialog)


async def show_quit_dialog(page, room_id):
    async def confirm_quit(e):
        if await post_quit_room(page, room_id):
            await page.push_route("/rooms")
        page.pop_dialog()

    dialog = ft.AlertDialog(
        title=ft.Text("Quitter le salon"),
        content=ft.Text("Voulez-vous vraiment quitter ce salon ?"),
        actions=[
            ft.TextButton("Annuler", on_click=lambda _: page.close(dialog)),
            ft.FilledButton("Quitter", on_click=confirm_quit, icon_color="red"),
        ],
    )
    page.show_dialog(dialog)
