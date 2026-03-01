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
	pwd_bytes = password.encode("utf-8")[:72]
	salt = bcrypt.gensalt()
	hashed = bcrypt.hashpw(pwd_bytes, salt)
	return hashed.decode("utf-8")


def verify_password(password_clair: str, password_hash: str):
	pwd_bytes = password_clair.encode("utf-8")[:72]
	hash_bytes = password_hash.encode("utf-8")
	return bcrypt.checkpw(pwd_bytes, hash_bytes)


# if __name__ == "__main__":
# 	print(get_password_hash("1234"))
