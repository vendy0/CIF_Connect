import flet as ft
from chat.models import Message
from utils import get_avatar_color, get_initials, COLORS_LOOKUP
from datetime import datetime, timedelta


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


class BaseChatMessage(ft.Row):
    def __init__(
        self,
        message: Message,
        page: ft.Page,
        on_copy,
        on_reply,
        on_edit,
        on_report,
        on_react,
        on_delete,
    ):
        super().__init__()
        self.message = message
        self._page_ref = page
        self.on_copy = on_copy
        self.on_reply = on_reply
        self.on_edit = on_edit
        self.on_react = on_react
        self.on_report = on_report
        self.on_delete = on_delete
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.parent_bubble = ft.Container()

        # 1. Message Parent (Reply) - Full Width (Style WhatsApp)
        if self.message.parent_content and self.message.parent_author:
            self.parent_bubble = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            self.message.parent_author,
                            size=11,
                            weight="bold",
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text(
                            self.message.parent_content,
                            size=12,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            italic=True,
                        ),
                    ],
                    spacing=1,
                ),
                padding=ft.padding.all(8),
                # Marge en bas pour espacer du vrai message
                margin=ft.margin.only(bottom=5),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE_VARIANT),
                border=ft.border.only(left=ft.BorderSide(4, ft.Colors.PRIMARY)),
                border_radius=5,
            )

    def get_reactions_row(self):
        reactions_row = ft.Row(spacing=4, tight=True)
        if self.message.reactions:
            for emoji, count in self.message.reactions.items():
                reactions_row.controls.append(
                    ft.Container(
                        content=ft.Text(f"{emoji} {count}", size=11),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    )
                )
        return reactions_row

    # Méthodes d'actions communes
    async def action_reply(self, e):
        # self._page_ref.show_dialog(self._page_ref.bottom_sheet)
        # self._page_ref.bottom_sheet.open = False
        self._page_ref.pop_dialog()
        self._page_ref.update()
        await self.on_reply(self.message)

    async def action_react(self, e):
        self._page_ref.pop_dialog()
        # self._page_ref.show_dialog(self._page_ref.bottom_sheet)
        self._page_ref.update()
        await self.on_react(e, self.message)

    # Fonction à ajouter dans ta classe :
    async def handle_swipe_reply(self, e: ft.DismissibleDismissEvent):
        # On déclenche la réponse
        await self.on_reply(self.message)
        await e.control.confirm_dismiss(False)
        # On renvoie False pour que le message revienne à sa place (il n'est pas supprimé)
        return False

    async def pass_func(self, e):
        pass


class MyChatMessage(BaseChatMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alignment = ft.MainAxisAlignment.END  # Aligné à droite

        # Menu spécifique : Copier, Modifier, Supprimer, Répondre
        self.menu_items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.CONTENT_COPY),
                title=ft.Text("Copier"),
                on_click=lambda e: self._page_ref.run_task(self.on_copy, e, self.message),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.EDIT),
                title=ft.Text("Modifier"),
                on_click=lambda e: self._page_ref.run_task(self.on_edit, e, self.message),
            )
            if (datetime.now() - timedelta(minutes=15)) < self.message.message_datetime
            else ft.Container(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DELETE_OUTLINE, color="error"),
                title=ft.Text("Supprimer"),
                on_click=lambda e: self._page_ref.run_task(self.on_delete, e, self.message),
            )
            if (datetime.now() - timedelta(days=3)) < self.message.message_datetime
            else ft.Container(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.REPLY),
                title=ft.Text("Répondre"),
                on_click=self.action_reply,
            ),
        ]

        bubble = ft.GestureDetector(
            on_tap=lambda _: self.show_menu(),
            content=ft.Container(
                content=ft.Column(
                    [
                        self.parent_bubble,
                        ft.Text(
                            self.message.pseudo,
                            size=12,
                            weight="bold",
                            color=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
                        ),
                        ft.Text(
                            self.message.content,
                            size=15,
                            color=ft.Colors.ON_PRIMARY_CONTAINER,
                        ),
                        ft.Row(
                            [
                                ft.Text("Modifié • ", size=9, italic=True) if self.message.modified else ft.Container(),
                                ft.Text(self.message.message_time.strftime("%H:%M"), size=10),
                            ],
                            alignment="end",
                            spacing=1,
                        ),
                    ],
                    tight=True,
                    horizontal_alignment="stretch",
                ),
                bgcolor=ft.Colors.PRIMARY_CONTAINER,  # Couleur différente pour nos messages
                padding=10,
                border_radius=ft.border_radius.only(top_left=15, top_right=0, bottom_left=15, bottom_right=15),
                width=200,
                # on_click=lambda _: self.show_menu(),
            ),
        )

        bulle_complet = ft.Row(
            [
                ft.Stack(
                    [
                        ft.Column(
                            [bubble, ft.Container(height=10 if self.message.reactions else 0)],
                            tight=True,
                        ),
                        ft.Container(content=self.get_reactions_row(), bottom=0, left=10),  # Réactions à gauche pour nos messages
                    ],
                ),
                ft.CircleAvatar(
                    content=ft.Text(get_initials(self.message.pseudo)),
                    bgcolor=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
                ),
            ]
        )

        message_avec_swipe = ft.Dismissible(
            key=str(self.message.id),  # Obligatoire pour un Dismissible
            content=bulle_complet,
            dismiss_thresholds={ft.DismissDirection.START_TO_END: 0.1},
            dismiss_direction=ft.DismissDirection.START_TO_END,  # Glisser vers la droite
            background=ft.Container(
                bgcolor=ft.Colors.TRANSPARENT,
                padding=10,
                alignment=ft.Alignment.CENTER_LEFT,
                content=ft.Icon(ft.Icons.REPLY_ROUNDED, color=ft.Colors.PRIMARY),
            ),
            # C'est ici qu'est la magie : on bloque la disparition de l'élément !
            on_confirm_dismiss=self.handle_swipe_reply,
        )

        self.controls = [message_avec_swipe]

    def show_menu(self):
        self._page_ref.bottom_sheet = ft.BottomSheet(ft.Container(ft.Column(self.menu_items, tight=True), padding=10))
        self._page_ref.show_dialog(self._page_ref.bottom_sheet)
        self._page_ref.update()


