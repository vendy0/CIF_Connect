from dataclasses import dataclass
from generate_pseudo import generer
from untitled import get_initials
import flet as ft

pseudo = generer()


@dataclass
class Message:
    user: str
    text: str
    message_type: str


@ft.control
class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.message = message
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(get_initials(pseudo)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(self.message.user_name),
            ),
            ft.Column(
                tight=True,
                spacing=5,
                controls=[
                    ft.Text(self.message.user_name, weight=ft.FontWeight.BOLD),
                    ft.Text(self.message.text, selectable=True),
                ],
            ),
        ]

    # def get_initials(self, user_name: str):
    # 	if user_name:
    # 		return user_name[:1].capitalize()
    # 	else:
    # 		return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "CIF Connect"
    page.auto_scroll = True

    def send_click(e):
        if not new_message.value:
            new_message.error = "Il n'y a rien à envoyer !"
            return
        page.pubsub.send_all(
            Message(
                user=page.session.store.get("user_name"),
                text=new_message.value,
                message_type="chat_message",
            )
        )
        new_message.value = ""

    chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    new_message = ft.TextField(
        autofocus=True,
        shift_enter=True,
        hint_text="Écrivez un message...",
        filled=True,
        expand=True,
        min_lines=1,
        on_submit=send_click,
        # on_tap_outside=lambda e: (setattr(new_message, "unfocus", True), page.update()),
    )

    def on_message(message: Message):
        if message.message_type == "chat_message":
            chat.controls.append(ft.Text(f"{message.user}: {message.text}"))
        elif message.message_type == "login_message":
            chat.controls.append(
                ft.Text(message.text, italic=True, color=ft.Colors.ORANGE_500, size=12)
            )
        page.update()

    def lose_focus(e):
        new_message.unfocus()
        page.update()

    page.pubsub.subscribe(on_message)

    def join_click(e):
        # if not user_name.value:
        # 	user_name.error = "Name cannot be blank!"
        # 	user_name.update()
        # else:
        page.session.store.set("user_name", pseudo)
        page.pop_dialog()
        page.pubsub.send_all(
            Message(
                user=pseudo,
                text=f"{pseudo} a rejoint le chat.",
                message_type="login_message",
            )
        )

    # user_name = ft.TextField(label="Enter your name")

    page.show_dialog(
        ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text(f"Welcome {pseudo} !"),
            # content=ft.Column([user_name], tight=True),
            actions=[ft.Button(content="Ok", on_click=join_click)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    )
    page.add(
        ft.Container(
            content=chat,
            # border=ft.border.all(1, ft.Colors.OUTLINE),
            # border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED,
                    tooltip="Envoyer message",
                    on_click=send_click,
                ),
            ]
        ),
    )


ft.run(main)
