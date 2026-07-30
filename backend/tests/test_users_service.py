import logging

import pytest
from _pytest.logging import LogCaptureFixture
from sqlalchemy.orm import Session

from domain.users.repository import UserRepository
from domain.users.service import UserService


@pytest.fixture
def user_service(db_session: Session) -> UserService:
    repository = UserRepository(db_session)
    return UserService(repository)


def test_create_user_persists_password_hash_not_plaintext(
    db_session: Session, user_service: UserService
) -> None:
    email = "test@example.com"
    password = "s3cr3tPassword!"

    user = user_service.create_user(email=email, password=password)

    assert user.email == email
    assert user.password_hash != password
    # Ensure it's stored in the DB
    repository = UserRepository(db_session)
    db_user = repository.find_by_email(email)
    assert db_user is not None
    assert db_user.id == user.id
    assert db_user.password_hash == user.password_hash


def test_verify_password_against_persisted_user(user_service: UserService) -> None:
    email = "test_verify@example.com"
    password = "correct_password"

    user = user_service.create_user(email=email, password=password)

    assert user_service.verify_password(user, password) is True
    assert user_service.verify_password(user, "wrong_password") is False


def test_find_by_email_returns_none_when_no_match(db_session: Session) -> None:
    repository = UserRepository(db_session)
    assert repository.find_by_email("nonexistent@example.com") is None


def test_find_by_email_returns_matching_user(
    db_session: Session, user_service: UserService
) -> None:
    email = "match@example.com"
    user = user_service.create_user(email=email, password="somepassword")

    repository = UserRepository(db_session)
    matched = repository.find_by_email(email)
    assert matched is not None
    assert matched.id == user.id
    assert matched.email == email


def test_create_and_verify_never_logs_raw_password(
    user_service: UserService, caplog: LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)

    distinct_password = "a-very-distinctive-raw-password-marker"
    user = user_service.create_user(email="logger@example.com", password=distinct_password)

    user_service.verify_password(user, distinct_password)

    for record in caplog.records:
        assert distinct_password not in record.message


def test_create_user_duplicate_email_raises_duplicate_email_error(
    user_service: UserService,
) -> None:
    from domain.exceptions import DuplicateEmailError

    email = "duplicate@example.com"
    user_service.create_user(email=email, password="password123")

    with pytest.raises(DuplicateEmailError) as exc_info:
        user_service.create_user(email=email, password="anotherpassword")

    assert "already exists" in str(exc_info.value)


def test_user_repr_omits_email() -> None:
    import uuid

    from domain.users.models import User

    user_id = uuid.uuid4()
    user = User(id=user_id, email="secret@example.com", password_hash="hash")
    representation = repr(user)
    assert "secret@example.com" not in representation
    assert str(user_id) in representation
