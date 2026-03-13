import hashlib
import random
import json
from pathlib import Path
import flet as ft
import secrets
import string
import asyncio
import base64
import json
from datetime import datetime, timedelta, date
import httpx
from typing import Optional

host = "127.0.0.1"
port = "8000"


async def view_pop(view, page):
	if len(page.views) > 1:
		page.views.pop()
		page.update()


# AVAILABLE_ICONS = [
# 	ft.Icons.MESSAGE,
# 	ft.Icons.GROUPS,
# 	ft.Icons.SCHOOL,
# 	ft.Icons.SPORTS_SOCCER,
# 	ft.Icons.SPORTS_BASKETBALL,
# 	ft.Icons.MUSIC_NOTE,
# 	ft.Icons.GAMEPAD,
# 	ft.Icons.COMPUTER,
# 	ft.Icons.SCIENCE,
# 	ft.Icons.BOOK,
# 	ft.Icons.COFFEE,
# 	ft.Icons.LOCAL_PIZZA,
# 	ft.Icons.LOCK,
# 	ft.Icons.STAR,
# 	ft.Icons.FAVORITE,
# ]

# Filtrer proprement (garde uniquement les icônes réellement exposées par ft.Icons)

icons = [
	"MESSAGE",
	"GROUPS",
	"SCHOOL",
	"SPORTS_SOCCER",
	"SPORTS_BASKETBALL",
	"MUSIC_NOTE",
	"GAMEPAD",
	"COMPUTER",
	"SCIENCE",
	"BOOK",
	"COFFEE",
	"LOCAL_PIZZA",
	"LOCK",
	"STAR",
	"FAVORITE",
	"FAVORITE_BORDER",
	"PERSON",
	"PERSON_ADD",
	"PEOPLE",
	"ACCOUNT_CIRCLE",
	"CHAT_BUBBLE",
	"CHAT_BUBBLE_OUTLINE",
	"FORUM",
	"EMAIL",
	"SEND",
	"INBOX",
	"ARCHIVE",
	"DELETE",
	"DELETE_FOREVER",
	"EDIT",
	"CREATE",
	"SAVE",
	"BOOKMARK",
	"BOOKMARK_BORDER",
	"HOME",
	"DASHBOARD",
	"SETTINGS",
	"SEARCH",
	"CLOSE",
	"CHECK",
	"CANCEL",
	"REFRESH",
	"SHARE",
	"LINK",
	"LOCK_OPEN",
	"NOTIFICATIONS",
	"NOTIFICATIONS_ACTIVE",
	"NOTIFICATIONS_OFF",
	"ALARM",
	"ACCESS_TIME",
	"CALENDAR_TODAY",
	"EVENT",
	"LOCATION_ON",
	"MAP",
	"PIN_DROP",
	"DIRECTIONS",
	"DIRECTIONS_CAR",
	"TRAIN",
	"FLIGHT",
	"PHONE",
	"VIDEO_CALL",
	"CAMERA",
	"PHOTO_CAMERA",
	"IMAGE",
	"PLAY_ARROW",
	"PAUSE",
	"STOP",
	"VOLUME_UP",
	"VOLUME_DOWN",
	"MIC",
	"MIC_OFF",
	"ATTACH_FILE",
	"ATTACH_MONEY",
	"CREDIT_CARD",
	"SHOPPING_CART",
	"SHOPPING_BAG",
	"STORE",
	"WORK",
	"BRIEFCASE",
	"BUILD",
	"TOOLS",
	"BUG_REPORT",
	"SECURITY",
	"SHIELD",
	"HEALTH_AND_SAFETY",
	"STAR_RATE",
	"TROPHY",
	"MEDAL",
	"SHOW_CHART",
	"INSIGHTS",
	"BAR_CHART",
	"PIE_CHART",
	"ANALYTICS",
	"HISTORY",
	"TIMELINE",
	"TRAVEL_EXPLORER",
	"LIGHT_MODE",
	"DARK_MODE",
	"BATTERY_FULL",
	"BATTERY_CHARGING_FULL",
	"WIFI",
	"PRINT",
	"LOCAL_CAFE",
	"RESTAURANT",
	"LOCAL_BAR",
	"LOCAL_HOTEL",
	"PLAYLIST_ADD",
	"MUSIC_VIDEO",
	"NIGHTLIFE",
	"LOCAL_BAR",
	"WINE_BAR",
	"LIQUOR",
	"SMOKING_ROOMS",
	"KING_BED",
	"HOTEL",
	"BATHTUB",
	"SPA",
	"SELF_IMPROVEMENT",
	"CELEBRATION",
	"CAKE",
	"LOCAL_DRINK",
	"MOOD",
	"MOOD_BAD",
	"WHATSHOT",
	"FLASH_ON",
	"VISIBILITY",
	"VISIBILITY_OFF",
	"PRIVACY_TIP",
	"NO_MEETING_ROOM",
	"MEETING_ROOM",
	"DOOR_FRONT",
	"DOOR_BACK",
	"LOCK_PERSON",
	"PERSON_SEARCH",
	"PERSON_REMOVE",
	"GROUP_REMOVE",
	"GROUP_ADD",
	"EIGHTEEN_UP_RATING",
	"NO_ADULT_CONTENT",
	"PRIVACY_TIP",
	"LOCK_PERSON",
	"VOLCANO",
	"INCOGNITO",
	"VISIBILITY_OFF",
	"FINGERPRINT",
	"SHIELD_MOON",
]

