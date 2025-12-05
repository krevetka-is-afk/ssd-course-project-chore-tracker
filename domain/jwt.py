import os

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# In production JWT_SECRET should be provided via env var. For local development/tests we fall back
# to a deterministic value so the app can start without extra configuration.
SECRET_KEY = os.getenv("JWT_SECRET", "insecure-dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
