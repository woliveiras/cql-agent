"""Script para gerar o arquivo FastAPI completo"""

# Parte 1: Imports e configuração inicial
part1 = '''"""
API FastAPI para o Agente de Reparos Residenciais
Fornece endpoints REST para integração com OpenWebUI e outros frontends
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timezone
import sys
import os

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.security.guardrails import ContentGuardrailError
from api.security.sanitizer import SanitizationError
from api.security import sanitize_input, ContentGuardrail
from agents import RepairAgent

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização do FastAPI
app = FastAPI(
    title="Repair Agent API",
    description="API para agente de IA especializado em reparos residenciais com RAG e busca web",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''

# Salvar o arquivo completo
with open('api/app.py', 'w', encoding='utf-8') as f:
    f.write(part1)

print("Arquivo FastAPI base criado: api/app.py")