# AVAILABLE_ICONS contient alors seulement les icons valides sur ta install (0.80.5)
AVAILABLE_ICONS = [getattr(ft.Icons, n) for n in icons if hasattr(ft.Icons, n)]


async def select_icon_dialog(page: ft.Page, current_icon_control: ft.Icon, on_select_callback=None):
	"""
	Ouvre un dialogue pour choisir une icône.
	Met à jour automatiquement le contrôle visuel fourni et exécute un callback si nécessaire.
	"""

	def handle_select(icon_name):
		current_icon_control.icon = icon_name
		page.pop_dialog()
		if on_select_callback:
			# On passe le nom de l'icône au callback pour mettre à jour l'état local du View
			on_select_callback(icon_name)
		page.update()

	grid = ft.GridView(
		expand=True,
		runs_count=4,
		max_extent=70,
		spacing=12,
		controls=[ft.IconButton(icon=i, on_click=lambda e, i=i: handle_select(i)) for i in AVAILABLE_ICONS],
	)

	dialog = ft.AlertDialog(
		title=ft.Text("Choisir une icône"),
		content=ft.Container(width=300, height=300, content=grid),
		actions=[ft.TextButton("Annuler", on_click=lambda _: page.pop_dialog())],
	)

	page.show_dialog(dialog)


def generate_secure_code():
	caracteres = string.ascii_letters + string.digits
	return "".join(secrets.choice(caracteres) for _ in range(10))


async def decode_token(token):
	# Décodage manuel du Payload (partie centrale du JWT)
	try:
		payload_b64 = token.split(".")[1]
		# Ajout de padding si nécessaire pour base64
		payload_json = base64.b64decode(payload_b64 + "==").decode("utf-8")
		user_info = json.loads(payload_json)
		return user_info
	except Exception as e:
		print(f"Erreur décodage token: {e}")


unread_badge = ft.Container(
	content=ft.Text("3", size=10, color=ft.Colors.WHITE, weight="bold"),
	bgcolor=ft.Colors.GREEN_500,
	border_radius=10,
	padding=ft.padding.symmetric(horizontal=6, vertical=2),
	visible=True,  # À conditionner selon tes calculs de dates
)


