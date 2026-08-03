from uuid import UUID

from sqlalchemy.orm import Session

from domain.shared.base import Base


class AbstractRepository[ModelT: Base]:
    """Base class every entity's repository extends.

    Services depend on a concrete Repository subclass, never on a raw
    SQLAlchemy Session directly — this is the DB-access boundary
    (CONTRIBUTING.md "Database access"). No raw SQL outside repositories
    and migrations.
    """

    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: UUID) -> ModelT | None:
        return self.session.get(self.model, id)

    def add(self, entity: ModelT) -> ModelT:
        """Persists a new entity: add, flush, refresh, commit; rolls back on failure."""
        self.session.add(entity)
        try:
            self.session.flush()
            self.session.refresh(entity)
            self.session.commit()
            return entity
        except Exception:
            self.session.rollback()
            raise
