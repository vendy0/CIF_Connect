import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Configuration JWT
SECRET_KEY = "6265f35102c7149eae6ab69103731f3a5802a4fdd09637352855d4e30263724e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_password_hash(password: str):
    # On encode et on coupe brutalement à 72 caractères pour éviter le crash
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password_clair: str, password_hash: str):
    pwd_bytes = password_clair.encode('utf-8')[:72]
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


# from datetime import datetime, timedelta
# from jose import JWTError, jwt
# from passlib.context import CryptContext

# # security.py
# from passlib.context import CryptContext

# # Remplace la configuration actuelle par celle-ci
# pwd_context = CryptContext(
#     schemes=["bcrypt"], 
#     deprecated="auto",
#     bcrypt__ident="2b" # Force l'identifiant moderne
# )

# # Configuration JWT
# SECRET_KEY = "6265f35102c7149eae6ab69103731f3a5802a4fdd09637352855d4e30263724e"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30


# def create_access_token(data: dict):
#     to_encode = data.copy()
#     # On définit l'expiration (ex: maintenant + 30 min)
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})

#     # On signe le tout avec notre SECRET_KEY
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# def get_password_hash(password: str):
#     return pwd_context.hash(password)


# def verify_password(password_clair: str, password_hash: str):
#     return pwd_context.verify(password_clair, password_hash)
