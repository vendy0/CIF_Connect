import flet as ft
from chat.api import put_message, post_report, delete_message_bdd, post_quit_room
import asyncio


async def show_edit_dialog(page, msg, on_success):
	edit_input = ft.TextField(value=msg.content, capitalization=ft.TextCapitalization.SENTENCES, multiline=True, expand=True, autofocus=True)

	async def save_click(e):
		if not edit_input.value.strip():
			edit_input.error = "Le champ est vide"
			page.update()
			return
		if msg.content == edit_input.value.strip():
			page.pop_dialog()
			return

		button_confirm.content = loading
		button_confirm.on_click = None  # Désactive le clic pendant le chargement
		page.update()

		msg.content = edit_input.value.strip()
		res = await put_message(page, edit_input, msg)
		if res:
			page.pop_dialog()
			await on_success()
			return
		button_confirm.content = button_content
		button_confirm.on_click = save_click  
	
	
	button_content = ft.Text("Enregistrer")
	button_confirm = ft.FilledButton(button_content, on_click=save_click)
	loading = ft.Container(
		content=ft.ProgressRing(width=20, height=20, stroke_width=2, color="white"),
		alignment=ft.Alignment.CENTER,
		width=80,  # On fixe une largeur pour éviter que le bouton ne rétrécisse trop
	)
	dialog = ft.AlertDialog(
		title=ft.Text("Modifier le message"),
		content=edit_input,
		actions=[ft.TextButton("Annuler", on_click=lambda _: page.pop_dialog()), button_confirm],
	)
	page.show_dialog(dialog)


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
	reason_input = ft.TextField(label="Raison du signalement", hint_text="Expliquez pourquoi...", autofocus=True)

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
			ft.TextButton("Annuler", on_click=lambda _: page.pop_dialog()),
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
			ft.TextButton("Annuler", on_click=lambda _: page.pop_dialog()),
			ft.FilledButton("Quitter", on_click=confirm_quit, icon_color="red"),
		],
	)
	page.show_dialog(dialog)
