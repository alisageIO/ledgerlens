import bcrypt

from constants import system_messages as SYS_MSG
from domain.exceptions import EmptyPasswordError

_ENCODING = "utf-8"


def hash_password(password: str) -> str:
    """Hashes a plaintext password with bcrypt using a fresh per-call salt."""
    if not password:
        raise EmptyPasswordError(SYS_MSG.EMPTY_PASSWORD)
    hashed = bcrypt.hashpw(password.encode(_ENCODING), bcrypt.gensalt())
    return hashed.decode(_ENCODING)


def verify_password(password: str, password_hash: str) -> bool:
    """Returns True if the plaintext password matches the stored bcrypt hash."""
    return bcrypt.checkpw(password.encode(_ENCODING), password_hash.encode(_ENCODING))
