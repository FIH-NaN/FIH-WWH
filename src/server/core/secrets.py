import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from src.server.config import get_settings


_ENCRYPTION_PREFIX = "enc:v1:"


@lru_cache()
def _get_fernet() -> Fernet:
    settings = get_settings()
    raw_key = (settings.PLAID_TOKEN_ENCRYPTION_KEY or "").strip()

    if raw_key:
        key_bytes = raw_key.encode("utf-8")
    else:
        digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        key_bytes = base64.urlsafe_b64encode(digest)

    return Fernet(key_bytes)


def encrypt_secret(value: str) -> str:
    token = _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return f"{_ENCRYPTION_PREFIX}{token}"


def decrypt_secret(value: str) -> str:
    if not value:
        return value

    if not value.startswith(_ENCRYPTION_PREFIX):
        return value

    payload = value[len(_ENCRYPTION_PREFIX):]
    try:
        return _get_fernet().decrypt(payload.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        raise ValueError("Invalid encrypted credential payload")
