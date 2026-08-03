import pytest

from domain.exceptions import EmptyPasswordError
from domain.users.hashing import hash_password, verify_password


def test_hash_password_returns_hash_different_from_plaintext() -> None:
    plaintext = "s3cr3t!"
    hashed = hash_password(plaintext)
    assert hashed != plaintext


def test_verify_password_correct_returns_true() -> None:
    plaintext = "s3cr3t!"
    hashed = hash_password(plaintext)
    assert verify_password(plaintext, hashed) is True


def test_verify_password_incorrect_returns_false() -> None:
    plaintext = "s3cr3t!"
    hashed = hash_password(plaintext)
    assert verify_password("wrong_password", hashed) is False


def test_hash_password_empty_string_raises_before_hashing() -> None:
    with pytest.raises(EmptyPasswordError) as exc_info:
        hash_password("")
    assert "Password must not be empty" in str(exc_info.value)


def test_hash_password_non_ascii_hashes_and_verifies() -> None:
    plaintext = "pässwörd123ñ"
    hashed = hash_password(plaintext)
    assert hashed != plaintext
    assert verify_password(plaintext, hashed) is True


def test_hash_password_same_password_twice_produces_different_hashes() -> None:
    plaintext = "same"
    hashed1 = hash_password(plaintext)
    hashed2 = hash_password(plaintext)
    assert hashed1 != hashed2


def test_hash_password_uses_bcrypt_not_fast_hash() -> None:
    plaintext = "s3cr3t!"
    hashed = hash_password(plaintext)
    # Bcrypt hashes typically start with $2a$, $2b$, or $2y$ and have length 60
    assert hashed.startswith(("$2a$", "$2b$", "$2y$"))
    assert len(hashed) == 60


def test_hash_password_never_appears_in_exception_message() -> None:
    with pytest.raises(EmptyPasswordError) as exc_info:
        hash_password("")
    # Ensure empty string/sensitive input is not formatted into the exception
    assert str(exc_info.value) == "Password must not be empty"


def test_hash_password_72_bytes_succeeds() -> None:
    password = "a" * 72
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_hash_password_above_72_bytes_raises_validation_error() -> None:
    from domain.exceptions import ValidationError

    password = "a" * 73
    with pytest.raises(ValidationError) as exc_info:
        hash_password(password)
    assert "Password must not exceed 72 bytes" in str(exc_info.value)


def test_verify_password_above_72_bytes_raises_validation_error() -> None:
    from domain.exceptions import ValidationError

    password = "a" * 73
    with pytest.raises(ValidationError) as exc_info:
        verify_password(password, "some_hash")
    assert "Password must not exceed 72 bytes" in str(exc_info.value)


def test_verify_password_empty_string_raises_empty_password_error() -> None:
    hashed = hash_password("s3cr3t!")
    with pytest.raises(EmptyPasswordError) as exc_info:
        verify_password("", hashed)
    assert "Password must not be empty" in str(exc_info.value)
