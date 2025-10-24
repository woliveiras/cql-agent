"""
NER (Named Entity Recognition) customizado para domínio de reparos residenciais

Identifica e classifica entidades específicas em mensagens sobre reparos:

- FERRAMENTA: Objetos que podem ser consertados (torneira, porta, tomada)
- PROBLEMA: Descrições de defeitos (vazamento, quebrado, entupido)
- ACAO: Verbos relacionados a reparos (consertar, trocar, arrumar)
- COMODO: Cômodos da casa (banheiro, cozinha, sala)
- MATERIAL: Materiais de construção (cano, fio, parafuso)
"""

import spacy
from spacy.tokens import Span
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class RepairNER:
    """
    NER customizado para identificar entidades relacionadas a reparos residenciais
    
    Usa patterns baseados em dicionários para identificação rápida sem necessidade
    de treinamento de modelo (PhraseMatcher do spaCy).
    """
    
    # Categorias e suas entidades
    ENTITIES = {
        "FERRAMENTA": [
            # Hidráulica
            "torneira", "pia", "chuveiro", "vaso sanitário", "privada", 
            "descarga", "caixa d'água", "registro", "sifão", "ralo",
            
            # Elétrica
            "tomada", "interruptor", "lâmpada", "lustre", "disjuntor",
            "fusível", "chuveiro elétrico", "ventilador", "ar condicionado",
            
            # Estrutura
            "porta", "janela", "fechadura", "maçaneta", "dobradiça",
            "vidro", "veneziana", "persiana", "cortina",
            
            # Parede/Teto
            "parede", "teto", "rodapé", "moldura", "sanca",
            "gesso", "forro",
            
            # Piso
            "piso", "azulejo", "cerâmica", "porcelanato", "mármore",
            "granito", "tábua", "piso laminado",
            
            # Móveis
            "armário", "gaveta", "prateleira", "corrediça", "trilho",
        ],
        
        "PROBLEMA": [
            # Hidráulica
            "vazamento", "vazando", "pingando", "entupido", "entupimento",
            "goteira", "infiltração", "umidade", "mofo",
            
            # Elétrica
            "queimado", "curto", "faísca", "choque", "desligando",
            "piscando", "apagando",
            
            # Estrutura
            "quebrado", "rachadura", "fissura", "trinca", "descascando",
            "soltando", "caindo", "travando", "emperrado", "rangendo",
            "frouxo", "solto", "bambo",
            
            # Gerais
            "defeito", "problema", "danificado", "estragado", "ruim",
        ],
        
        "ACAO": [
            "consertar", "reparar", "arrumar", "corrigir", "resolver",
            "instalar", "trocar", "substituir", "mudar", "remover",
            "fixar", "ajustar", "apertar", "soltar", "desatarraxar",
            "vedar", "calafetar", "tapar", "fechar", "desentupir",
            "limpar", "lavar", "pintar", "reformar", "restaurar",
        ],
        
        "COMODO": [
            "banheiro", "cozinha", "sala", "quarto", "lavanderia",
            "área de serviço", "garagem", "quintal", "jardim", "varanda",
            "sacada", "corredor", "hall", "escritório", "despensa",
        ],
        
        "MATERIAL": [
            # Hidráulica
            "cano", "tubo", "encanamento", "tubulação", "mangueira",
            "vedante", "silicone", "veda rosca", "borracha", "o-ring",
            
            # Elétrica
            "fio", "cabo", "fiação", "benjamim", "extensão", "plug",
            
            # Construção
            "parafuso", "prego", "bucha", "cola", "massa corrida",
            "argamassa", "cimento", "reboco", "tinta", "verniz",
            "lixa", "selador", "primer",
        ],
    }
    
    def __init__(self):
        """Inicializa o NER com modelo spaCy em português"""
        try:
            # Carrega modelo pequeno de português
            self.nlp = spacy.load("pt_core_news_sm")
            logger.info("Modelo spaCy pt_core_news_sm carregado")
        except OSError:
            logger.warning("Modelo pt_core_news_sm não encontrado, usando blank")
            self.nlp = spacy.blank("pt")
        
        # Adiciona PhraseMatcher para cada categoria
        from spacy.matcher import PhraseMatcher
        self.matchers = {}
        
        for entity_type, terms in self.ENTITIES.items():
            matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
            patterns = [self.nlp.make_doc(term) for term in terms]
            matcher.add(entity_type, patterns)
            self.matchers[entity_type] = matcher
            
        logger.info(
            f"RepairNER initialized with {len(self.ENTITIES)} entity types, "
            f"total terms: {sum(len(terms) for terms in self.ENTITIES.values())}"
        )
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extrai entidades do texto
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Dict com listas de entidades por tipo:
            {
                "FERRAMENTA": ["torneira", "pia"],
                "PROBLEMA": ["vazando"],
                "ACAO": ["consertar"],
                ...
            }
        """
        doc = self.nlp(text.lower())
        entities = {entity_type: [] for entity_type in self.ENTITIES.keys()}
        
        # Para cada tipo de entidade, usa seu matcher
        for entity_type, matcher in self.matchers.items():
            matches = matcher(doc)
            for match_id, start, end in matches:
                span = doc[start:end]
                entity_text = span.text
                if entity_text not in entities[entity_type]:
                    entities[entity_type].append(entity_text)
        
        # Remove categorias vazias
        entities = {k: v for k, v in entities.items() if v}
        
        logger.debug(f"Extracted entities: {entities}")
        return entities
    
    def calculate_weighted_score(
        self,
        entities: Dict[str, List[str]],
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calcula score ponderado baseado nas entidades encontradas
        
        Args:
            entities: Dict de entidades extraídas
            weights: Pesos customizados por tipo (opcional)
            
        Returns:
            Score de 0.0 a 1.0
        """
        if weights is None:
            # Pesos padrão (FERRAMENTA e PROBLEMA são mais importantes)
            weights = {
                "FERRAMENTA": 2.0,  # Mais importante
                "PROBLEMA": 2.0,    # Mais importante
                "ACAO": 1.5,        # Importante
                "COMODO": 1.0,      # Contexto útil
                "MATERIAL": 1.0,    # Contexto útil
            }
        
        total_score = 0.0
        
        for entity_type, entity_list in entities.items():
            weight = weights.get(entity_type, 1.0)
            count = len(entity_list)
            total_score += min(count, 2) * weight  # Cap em 2 entidades por tipo
        
        # Normaliza para 0-1 baseado no cenário ideal (FERRAMENTA + PROBLEMA)
        # Score máximo = 2 FERRAMENTAs (2*2.0) + 2 PROBLEMAs (2*2.0) = 8.0
        ideal_max = 8.0
        normalized_score = min(total_score / ideal_max, 1.0)
        
        logger.debug(
            f"Weighted score: {normalized_score:.2f} "
            f"(raw: {total_score:.2f}, ideal_max: {ideal_max:.2f})"
        )
        
        return normalized_score
    
    def get_entity_summary(self, text: str) -> Dict:
        """
        Retorna um resumo completo das entidades no texto
        
        Returns:
            {
                "entities": Dict de entidades por tipo,
                "score": float (score ponderado),
                "has_repair_context": bool,
                "primary_category": str (categoria dominante)
            }
        """
        entities = self.extract_entities(text)
        score = self.calculate_weighted_score(entities)
        
        # Verifica se tem contexto de reparo (FERRAMENTA + PROBLEMA ou ACAO)
        has_repair_context = (
            ("FERRAMENTA" in entities and "PROBLEMA" in entities) or
            ("ACAO" in entities and "FERRAMENTA" in entities)
        )
        
        # Identifica categoria dominante
        primary_category = None
        if entities:
            primary_category = max(
                entities.keys(),
                key=lambda k: len(entities[k])
            )
        
        return {
            "entities": entities,
            "score": score,
            "has_repair_context": has_repair_context,
            "primary_category": primary_category,
            "entity_count": sum(len(v) for v in entities.values())
        }


# Singleton global (lazy initialization)
_repair_ner_instance = None


def get_repair_ner() -> RepairNER:
    """
    Retorna instância singleton do RepairNER
    
    Usa lazy initialization para evitar carregamento desnecessário do spaCy
    """
    global _repair_ner_instance
    if _repair_ner_instance is None:
        _repair_ner_instance = RepairNER()
    return _repair_ner_instance
