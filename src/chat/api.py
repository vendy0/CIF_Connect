import httpx
from utils import api, show_top_toast


async def fetch_room_messages(page, room_id):
    """
    Récupère la liste des messages d'un salon.
    Gère les erreurs 401 et les erreurs réseau.
    """
    try:
        response = await api.get(f"/room/{room_id}/messages")

        if response.status_code == 401:
            await show_top_toast(page, "La session a expiré !", True)
            await page.push_route("/login")
            return None

        if response.status_code != 200:
            await show_top_toast(page, "Erreur lors de la récupération", True)
            return None

        return response.json()

    except httpx.RequestError:
        await show_top_toast(page, "Erreur réseau !", True)
        return None


async def put_message(page, edit_message_input, msg):
    try:
        response = await api.put(f"/message/{msg.id}", data={"content": msg.content})
        # Si le jeton est expiré ou invalide (401)
        if response.status_code not in [200, 201]:
            edit_message_input.error = response.json().get("detail", "Erreur inconnue")
            await show_top_toast(page, "La session a expiré !", True)
            page.update()
            return response.json()
        return

    except httpx.RequestError as ex:
        await show_top_toast(page, "Erreur réseau !", True)
        return


async def post_reaction(page, msg_id, emoji):
    # 2. Appeler ton API pour envoyer la réaction
    try:
        response = await api.post(f"/message/{msg_id}/reaction", data={"emoji": emoji})
        # Si le jeton est expiré ou invalide (401)
        if response.status_code == 401:
            await show_top_toast(page, "La session a expiré !", True)
            await page.push_route("/login")  # On redirige
            return
        return response.json()
    except httpx.RequestError as ex:
        await show_top_toast(page, "Erreur réseau !", True)
        await page.push_route("/rooms")
        return


async def post_report(page, msg_id, report_reason_input):
    # 3. On demande la liste fraîche au serveur
    try:
        payload = {"message_id": msg_id, "raison": report_reason_input.value.strip()}
        response = await api.post(f"/reports", data=payload)

        # Si le jeton est expiré ou invalide (401)
        if response.status_code != 201:
            await show_top_toast(page, "Erreur lors du signalement !", True)
            report_reason_input.error = "Il y a eu urreur lors du signalement !"
            page.update()
            return

        await show_top_toast(page, "Signalement envoyé à la modération.")

    except httpx.RequestError as ex:
        await show_top_toast(page, "Erreur réseau !", True)
        report_reason_input.error = "Serveur injoignable"
        page.update()
        return


async def delete_message_bdd(page, msg_id):
    try:
        response = await api.delete(endpoint=f"/message/{msg_id}")

        if response.status_code != 204:
            await show_top_toast(page, response.json().get("detail", "Erreur lors de la suppression !"), True)
            return

        page.pop_dialog()
        await show_top_toast(page, "Message supprimé !")
        page.update()

    except httpx.RequestError as ex:
        await show_top_toast(page, "Erreur lors de la suppression !", True)
        page.update()
        return


async def post_message(page, room_id, parent_id, new_message_input):
    try:
        payload = {"content": new_message_input.value.strip(), "parent_id": parent_id}
        response = await api.post(f"/room/{room_id}/messages", data=payload)

        # Si le jeton est expiré ou invalide (401)
        if response.status_code != 201:
            await show_top_toast(page, "Erreur lors de l'envoi du message !", True)
            new_message_input.error = "Message non envoyé !"
            page.update()
            return

        new_message_input.error = None
        new_message_input.value = ""
        await new_message_input.focus()
        return response.json()

    except httpx.RequestError as ex:
        await show_top_toast(page, "Erreur lors de l'envoi du message !", True)
        new_message_input.error = "Erreur, Message non envoyé !"
        page.update()
        return


async def post_quit_room(
    page,room_id
):
    try:
        response = await api.post(f"/user/rooms/{room_id}/quit")
        # Si le jeton est expiré ou invalide (401)
        if response.status_code != 204:
            await show_top_toast(page, response.json().get("detail", "Erreur inconnue"), True)
            return

        await page.push_route("/rooms")
        await show_top_toast(page, "Salon supprimé")

    except httpx.RequestError as ex:
        await show_top_toast(page, "Erreur réseau !", True)
        return
