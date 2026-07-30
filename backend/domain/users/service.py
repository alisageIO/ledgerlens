from domain.users.hashing import hash_password, verify_password as _verify_password
from domain.users.models import User
from domain.users.repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_user(self, email: str, password: str) -> User:
        """Hashes the password and persists a new User; never stores the raw value."""
        user = User(email=email, password_hash=hash_password(password))
        self.repository.session.add(user)
        self.repository.session.commit()
        self.repository.session.refresh(user)
        return user

    def verify_password(self, user: User, password: str) -> bool:
        """Returns True if the plaintext password matches this user's stored hash."""
        return _verify_password(password, user.password_hash)
