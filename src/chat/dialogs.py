import flet as ft
from chat.api import put_message, post_report, delete_message_bdd, post_quit_room
import asyncio

loading = ft.Container(
	content=ft.ProgressRing(width=20, height=20, stroke_width=2, color="white"),
	alignment=ft.Alignment.CENTER,
	width=80,  # On fixe une largeur pour éviter que le bouton ne rétrécisse trop
)


async def show_edit_dialog(page, msg, on_success):
	global loading
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
		if await put_message(page, edit_input, msg):
			page.pop_dialog()
			await on_success()
			return
		button_confirm.content = button_content
		button_confirm.on_click = save_click
		page.update()

	button_content = ft.Text("Enregistrer")
	button_confirm = ft.FilledButton(button_content, on_click=save_click)

	dialog = ft.AlertDialog(
		title=ft.Text("Modifier le message"),
		content=edit_input,
		actions=[ft.TextButton("Annuler", on_click=lambda _: page.pop_dialog()), button_confirm],
	)
	page.show_dialog(dialog)


async def show_delete_dialog(page, msg_id, on_success):
	global loading

	async def confirm_delete(e):
		delete_button.icon = None
		delete_button.on_click = None
		delete_button.content = loading
		page.update()
		if await delete_message_bdd(page, msg_id):
			page.pop_dialog()
			await on_success()
			return
		delete_button.icon = delete_button_icon
		delete_button.on_click = confirm_delete
		delete_button.content = delete_button_text
		page.update()

	delete_button_text = ft.Text("Oui, supprimer")
	delete_button_icon = ft.Icons.DELETE_FOREVER
	delete_button = ft.FilledButton(delete_button_text, on_click=confirm_delete, icon=delete_button_icon, icon_color="red")

	dialog = ft.AlertDialog(
		title=ft.Text("Supprimer ?"),
		content=ft.Text("Voulez-vous vraiment supprimer ce message ?"),
		actions=[ft.TextButton("Non", on_click=lambda _: page.pop_dialog()), delete_button],
	)
	page.show_dialog(dialog)


async def show_report_dialog(page, msg_id):
	global loading
	reason_input = ft.TextField(label="Raison du signalement", hint_text="Expliquez pourquoi...", autofocus=True)

	async def send_report(e):
		if not reason_input.value.strip():
			reason_input.error = "Veuillez mentionner la raison"
			return
		reason_input.error = None
		report_button.content = loading
		report_button.on_click = None
		page.update()

		if await post_report(page, msg_id, reason_input):
			page.pop_dialog()
			return
		report_button.content = report_button_content
		report_button.on_click = send_report
		page.update()

	report_button_content = ft.Text("Signaler")
	report_button = ft.FilledButton(report_button_content, on_click=send_report)

	dialog = ft.AlertDialog(
		title=ft.Text("Signaler le message"),
		content=reason_input,
		actions=[ft.TextButton("Annuler", on_click=lambda _: page.pop_dialog()), report_button],
	)
	page.show_dialog(dialog)


async def show_quit_dialog(page, room_id):
	global loading

	async def confirm_quit(e):
		button.content = loading
		button.on_click = None
		page.update()
		if await post_quit_room(page, room_id):
			await page.push_route("/rooms")
		page.pop_dialog()

	button_content = ft.Text("Quitter")
	button = ft.FilledButton(button_content, on_click=confirm_quit, icon_color="red")

	dialog = ft.AlertDialog(
		title=ft.Text("Quitter le salon"),
		content=ft.Text("Voulez-vous vraiment quitter ce salon ?"),
		actions=[ft.TextButton("Annuler", on_click=lambda _: page.pop_dialog()), button],
	)
	page.show_dialog(dialog)
