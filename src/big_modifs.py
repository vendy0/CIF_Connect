# APP BAR

app_bar = ft.AppBar(
    # --- BOUTON RETOUR ---
    leading=ft.IconButton(
        icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
        on_click=lambda _: page.go("/rooms"),  # Utilise page.go() pour la navigation Flet moderne
    ),
    leading_width=40,
    # --- TITRE CLIQUABLE (Pour les infos du salon) ---
    title=ft.GestureDetector(
        on_tap=lambda _: page.go(f"/room_info/{current_room_id}"),  # On verra cette vue plus bas
        content=ft.Text(current_room_name, size=20, weight="bold", color="onsurface"),
    ),
    center_title=False,
    bgcolor="surface",
    elevation=2,
    # --- MENU 3 POINTS ---
    actions=[
        ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(icon=ft.Icons.SEARCH, text="Rechercher un message"),
                # On peut conditionner cet affichage si l'utilisateur est admin du salon :
                # ft.PopupMenuItem(icon=ft.Icons.EDIT, text="Modifier le salon") if is_admin else None,
                ft.PopupMenuItem(),  # Séparateur visuel (ligne)
                ft.PopupMenuItem(
                    icon=ft.Icons.LOGOUT_ROUNDED,
                    text="Quitter le salon",
                    on_click=go_to_rooms,  # Ton ancienne fonction
                ),
            ]
        ),
    ],
)


# FOND D'ÉCRAN

# Dans ton return ft.View, modifie le Container central :

