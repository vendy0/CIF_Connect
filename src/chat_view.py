import flet as ft
from dataclasses import dataclass, field
from typing import List, Optional
import httpx
from utils import get_initials, get_avatar_color, get_colors, host, port

# =============================================================================
# 1. MODÈLES DE DONNÉES
# =============================================================================


@dataclass
class Message:
    id: int
    pseudo: str
    content: str
    message_type: str
    parent_id: Optional[int] = None
    reactions: dict = field(default_factory=dict)


COLORS_LOOKUP = get_colors()

# =============================================================================
# 2. COMPOSANTS VISUELS DES MESSAGES
# =============================================================================


class SystemMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.alignment = ft.MainAxisAlignment.CENTER

        color = ft.Colors.GREEN_600 if message.message_type == "join" else ft.Colors.ERROR
        icon = ft.Icons.LOGIN_ROUNDED if message.message_type == "join" else ft.Icons.LOGOUT_ROUNDED

        self.controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(icon, size=14, color=color),
                        ft.Text(
                            message.content,
                            italic=True,
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    tight=True,
                    spacing=5,
                ),
                bgcolor="surfacecontainerhighest",  # Syntaxe sécurisée
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border_radius=15,
            )
        ]


class ChatMessage(ft.Column):
    def __init__(self, message: Message, page: ft.Page, on_reply, on_report, on_react):
        super().__init__()
        self.message = message
        self._page_ref = page
        self.on_reply = on_reply
        self.on_report = on_report
        self.on_react = on_react
        self.spacing = 2

        # --- Création du BottomSheet ---
        self.bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Text("Actions", weight="bold"),
                        ft.Row(
                            [
                                # CORRECTION: Utilisation de TextButton pour les emojis
                                ft.TextButton(content="👍", on_click=lambda e: self.action_react(e, "👍")),
                                ft.TextButton(content="❤️", on_click=lambda e: self.action_react(e, "❤️")),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.ListTile(leading=ft.Icon(ft.Icons.REPLY), title=ft.Text("Répondre"), on_click=self.action_reply),
                        ft.ListTile(leading=ft.Icon(ft.Icons.REPORT, color="error"), title=ft.Text("Signaler"), on_click=self.action_report),
                    ],
                ),
            )
        )

        # Avatar et bulles
        self.controls = [
            ft.Row(
                [
                    ft.CircleAvatar(content=ft.Text(get_initials(self.message.pseudo))),
                    ft.GestureDetector(
                        on_long_press=self.open_menu,
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(self.message.pseudo, weight="bold"),
                                    ft.Text(self.message.content),
                                ],
                                spacing=2,
                            ),
                            bgcolor="surfacevariant",
                            padding=10,
                            border_radius=10,
                        ),
                    ),
                ]
            )
        ]

    async def open_menu(self, e):
        await self._page_ref.open(self.bottom_sheet)

    async def action_reply(self, e):
        await self._page_ref.close(self.bottom_sheet)
        await self.on_reply(self.message)  # Ajout du await ici pour la fonction async

    async def action_report(self, e):
        await self._page_ref.close(self.bottom_sheet)
        await self.on_report(self.message)

    async def action_react(self, e, emoji):
        await self._page_ref.close(self.bottom_sheet)
        await self.on_react(self.message, emoji)


# =============================================================================
# 3. VUE PRINCIPALE DU CHAT
# =============================================================================


