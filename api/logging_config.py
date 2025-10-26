"""
Configuração de logging estruturado em JSON para o CQL Agent

Este módulo fornece configuração centralizada de logging com suporte a:
- Logs estruturados em formato JSON para produção
- Logs legíveis para desenvolvimento
- Contexto adicional (session_id, request_id, component, etc.)
- Diferentes níveis de log por ambiente
"""

import logging
import sys
import os
from typing import Optional, Dict, Any

try:
    # Novo caminho (python-json-logger >= 3.0)
    from pythonjsonlogger.json import JsonFormatter
except ImportError:
    # Caminho antigo (python-json-logger < 3.0)
    from pythonjsonlogger import jsonlogger
    JsonFormatter = jsonlogger.JsonFormatter


class CustomJsonFormatter(JsonFormatter):
    """
    Formatter customizado para logs em JSON com campos adicionais

    Adiciona automaticamente campos úteis para rastreamento:
    - timestamp: ISO 8601 timestamp
    - level: Nível do log (INFO, ERROR, etc.)
    - logger: Nome do logger
    - module: Módulo que gerou o log
    - function: Função que gerou o log
    - line: Linha do código
    """

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """
        Adiciona campos customizados ao log record

        Args:
            log_record: Dicionário do log que será serializado
            record: LogRecord original do Python
            message_dict: Dicionário com campos extras da mensagem
        """
        super().add_fields(log_record, record, message_dict)

        # Campos padrão sempre presentes
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno

        # Lista de campos conhecidos que devemos buscar
        known_fields = [
            'session_id', 'request_id', 'user_id', 'component',
            'event_type', 'duration_ms', 'error', 'error_type',
            'message_length', 'use_rag', 'use_web_search',
            'relevance_score', 'state', 'current_attempt'
        ]

        # Adicionar campos extras conhecidos se existirem
        for field in known_fields:
            if hasattr(record, field):
                log_record[field] = getattr(record, field)

        # Adicionar quaisquer outros campos extras do message_dict
        for key, value in message_dict.items():
            if key not in log_record and key not in ['message', 'exc_info', 'stack_info', 'extra']:
                log_record[key] = value


def setup_logging(
    level: str = "INFO",
    json_logs: bool = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configura o sistema de logging da aplicação

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Se True, usa JSON. Se None, detecta automaticamente
                  (JSON em produção, texto em desenvolvimento)
        log_file: Caminho opcional para arquivo de log

    Examples:
        >>> setup_logging(level="INFO", json_logs=True)
        >>> setup_logging(level="DEBUG", json_logs=False, log_file="app.log")
    """
    # Detectar ambiente
    env = os.getenv("ENVIRONMENT", "development")

    # Se json_logs não foi especificado, detectar automaticamente
    if json_logs is None:
        json_logs = env == "production"

    # Converter string de level para constante
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configurar handlers
    handlers = []

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if json_logs:
        # Formato JSON para produção
        json_formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(logger)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Formato legível para desenvolvimento
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

    handlers.append(console_handler)

    # Handler para arquivo (opcional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)

        # Sempre usar JSON em arquivo
        json_formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(logger)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        file_handler.setFormatter(json_formatter)
        handlers.append(file_handler)

    # Configurar logging root
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True  # Força reconfiguração mesmo se já configurado
    )

    # Silenciar logs verbosos de bibliotecas externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    LoggerAdapter customizado que mescla extras do adapter com extras da chamada

    Garante que tanto o contexto padrão (component) quanto os extras
    passados em cada chamada de log sejam incluídos no log record.
    """

    def process(self, msg, kwargs):
        """
        Processa a mensagem e kwargs, mesclando extras
        """
        # Mesclar extras do adapter com extras da chamada
        extra = self.extra.copy()
        if 'extra' in kwargs:
            extra.update(kwargs['extra'])

        # Atualizar kwargs com extras mesclados
        kwargs['extra'] = extra

        return msg, kwargs


def get_logger(name: str, component: Optional[str] = None) -> ContextLoggerAdapter:
    """
    Retorna um logger com contexto adicional

    Args:
        name: Nome do logger (geralmente __name__)
        component: Componente da aplicação (api, agent, rag, security, etc.)

    Returns:
        ContextLoggerAdapter com contexto adicional

    Examples:
        >>> logger = get_logger(__name__, component="api")
        >>> logger.info("Processando request", extra={"session_id": "123"})
    """
    logger = logging.getLogger(name)

    # Adicionar contexto padrão
    extra = {}
    if component:
        extra['component'] = component

    return ContextLoggerAdapter(logger, extra)


class LogContext:
    """
    Context manager para adicionar contexto temporário aos logs

    Examples:
        >>> with LogContext(session_id="123", request_id="abc"):
        ...     logger.info("Processing request")
        # Log terá session_id e request_id automaticamente
    """

    def __init__(self, **context):
        """
        Args:
            **context: Campos de contexto (session_id, request_id, etc.)
        """
        self.context = context
        self.old_factory = None

    def __enter__(self):
        """Ativa o contexto"""
        self.old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Desativa o contexto"""
        logging.setLogRecordFactory(self.old_factory)


# Exemplo de uso
if __name__ == "__main__":
    # Desenvolvimento (logs legíveis)
    setup_logging(level="DEBUG", json_logs=False)
    logger = get_logger(__name__, component="example")

    logger.info("Mensagem simples")
    logger.info("Mensagem com contexto", extra={"session_id": "123", "user_id": "user-1"})

    with LogContext(request_id="req-456"):
        logger.info("Dentro do contexto")

    # Produção (logs JSON)
    print("\n--- JSON Logs ---\n")
    setup_logging(level="INFO", json_logs=True)
    logger = get_logger(__name__, component="api")

    logger.info("Request recebido", extra={
        "session_id": "session-123",
        "event_type": "request",
        "duration_ms": 150
    })