pattern_svg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 304 304' width='304' height='304'%3E%3Cpath fill='%239C92AC' fill-opacity='0.4' d='M44.1 224a5 5 0 1 1 0 2H0v-2h44.1zm160 48a5 5 0 1 1 0 2H82v-2h122.1zm57.8-46a5 5 0 1 1 0-2H304v2h-42.1zm0 16a5 5 0 1 1 0-2H304v2h-42.1zm6.2-114a5 5 0 1 1 0 2h-86.2a5 5 0 1 1 0-2h86.2zm-256-48a5 5 0 1 1 0 2H0v-2h12.1zm185.8 34a5 5 0 1 1 0-2h86.2a5 5 0 1 1 0 2h-86.2zM258 12.1a5 5 0 1 1-2 0V0h2v12.1zm-64 208a5 5 0 1 1-2 0v-54.2a5 5 0 1 1 2 0v54.2zm48-198.2V80h62v2h-64V21.9a5 5 0 1 1 2 0zm16 16V64h46v2h-48V37.9a5 5 0 1 1 2 0zm-128 96V208h16v12.1a5 5 0 1 1-2 0V210h-16v-76.1a5 5 0 1 1 2 0zm-5.9-21.9a5 5 0 1 1 0 2H114v48H85.9a5 5 0 1 1 0-2H112v-48h12.1zm-6.2 130a5 5 0 1 1 0-2H176v-74.1a5 5 0 1 1 2 0V242h-60.1zm-16-64a5 5 0 1 1 0-2H114v48h10.1a5 5 0 1 1 0 2H112v-48h-10.1zM66 284.1a5 5 0 1 1-2 0V274H50v30h-2v-32h18v12.1zM236.1 176a5 5 0 1 1 0 2H226v94h48v32h-2v-30h-48v-98h12.1zm25.8-30a5 5 0 1 1 0-2H274v44.1a5 5 0 1 1-2 0V146h-10.1zm-64 96a5 5 0 1 1 0-2H208v-80h16v-14h-42.1a5 5 0 1 1 0-2H226v18h-16v80h-12.1zm86.2-210a5 5 0 1 1 0 2H272V0h2v32h10.1zM98 101.9V146H53.9a5 5 0 1 1 0-2H96v-42.1a5 5 0 1 1 2 0zM53.9 34a5 5 0 1 1 0-2H80V0h2v34H53.9zm60.1 3.9V66H82v64H69.9a5 5 0 1 1 0-2H80V64h32V37.9a5 5 0 1 1 2 0zM101.9 82a5 5 0 1 1 0-2H128V37.9a5 5 0 1 1 2 0V82h-28.1zm16-64a5 5 0 1 1 0-2H146v44.1a5 5 0 1 1-2 0V18h-26.1zm102.2 270a5 5 0 1 1 0 2H98v14h-2v-16h124.1zM242 149.9V160h16v34h-16v62h48v48h-2v-46h-48v-66h16v-30h-16v-12.1a5 5 0 1 1 2 0zM53.9 18a5 5 0 1 1 0-2H64V2H48V0h18v18H53.9zm112 32a5 5 0 1 1 0-2H192V0h50v2h-48v48h-28.1zm-48-48a5 5 0 0 1-9.8-2h2.07a3 3 0 1 0 5.66 0H178v34h-18V21.9a5 5 0 1 1 2 0V32h14V2h-58.1zm0 96a5 5 0 1 1 0-2H137l32-32h39V21.9a5 5 0 1 1 2 0V66h-40.17l-32 32H117.9zm28.1 90.1a5 5 0 1 1-2 0v-76.51L175.59 80H224V21.9a5 5 0 1 1 2 0V82h-49.59L146 112.41v75.69zm16 32a5 5 0 1 1-2 0v-99.51L184.59 96H300.1a5 5 0 0 1 3.9-3.9v2.07a3 3 0 0 0 0 5.66v2.07a5 5 0 0 1-3.9-3.9H185.41L162 121.41v98.69zm-144-64a5 5 0 1 1-2 0v-3.51l48-48V48h32V0h2v50H66v55.41l-48 48v2.69zM50 53.9v43.51l-48 48V208h26.1a5 5 0 1 1 0 2H0v-65.41l48-48V53.9a5 5 0 1 1 2 0zm-16 16V89.41l-34 34v-2.82l32-32V69.9a5 5 0 1 1 2 0zM12.1 32a5 5 0 1 1 0 2H9.41L0 43.41V40.6L8.59 32h3.51zm265.8 18a5 5 0 1 1 0-2h18.69l7.41-7.41v2.82L297.41 50H277.9zm-16 160a5 5 0 1 1 0-2H288v-71.41l16-16v2.82l-14 14V210h-28.1zm-208 32a5 5 0 1 1 0-2H64v-22.59L40.59 194H21.9a5 5 0 1 1 0-2H41.41L66 216.59V242H53.9zm150.2 14a5 5 0 1 1 0 2H96v-56.6L56.6 162H37.9a5 5 0 1 1 0-2h19.5L98 200.6V256h106.1zm-150.2 2a5 5 0 1 1 0-2H80v-46.59L48.59 178H21.9a5 5 0 1 1 0-2H49.41L82 208.59V258H53.9zM34 39.8v1.61L9.41 66H0v-2h8.59L32 40.59V0h2v39.8zM2 300.1a5 5 0 0 1 3.9 3.9H3.83A3 3 0 0 0 0 302.17V256h18v48h-2v-46H2v42.1zM34 241v63h-2v-62H0v-2h34v1zM17 18H0v-2h16V0h2v18h-1zm273-2h14v2h-16V0h2v16zm-32 273v15h-2v-14h-14v14h-2v-16h18v1zM0 92.1A5.02 5.02 0 0 1 6 97a5 5 0 0 1-6 4.9v-2.07a3 3 0 1 0 0-5.66V92.1zM80 272h2v32h-2v-32zm37.9 32h-2.07a3 3 0 0 0-5.66 0h-2.07a5 5 0 0 1 9.8 0zM5.9 0A5.02 5.02 0 0 1 0 5.9V3.83A3 3 0 0 0 3.83 0H5.9zm294.2 0h2.07A3 3 0 0 0 304 3.83V5.9a5 5 0 0 1-3.9-5.9zm3.9 300.1v2.07a3 3 0 0 0-1.83 1.83h-2.07a5 5 0 0 1 3.9-3.9zM97 100a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-48 32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm32 48a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm32-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0-32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm32 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16-64a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 96a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16-144a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16-32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-96 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16-32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm96 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16-64a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-32 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM49 36a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-32 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm32 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM33 68a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16-48a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 240a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16-64a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16-32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm80-176a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm32 48a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0-32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm112 176a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-16 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM17 180a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0-32a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM17 84a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm32 64a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm16-16a3 3 0 1 0 0-6 3 3 0 0 0 0 6z'%3E%3C/path%3E%3C/svg%3E"
ft.Container(
    content=chat_list,
    padding=0,
    expand=True,
    # --- AJOUT DU FOND ---
    image_src=pattern_svg,  # Ton image de fond
    image_repeat=ft.ImageRepeat.REPEAT,
    image_fit=ft.ImageFit.CONTAIN,
    image_opacity=0.05,  # Très léger pour que ça s'adapte au mode sombre/clair sans gêner la lecture
)

chat_container = ft.Container(
    content=chat_list,
    expand=True,
    # On utilise 'image' avec ft.DecorationImage
    image=ft.DecorationImage(
        src="pattern.png",
        repeat=ft.ImageRepeat.REPEAT,
        fit=ft.ImageFit.NONE,
        opacity=0.04,  # Ton réglage de douceur
    ),
    bgcolor=ft.Colors.SURFACE,
)

