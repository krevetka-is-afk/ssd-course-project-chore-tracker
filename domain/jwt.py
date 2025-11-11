from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

SECRET_KEY = "change_this_to_a_random_secret_key_please"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 час

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
