"""
Middleware de autenticação e rate limiting para FastAPI
Integra fingerprinting, JWT e rate limiting de forma transparente
"""

import os
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.logging_config import get_logger
from .fingerprint import generate_fingerprint, get_client_info
from .jwt_handler import JWTHandler, AnonymousToken
from .rate_limiter import RateLimiter, RateLimitExceeded

# Configurar logger
logger = get_logger(__name__, component="auth_middleware")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticação híbrida (fingerprint + JWT anônimo) e rate limiting

    Fluxo:
    1. Extrai token JWT do header Authorization (se existir)
    2. Valida token e extrai informações do usuário
    3. Se não houver token válido, gera fingerprint
    4. Verifica rate limiting
    5. Adiciona informações de usuário ao request.state
    6. Gera novo token se necessário e adiciona no header de resposta

    Example:
        >>> app.add_middleware(AuthMiddleware, enabled=True)
    """

    def __init__(
        self,
        app,
        enabled: bool = True,
        rate_limit_enabled: bool = True,
        rate_limit: int = 100,
        rate_window: int = 3600,
        use_redis: bool = False,
        excluded_paths: Optional[list] = None
    ):
        """
        Inicializa o middleware

        Args:
            app: Aplicação FastAPI
            enabled: Se False, middleware não faz nada (útil para testes)
            rate_limit_enabled: Habilitar rate limiting
            rate_limit: Limite de requests por janela
            rate_window: Janela de tempo em segundos (3600 = 1 hora)
            use_redis: Usar Redis para rate limiting
            excluded_paths: Lista de paths que não aplicam rate limit
        """
        super().__init__(app)
        self.enabled = enabled
        self.rate_limit_enabled = rate_limit_enabled
        self.excluded_paths = excluded_paths or ['/health', '/docs', '/redoc', '/openapi.json']

        # Inicializar handlers
        self.jwt_handler = JWTHandler(
            token_expiration_hours=int(os.getenv('JWT_EXPIRATION_HOURS', '24')),
            quota_limit=rate_limit
        )

        if rate_limit_enabled:
            self.rate_limiter = RateLimiter(
                use_redis=use_redis,
                default_limit=rate_limit,
                default_window=rate_window
            )
        else:
            self.rate_limiter = None

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Processa cada request

        Args:
            request: Request do FastAPI
            call_next: Próxima função no pipeline

        Returns:
            Response
        """
        # Pular se middleware desabilitado ou path excluído
        if not self.enabled or request.url.path in self.excluded_paths:
            return await call_next(request)

        try:
            # 1. Extrair e validar token JWT (se existir)
            token_data = self._extract_token(request)
            fingerprint = generate_fingerprint(request)

            if token_data:
                # Validar token existente
                anonymous_token = self.jwt_handler.verify_token(token_data)
                if anonymous_token:
                    # Token válido: verificar se fingerprint bate (segurança)
                    if anonymous_token.fingerprint != fingerprint:
                        # Fingerprint mudou: gerar novo token
                        anonymous_token = None
                        new_token_needed = True
                    else:
                        new_token_needed = False
                else:
                    # Token inválido/expirado: gerar novo
                    new_token_needed = True
                    anonymous_token = None
            else:
                # Sem token: gerar novo
                new_token_needed = True
                anonymous_token = None

            # 2. Gerar novo token se necessário
            if new_token_needed:
                new_jwt = self.jwt_handler.create_token(fingerprint=fingerprint)
                anonymous_token = self.jwt_handler.verify_token(new_jwt)
            else:
                new_jwt = None

            # 3. Determinar identificador para rate limiting
            if anonymous_token:
                identifier = anonymous_token.user_id
            else:
                identifier = fingerprint

            # 4. Verificar rate limiting
            if self.rate_limit_enabled and self.rate_limiter:
                allowed, retry_after = self.rate_limiter.check_rate_limit(
                    identifier=identifier,
                    namespace="api"
                )

                if not allowed:
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            'error': 'Rate limit excedido',
                            'details': f'Você fez muitas requisições. Tente novamente em {retry_after} segundos.',
                            'retry_after': retry_after
                        },
                        headers={'Retry-After': str(retry_after)}
                    )

            # 5. Adicionar informações ao request.state
            request.state.user_id = anonymous_token.user_id if anonymous_token else identifier
            request.state.fingerprint = fingerprint
            request.state.anonymous_token = anonymous_token
            request.state.is_authenticated = anonymous_token is not None

            # Informações do cliente para logging
            request.state.client_info = get_client_info(request)

            # 6. Processar request
            response = await call_next(request)

            # 7. Adicionar token no header de resposta se novo
            if new_jwt:
                response.headers['X-Anonymous-Token'] = new_jwt

            # 8. Adicionar informações de rate limit nos headers
            if self.rate_limit_enabled and self.rate_limiter:
                usage = self.rate_limiter.get_usage(identifier, namespace="api")
                response.headers['X-RateLimit-Limit'] = str(usage['limit'])
                response.headers['X-RateLimit-Remaining'] = str(usage['requests_remaining'])
                response.headers['X-RateLimit-Reset'] = str(usage['window_size'])

            return response

        except Exception as e:
            # Log erro mas não bloqueia request (fail-open)
            logger.error(
                "Erro no AuthMiddleware",
                extra={
                    "error_type": type(e).__name__,
                    "error": str(e),
                    "path": request.url.path,
                    "event_type": "auth_middleware_error"
                },
                exc_info=True
            )
            return await call_next(request)

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extrai token JWT do header Authorization

        Args:
            request: Request do FastAPI

        Returns:
            Token JWT ou None se não existir

        Formatos suportados:
        - Authorization: Bearer <token>
        - Authorization: <token>
        """
        auth_header = request.headers.get('authorization')
        if not auth_header:
            return None

        # Remover prefixo "Bearer " se existir
        if auth_header.startswith('Bearer '):
            return auth_header[7:]

        return auth_header


# Dependency injection para obter usuário atual
async def get_current_user(request: Request) -> dict:
    """
    Dependency para obter informações do usuário atual

    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}

    Args:
        request: Request do FastAPI

    Returns:
        Dicionário com informações do usuário

    Raises:
        HTTPException: Se usuário não autenticado (não deve acontecer com middleware ativo)
    """
    if not hasattr(request.state, 'user_id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Não autenticado'
        )

    return {
        'user_id': request.state.user_id,
        'fingerprint': request.state.fingerprint,
        'is_authenticated': request.state.is_authenticated,
        'anonymous_token': request.state.anonymous_token,
        'client_info': request.state.client_info,
    }
