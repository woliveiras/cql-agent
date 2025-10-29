"""
API FastAPI para o Agente de Reparos Residenciais
Fornece endpoints REST para integração com OpenWebUI e outros frontends
"""

import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Adicionar path para imports (deve vir antes dos imports locais)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, status, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402
from pydantic import BaseModel, Field, field_validator, ValidationError  # noqa: E402
from typing import Optional, Dict, Any, List  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
import time  # noqa: E402
import re  # noqa: E402

from api.logging_config import setup_logging, get_logger, LogContext  # noqa: E402
from api.session_manager import SessionManager  # noqa: E402
from api.security.guardrails import ContentGuardrailError  # noqa: E402
from api.security.sanitizer import SanitizationError  # noqa: E402
from api.security import sanitize_input, ContentGuardrail  # noqa: E402
from api.auth import AuthMiddleware  # noqa: E402
from agents import RepairAgent  # noqa: E402
import asyncio  # noqa: E402

# Configuração de logging estruturado
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    json_logs=os.getenv("JSON_LOGS", "false").lower() == "true"
)
logger = get_logger(__name__, component="api")

# Inicialização do FastAPI
app = FastAPI(
    title="CQL Assistant API",
    description="API para agente de IA especializado em reparos residenciais com RAG e busca web",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Middleware de Request Body Size Limit
@app.middleware("http")
async def limit_request_body_size(request: Request, call_next):
    """
    Limita o tamanho do corpo da requisição para prevenir ataques de DoS
    """
    max_size = int(os.getenv("MAX_REQUEST_BODY_SIZE", str(10 * 1024 * 1024)))  # 10MB padrão

    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")

        if content_length:
            content_length = int(content_length)
            if content_length > max_size:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Payload Too Large",
                        "detail": f"Request body too large. Maximum size: {max_size / 1024 / 1024:.1f}MB"
                    }
                )

    return await call_next(request)

