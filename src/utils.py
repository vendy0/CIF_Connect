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


def generate_secure_code():
	caracteres = string.ascii_letters + string.digits
	return "".join(secrets.choice(caracteres) for _ in range(4))


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


# Assurez-vous que les fichiers json sont dans le même dossier ou ajustez le cheminimport json
class Room:
	def __init__(
		self, page, room_id, name, description, icon=ft.Icons.CHAT_BUBBLE_ROUNDED, code="ab12"
	):
		self.page = page
		self.id: int = room_id
		self.name: str = name
		self.description: str = description
		self.icon: ft.Icons = icon
		self.code: str = code

		self.controls = ft.ListTile(
			leading=ft.Icon(icon=self.icon, color=ft.Colors.BLUE_600),
			title=ft.Text(self.name, weight="bold"),
			subtitle=ft.Text(self.description),
			trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
			data=self.id,
			on_click=self.join_room,
		)

	async def join_room(self, e):
		self.page.session.store.set("current_room_id", self.id)
		self.page.session.store.set("current_room_name", self.name)
		asyncio.create_task(self.page.push_route(route="/chat"))


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
		return await self.client.get(endpoint)

	async def post(self, endpoint: str, data: dict):
		return await self.client.post(endpoint, json=data)


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


def format_date(date_to_format: datetime):
	day = date_to_format.strftime("%d")

	day_diff = int(date.today().strftime("%d")) - int(day)
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


def get_avatar_color(username, colors_lookup):
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
