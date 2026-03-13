"""
# - Connexion avec email et vérification
# - Mot de passe oublié
# - Boite de dialogue de bienvenue
# - Quand qlq'un change de pseudo faut l'avertir que ça se verra dans les rooms créés.
# - Ne peut pas changer de pseudo si les 7 jours ne sont pas encore écoulés
# - Quand il y a une nouvelle version
# - Mot de passe oublié
# - Changer "/chat" par f"/room/{current_room_id}"
# - Interface Administrateur
# - Annonces
# - Les notifs (Quand on se fait tag aussi)
# - Désactiver l'auto scroll quand on remonte
# - Mettre les messages en fil d'attente



# - Mettre les options de message dans le swipe

# - Quitter le Salon général

# - Rechercher un message ne l'affiche pas mais swipe jusqu'à lui. Je pensais plutôt faire une requête api si l'utilisateur demande plus parce que le chat ne contient que les 100 derniers messages. Cette requête retournerais tous les messages jusqu'à celui qu'on cherche.



# Maintenant je veux :
# Analyse attentivement ma chat_view
# - Et puis je n'arrive pas à ajouter Scroll btn à la page
# - Afficher le nombre de messages non lus dans la room view (pour chaque room, style whatsapp). J'optimiserai plus tard avec les websocket pour chaque nouveau message reçu




- Maintnant imagine. La personne voit ses messages non lus mais quand il ouvre il tombe tout en bas. J'avais une idée. On récupère le last message read. En affichant les message, quand on tombe sur le last message read on désactive l'auto scroll et on affiche un divider qui dit (x messages non lus)
- Une chose que j'avais complètement oublié est la fil d'attente. Vu que je travaille avec sqlite je dois mettre chaque message envoyé sur une sorte de liste d'attente à ce qu'il parait pour ne pas avoir une erreur du genre (database is locked)
- Puis jette un coup d'oeil à tous mes autres trucs pour voir si tout est correct stp.
- Maintenant je crois qu'il me reste à : ajouter l'interface adm, travailler sur les notifications, Changer "/chat" par f"/room/{current_room_id}", afficher un délai pour changer de pseudo (7 jours) et enfin finaliser la page de connexion (vérification par email, mot de passe oublié...)


Pour les messages non lus :
La meilleure approche (hybride) :
 * Ajoute une colonne last_read_at dans models.py sur ta table de liaison user_room (c'est la BDD qui fait foi).
 * Quand l'élève quitte ChatView, tu envoies une requête PUT /user/rooms/{id}/read avec l'heure actuelle.
 * Le badge dans utils.py sera conditionné par le calcul fait par le backend (total_messages - messages_before_last_read), renvoyé lors du /user/rooms. Ne te casse pas la tête à le calculer en front-end, le back-end est fait pour ça !
3. Logique de ChatView (Scroll, Recherche et Menu)
Désactiver l'auto-scroll si on remonte :
La détection de scroll dans Flet est capricieuse si on ne laisse pas une marge (tolérance).
# Dans chat_view.py, avant de définir chat_list :
    def on_chat_scroll(e: ft.OnScrollEvent):
        # Si on est à moins de 30 pixels du bas, on réactive l'autoscroll
        is_at_bottom = e.pixels >= (e.max_scroll_extent - 30)
        chat_list.auto_scroll = is_at_bottom
        page.update()

    chat_list = ft.ListView(expand=True, spacing=15, auto_scroll=True, padding=10, on_scroll=on_chat_scroll)

Recherche de message par Scroll :
Au lieu de cacher les messages, on défile jusqu'à eux grâce à la propriété key.
# Remplacer ta fonction filter_messages dans chat_view.py par :
    async def filter_messages(query: str):
        if not query:
            return
        query = query.lower()

        # On cherche d'abord dans les messages déjà chargés localement
        for ctrl in chat_list.controls:
            if hasattr(ctrl, "message") and query in ctrl.message.content.lower():
                await chat_list.scroll_to(key=str(ctrl.message.id), duration=300)
                await show_top_toast(page, "Message trouvé ! (En local)")
                return

        # TODO plus tard : Si on n'a pas trouvé, faire une requête API pour récupérer l'historique plus ancien.
        await show_top_toast(page, "Message non trouvé dans l'historique récent.", True)

Unifier le rendu des messages :
Créer deux classes distinctes (MyChatMessage, OtherChatMessage) te fait dupliquer du code. Crée une fonction générique pour centraliser :
# Dans chat_view.py, remplace les appels if message.pseudo != current_pseudo par :
    def render_single_message(message: Message, is_me: bool):
        # Assigne l'id comme clé pour le scroll_to()
        key_str = str(message.id)

        if is_me:
            return MyChatMessage(key=key_str, message=message, page=page, ...) # Passe les callbacks
        else:
            return OtherChatMessage(key=key_str, message=message, page=page, ...)

# Et dans def on_message(message: Message):
    if message.message_type == "chat":
        is_me = (message.pseudo == current_pseudo)
        chat_list.controls.append(render_single_message(message, is_me))

"""