# Middleware de Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Adiciona headers de segurança HTTP em todas as respostas
    """
    response = await call_next(request)

    # Previne clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Previne MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # XSS Protection (navegadores antigos)
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Força HTTPS (apenas em produção)
    if os.getenv("ENVIRONMENT") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content Security Policy
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Content-Security-Policy"] = csp_policy

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response

# Configuração CORS - Origens específicas baseadas no ambiente
def get_allowed_origins() -> list[str]:
    """Retorna lista de origens permitidas baseada no ambiente"""
    # Origens padrão de desenvolvimento
    dev_origins = [
        "http://localhost:5001",
        "http://127.0.0.1:5001",
        "http://localhost:5173",  # Frontend React (Vite)
        "http://127.0.0.1:5173",
    ]

    # Em produção, usar variável de ambiente
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        # Pegar origens da variável de ambiente (separadas por vírgula)
        prod_origins = os.getenv("CORS_ORIGINS", "")
        if prod_origins:
            return [origin.strip() for origin in prod_origins.split(",")]
        # Se não configurado, retornar lista vazia (bloqueará tudo)
        logger.warning("CORS_ORIGINS não configurado em produção!")
        return []

    # Em desenvolvimento, permitir origens locais
    return dev_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Anonymous-Token"],
    expose_headers=["X-Anonymous-Token", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Middleware de autenticação e rate limiting
# Configurável via variáveis de ambiente
auth_enabled = os.getenv("AUTH_ENABLED", "true").lower() == "true"
rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
rate_limit = int(os.getenv("RATE_LIMIT", "100"))
rate_window = int(os.getenv("RATE_WINDOW", "3600"))

if auth_enabled:
    logger.info(
        "Middleware de autenticação ativado",
        extra={
            "rate_limit_enabled": rate_limit_enabled,
            "rate_limit": rate_limit,
            "rate_window": rate_window,
            "use_redis": os.getenv("USE_REDIS", "false").lower() == "true"
        }
    )
    app.add_middleware(
        AuthMiddleware,
        enabled=True,
        rate_limit_enabled=rate_limit_enabled,
        rate_limit=rate_limit,
        rate_window=rate_window,
        use_redis=os.getenv("USE_REDIS", "false").lower() == "true",
        excluded_paths=["/health", "/docs", "/redoc", "/openapi.json", "/api/v1/openapi.json", "/"]
    )


# Modelos Pydantic


class ChatRequest(BaseModel):
    """Modelo de requisição de chat com validação rigorosa"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Mensagem do usuário (1-4096 caracteres)",
        examples=["Como consertar uma torneira pingando?"]
    )
    session_id: Optional[str] = Field(
        default="default",
        min_length=1,
        max_length=128,
        pattern=r'^[a-zA-Z0-9_\-]+$',
        description="ID da sessão (alfanumérico, _ e - permitidos)"
    )
    use_rag: Optional[bool] = Field(
        default=True,
        description="Usar RAG (base de conhecimento)"
    )
    use_web_search: Optional[bool] = Field(
        default=True,
        description="Usar busca web como fallback"
    )

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """
        Valida e sanitiza a mensagem do usuário

        Args:
            v: Mensagem a validar

        Returns:
            Mensagem sanitizada (trim de espaços)

        Raises:
            ValueError: Se a mensagem for inválida
        """
        # Remover espaços em branco no início e fim
        v = v.strip()

        # Verificar se não ficou vazia após trim
        if not v:
            raise ValueError('Mensagem não pode ser vazia ou conter apenas espaços')

        # Verificar se não contém apenas caracteres especiais
        if not re.search(r'[a-zA-Z0-9\u00C0-\u017F]', v):
            raise ValueError('Mensagem deve conter pelo menos letras ou números')

        # Verificar caracteres nulos (segurança)
        if '\x00' in v:
            raise ValueError('Mensagem contém caracteres inválidos (null bytes)')

        # Verificar excesso de caracteres repetidos (possível DoS)
        if re.search(r'(.)\1{49,}', v):  # 50+ caracteres repetidos
            raise ValueError('Mensagem contém caracteres repetidos excessivamente')

        # Verificar excesso de quebras de linha
        if v.count('\n') > 20:
            raise ValueError('Mensagem contém muitas quebras de linha')

        return v

    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v: Optional[str]) -> str:
        """
        Valida o session_id

        Args:
            v: Session ID a validar

        Returns:
            Session ID validado

        Raises:
            ValueError: Se o session_id for inválido
        """
        if v is None:
            return "default"

        v = v.strip()

        if not v:
            return "default"

        # Verificar tamanho mínimo
        if len(v) < 1:
            raise ValueError('Session ID muito curto')

        # Verificar padrão (já validado pelo Field pattern, mas reforçando)
        if not re.match(r'^[a-zA-Z0-9_\-]+$', v):
            raise ValueError('Session ID deve conter apenas letras, números, _ e -')

        # Verificar se não é uma tentativa de path traversal
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError('Session ID contém caracteres não permitidos')

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "message": "Como consertar uma torneira pingando?",
                "session_id": "user-123",
                "use_rag": True,
                "use_web_search": True
            }]
        }
    }


class ChatResponse(BaseModel):
    """Modelo de resposta de chat"""
    response: str = Field(..., description="Resposta do agente")
    session_id: str = Field(..., description="ID da sessão")
    state: str = Field(..., description="Estado atual da conversação")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")
    timestamp: str = Field(..., description="Timestamp da resposta")


class ErrorResponse(BaseModel):
    """Modelo de resposta de erro"""
    error: str = Field(..., description="Mensagem de erro")
    details: str = Field(..., description="Detalhes do erro")


class SessionInfo(BaseModel):
    """Informação de uma sessão"""
    session_id: str
    state: str
    current_attempt: int


class SessionsResponse(BaseModel):
    """Lista de sessões ativas"""
    sessions: List[SessionInfo]
    total: int


class HealthResponse(BaseModel):
    """Resposta do health check"""
    status: str
    service: str
    version: str
    timestamp: str


class MessageResponse(BaseModel):
    """Resposta de operação bem-sucedida"""
    message: str


# Inicialização do gerenciador de sessões
use_redis = os.getenv("USE_REDIS", "false").lower() == "true"
session_manager = SessionManager(use_redis=use_redis)

# Inicialização do Content Guardrail
content_guardrail = ContentGuardrail(strict_mode=False)


