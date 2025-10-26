"""
Handler de JWT para tokens anônimos
Gera e valida tokens JWT sem necessidade de login
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from dataclasses import dataclass

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError


@dataclass
class AnonymousToken:
    """
    Representa um token JWT anônimo

    Attributes:
        user_id: ID único do usuário anônimo (gerado automaticamente)
        fingerprint: Fingerprint do cliente
        issued_at: Timestamp de criação
        expires_at: Timestamp de expiração
        quota_limit: Limite de requests permitidos
        quota_used: Número de requests já utilizados
    """
    user_id: str
    fingerprint: str
    issued_at: datetime
    expires_at: datetime
    quota_limit: int = 100
    quota_used: int = 0

    @property
    def is_expired(self) -> bool:
        """Verifica se o token expirou"""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def quota_remaining(self) -> int:
        """Retorna o número de requests restantes"""
        return max(0, self.quota_limit - self.quota_used)

    @property
    def quota_exceeded(self) -> bool:
        """Verifica se a quota foi excedida"""
        return self.quota_used >= self.quota_limit

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'user_id': self.user_id,
            'fingerprint': self.fingerprint,
            'issued_at': self.issued_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'quota_limit': self.quota_limit,
            'quota_used': self.quota_used,
        }


class JWTHandler:
    """
    Handler para criação e validação de tokens JWT anônimos

    Example:
        >>> handler = JWTHandler()
        >>> token = handler.create_token(fingerprint="abc123")
        >>> decoded = handler.verify_token(token)
        >>> print(decoded.user_id)
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        token_expiration_hours: int = 24,
        quota_limit: int = 100
    ):
        """
        Inicializa o handler de JWT

        Args:
            secret_key: Chave secreta para assinar tokens (gerada automaticamente se não fornecida)
            algorithm: Algoritmo de assinatura (padrão: HS256)
            token_expiration_hours: Tempo de expiração em horas (padrão: 24h)
            quota_limit: Limite padrão de requests por token (padrão: 100)
        """
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY') or self._generate_secret_key()
        self.algorithm = algorithm
        self.token_expiration_hours = token_expiration_hours
        self.quota_limit = quota_limit

    def _generate_secret_key(self) -> str:
        """
        Gera uma chave secreta aleatória forte

        Returns:
            Chave secreta de 64 caracteres hexadecimais
        """
        return secrets.token_hex(32)

    def create_token(
        self,
        fingerprint: str,
        quota_limit: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Cria um novo token JWT anônimo

        Args:
            fingerprint: Fingerprint do cliente
            quota_limit: Limite customizado de requests (usa o padrão se não fornecido)
            user_id: ID customizado (gerado automaticamente se não fornecido)

        Returns:
            Token JWT assinado (string)

        Example:
            >>> handler = JWTHandler()
            >>> token = handler.create_token(fingerprint="abc123")
            >>> print(token)
            'eyJhbGciOiJIUzI1NiIs...'
        """
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=self.token_expiration_hours)

        # Gerar ID único se não fornecido
        if user_id is None:
            user_id = f"anon_{secrets.token_urlsafe(16)}"

        # Usar quota padrão se não fornecido
        if quota_limit is None:
            quota_limit = self.quota_limit

        # Payload do token
        payload = {
            'user_id': user_id,
            'fingerprint': fingerprint,
            'iat': now,
            'exp': expires,
            'quota_limit': quota_limit,
            'quota_used': 0,
            'type': 'anonymous'
        }

        # Assinar e retornar token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[AnonymousToken]:
        """
        Verifica e decodifica um token JWT

        Args:
            token: Token JWT a ser verificado

        Returns:
            Objeto AnonymousToken se válido, None se inválido

        Example:
            >>> handler = JWTHandler()
            >>> token = handler.create_token(fingerprint="abc123")
            >>> decoded = handler.verify_token(token)
            >>> print(decoded.user_id)
            'anon_...'
        """
        try:
            # Decodificar token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Verificar tipo de token
            if payload.get('type') != 'anonymous':
                return None

            # Converter timestamps
            issued_at = datetime.fromisoformat(payload['iat'].isoformat()) if isinstance(payload['iat'], datetime) else datetime.fromtimestamp(payload['iat'], tz=timezone.utc)
            expires_at = datetime.fromisoformat(payload['exp'].isoformat()) if isinstance(payload['exp'], datetime) else datetime.fromtimestamp(payload['exp'], tz=timezone.utc)

            # Criar objeto AnonymousToken
            return AnonymousToken(
                user_id=payload['user_id'],
                fingerprint=payload['fingerprint'],
                issued_at=issued_at,
                expires_at=expires_at,
                quota_limit=payload.get('quota_limit', self.quota_limit),
                quota_used=payload.get('quota_used', 0)
            )

        except ExpiredSignatureError:
            # Token expirado
            return None
        except InvalidTokenError:
            # Token inválido
            return None
        except Exception:
            # Erro inesperado
            return None

    def refresh_token(self, old_token: str, new_quota_used: int) -> Optional[str]:
        """
        Renova um token existente mantendo o user_id mas atualizando a quota

        Args:
            old_token: Token antigo
            new_quota_used: Novo valor de quota utilizada

        Returns:
            Novo token JWT ou None se o token antigo for inválido

        Example:
            >>> handler = JWTHandler()
            >>> old_token = handler.create_token(fingerprint="abc123")
            >>> new_token = handler.refresh_token(old_token, quota_used=10)
        """
        # Verificar token antigo
        decoded = self.verify_token(old_token)
        if not decoded:
            return None

        # Criar novo token com mesmos dados mas quota atualizada
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=self.token_expiration_hours)

        payload = {
            'user_id': decoded.user_id,
            'fingerprint': decoded.fingerprint,
            'iat': now,
            'exp': expires,
            'quota_limit': decoded.quota_limit,
            'quota_used': new_quota_used,
            'type': 'anonymous'
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
