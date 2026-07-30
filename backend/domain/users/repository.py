from domain.shared.repository import AbstractRepository
from domain.users.models import User


class UserRepository(AbstractRepository[User]):
    model = User

    def find_by_email(self, email: str) -> User | None:
        """Returns the user with this email, or None if no such user exists."""
        return self.session.query(User).filter_by(email=email).first()