# Validação de configuração em produção
@app.on_event("startup")
async def validate_production_config():
    """Valida configurações obrigatórias em produção"""
    env = os.getenv("ENVIRONMENT", "development")

    logger.info(
        "Iniciando aplicação",
        extra={"environment": env, "use_redis": use_redis}
    )

    if env == "production":
        # Validar JWT_SECRET_KEY
        jwt_secret = os.getenv("JWT_SECRET_KEY", "")
        if not jwt_secret or len(jwt_secret) < 32:
            error_msg = (
                "JWT_SECRET_KEY obrigatório em produção (mínimo 32 caracteres)! "
                "Configure a variável de ambiente antes de iniciar."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Validar CORS_ORIGINS
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if not cors_origins:
            logger.warning(
                "CORS_ORIGINS não configurado em produção! "
                "Todas as origens serão bloqueadas."
            )

        # Validar que não está usando valores padrão inseguros
        if os.getenv("REDIS_PASSWORD", "") == "":
            logger.warning(
                "Redis sem senha em produção! "
                "Configure REDIS_PASSWORD para maior segurança."
            )

        logger.info("Validação de configuração de produção: OK")


# Exception Handlers Globais
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    with LogContext(path=request.url.path, event_type="unhandled_error"):
        logger.error(
            "Erro não tratado",
            exc_info=True,
            extra={"error_type": type(exc).__name__}
        )

    # Não expor detalhes em produção
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        detail = "Erro interno do servidor. Por favor, tente novamente mais tarde."
    else:
        detail = f"Erro: {str(exc)}"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro interno",
            "detail": detail
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação do Pydantic"""
    with LogContext(path=request.url.path, event_type="validation_error"):
        logger.warning(
            "Erro de validação",
            extra={
                "errors": exc.errors(),
                "body": str(exc.body)[:200]  # Limitar tamanho do log
            }
        )

    # Sanitizar mensagens de erro para não expor estrutura interna
    errors = []
    for error in exc.errors():
        field = " -> ".join([str(x) for x in error["loc"]])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Dados inválidos",
            "detail": "Verifique os campos e tente novamente.",
            "errors": errors
        }
    )


def get_or_create_agent(session_id: str, use_rag: bool = True, use_web_search: bool = True) -> RepairAgent:
    """Obtém ou cria um agente para a sessão"""
    return session_manager.get_or_create_agent(
        session_id=session_id,
        use_rag=use_rag,
        use_web_search=use_web_search
    )


# Endpoints
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check"
)
async def health_check():
    """Endpoint de health check"""
    return HealthResponse(
        status="healthy",
        service="repair-agent-api",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.post(
    "/api/v1/chat/message",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Enviar mensagem"
)
async def send_message(request: ChatRequest):
    """Envia uma mensagem para o agente"""
    try:
        # Sanitização
        try:
            sanitized_message = sanitize_input(request.message)
        except SanitizationError as e:
            logger.warning(
                "Sanitização falhou",
                extra={
                    "session_id": request.session_id,
                    "error": str(e),
                    "event_type": "sanitization_failed"
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': 'Entrada inválida',
                    'details': 'A mensagem contém caracteres ou padrões não permitidos'
                }
            )

        # Obter ou criar agente
        agent = get_or_create_agent(request.session_id, request.use_rag, request.use_web_search)

        # Validação para feedback
        if agent.state.value == "waiting_feedback":
            valid_feedback = ['sim', 's', 'yes', 'y', 'ok', 'não', 'nao', 'n', 'no', 'nope']
            message_lower = sanitized_message.lower().strip()
            is_valid_feedback = False
            word_count = len(message_lower.split())

            if message_lower in valid_feedback:
                is_valid_feedback = True
            elif word_count <= 10:
                feedback_keywords = ['sim', 'não', 'nao', 'yes', 'no']
                first_word = message_lower.split()[0] if message_lower else ''
                if first_word in feedback_keywords:
                    is_valid_feedback = True
                elif any(kw in message_lower for kw in feedback_keywords):
                    suspicious = ['ignore', 'system', 'admin', 'prompt', 'instruc', 'forget', 'esqueça']
                    if not any(susp in message_lower for susp in suspicious):
                        is_valid_feedback = True

            if not is_valid_feedback:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        'error': 'Resposta inválida',
                        'details': 'Por favor, responda apenas com "sim" ou "não". O problema foi resolvido?'
                    }
                )
            validation_result = {'is_valid': True, 'score': 1.0, 'reason': None}

        elif agent.state.value in ["max_attempts", "resolved"]:
            try:
                validation_result = content_guardrail.validate(sanitized_message)
                if not validation_result['is_valid']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            'error': 'Conteúdo não permitido',
                            'details': 'Sou um assistente especializado em reparos residenciais.'
                        }
                    )
            except ContentGuardrailError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={'error': 'Conteúdo não permitido', 'details': str(e)}
                )
        else:
            try:
                validation_result = content_guardrail.validate(sanitized_message)
                if not validation_result['is_valid']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            'error': 'Conteúdo não permitido',
                            'details': 'Sou um assistente especializado em reparos residenciais.'
                        }
                    )
            except ContentGuardrailError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={'error': 'Conteúdo não permitido', 'details': str(e)}
                )

        # Processar mensagem
        start_time = time.time()

        with LogContext(session_id=request.session_id, event_type="message_processing"):
            logger.info(
                "Processando mensagem",
                extra={
                    "message_length": len(sanitized_message),
                    "use_rag": request.use_rag,
                    "use_web_search": request.use_web_search,
                    "relevance_score": validation_result['score']
                }
            )

            # Timeout configurável (padrão: 60 segundos)
            timeout_seconds = int(os.getenv("LLM_TIMEOUT", "60"))

            try:
                # Executar agent.chat() com timeout usando asyncio.to_thread
                response = await asyncio.wait_for(
                    asyncio.to_thread(agent.chat, sanitized_message),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(
                    "Timeout ao processar mensagem",
                    extra={"timeout_seconds": timeout_seconds}
                )
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"Tempo limite excedido ({timeout_seconds}s). Por favor, tente novamente."
                )

            # Persistir mudanças de estado do agente
            session_manager.update_agent(request.session_id, agent)

            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(
                "Mensagem processada com sucesso",
                extra={
                    "state": agent.state.value,
                    "current_attempt": agent.current_attempt,
                    "duration_ms": duration_ms
                }
            )

        return ChatResponse(
            response=response,
            session_id=request.session_id,
            state=agent.state.value,
            metadata={
                "rag_enabled": request.use_rag,
                "web_search_enabled": request.use_web_search,
                "current_attempt": agent.current_attempt,
                "max_attempts": agent.max_attempts,
                "relevance_score": validation_result['score']
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Erro inesperado ao processar mensagem",
            extra={
                "session_id": request.session_id,
                "error_type": type(e).__name__,
                "error": str(e),
                "event_type": "error"
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={'error': 'Erro interno', 'details': str(e)}
        )


@app.delete("/api/v1/chat/reset/{session_id}", response_model=MessageResponse, tags=["Chat"])
async def reset_session(session_id: str):
    """Reseta uma sessão"""
    agent = session_manager.store.get(session_id)
    if agent:
        agent.reset()
        session_manager.update_agent(session_id, agent)
        return MessageResponse(message=f"Sessão {session_id} resetada")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={'error': 'Sessão não encontrada'}
    )


@app.get("/api/v1/chat/sessions", response_model=SessionsResponse, tags=["Chat"])
async def list_sessions():
    """Lista sessões ativas"""
    sessions_data = session_manager.list_sessions()
    session_list = [
        SessionInfo(
            session_id=s['session_id'],
            state=s['state'],
            current_attempt=s['current_attempt']
        )
        for s in sessions_data
    ]
    return SessionsResponse(sessions=session_list, total=len(session_list))


@app.get("/", include_in_schema=False)
async def root():
    """Rota raiz"""
    return JSONResponse(content={"message": "CQL Assistant API", "docs": "/docs"})


if __name__ == "__main__":
    import uvicorn
    logger.info(
        "Iniciando CQL Assistant API",
        extra={
            "event_type": "startup",
            "host": "0.0.0.0",
            "port": 5000,
            "reload": True
        }
    )
    uvicorn.run("api.app:app", host="0.0.0.0", port=5000, reload=True)