class Room:
	def __init__(self, page, room_id, name, last_msg_content, last_msg_author, last_msg_time, unread_count,last_read_id, icon=ft.Icons.CHAT_BUBBLE_ROUNDED):
		self.page = page
		self.id = room_id
		self.name = name
		self.icon = icon
		self.last_read_id = last_read_id

		# Formater le sous-titre (Style WhatsApp)
		if last_msg_author:
			subtitle_text = f"~{last_msg_author}: {last_msg_content}"
		else:
			subtitle_text = last_msg_content

		# Rendre le badge dynamique
		unread_badge = ft.Container(
			content=ft.Text(str(unread_count), size=10, color=ft.Colors.WHITE, weight="bold"),
			bgcolor=ft.Colors.GREEN_500,
			border_radius=10,
			padding=ft.padding.symmetric(horizontal=6, vertical=2),
			visible=unread_count > 0,  # Caché si 0 non-lu
		)

		self.controls = ft.ListTile(
			key=str(self.id),
			leading=ft.Icon(icon=self.icon, color=ft.Colors.BLUE_600),
			title=ft.Text(self.name, weight="bold"),
			subtitle=ft.Text(subtitle_text, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.GREEN_500 if unread_count > 0 else None),  # Tronquer si trop long
			data=self.id,
			on_click=self.join_room,
			trailing=ft.Column(
				[
					ft.Text(last_msg_time or "", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
					unread_badge,
				],
				alignment=ft.MainAxisAlignment.CENTER,
				spacing=2,
			),
		)

	async def join_room(self, e):
		self.page.session.store.set("current_room_id", self.id)
		self.page.session.store.set("current_room_name", self.name)
		self.page.session.store.set("last_read_id", self.last_read_id) # <-- AJOUT
		await self.page.push_route(route="/chat")


host = "127.0.0.1"  # Ton IP
port = 8000


class APIClient:
	def __init__(self):
		# Initialise un client persistant
		self.client = httpx.AsyncClient(base_url=f"http://{host}:{port}")
		self.token: Optional[str] = None

	def set_token(self, token: str):
		self.token = token
		self.client.headers.update({"Authorization": f"Bearer {token}"})

	async def get(self, endpoint: str):
		response = await self.client.get(endpoint)
		return response

	async def post(self, endpoint: str, data: dict = None):
		response = await self.client.post(endpoint, json=data)
		return response

	async def put(self, endpoint: str, data: dict = None):
		response = await self.client.put(endpoint, json=data)
		return response

	async def delete(self, endpoint: str, data: dict = None):
		response = await self.client.request("DELETE", endpoint, json=data)
		return response

	async def close(self):
		await self.client.aclose()


# On instancie un client unique qui sera importé partout
api = APIClient()


async def show_top_toast(page: ft.Page, message: str, is_error: bool = False):
	color = ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600

	# On crée la bulle de notification
	toast = ft.Container(
		content=ft.Text(message, color=ft.Colors.WHITE, weight="bold"),
		bgcolor=color,
		padding=ft.padding.symmetric(horizontal=20, vertical=10),
		border_radius=30,
		top=20,  # Affichage en haut
		right=20,  # On l'aligne en haut à droite (ou retire 'right' et gère l'alignement pour centrer)
		animate_position=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
		animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
		# alignment=ft.Alignment.CENTER,
	)

	# Avec Flet 0.80.5, on ajoute simplement à l'overlay pour ce genre d'éléments flottants non-modaux
	page.overlay.append(toast)
	page.update()

	# On attend 3 secondes et on le fait disparaître
	import asyncio

	await asyncio.sleep(3)
	toast.opacity = 0
	page.update()
	await asyncio.sleep(0.3)  # Temps de l'animation
	page.overlay.remove(toast)
	page.update()


async def copy_message(e, page, content, success_message="Copié"):
	await ft.Clipboard().set(content)
	page.pop_dialog()
	await show_top_toast(page, success_message)


async def refresh_rooms(page, storage):
	try:
		response = await api.get("/user/rooms")

		if response.status_code == 401:
			await storage.remove("cif_token")
			await page.push_route("/login")
			return

		data = response.json()

		# Dans rooms_view.py, juste après "rooms = response.json()"
		await storage.set("rooms_cache", json.dumps(data))
		storage.update()

		page.update()

	except httpx.RequestError:
		await show_top_toast(page, "Erreur réseau !", True)


def format_date(date_to_format: datetime):
	day = date_to_format.strftime("%d")

	day_diff = int(date.today().strftime("%d")) - int(day)
	if day_diff == -1:
		return "Demain"
	if day_diff == 0:
		return "Aujourd'hui"
	elif day_diff == 1:
		return "Hier"

	month_dict = {
		1: "Janvier",
		2: "Février",
		3: "Mars",
		4: "Avril",
		5: "Mai",
		6: "Juin",
		7: "Juillet",
		8: "Août",
		9: "Septembre",
		10: "Octobre",
		11: "Novembre",
		12: "Décembre",
	}

	month_number = date_to_format.strftime("%m")
	year = date_to_format.strftime("%Y")

	month_name = month_dict[int(month_number)]

	return f"{int(day)} {month_name} {int(year)}"


def load_json_file(filename):
	try:
		path_autres = Path("autres") / filename
		path_source = Path("src") / filename
		path_actuel = Path(filename)
		path_parent = Path("..") / filename

		# Utilisation de .exists() avec parenthèses
		if path_actuel.exists():
			with open(path_actuel, "r", encoding="utf-8") as f:
				return json.load(f)

		elif path_parent.exists():
			with open(path_parent, "r", encoding="utf-8") as f:
				return json.load(f)
		elif path_autres.exists():
			with open(path_autres, "r", encoding="utf-8") as f:
				return json.load(f)

		elif path_source.exists():
			with open(path_source, "r", encoding="utf-8") as f:
				return json.load(f)

		else:
			print(path_parent)
			print(path_actuel)
			print("Rien")
			return []

	except Exception as e:
		print(f"Erreur chargement {filename}: {e}")
		return []


def get_colors():
	# Si le fichier n'existe pas, retourne une liste de couleurs par défaut
	cols = load_json_file("ft_cols.json")
	if not cols:
		return ["#FF5733", "#33FF57", "#3357FF", "#F0F0F0"]
	return cols


COLORS_LOOKUP = get_colors()


def get_avatar_color(username, colors_lookup=COLORS_LOOKUP):
	# Création d'un hash unique à partir du pseudo
	# (Contrairement à hash(), hashlib est constant entre les redémarrages)
	hash_object = hashlib.md5(username.encode())
	hash_int = int(hash_object.hexdigest(), 16)

	# Sélection du nom de la couleur dans ta liste
	color_name = colors_lookup[hash_int % len(colors_lookup)]

	# Conversion de la chaîne (ex: "AMBER_500") en constante Flet
	# On utilise getattr pour transformer la string en objet ft.colors
	try:
		return getattr(ft.Colors, color_name)
	except AttributeError:
		return ft.Colors.BLUE  # Fallback si le nom est mal orthographié


def generer_pseudo():
	def is_prime(num):
		for x in range(2, int(num**0.5) + 1):
			if (num % x) == 0:
				return False
		return True

	list_pseudos = load_json_file("pseudos.json")

	# Fallback si le fichier pseudos est vide ou absent
	if not list_pseudos:
		return f"User{random.randint(1000, 9999)}"

	# On suppose que list_pseudos est une liste de listes [[adj...], [animaux...]]
	# Si c'est juste une liste simple, il faut adapter.
	# Ici, on garde votre logique de "groupe"
	groupe1 = random.choice(list_pseudos)
	groupe2 = random.choice(list_pseudos)

	# Sécurité pour éviter boucle infinie si liste trop petite
	if len(list_pseudos) > 1:
		while groupe1 == groupe2:
			groupe2 = random.choice(list_pseudos)

	mot1 = random.choice(groupe1) if isinstance(groupe1, list) else groupe1
	mot2 = random.choice(groupe2) if isinstance(groupe2, list) else groupe2

	primes = [x for x in range(1, 1000) if is_prime(x)]
	num = random.choice(primes) if primes else 1

	pseudo = f"{mot1}{mot2}{num}"
	return pseudo


def get_initials(pseudo):
	# Correction majeure : la variable d'entrée est 'pseudo', pas 'initials'
	initials = ""
	if not pseudo:
		return "??"

	# Logique : prendre les majuscules, max 2 lettres
	for char in pseudo:
		if char.isupper():
			initials += char
			if len(initials) == 2:
				break

	# Si pas de majuscules trouvées (ex: pseudo tout en minuscules), prendre les 2 premières lettres
	if not initials:
		initials = pseudo[:2].upper()

	return initials


async def shake(control: ft.Control, page: ft.Page):
	# Animation : déplacement gauche-droite rapide
	offsets = [-10, 10, -8, 8, -5, 5, 0]  # valeur en pixels
	for x in offsets:
		control.offset = ft.Offset(x, 0)
		control.update()
		await asyncio.sleep(0.03)  # vitesse du shake