# Swipe to reply
# Exemple de structure simplifiée :
bulle_de_chat = ft.Container(...) # Ta bulle actuelle

message_avec_swipe = ft.Dismissible(
    key=str(self.message.id), # Obligatoire pour un Dismissible
    content=bulle_de_chat,
    dismiss_direction=ft.DismissDirection.START_TO_END, # Glisser vers la droite
    background=ft.Container(
        bgcolor=ft.Colors.TRANSPARENT,
        padding=10,
        alignment=ft.alignment.center_left,
        content=ft.Icon(ft.Icons.REPLY_ROUNDED, color=ft.Colors.PRIMARY)
    ),
    # C'est ici qu'est la magie : on bloque la disparition de l'élément !
    confirm_dismiss=self.handle_swipe_reply 
)

# Fonction à ajouter dans ta classe :
async def handle_swipe_reply(self, e: ft.DismissibleConfirmDismissEvent):
    # On déclenche la réponse
    await self.on_reply(self.message)
    # On renvoie False pour que le message revienne à sa place (il n'est pas supprimé)
    return False

swipeable_message = ft.Dismissible(
    key="1",
    content=ft.Container(
        content=bubble,
        width=300,  # largeur max
    ),
    dismiss_direction=ft.DismissDirection.START_TO_END,
    dismiss_thresholds={
        ft.DismissDirection.START_TO_END: 0.1
    },
    on_dismiss=lambda e: print("Supprimé"),
    background=ft.Container(
        bgcolor=ft.Colors.RED,
        alignment=ft.alignment.center_left,
        padding=ft.Padding.only(left=10),
        content=ft.Text("Supprimer")
    ),
    # Ajoute éventuellement une animation ou limite ici
)


# 
# 
# Salut ! C'est une excellente feuille de route. Tu as une très bonne vision de ce que doit être une application de chat moderne.
# On va décortiquer ça point par point, en gardant en tête nos contraintes : Flet 0.80.5, l'optimisation pour mobile (.apk), et surtout les piliers de CIF Connect (notamment l'anonymat).
# Voici mon analyse et comment implémenter tout ça.
# 1. Le bouton Retour et le Menu (3 points) dans l'AppBar
# C'est la modification la plus simple. On va utiliser un ft.PopupMenuButton pour les options, et un ft.IconButton pour le retour.
# Voici à quoi doit ressembler ton app_bar mis à jour :


# app_bar = ft.AppBar(
    --- BOUTON RETOUR ---
#     leading=ft.IconButton(
#         icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, 
#         on_click=lambda _: page.go("/rooms") # Utilise page.go() pour la navigation Flet moderne
#     ),
#     leading_width=40,
#     
    --- TITRE CLIQUABLE (Pour les infos du salon) ---
#     title=ft.GestureDetector(
#         on_tap=lambda _: page.go(f"/room_info/{current_room_id}"), # On verra cette vue plus bas
#         content=ft.Text(current_room_name, size=20, weight="bold", color="onsurface"),
#     ),
#     center_title=False,
#     bgcolor="surface",
#     elevation=2,
#     
    --- MENU 3 POINTS ---
#     actions=[
#         ft.PopupMenuButton(
#             items=[
#                 ft.PopupMenuItem(icon=ft.Icons.SEARCH, text="Rechercher un message"),
                On peut conditionner cet affichage si l'utilisateur est admin du salon :
                ft.PopupMenuItem(icon=ft.Icons.EDIT, text="Modifier le salon") if is_admin else None,
#                 ft.PopupMenuItem(), # Séparateur visuel (ligne)
#                 ft.PopupMenuItem(
#                     icon=ft.Icons.LOGOUT_ROUNDED, 
#                     text="Quitter le salon", 
#                     on_click=go_to_rooms # Ton ancienne fonction
#                 ),
#             ]
#         ),
#     ],
# )
# 
# 2. Le fond d'écran (Style WhatsApp)
# Flet permet de mettre une image en fond très facilement. Il te suffit d'envelopper ta chat_list dans un ft.Container avec une image en répétition.
# Note : Tu devras ajouter une petite image (ex: pattern.png) dans le dossier assets de ton projet.
Dans ton return ft.View, modifie le Container central :
# ft.Container(
#     content=chat_list,
#     padding=0,
#     expand=True,
    --- AJOUT DU FOND ---
