"""
title: Repair Agent
author: woliveiras
author_url: https://github.com/woliveiras
funding_url: https://github.com/woliveiras
version: 1.0.0
description: Agente de reparos residenciais com RAG, busca web e LLM local
"""

from typing import List, Union, Generator, Iterator
from pydantic import BaseModel, Field
import requests
import uuid


class Pipe:
    """
    Pipe para OpenWebUI
    Conecta o OpenWebUI ao Repair Agent via API REST
    """

    class Valves(BaseModel):
        API_BASE_URL: str = Field(
            default="http://api:5000/api/v1",
            description="URL base da API do Repair Agent"
        )
        USE_RAG: bool = Field(
            default=True,
            description="Habilitar busca em documentos (RAG)"
        )
        USE_WEB_SEARCH: bool = Field(
            default=True,
            description="Habilitar busca na internet"
        )
        SESSION_PREFIX: str = Field(
            default="openwebui",
            description="Prefixo das sessões"
        )
        TIMEOUT: int = Field(
            default=30,
            description="Timeout das requisições em segundos"
        )

    def __init__(self):
        self.valves = self.Valves()

    def pipes(self) -> List[dict]:
        """Retorna lista de modelos disponíveis"""
        return [
            {
                "id": "repair-agent-rag-web",
                "name": "Repair Agent (RAG + Web Search)"
            },
            {
                "id": "repair-agent-rag",
                "name": "Repair Agent (RAG Only)"
            },
            {
                "id": "repair-agent-base",
                "name": "Repair Agent (Base LLM)"
            }
        ]

    def pipe(self, body: dict) -> Union[str, Generator, Iterator]:
        """
        Função principal que processa mensagens
        Complexidade justificada: orquestração com múltiplos tratamentos de erro

        Args:
            body: Corpo da requisição do OpenWebUI (model, messages, user)

        Returns:
            Resposta do agente (string ou generator para streaming)
        """
        try:
            model_id = body.get("model", "")
            messages = body.get("messages", [])
            user_message = messages[-1]["content"] if messages else ""
            user_id = body.get("user", {}).get("id", "anonymous")

            # Ignorar tarefas automáticas do OpenWebUI (ex: "### Task: Suggest follow-up questions")
            if user_message.startswith("### Task:"):
                return ""

            # Gerar session_id único e persistente
            # Estratégia: Procurar por session_id nas mensagens do assistant, se não existir gerar novo UUID
            session_id = None

            # Procurar session_id em mensagens do assistant (padrão: [SESSÃO: uuid])
            for msg in messages:
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    if "[SESSÃO:" in content:
                        start = content.find("[SESSÃO:") + 9
                        end = content.find("]", start)
                        if end > start:
                            extracted_id = content[start:end].strip()
                            if extracted_id.startswith("openwebui-"):
                                session_id = extracted_id
                                break

            if not session_id:
                unique_id = str(uuid.uuid4())[:8]
                session_id = f"{self.valves.SESSION_PREFIX}-{unique_id}"
                is_new_session = True
            else:
                is_new_session = False

            print(f"[PIPE] Session: {session_id}, Msgs: {len(messages)}, User: {user_id}, Msg: {user_message[:40]}...")

            use_rag = "rag" in model_id.lower()
            use_web_search = "web" in model_id.lower()

            if model_id == "repair-agent-rag-web":
                use_rag = self.valves.USE_RAG
                use_web_search = self.valves.USE_WEB_SEARCH
            elif model_id == "repair-agent-rag":
                use_rag = True
                use_web_search = False
            elif model_id == "repair-agent-base":
                use_rag = False
                use_web_search = False

            api_url = f"{self.valves.API_BASE_URL}/chat/message"
            payload = {
                "message": user_message,
                "session_id": session_id,
                "use_rag": use_rag,
                "use_web_search": use_web_search
            }

            response = requests.post(
                api_url,
                json=payload,
                timeout=self.valves.TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            agent_response = data.get("response", "Desculpe, não consegui processar sua mensagem.")

            if is_new_session:
                agent_response = f"{agent_response}\n\n[SESSÃO: {session_id}]"

            print(f"[PIPE] Response received: {agent_response[:100]}...")

            state = data.get("state", "unknown")

            if body.get("debug", False):
                footer = f"\n\n---\n*Estado: {state} | RAG: {use_rag} | Web: {use_web_search}*"
                agent_response += footer

            return agent_response

        except requests.exceptions.Timeout:
            return "⚠️ Tempo esgotado ao conectar com o agente. Por favor, tente novamente."

        except requests.exceptions.ConnectionError:
            return f"❌ Não foi possível conectar à API do agente em {
                self.valves.API_BASE_URL}. Verifique se o serviço está rodando."

        except requests.exceptions.HTTPError as e:
            return f"❌ Erro na API do agente: {e.response.status_code} - {e.response.text}"

        except Exception as e:
            return f"❌ Erro inesperado: {str(e)}"


# Testes locais (não usado pelo OpenWebUI)
if __name__ == "__main__":
    print("🧪 Testando Pipe...")

    pipe = Pipe()

    print("\n📋 Modelos disponíveis:")
    for model in pipe.pipes():
        print(f"  - {model['name']} (id: {model['id']})")

    test_body = {
        "model": "repair-agent-rag-web",
        "user": {"id": "test-user"},
        "messages": [{"role": "user", "content": "Como consertar uma torneira pingando?"}]
    }

    print("\n🔄 Testando pipe()...")
    print(f"Modelo: {test_body['model']}")

    try:
        response = pipe.pipe(test_body)
        print(f"\n✅ Resposta:\n{response}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

    print("\n✅ Teste concluído!")
