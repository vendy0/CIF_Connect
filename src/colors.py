import hashlib

def get_colors():
    list_cols = []
    with open("../ft_cols.json",  "r", encoding="utf-8") as f:
        list_cols = json.load(f)
        return list_cols
        

def get_user_color(user_name, colors_lookup):
    # On crée un hash stable à partir du nom d'utilisateur
    hash_object = hashlib.md5(user_name.encode())
    hash_hex = hash_object.hexdigest()
    
    # On convertit une partie du hash hexadécimal en entier
    # (int(..., 16) transforme l'hexa en base 10)
    hash_int = int(hash_hex[:8], 16) 
    
    return colors_lookup[hash_int % len(colors_lookup)]