async def ChatView(page: ft.Page):
    sp = ft.SharedPreferences()
    token = await sp.get("cif_token")

    current_room_id = page.session.store.get("current_room_id") or 1
    current_room_name = page.session.store.get("current_room_name") or "Salon Général"
    current_pseudo = await sp.get("user_pseudo") or "Anonyme"

    replying_to_message: Optional[Message] = None

    chat_list = ft.ListView(expand=True, spacing=15, auto_scroll=True, padding=10)

    reply_banner = ft.Container(
        visible=False,
        bgcolor="surfacevariant",
        padding=10,
        border_radius=ft.border_radius.only(top_left=15, top_right=15),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=0,
                    controls=[
                        ft.Text("Réponse à", size=11, color="primary"),
                        ft.Text("", size=13, italic=True, no_wrap=True),
                    ],
                ),
                ft.IconButton(ft.Icons.CLOSE, icon_size=16, on_click=lambda e: cancel_reply(e)),  # Sera awaité plus tard
            ],
        ),
    )

    new_message = ft.TextField(
        hint_text="Écrivez un message...",
        autofocus=True,
        expand=True,
        min_lines=1,
        border_radius=20,
        shift_enter=True,
        on_submit=lambda e: send_click(e),  # Sera awaité via le framework Flet
    )

    async def go_to_rooms(e):
        await page.push_route("/rooms")

    async def cancel_reply(e):  # Rendu async pour pouvoir être awaité
        nonlocal replying_to_message
        replying_to_message = None
        reply_banner.visible = False
        reply_banner.content.controls[0].controls[1].value = ""
        page.update()

    async def prepare_reply(msg: Message):  # Rendu async
        nonlocal replying_to_message
        replying_to_message = msg
        reply_banner.visible = True
        reply_banner.content.controls[0].controls[1].value = f"{msg.pseudo}: {msg.content[:30]}..."
        await new_message.focus()  # CORRECTION DU WARNING ICI
        page.update()

    async def react_to_message(msg: Message, emoji: str):
        if emoji in msg.reactions:
            msg.reactions[emoji] += 1
        else:
            msg.reactions[emoji] = 1
        # (La logique UI sera faite plus tard si tu veux l'afficher)

    async def report_message(msg: Message):
        report_reason_input = ft.TextField(label="Raison du signalement", multiline=True)

        async def submit_report(e):
            print(f"Signalement envoyé pour le message {msg.id}: {report_reason_input.value}")
            await page.close(report_dialog)
            page.snack_bar = ft.SnackBar(ft.Text("Signalement envoyé à la modération."))
            page.snack_bar.open = True
            page.update()

        async def cancel_report(e):
            await page.close(report_dialog)

        report_dialog = ft.AlertDialog(
            title=ft.Text("Signaler ce message"),
            content=ft.Column(tight=True, controls=[ft.Text(f"Message de {msg.pseudo} :"), ft.Text(f'"{msg.content}"', italic=True), report_reason_input]),
            actions=[
                ft.TextButton(content="Annuler", on_click=cancel_report),
                ft.ElevatedButton("Envoyer", bgcolor=ft.Colors.ERROR, color=ft.Colors.WHITE, on_click=submit_report),
            ],
        )
        await page.open(report_dialog)

    async def send_click(e):
        if not new_message.value:
            return

        text = new_message.value
        parent_id = replying_to_message.id if replying_to_message else None

        page.pubsub.send_all(Message(id=1001, pseudo=current_pseudo, content=text, message_type="chat_message", parent_id=parent_id))

        new_message.value = ""
        await cancel_reply(None)
        await new_message.focus()  # CORRECTION DU WARNING ICI
        page.update()

    def on_message(message: Message):
        if message.message_type in ["join", "quit"]:
            chat_list.controls.append(SystemMessage(message))
        elif message.message_type == "chat_message":
            chat_list.controls.append(
                ChatMessage(
                    message=message,
                    page=page,
                    on_reply=prepare_reply,
                    on_report=report_message,
                    on_react=react_to_message,
                )
            )
        page.update()  # Reste synchrone car c'est un callback PubSub

    page.pubsub.subscribe(on_message)

    app_bar = ft.AppBar(
        leading=ft.Icon(ft.Icons.FORUM_ROUNDED, color="primary"),
        leading_width=40,
        title=ft.Text(current_room_name, size=20, weight="bold", color="onsurface"),
        center_title=False,
        bgcolor="surface",
        elevation=2,
        actions=[
            ft.IconButton(icon=ft.Icons.LOGOUT_ROUNDED, icon_color="error", tooltip="Quitter le salon", on_click=go_to_rooms),
        ],
    )

    return ft.View(
        route="/chat",
        controls=[
            app_bar,
            ft.Container(
                content=chat_list,
                padding=0,
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    spacing=0,
                    controls=[
                        reply_banner,
                        ft.Row(
                            [
                                new_message,
                                ft.IconButton(
                                    icon=ft.Icons.SEND_ROUNDED,
                                    icon_color="blue",
                                    tooltip="Envoyer",
                                    on_click=send_click,
                                ),
                            ]
                        ),
                    ],
                ),
                padding=ft.padding.Padding(left=10, top=5, right=10, bottom=15),
            ),
        ],
    )