#     image_src="assets/pattern.png", # Ton image de fond
#     image_repeat=ft.ImageRepeat.REPEAT,
#     image_fit=ft.ImageFit.CONTAIN,
#     image_opacity=0.05, # Très léger pour que ça s'adapte au mode sombre/clair sans gêner la lecture
# )
# 
# 3. Glisser pour répondre (Swipe to reply)
# C'est un super ajout UX. En Flet mobile, on utilise le contrôle ft.Dismissible. Normalement c'est fait pour "supprimer" en glissant, mais on va le tromper : on va intercepter le glissement, annuler la suppression, et déclencher ta fonction on_reply.
# Dans ta classe BaseChatMessage (ou au moment de créer la bulle), tu dois l'envelopper :
Exemple de structure simplifiée :
# bulle_de_chat = ft.Container(...) # Ta bulle actuelle
# 
# message_avec_swipe = ft.Dismissible(
#     key=str(self.message.id), # Obligatoire pour un Dismissible
#     content=bulle_de_chat,
#     dismiss_direction=ft.DismissDirection.START_TO_END, # Glisser vers la droite
#     background=ft.Container(
#         bgcolor=ft.Colors.TRANSPARENT,
#         padding=10,
#         alignment=ft.alignment.center_left,
#         content=ft.Icon(ft.Icons.REPLY_ROUNDED, color=ft.Colors.PRIMARY)
#     ),
    C'est ici qu'est la magie : on bloque la disparition de l'élément !
#     confirm_dismiss=self.handle_swipe_reply 
# )
# 
# Fonction à ajouter dans ta classe :
# # async def handle_swipe_reply(self, e: ft.DismissibleConfirmDismissEvent):
#     On déclenche la réponse
# #     await self.on_reply(self.message)
#     On renvoie False pour que le message revienne à sa place (il n'est pas supprimé)
# #     return False

# 4. Le bouton Emojis (La dure réalité)
# Je vais être franc : Flet n'a pas de clavier à emojis intégré.
# Pour une application native Flet (Mobile), la meilleure pratique (et de loin) est de laisser l'utilisateur utiliser la touche emoji de son propre clavier Android/iOS.
# Si tu essaies de fabriquer un clavier emoji toi-même (un GridView avec 300 boutons textuels), ça va alourdir ton application et ça ne sera jamais aussi fluide que le clavier natif du téléphone. Je te conseille vivement d'ignorer ce bouton et de te reposer sur le clavier de l'OS.


# 5. Reprendre là où on a quitté
# Pour faire ça, il faut mémoriser le dernier message lu. Puisque nous avons décidé d'utiliser SharedPreferences(), voici la logique :
#  * Quand l'utilisateur quitte le salon, tu sauvegardes l'ID du dernier message affiché.
#  * Quand il rouvre le salon, tu dis à Flet de scroller jusqu'à ce composant.
# <!-- end list -->
# # 1. Sauvegarder (lorsqu'on quitte ou reçoit un msg)
sp = ft.SharedPreferences()
await sp.set(f"last_read_{current_room_id}", last_message_id)

# 2. Restaurer (après avoir chargé les messages dans chat_list)
# last_read = await sp.get(f"last_read_{current_room_id}")
# if last_read:
#     # Flet permet de scroller vers une "key" spécifique
#     chat_list.scroll_to(key=str(last_read), duration=300)
# else:
#     # Sinon, on va tout en bas
#     chat_list.scroll_to(offset=-1, duration=300)

# (Attention : il faut que tes messages dans la chat_list aient leur paramètre key=str(message.id) pour que ça fonctionne).
6. La Vue "Infos du Salon" et l'Anonymat
(Accessible en cliquant sur le titre de l'AppBar, voir point 1)
Tu devras créer un nouveau fichier (ex: room_info_view.py).
Mon avis sur l'affichage des utilisateurs : CIF Connect repose sur l'Anonymat Contrôlé. Afficher la liste des membres d'un salon peut être dangereux si on affiche des emails ou des vrais noms.
 * Si tu affiches la liste : n'affiche que les pseudos (Adjectif + Animal) et l'avatar.
 * Encore mieux pour un "Salon Général" : n'affiche pas de liste du tout, juste un compteur textuel : "👥 142 membres". Cela renforce le sentiment de sécurité et d'anonymat.
Pour les options du salon, c'est une bonne idée de ne pas les répéter. Le menu "3 points" de l'AppBar du chat sert pour les actions rapides. La vue "Infos du Salon" sert pour l'administration (Changer la description, régénérer le code d'invitation, expulser un pseudo si on est admin).
Quelle est la prochaine étape que tu veux attaquer ensemble ? On peut configurer le ft.Dismissible pour le swipe-to-reply, ou bien créer le squelette de la vue "Infos du Salon" ?
