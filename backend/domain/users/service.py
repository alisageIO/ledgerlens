from sqlalchemy.exc import IntegrityError

from constants import system_messages as SYS_MSG
from domain.exceptions import DuplicateEmailError
from domain.users.hashing import hash_password
from domain.users.hashing import verify_password as _verify_password
from domain.users.models import User
from domain.users.repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_user(self, email: str, password: str) -> User:
        """Hashes the password and persists a new User; never stores the raw value."""
        user = User(email=email, password_hash=hash_password(password))
        self.repository.session.add(user)
        try:
            self.repository.session.flush()
            self.repository.session.refresh(user)
            self.repository.session.commit()
            return user
        except IntegrityError as exc:
            self.repository.session.rollback()
            err_msg = str(exc.orig).lower() if exc.orig else str(exc).lower()
            if "unique" in err_msg and "email" in err_msg:
                raise DuplicateEmailError(SYS_MSG.DUPLICATE_EMAIL) from exc
            raise
        except Exception:
            self.repository.session.rollback()
            raise

    def verify_password(self, user: User, password: str) -> bool:
        """Returns True if the plaintext password matches this user's stored hash."""
        return _verify_password(password, user.password_hash)
