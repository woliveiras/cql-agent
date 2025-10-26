"""
Testes para o handler de JWT anônimo
"""

import pytest
import time
from datetime import datetime, timedelta, timezone
from api.auth.jwt_handler import JWTHandler, AnonymousToken


def test_create_token():
    """Testa criação de token JWT"""
    handler = JWTHandler(secret_key="test_secret_key_123")
    token = handler.create_token(fingerprint="test_fingerprint")

    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token():
    """Testa verificação de token válido"""
    handler = JWTHandler(secret_key="test_secret_key_123")
    token = handler.create_token(fingerprint="test_fp")

    decoded = handler.verify_token(token)

    assert decoded is not None
    assert isinstance(decoded, AnonymousToken)
    assert decoded.fingerprint == "test_fp"
    assert decoded.user_id.startswith("anon_")


def test_verify_invalid_token():
    """Testa verificação de token inválido"""
    handler = JWTHandler(secret_key="test_secret_key_123")

    decoded = handler.verify_token("invalid_token_xyz")

    assert decoded is None


def test_verify_token_wrong_secret():
    """Testa verificação de token com chave secreta diferente"""
    handler1 = JWTHandler(secret_key="secret1")
    handler2 = JWTHandler(secret_key="secret2")

    token = handler1.create_token(fingerprint="test_fp")
    decoded = handler2.verify_token(token)

    assert decoded is None


def test_token_expiration():
    """Testa expiração de token"""
    handler = JWTHandler(
        secret_key="test_secret",
        token_expiration_hours=0  # Expira imediatamente
    )

    token = handler.create_token(fingerprint="test_fp")

    # Aguardar um pouco para garantir expiração
    time.sleep(0.1)

    decoded = handler.verify_token(token)
    assert decoded is None  # Token expirado


def test_token_quota_limit():
    """Testa criação de token com quota customizada"""
    handler = JWTHandler(secret_key="test_secret")
    token = handler.create_token(fingerprint="test_fp", quota_limit=50)

    decoded = handler.verify_token(token)

    assert decoded is not None
    assert decoded.quota_limit == 50
    assert decoded.quota_used == 0


def test_token_custom_user_id():
    """Testa criação de token com user_id customizado"""
    handler = JWTHandler(secret_key="test_secret")
    token = handler.create_token(
        fingerprint="test_fp",
        user_id="custom_user_123"
    )

    decoded = handler.verify_token(token)

    assert decoded is not None
    assert decoded.user_id == "custom_user_123"


def test_anonymous_token_is_expired():
    """Testa propriedade is_expired"""
    now = datetime.now(timezone.utc)

    # Token expirado
    token1 = AnonymousToken(
        user_id="user1",
        fingerprint="fp1",
        issued_at=now - timedelta(hours=2),
        expires_at=now - timedelta(hours=1)
    )
    assert token1.is_expired is True

    # Token válido
    token2 = AnonymousToken(
        user_id="user2",
        fingerprint="fp2",
        issued_at=now,
        expires_at=now + timedelta(hours=1)
    )
    assert token2.is_expired is False


def test_anonymous_token_quota_remaining():
    """Testa propriedade quota_remaining"""
    token = AnonymousToken(
        user_id="user1",
        fingerprint="fp1",
        issued_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        quota_limit=100,
        quota_used=30
    )

    assert token.quota_remaining == 70


def test_anonymous_token_quota_exceeded():
    """Testa propriedade quota_exceeded"""
    # Quota não excedida
    token1 = AnonymousToken(
        user_id="user1",
        fingerprint="fp1",
        issued_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        quota_limit=100,
        quota_used=50
    )
    assert token1.quota_exceeded is False

    # Quota excedida
    token2 = AnonymousToken(
        user_id="user2",
        fingerprint="fp2",
        issued_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        quota_limit=100,
        quota_used=100
    )
    assert token2.quota_exceeded is True


def test_anonymous_token_to_dict():
    """Testa conversão de token para dicionário"""
    now = datetime.now(timezone.utc)
    token = AnonymousToken(
        user_id="user1",
        fingerprint="fp1",
        issued_at=now,
        expires_at=now + timedelta(hours=1),
        quota_limit=100,
        quota_used=10
    )

    data = token.to_dict()

    assert data['user_id'] == "user1"
    assert data['fingerprint'] == "fp1"
    assert data['quota_limit'] == 100
    assert data['quota_used'] == 10
    assert 'issued_at' in data
    assert 'expires_at' in data


def test_refresh_token():
    """Testa renovação de token"""
    handler = JWTHandler(secret_key="test_secret")

    # Criar token inicial
    old_token = handler.create_token(fingerprint="test_fp")
    old_decoded = handler.verify_token(old_token)

    # Renovar token com quota atualizada
    new_token = handler.refresh_token(old_token, new_quota_used=25)
    new_decoded = handler.verify_token(new_token)

    assert new_token is not None
    assert new_decoded is not None
    assert new_decoded.user_id == old_decoded.user_id  # Mantém mesmo user_id
    assert new_decoded.fingerprint == old_decoded.fingerprint
    assert new_decoded.quota_used == 25  # Quota atualizada


def test_refresh_invalid_token():
    """Testa renovação de token inválido"""
    handler = JWTHandler(secret_key="test_secret")

    new_token = handler.refresh_token("invalid_token", new_quota_used=10)

    assert new_token is None


def test_generate_secret_key():
    """Testa geração automática de chave secreta"""
    handler = JWTHandler()  # Sem fornecer secret_key

    assert handler.secret_key is not None
    assert len(handler.secret_key) == 64  # 32 bytes em hex = 64 caracteres
