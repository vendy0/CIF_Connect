import hashlib
import random
import json
from pathlib import Path
import flet as ft
import secrets
import string
import asyncio


def generate_secure_code():
    caracteres = string.ascii_letters + string.digits
    return "".join(secrets.choice(caracteres) for _ in range(4))


# Assurez-vous que les fichiers json sont dans le même dossier ou ajustez le cheminimport json
class Room:
    def __init__(self, page, room_id, name, description, icon=ft.Icons.CHAT_BUBBLE_ROUNDED, code="ab12"):
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

    def join_room(self, e):
        asyncio.create_task(self.page.push_route(route="/chat"))


rooms = []


def load_json_file(filename):
    try:
        path_actuel = Path(filename)
        path_parent = Path("..") / filename

        # Utilisation de .exists() avec parenthèses
        if path_actuel.exists():
            with open(path_actuel, "r", encoding="utf-8") as f:
                return json.load(f)

        elif path_parent.exists():
            with open(path_parent, "r", encoding="utf-8") as f:
                return json.load(f)

        else:
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


# def get_avatar_color(user_name, colors_lookup):
# 	if not colors_lookup:
# 		return "#CCCCCC"
# 	hash_object = hashlib.md5(user_name.encode())
# 	hash_hex = hash_object.hexdigest()
# 	hash_int = int(hash_hex[:8], 16)
# 	print(colors_lookup[hash_int % len(colors_lookup)])
# 	return Colors.colors_lookup[hash_int % len(colors_lookup)]


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


# if __name__ == "__main__":
# 	print()
# 	for i in range(1,100):
# 		print(f"\n{generer_pseudo()}")
# print(Path("./src/chat.py").exists())
# load_json_file("ft_cols.json")
# get_avatar_color("SansDetermin108", get_colors())

# async def view_pop(e):
#     if e.view is not None:
#         print("View pop:", e.view)
#         page.views.remove(e.view)
#         top_view = page.views[-1]
#         await page.push_route(top_view.route)
# pass

# if __name__ == "__main__":
# 	pseudo = generer_pseudo()
# 	COLORS_LOOKUP = get_colors()
# 	color = get_avatar_color(pseudo, COLORS_LOOKUP)
# 	print("Pseudo :", pseudo)
# 	print("Couleur :", color)
