"""
Guardrails de conteúdo para validar a intenção do prompt
Verifica se a mensagem está relacionada ao domínio do agente (reparos residenciais)
"""

import re
import math
import logging
from typing import Dict, List, Optional, Tuple, Pattern
from collections import Counter
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)


class ContentGuardrailError(Exception):
    """Exceção levantada quando o conteúdo viola os guardrails"""
    pass


class ContentGuardrail:
    """
    Guardrail de conteúdo que valida se a mensagem é apropriada
    para o domínio de reparos residenciais
    
    Usa múltiplas estratégias de validação:
    1. Fuzzy matching para detectar typos em keywords
    2. NER (Named Entity Recognition) para extrair entidades
    3. Patterns de prompt injection
    4. Análise de entropia e repetição
    """

    # Configurações de validação de tamanho e entropia
    MIN_MESSAGE_LENGTH = 3          # Mensagens muito curtas (ex: "ok", "hi")
    MAX_MESSAGE_LENGTH = 2000       # Mensagens muito longas (possível DOS)
    MAX_ENTROPY = 5.0               # Entropia máxima (bits por caractere)
    MAX_NON_ALPHA_RATIO = 0.4       # 40% de caracteres não-alfabéticos

    # Configurações de detecção de repetição
    MAX_CHAR_REPETITION = 5         # Máximo de caracteres iguais consecutivos
    MAX_SEQUENCE_REPETITION = 3     # Máximo de sequências repetidas
    MIN_SEQUENCE_LENGTH = 3         # Tamanho mínimo de sequência para detectar

    # Configurações de fuzzy matching
    FUZZY_THRESHOLD = 85            # Limiar de similaridade (0-100)
    FUZZY_MAX_MATCHES = 3           # Máximo de matches por palavra

    # Palavras-chave relacionadas a reparos residenciais
    REPAIR_KEYWORDS = [
        # Estruturas
        "torneira", "pia", "cano", "encanamento", "vazamento", "tubulação",
        "chuveiro", "registro", "válvula", "sifão", "ralo", "esgoto",
        "porta", "janela", "fechadura", "dobradiça", "maçaneta", "trinco",
        "parede", "reboco", "massa", "pintura", "tinta", "rachadura", "fissura",
        "teto", "telhado", "telha", "calha", "goteira", "infiltração",
        "piso", "azulejo", "cerâmica", "rejunte", "ladrilho",

        # Elétrica
        "tomada", "interruptor", "luz", "lâmpada", "fiação", "disjuntor",
        "fusível", "eletricidade", "elétrico", "curto", "voltagem",

        # Móveis e objetos
        "gaveta", "armário", "prateleira", "móvel", "estante",

        # Ações
        "consertar", "reparar", "arrumar", "corrigir", "instalar", "trocar",
        "substituir", "fixar", "ajustar", "vedar", "calafetar", "desentupir",
        "limpar", "manutenção", "resolver", "problema", "quebrado", "defeito",

        # Geral
        "casa", "residencial", "doméstico", "lar", "apartamento",
        "reparo", "manutenção", "diy", "faça você mesmo"
    ]

    # Sistema de pesos para keywords (importância/urgência)
    KEYWORD_WEIGHTS = {
        # URGENTES (peso 3.0) - Situações de emergência ou alto risco
        "urgente": 3.0,
        "emergência": 3.0,
        "vazamento": 3.0,
        "fogo": 3.0,
        "gás": 3.0,
        "curto": 3.0,           # Curto-circuito
        "choque": 3.0,
        "incêndio": 3.0,
        "perigo": 3.0,
        "segurança": 3.0,
        
        # CRÍTICOS (peso 2.0) - Problemas graves que precisam atenção rápida
        "quebrado": 2.0,
        "entupido": 2.0,
        "infiltração": 2.0,
        "goteira": 2.0,
        "rachadura": 2.0,
        "fissura": 2.0,
        "defeito": 2.0,
        "danificado": 2.0,
        "travando": 2.0,
        "pingando": 2.0,
        "molhado": 2.0,
        "umidade": 2.0,
        
        # IMPORTANTES (peso 1.5) - Ações e problemas comuns
        "consertar": 1.5,
        "reparar": 1.5,
        "arrumar": 1.5,
        "trocar": 1.5,
        "substituir": 1.5,
        "instalar": 1.5,
        "problema": 1.5,
        "corrigir": 1.5,
        "ajustar": 1.5,
        "fixar": 1.5,
        "manutenção": 1.5,
        
        # CONTEXTUAIS (peso 1.0) - Termos descritivos/localização (padrão)
        # Todos os outros termos não listados acima têm peso 1.0
    }

    # Padrões de perguntas legítimas (serão compilados no __init__)
    QUESTION_PATTERNS_RAW = [
        r"\bcomo\s+(consertar|reparar|arrumar|resolver|instalar|trocar|fixar)",
        r"\bpor\s+que\s+(está|ta|ficou).+(quebrado|vazando|pingando|travando)",
        r"\bo\s+que\s+fazer\s+(quando|se|com)",
        r"\bpreciso\s+(consertar|reparar|arrumar|ajuda|resolver)",
        r"\btenho\s+(um\s+)?problema\s+(com|na|no)",
        r"\bestá\s+(quebrado|vazando|pingando|travando|entupido)",
        r"\b(dicas|tutorial|passo\s+a\s+passo|instruções)\s+(para|de)"
    ]

    # Tópicos proibidos (off-topic claro) (serão compilados no __init__)
    PROHIBITED_TOPICS_RAW = [
        # Conteúdo ilegal
        r"\b(bomb|weapon|gun|explosive|drug|hack|crack|pirat|steal|illegal)\b",

        # Conteúdo adulto/ofensivo
        r"\b(porn|xxx|sex|nude|naked|adult\s+content)\b",

        # Tentativas de jailbreak básicas
        r"ignore\s+(previous|all|above)\s+(instructions?|prompts?|commands?|rules?)",
        r"you\s+are\s+now\s+(a|an|acting|pretending)",
        r"forget\s+(everything|all|your|the)\s*(you|instructions?|rules?)?",
        r"new\s+(role|character|personality|identity|system)",
        r"disregard\s+(previous|all|above|the)\s*(instructions?|rules?)?",

        # Prompt injection avançada - comandos de sistema
        r"<\|.*?\|>",  # Tokens especiais do sistema
        r"\[SYSTEM\]|\[INST\]|\[/INST\]",  # Tags de instrução
        r"###\s*(System|Instruction|User|Assistant)",  # Markdown de sistema
        r"<start_of_turn>|<end_of_turn>",  # Delimitadores de turno

        # Tentativas de role manipulation
        r"(act|behave|pretend|play|roleplay)\s+(as|like)\s+(a|an)",
        r"from\s+now\s+on",
        r"switch\s+to\s+(mode|role|character)",
        r"override\s+(your|the)\s+(instructions?|rules?|programming)",

        # Tentativas de extrair informações do sistema
        r"(show|display|print|reveal|tell)\s+(me\s+)?(your|the)\s+(prompt|instructions?|system|rules?)",
        r"what\s+(are|is)\s+your\s+(instructions?|prompt|rules?|system\s+message)",
        r"repeat\s+(your|the)\s+(prompt|instructions?|system)",

        # Encoding attacks (base64, hex, etc)
        r"base64|decode|encode|hex|ascii|unicode|\\x[0-9a-f]{2}",
        r"eval\(|exec\(|system\(|shell\(",  # Code execution

        # Tentativas de bypass com separadores
        r"---+\s*(ignore|new|system|instruction)",
        r"\*\*\*+\s*(ignore|new|system|instruction)",
        r"===+\s*(ignore|new|system|instruction)",

        # Payload injection
        r";\s*(drop|delete|insert|update|select)\s+",  # SQL injection patterns
        r"\$\{|\{\{.*?\}\}",  # Template injection

        # Multi-language jailbreaking
        r"traduza|traduzir|translate|翻译",  # Bypass via translation

        # Tópicos completamente fora do escopo
        r"\b(crypto|bitcoin|invest|stock|trade|forex)\b",
        r"\b(recipe|cooking|food|meal)\b",
        r"\b(medical|doctor|disease|medication|surgery)\b",
        r"\b(legal|lawyer|lawsuit|court)\b"
    ]

    def __init__(
        self,
        strict_mode: bool = False,
        use_ner: bool = True
    ):
        """
        Inicializa o guardrail

        Args:
            strict_mode: Se True, aplica validação mais rigorosa
            use_ner: Se True, usa NER para análise de entidades (recomendado)
        """
        self.strict_mode = strict_mode
        self.use_ner = use_ner

        # Pré-compila todos os patterns regex para melhor performance
        self.question_patterns: List[Pattern] = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.QUESTION_PATTERNS_RAW
        ]

        self.prohibited_patterns: List[Pattern] = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.PROHIBITED_TOPICS_RAW
        ]

        # NER lazy loading (carrega apenas quando necessário)
        self._ner = None

        logger.info(
            f"ContentGuardrail initialized: strict_mode={strict_mode}, "
            f"use_ner={use_ner}, "
            f"question_patterns={len(self.question_patterns)}, "
            f"prohibited_patterns={len(self.prohibited_patterns)}"
        )

    @property
    def ner(self):
        """Lazy loading do NER (carrega apenas quando usado)"""
        if self.use_ner and self._ner is None:
            from api.security.ner_repair import get_repair_ner
            self._ner = get_repair_ner()
            logger.info("RepairNER loaded (lazy initialization)")
        return self._ner

    def _fuzzy_match_keywords(
        self,
        message: str,
        threshold: int = None
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Usa fuzzy matching para detectar keywords com typos ou variações

        Detecta palavras similares às keywords mesmo com erros de digitação:
        - "tornera" → "torneira" (typo comum)
        - "conserto" → "consertar" (variação)
        - "vaza mento" → "vazamento" (espaço extra)
        - "fechadra" → "fechadura" (troca de letras)

        Args:
            message: Mensagem a ser analisada
            threshold: Limiar de similaridade (0-100). Usa FUZZY_THRESHOLD se None

        Returns:
            (matched_keywords, corrections_map)
            - matched_keywords: Lista de keywords encontradas (originais)
            - corrections_map: Dict mapeando palavras do usuário para keywords {typo: correct}

        Examples:
            >>> guardrail._fuzzy_match_keywords("como consertar tornera pingando")
            (['torneira', 'consertar'], {'tornera': 'torneira'})
        """
        if threshold is None:
            threshold = self.FUZZY_THRESHOLD

        # Normaliza a mensagem
        message_lower = message.lower()
        words = re.findall(r'\b\w+\b', message_lower)

        matched_keywords = set()
        corrections_map = {}

        # Para cada palavra na mensagem
        for word in words:
            if len(word) < 3:  # Ignora palavras muito curtas
                continue

            # Verifica match exato primeiro (mais rápido)
            if word in self.REPAIR_KEYWORDS:
                matched_keywords.add(word)
                continue

            # Usa fuzzy matching para encontrar palavras similares
            matches = process.extract(
                word,
                self.REPAIR_KEYWORDS,
                scorer=fuzz.ratio,
                score_cutoff=threshold,
                limit=self.FUZZY_MAX_MATCHES
            )

            if matches:
                # Pega o melhor match
                best_match, score, _ = matches[0]
                matched_keywords.add(best_match)
                corrections_map[word] = best_match

                logger.debug(
                    f"Fuzzy match: '{word}' → '{best_match}' "
                    f"(score: {score})"
                )

        return list(matched_keywords), corrections_map

    def _calculate_entropy(self, message: str) -> float:
        """
        Calcula a entropia de Shannon do texto (bits por caractere)

        Entropia mede a "aleatoriedade" ou "imprevisibilidade" do texto.
        Valores típicos:
        - Texto normal em português: 3.0 - 4.5 bits/char
        - Texto aleatório/spam: > 5.0 bits/char
        - Payloads codificados: > 5.5 bits/char

        Returns:
            Entropia em bits por caractere
        """
        if not message:
            return 0.0

        # Conta a frequência de cada caractere
        char_counts = Counter(message)
        message_len = len(message)

        # Calcula a entropia de Shannon
        entropy = 0.0
        for count in char_counts.values():
            probability = count / message_len
            if probability > 0:
                entropy -= probability * math.log2(probability)

        logger.debug(f"Entropy calculated: {entropy:.2f} bits/char for message length {message_len}")
        return entropy

    def _validate_message_size_and_entropy(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Valida tamanho da mensagem e analisa entropia para detectar spam/payloads

        Verifica:
        - Tamanho mínimo e máximo
        - Entropia (aleatoriedade do texto)
        - Proporção de caracteres não-alfabéticos

        Returns:
            (is_valid, reason)
        """
        message_len = len(message)

        # 1. Valida tamanho mínimo
        if message_len < self.MIN_MESSAGE_LENGTH:
            logger.warning(f"Mensagem muito curta: {message_len} caracteres")
            return False, "Mensagem muito curta"

        # 2. Valida tamanho máximo (proteção contra DOS)
        if message_len > self.MAX_MESSAGE_LENGTH:
            logger.warning(f"Mensagem muito longa: {message_len} caracteres")
            return False, "Mensagem muito longa"

        # 3. Calcula e valida entropia
        entropy = self._calculate_entropy(message)
        if entropy > self.MAX_ENTROPY:
            logger.warning(f"Entropia muito alta: {entropy:.2f} bits/char (max: {self.MAX_ENTROPY})")
            return False, "Texto com padrão aleatório detectado"

        # 4. Valida proporção de caracteres não-alfabéticos
        alpha_count = sum(1 for char in message if char.isalpha())
        non_alpha_ratio = 1 - (alpha_count / message_len) if message_len > 0 else 0

        if non_alpha_ratio > self.MAX_NON_ALPHA_RATIO:
            logger.warning(
                f"Excesso de caracteres não-alfabéticos: {non_alpha_ratio:.2%} "
                f"(max: {self.MAX_NON_ALPHA_RATIO:.2%})"
            )
            return False, "Proporção suspeita de caracteres especiais"

        return True, None

    def _detect_character_repetition(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Detecta padrões suspeitos de repetição de caracteres
        Complexidade justificada: múltiplos padrões de ataque

        Verifica:
        - Caracteres iguais consecutivos (ex: "aaaaaaa", "!!!!!!!")
        - Sequências repetidas (ex: "abcabcabc", "123123123")
        - Padrões de spam/flooding

        Returns:
            (is_valid, reason)
        """
        if not message:
            return True, None

        # 1. Detecta caracteres consecutivos repetidos
        max_consecutive = 1
        current_char = message[0]
        current_count = 1

        for char in message[1:]:
            if char == current_char:
                current_count += 1
                max_consecutive = max(max_consecutive, current_count)
            else:
                current_char = char
                current_count = 1

        if max_consecutive > self.MAX_CHAR_REPETITION:
            logger.warning(
                f"Excesso de caracteres consecutivos: '{current_char}' repetido {max_consecutive} vezes"
            )
            return False, "Padrão de repetição excessiva detectado"

        # 2. Detecta sequências repetidas (padrão: substring repetida múltiplas vezes)
        message_len = len(message)

        # Testa diferentes tamanhos de sequência
        for seq_len in range(self.MIN_SEQUENCE_LENGTH, min(message_len // 2, 20)):
            # Extrai sequências possíveis
            sequences = {}
            for i in range(message_len - seq_len + 1):
                seq = message[i:i + seq_len]
                if seq in sequences:
                    sequences[seq] += 1
                else:
                    sequences[seq] = 1

            # Verifica se alguma sequência se repete demais
            for seq, count in sequences.items():
                # Ignora sequências de espaços ou caracteres únicos
                if len(set(seq.strip())) <= 1:
                    continue

                if count > self.MAX_SEQUENCE_REPETITION:
                    logger.warning(
                        f"Sequência repetida detectada: '{seq}' aparece {count} vezes"
                    )
                    return False, "Padrão de repetição suspeito detectado"

        return True, None

    def _detect_prompt_injection(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Detecta tentativas sofisticadas de prompt injection

        Analisa:
        - Delimitadores suspeitos (---, ***, ===, ||)
        - Caracteres especiais em excesso (>, <, {, }, [, ])
        - Padrões de encoding (base64-like, hex)
        - Tokens especiais do sistema
        - Comandos imperativos suspeitos

        Returns:
            (is_safe, reason)
        """
        # 1. Verifica excesso de delimitadores suspeitos
        delimiter_count = sum([
            message.count('---'),
            message.count('***'),
            message.count('==='),
            message.count('|||'),
            message.count('###')
        ])
        if delimiter_count >= 2:
            logger.warning(f"Excesso de delimitadores detectado: {delimiter_count}")
            return False, "Padrão suspeito de delimitadores detectado"

        # 2. Verifica excesso de caracteres especiais (possível payload)
        special_chars = '<>{}[]$|\\`'
        special_count = sum(1 for char in message if char in special_chars)
        if special_count > len(message) * 0.1:  # Mais de 10% são caracteres especiais
            logger.warning(f"Excesso de caracteres especiais: {special_count}/{len(message)}")
            return False, "Excesso de caracteres especiais detectado"

        # 3. Detecta sequências que parecem base64 longas
        # Base64 tem padrão: letras, números, +, /, = no final
        base64_pattern = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')
        if base64_pattern.search(message):
            logger.warning("Possível payload base64 detectado")
            return False, "Sequência codificada suspeita detectada"

        # 4. Detecta múltiplas quebras de linha (tentativa de injeção multi-linha)
        if message.count('\n') > 5:
            logger.warning(f"Excesso de quebras de linha: {message.count(chr(10))}")
            return False, "Formato de mensagem suspeito"

        # 5. Detecta comandos imperativos em sequência
        imperative_words = ['ignore', 'forget', 'disregard', 'override', 'bypass',
                            'skip', 'disable', 'remove', 'delete', 'change', 'modify']
        imperative_count = sum(1 for word in imperative_words if word in message.lower())
        if imperative_count >= 3:
            logger.warning(f"Múltiplos comandos imperativos: {imperative_count}")
            return False, "Múltiplos comandos de manipulação detectados"

        # 6. Detecta tentativas de fechar/abrir contextos
        context_markers = ['</system>', '<system>', '[/INST]', '[INST]',
                           '<|endoftext|>', '<|im_end|>', '<|im_start|>']
        if any(marker in message for marker in context_markers):
            logger.warning("Marcadores de contexto do sistema detectados")
            return False, "Tentativa de manipulação de contexto detectada"

        return True, None

    def _check_prohibited_content(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica se a mensagem contém conteúdo proibido usando patterns pré-compilados

        Returns:
            (is_valid, reason)
        """
        for pattern in self.prohibited_patterns:
            if pattern.search(message):
                logger.warning(f"Conteúdo proibido detectado: {pattern.pattern}")
                return False, "Conteúdo inapropriado ou fora do escopo"

        return True, None

    def _calculate_weighted_keyword_score(self, keywords: List[str]) -> float:
        """
        Calcula score ponderado baseado na importância das keywords
        
        Keywords urgentes (peso 3.0) contribuem mais que contextuais (peso 1.0).
        Score é normalizado para 0.0-1.0.
        
        Args:
            keywords: Lista de keywords encontradas
            
        Returns:
            Score normalizado de 0.0 a 1.0
        """
        if not keywords:
            return 0.0
        
        # Calcula soma ponderada
        total_weight = 0.0
        max_possible_weight = 0.0
        
        for keyword in keywords:
            # Pega peso da keyword (padrão 1.0 se não especificado)
            weight = self.KEYWORD_WEIGHTS.get(keyword, 1.0)
            total_weight += weight
            
            # Para normalização, assume peso máximo possível (3.0 urgente)
            max_possible_weight += 3.0
        
        # Normaliza para 0-1 (considera que 3 keywords urgentes = 1.0)
        # Ajusta para que 3 keywords de peso médio (1.5) ≈ 0.75
        normalized_score = min(total_weight / 9.0, 1.0)  # 9.0 = 3 keywords × peso 3.0
        
        logger.debug(
            f"Weighted keyword score: {normalized_score:.2f} "
            f"(total_weight: {total_weight:.1f}, keywords: {len(keywords)})"
        )
        
        return normalized_score

    def _check_repair_relevance(self, message: str) -> float:
        """
        Calcula score de relevância para reparos residenciais

        Usa múltiplas estratégias:
        1. NER (Named Entity Recognition) se habilitado - mais preciso
        2. Fuzzy matching para detectar keywords com typos - fallback
        3. Patterns de pergunta pré-compilados
        4. Score combinado ponderado

        Returns:
            Score de 0.0 a 1.0
        """
        # Estratégia 1: NER (mais inteligente, entende contexto)
        ner_score = 0.0
        has_repair_context = False
        
        if self.use_ner and self.ner:
            ner_summary = self.ner.get_entity_summary(message)
            ner_score = ner_summary["score"]
            has_repair_context = ner_summary["has_repair_context"]
            
            # Log entidades encontradas
            if ner_summary["entities"]:
                logger.info(
                    f"NER entities found: {ner_summary['entity_count']} total, "
                    f"primary: {ner_summary['primary_category']}, "
                    f"has_repair_context: {has_repair_context}"
                )
                logger.debug(f"NER entities detail: {ner_summary['entities']}")
        
        # Estratégia 2: Fuzzy matching (detecta typos) - SEMPRE executa
        matched_keywords, corrections = self._fuzzy_match_keywords(message)
        
        # Log das correções aplicadas
        if corrections:
            logger.info(f"Fuzzy corrections applied: {corrections}")

        # Estratégia 3: Verifica padrões de pergunta
        pattern_matches = sum(1 for pattern in self.question_patterns if pattern.search(message))

        # Estratégia 4: Calcula score ponderado de keywords
        keyword_score = self._calculate_weighted_keyword_score(matched_keywords)
        pattern_score = min(pattern_matches / 2, 1.0)  # Normaliza em 2 padrões

        # Estratégia 5: Combina scores de forma inteligente
        if self.use_ner and self.ner:
            # Se NER encontrou bom contexto, usa como base
            if has_repair_context:
                # Média ponderada: NER (70%), keywords (20%), patterns (10%)
                final_score = (ner_score * 0.7) + (keyword_score * 0.2) + (pattern_score * 0.1)
            else:
                # NER não encontrou contexto, dá mais peso ao fuzzy matching
                # Média ponderada: keywords (50%), NER (30%), patterns (20%)
                final_score = (keyword_score * 0.5) + (ner_score * 0.3) + (pattern_score * 0.2)
        else:
            # Sem NER: média ponderada keywords (70%) + patterns (30%)
            final_score = (keyword_score * 0.7) + (pattern_score * 0.3)

        logger.debug(
            f"Relevance score: {final_score:.2f} "
            f"(weighted_keywords: {keyword_score:.2f}, patterns: {pattern_matches}, "
            f"corrections: {len(corrections)}, ner_score: {ner_score:.2f})"
        )

        return final_score

    def validate(self, message: str) -> Dict[str, any]:
        """
        Valida se a mensagem é apropriada para o agente
        Complexidade justificada: validação em múltiplas camadas

        Args:
            message: Mensagem a ser validada

        Returns:
            Dict com:
                - is_valid: bool
                - reason: str (se inválido)
                - score: float (score de relevância)

        Raises:
            ContentGuardrailError: Se a validação falhar em modo strict
        """
        # 1. Valida tamanho e entropia
        is_valid, reason = self._validate_message_size_and_entropy(message)
        if not is_valid:
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": 0.0}

        # 2. Detecta repetição de caracteres
        is_valid, reason = self._detect_character_repetition(message)
        if not is_valid:
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": 0.0}

        # 3. Detecta prompt injection avançada
        is_safe, reason = self._detect_prompt_injection(message)
        if not is_safe:
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": 0.0}

        # 4. Verifica conteúdo proibido via patterns
        is_valid, reason = self._check_prohibited_content(message)
        if not is_valid:
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": 0.0}

        # 5. Calcula relevância
        relevance_score = self._check_repair_relevance(message)

        # 6. Decisão final
        # Em modo strict, exige score mínimo de 0.2
        # Em modo normal, exige score mínimo de 0.1
        min_score = 0.2 if self.strict_mode else 0.1

        if relevance_score < min_score:
            reason = "Mensagem não parece estar relacionada a reparos residenciais"
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": relevance_score}

        return {"is_valid": True, "reason": None, "score": relevance_score}
