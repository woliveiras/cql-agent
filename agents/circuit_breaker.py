"""
Circuit Breaker Pattern Implementation
Protege o sistema contra falhas em cascata em serviços externos (LLM, Web Search, RAG)
"""

from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
import threading
from api.logging_config import get_logger

logger = get_logger(__name__, component="circuit_breaker")


class CircuitState(Enum):
    """Estados do Circuit Breaker"""
    CLOSED = "closed"  # Funcionando normalmente
    OPEN = "open"  # Circuito aberto (muitas falhas)
    HALF_OPEN = "half_open"  # Testando se pode fechar


class CircuitBreakerError(Exception):
    """Exceção lançada quando o circuit breaker está aberto"""
    pass


class CircuitBreaker:
    """
    Implementação do padrão Circuit Breaker

    O circuit breaker monitora falhas em chamadas a serviços externos.
    Quando muitas falhas ocorrem, ele "abre" o circuito e impede novas chamadas
    temporariamente, dando tempo para o serviço se recuperar.

    Estados:
    - CLOSED: Normal, chamadas passam
    - OPEN: Muitas falhas, chamadas são bloqueadas
    - HALF_OPEN: Testando se o serviço se recuperou
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        success_threshold: int = 2
    ):
        """
        Args:
            name: Nome do serviço protegido (para logs)
            failure_threshold: Número de falhas antes de abrir o circuito
            timeout_seconds: Tempo em segundos antes de tentar fechar novamente
            success_threshold: Sucessos necessários no HALF_OPEN para fechar
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None

        # Thread safety
        self._lock = threading.Lock()

        logger.info(
            f"Circuit breaker inicializado",
            extra={
                "service": name,
                "failure_threshold": failure_threshold,
                "timeout_seconds": timeout_seconds
            }
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa uma função protegida pelo circuit breaker

        Args:
            func: Função a ser executada
            *args: Argumentos posicionais da função
            **kwargs: Argumentos nomeados da função

        Returns:
            Resultado da função

        Raises:
            CircuitBreakerError: Se o circuito estiver aberto
            Exception: Qualquer exceção lançada pela função
        """
        with self._lock:
            # Se o circuito está aberto, verificar se deve tentar novamente
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info(f"Circuit breaker: tentando fechar", extra={"service": self.name})
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    # Ainda no período de timeout
                    logger.warning(
                        f"Circuit breaker: circuito aberto, bloqueando chamada",
                        extra={"service": self.name}
                    )
                    raise CircuitBreakerError(
                        f"Circuit breaker aberto para {self.name}. "
                        f"Tente novamente em alguns segundos."
                    )

        # Tentar executar a função
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Chamado quando uma execução é bem-sucedida"""
        with self._lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.debug(
                    f"Circuit breaker: sucesso em HALF_OPEN",
                    extra={
                        "service": self.name,
                        "success_count": self.success_count,
                        "threshold": self.success_threshold
                    }
                )

                if self.success_count >= self.success_threshold:
                    logger.info(f"Circuit breaker: fechando circuito", extra={"service": self.name})
                    self.state = CircuitState.CLOSED
                    self.success_count = 0

    def _on_failure(self):
        """Chamado quando uma execução falha"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            logger.warning(
                f"Circuit breaker: falha registrada",
                extra={
                    "service": self.name,
                    "failure_count": self.failure_count,
                    "threshold": self.failure_threshold
                }
            )

            if self.state == CircuitState.HALF_OPEN:
                # Se falhar em HALF_OPEN, volta para OPEN
                logger.warning(f"Circuit breaker: abrindo circuito novamente", extra={"service": self.name})
                self.state = CircuitState.OPEN
                self.failure_count = 0
                self.success_count = 0
            elif self.failure_count >= self.failure_threshold:
                # Muitas falhas, abrir circuito
                logger.error(
                    f"Circuit breaker: abrindo circuito (limite de falhas atingido)",
                    extra={"service": self.name}
                )
                self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar fechar o circuito"""
        if self.last_failure_time is None:
            return True

        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure >= timedelta(seconds=self.timeout_seconds)

    def reset(self):
        """Reseta o circuit breaker manualmente (para testes ou admin)"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            logger.info(f"Circuit breaker: resetado manualmente", extra={"service": self.name})

    @property
    def is_closed(self) -> bool:
        """Retorna True se o circuito está fechado (funcionando normalmente)"""
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Retorna True se o circuito está aberto (bloqueando chamadas)"""
        return self.state == CircuitState.OPEN

    def get_status(self) -> dict:
        """Retorna o status atual do circuit breaker"""
        with self._lock:
            return {
                "service": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
            }
