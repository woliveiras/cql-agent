"""
API Flask para o Agente de Reparos Residenciais
Fornece endpoints REST para integração com OpenWebUI e outros frontends
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import RepairAgent

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para integração com frontends

# Configuração do Swagger/OpenAPI
api = Api(
    app,
    version='1.0',
    title='Repair Agent API',
    description='API para agente de IA especializado em reparos residenciais com RAG e busca web',
    doc='/docs',  # Documentação disponível em /docs
    prefix='/api/v1'
)

# Namespace para organização
ns = api.namespace('chat', description='Operações de conversação com o agente')

# Modelos Pydantic para validação
class ChatRequest(BaseModel):
    """Modelo de requisição de chat"""
    message: str = Field(..., min_length=1, max_length=2000, description="Mensagem do usuário")
    session_id: Optional[str] = Field(default="default", description="ID da sessão para manter contexto")
    use_rag: Optional[bool] = Field(default=True, description="Usar RAG (base de conhecimento)")
    use_web_search: Optional[bool] = Field(default=True, description="Usar busca web como fallback")

class ChatResponse(BaseModel):
    """Modelo de resposta de chat"""
    response: str = Field(..., description="Resposta do agente")
    session_id: str = Field(..., description="ID da sessão")
    state: str = Field(..., description="Estado atual da conversação")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")
    timestamp: str = Field(..., description="Timestamp da resposta")

# Modelos Flask-RESTX para documentação Swagger
chat_request_model = api.model('ChatRequest', {
    'message': fields.String(required=True, description='Mensagem do usuário', example='Como consertar uma torneira pingando?'),
    'session_id': fields.String(required=False, description='ID da sessão', example='user-123'),
    'use_rag': fields.Boolean(required=False, description='Usar RAG', default=True),
    'use_web_search': fields.Boolean(required=False, description='Usar busca web', default=True)
})

chat_response_model = api.model('ChatResponse', {
    'response': fields.String(description='Resposta do agente'),
    'session_id': fields.String(description='ID da sessão'),
    'state': fields.String(description='Estado da conversação'),
    'metadata': fields.Raw(description='Metadados adicionais'),
    'timestamp': fields.String(description='Timestamp ISO 8601')
})

error_model = api.model('Error', {
    'error': fields.String(description='Mensagem de erro'),
    'details': fields.String(description='Detalhes do erro')
})

# Armazenamento de sessões em memória (em produção, usar Redis ou similar)
sessions: Dict[str, RepairAgent] = {}

def get_or_create_agent(session_id: str, use_rag: bool = True, use_web_search: bool = True) -> RepairAgent:
    """Obtém ou cria um agente para a sessão"""
    if session_id not in sessions:
        logger.info(f"Criando novo agente para sessão: {session_id}")
        sessions[session_id] = RepairAgent(
            use_rag=use_rag,
            use_web_search=use_web_search
        )
    return sessions[session_id]

@ns.route('/message')
class ChatEndpoint(Resource):
    """Endpoint principal para conversação"""
    
    @ns.doc('send_message')
    @ns.expect(chat_request_model)
    @ns.response(200, 'Sucesso', chat_response_model)
    @ns.response(400, 'Requisição inválida', error_model)
    @ns.response(500, 'Erro interno', error_model)
    def post(self):
        """Envia uma mensagem para o agente"""
        try:
            # Validação com Pydantic
            data = ChatRequest(**request.json)
            
            # Obter ou criar agente para sessão
            agent = get_or_create_agent(
                data.session_id,
                data.use_rag,
                data.use_web_search
            )
            
            # Processar mensagem
            logger.info(f"Processando mensagem da sessão {data.session_id}: {data.message[:50]}...")
            response = agent.chat(data.message)
            
            # Preparar resposta
            chat_response = ChatResponse(
                response=response,
                session_id=data.session_id,
                state=agent.state.value,
                metadata={
                    "rag_enabled": data.use_rag,
                    "web_search_enabled": data.use_web_search,
                    "current_attempt": agent.current_attempt,
                    "max_attempts": agent.max_attempts
                },
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            logger.info(f"Resposta enviada para sessão {data.session_id}")
            return chat_response.model_dump(), 200
            
        except ValidationError as e:
            logger.error(f"Erro de validação: {e}")
            return {
                'error': 'Requisição inválida',
                'details': str(e)
            }, 400
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            return {
                'error': 'Erro interno do servidor',
                'details': str(e)
            }, 500

@ns.route('/reset/<string:session_id>')
class ResetEndpoint(Resource):
    """Endpoint para resetar sessão"""
    
    @ns.doc('reset_session')
    @ns.response(200, 'Sessão resetada com sucesso')
    @ns.response(404, 'Sessão não encontrada', error_model)
    def delete(self, session_id):
        """Reseta o estado de uma sessão"""
        try:
            if session_id in sessions:
                sessions[session_id].reset()
                logger.info(f"Sessão {session_id} resetada")
                return {'message': f'Sessão {session_id} resetada com sucesso'}, 200
            else:
                return {
                    'error': 'Sessão não encontrada',
                    'details': f'Sessão {session_id} não existe'
                }, 404
                
        except Exception as e:
            logger.error(f"Erro ao resetar sessão: {e}", exc_info=True)
            return {
                'error': 'Erro ao resetar sessão',
                'details': str(e)
            }, 500

@ns.route('/sessions')
class SessionsEndpoint(Resource):
    """Endpoint para listar sessões ativas"""
    
    @ns.doc('list_sessions')
    @ns.response(200, 'Lista de sessões ativas')
    def get(self):
        """Lista todas as sessões ativas"""
        try:
            session_list = [
                {
                    'session_id': sid,
                    'state': agent.state.value,
                    'current_attempt': agent.current_attempt
                }
                for sid, agent in sessions.items()
            ]
            return {
                'sessions': session_list,
                'total': len(session_list)
            }, 200
            
        except Exception as e:
            logger.error(f"Erro ao listar sessões: {e}", exc_info=True)
            return {
                'error': 'Erro ao listar sessões',
                'details': str(e)
            }, 500

# Endpoint de health check (fora do namespace para simplicidade)
@app.route('/health')
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'repair-agent-api',
        'version': '1.0.0',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200

# Nota: Flask-RESTX já cria uma rota '/' para a documentação Swagger
# Não precisamos criar outra rota para '/' pois causaria conflito

if __name__ == '__main__':
    logger.info("Iniciando Repair Agent API...")
    logger.info("Documentação disponível em: http://localhost:5000/docs")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