# - Quand on scroll ça doit afficher la dernière date (style whatsapp). Quand on arrive à l'endroit où cette date délimite elle s'arrete et la date precedente prend le relai
# - Comment je conditionne ce unread messages
# - Pour le dernier message lu je comptais plutot utiliser la date pour reprendre la room où on l'a laissée
# - Les marqueurs de dates visibles
# =========== LES WEBSOCKETS ========== #
# - Actualiser un seul élément plutôt que de refaire toute la liste
# - Afficher les salons à partir du dernier message reçu
# - Mettre à jour la page room_info pour changer le nombre de membres en ligne
# - Ajouter la colonne last read dans la bdd
# - Afficher les membres
# - Swipe de l'autre coté affiche la date ou un truc du genre
# - Taguer (Un message) (Optionnel)
# - Les chargements
# * Je veux que tu me fournisses la page info du salon (room_info.py). Sur cette page l'adm va pouvoir modifier les infos du salons comme c'est indiqué dans le crud.py. On pourra voir le nombre de membres totaux et combien sont en ligne (ex: 30/126 online). Je crois que je pourrais aussi afficher ça dans l'AppBar.
# - Sur la page y aura aussi le nom du salon, l'icon flet du salon aussi et les autres détails que tu juges nécéssaire. Et aussi le code du salon
# * Remplacer le bouton pour sortir de la Room par un menu (3 points) avec des options:
# - Puis une view quand on clique sur L'app bar qui affiche les infos du Salon (Nom, code invitation, description, Changer les informarions du salon (nom, description), Je ne sais pas si je peux afficher les utilisateurs même si c'est un adm pour l'anonymat, tu me donneras ton avis, avec les options qui vont suivre (Je ne sais pas si les répéter est une bonne chose))
# - Le bouton qui affiche les émojis à gauche de la new_message_input (Je ne sais pas si flet possède des émojis préfabriqués)
# - Un fond d'écran simple et doux qui s'adapte au thème à la manière de whatsapp
# - Puis un bouton à gauche de l'app bar pour retourner à la rooms_view
# - Quitter le Salon
# - Glisser un message vers la droite pour y répondre (comme la plupart des applications de chat)
# - Modifier et supprimer un salon (Si on est adm du salon)
# - Afficher les salons en fonction du dernier message. On gerera peut-être avec les websockets
# - Faire un soft delete sur les rooms
# - Ajouter d'autres icones
# - Émoji
# - Modifier et supprimer un salon
# - Glisser pour répondre
# - Fond d'écran
# - Avant d'envoyer vers bdd, vérifier si il y a changement
# - Generate secure code
# - Changer la couleur du pseudo
# - Premiere lettre en majuscule
# - Supprimer le selected
# - Copier un message (ft.Clipboard().set(message))
# - Je devrait peut-être faire un soft delete. Quand on repond a un message supprimé, le parent_bubble disparait.
# - Sauvegarder le pseudo changé en bdd
# - Changer les print pour utiliser des barres d'infos
# - Délimiteur parent message dans le front
# - Informer par snack bar ou qlq chose de plus stylé
# - Page de connexion
# - Le jwt à la place des id dans les requetes.


# // "ON_PRIMARY",
# // // "ON_PRIMARY_CONTAINER",
# // "ON_PRIMARY_FIXED",
# // "ON_PRIMARY_FIXED_VARIANT",
# // "ON_SECONDARY",
# // "ON_SECONDARY_CONTAINER",
# // "ON_SECONDARY_FIXED",
# // "ON_SECONDARY_FIXED_VARIANT",
# // "ON_SURFACE",
# // "ON_SURFACE_VARIANT",
# // "ON_TERTIARY",
# // "ON_TERTIARY_CONTAINER",
# // "ON_TERTIARY_FIXED",
# // "ON_TERTIARY_FIXED_VARIANT",


# // "SURFACE",
# // "SURFACE_BRIGHT",
# // "SURFACE_CONTAINER",
# // "SURFACE_CONTAINER_HIGH",
# // "SURFACE_CONTAINER_HIGHEST",