class OtherChatMessage(BaseChatMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alignment = ft.MainAxisAlignment.START

        # Menu spécifique : Répondre, Réagir, Signaler
        self.menu_items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.CONTENT_COPY),
                title=ft.Text("Copier"),
                on_click=lambda e: self._page_ref.run_task(self.on_copy, e, self.message),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.REPLY),
                title=ft.Text("Répondre"),
                on_click=lambda e: self._page_ref.run_task(self.action_reply, e),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.FAVORITE_BORDER),
                title=ft.Text("Réagir"),
                on_click=self.action_react,
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.REPORT, color="error"),
                title=ft.Text("Signaler"),
                on_click=lambda e: self._page_ref.run_task(self.on_report, e, self.message),
            ),
        ]

        # Construction UI (Bulle classique à gauche avec Avatar)
        bubble = self.build_bubble(ft.Colors.SURFACE_CONTAINER_HIGHEST)

        bulle_complet = ft.Row(
            [
                ft.CircleAvatar(
                    content=ft.Text(get_initials(self.message.pseudo)),
                    bgcolor=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
                ),
                ft.Stack(
                    [
                        self.parent_bubble,
                        ft.Column(
                            [bubble, ft.Container(height=10 if self.message.reactions else 0)],
                            tight=True,
                        ),
                        ft.Container(content=self.get_reactions_row(), bottom=0, right=10),
                    ]
                ),
            ]
        )
        
        message_avec_swipe = ft.Dismissible(
            key=str(self.message.id),  # Obligatoire pour un Dismissible
            content=bulle_complet,
            dismiss_thresholds={ft.DismissDirection.START_TO_END: 0.1},
            dismiss_direction=ft.DismissDirection.START_TO_END,  # Glisser vers la droite
            background=ft.Container(
                bgcolor=ft.Colors.TRANSPARENT,
                padding=10,
                alignment=ft.Alignment.CENTER_LEFT,
                content=ft.Icon(ft.Icons.REPLY_ROUNDED, color=ft.Colors.PRIMARY),
            ),
            # C'est ici qu'est la magie : on bloque la disparition de l'élément !
            on_confirm_dismiss=self.handle_swipe_reply,
        )
        self.controls = [message_avec_swipe]

    def build_bubble(self, color):
        # Code de ta bulle actuelle (avec max_width=200)
        return ft.GestureDetector(
            on_tap=lambda _: self.show_menu(),
            # on_long_press=lambda _: self.show_menu(),
            content=ft.Container(
                content=ft.Column(
                    [
                        self.parent_bubble,
                        ft.Text(
                            self.message.pseudo,
                            size=12,
                            weight="bold",
                            color=get_avatar_color(self.message.pseudo, COLORS_LOOKUP),
                        ),
                        ft.Text(self.message.content, size=15),
                        ft.Row(
                            [
                                ft.Text("Modifié •", size=9, italic=True) if self.message.modified else ft.Container(),
                                ft.Text(self.message.message_time.strftime("%H:%M"), size=10),
                            ],
                            alignment="end",
                            spacing=2,
                        ),
                    ],
                    tight=True,
                    horizontal_alignment="stretch",
                ),
                bgcolor=color,
                padding=10,
                border_radius=ft.border_radius.only(top_left=0, top_right=15, bottom_left=15, bottom_right=15),
                width=200,
                # on_click=lambda _: self.show_menu(),
            ),
        )

    def show_menu(self):
        self._page_ref.bottom_sheet = ft.BottomSheet(ft.Container(ft.Column(self.menu_items, tight=True), padding=10))
        self._page_ref.show_dialog(self._page_ref.bottom_sheet)
        self._page_ref.update()
