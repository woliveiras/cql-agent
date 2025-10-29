# 🎨 CQL Assistant - Frontend

Interface web moderna para o assistente de IA de reparos residenciais.

## 🛠️ Stack Tecnológica

- **Framework:** React + TypeScript
- **Build Tool:** Vite
- **Styling:** EmotionCSS
- **State Management:** Zustand
- **Data Fetching:** React Query (TanStack Query)
- **Forms:** React Hook Form
- **Routing:** React Router DOM
- **Testing:** Vitest + Testing Library + happy-dom
- **Code Quality:** Biome.js (linting + formatting)
- **Package Manager:** pnpm

## 🚀 Como Rodar

### Pré-requisitos

- Node.js 18+ ou 20+
- pnpm 10+
- Backend da API rodando (porta 5000)

### Instalação

```bash
# Instalar dependências
pnpm install

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com a URL da API (padrão: http://localhost:5000)
```

### Desenvolvimento

```bash
# Iniciar servidor de desenvolvimento (porta 5001)
pnpm dev

# A aplicação estará disponível em:
# http://localhost:5001
```

**⚠️ Importante:** Certifique-se de que o backend está rodando antes de iniciar o frontend!

### Build para Produção

```bash
# Criar build otimizado
pnpm build

# Preview do build de produção
pnpm preview
```

### Testes

```bash
# Executar testes (watch mode)
pnpm test

# Executar testes com UI
pnpm test:ui

# Gerar relatório de cobertura
pnpm test:coverage
```

### Qualidade de Código

```bash
# Verificar linting
pnpm lint

# Corrigir problemas automaticamente
pnpm lint:fix

# Formatar código
pnpm format
```

## 📁 Estrutura do Projeto

```text
web/
├── src/
│   ├── components/     # Componentes reutilizáveis
│   ├── containers/     # Componentes agregadores
│   ├── pages/          # Páginas da aplicação
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API clients e serviços
│   ├── store/          # Zustand stores
│   ├── styles/         # Theme e estilos globais
│   ├── config/         # Configurações (env, etc)
│   ├── lib/            # Utilitários e bibliotecas
│   └── test/           # Setup de testes
├── public/             # Arquivos estáticos
├── .env.example        # Exemplo de variáveis de ambiente
└── package.json
```

## 🔌 Integração com Backend

O frontend se conecta com a API REST através de:

### Configuração

Configure a URL da API no arquivo `.env`:

```bash
VITE_API_URL=http://localhost:5000
```

### Portas

- **Frontend:** http://localhost:5001
- **Backend:** http://localhost:5000

### Endpoints Utilizados

- `POST /chat/message` - Enviar mensagem ao assistente
- `GET /health` - Health check da API

### Services

- **chatService**: Gerencia comunicação com a API de chat
- **api**: Cliente Axios configurado com interceptors
- **React Query**: Cache e gerenciamento de estado assíncrono
- **Zustand**: Estado global (mensagens, conversationId, loading, erro)

### Fluxo de Dados

1. Usuário digita mensagem
2. Store Zustand adiciona mensagem do usuário
3. React Query envia requisição para API
4. API retorna resposta do Vicente
5. Store adiciona resposta às mensagens
6. UI atualiza automaticamente

## 🎨 Design System

O projeto utiliza um design system customizado inspirado em reparos residenciais:

- **Cores Primárias:** Vermelho (urgência/ação)
- **Cores Secundárias:** Cinza azulado (profissionalismo)
- **Tipografia:** System fonts otimizadas
- **Componentes:** Button, Input, Card, Avatar (customizados)

## 🔗 Integração com Backend

O frontend se conecta com a API REST do backend em:

- **Development:** `http://localhost:5000`
- **Production:** Configurável via variáveis de ambiente

## 📝 Convenções

### Componentes

- PascalCase para nomes
- Um componente por pasta
- Types em `types.ts`
- Testes em `*.test.tsx`

### Coverage

- Cobertura mínima: 80%
- Testar comportamento, não implementação
- Um arquivo de teste por componente

### Code Style

- Gerenciado pelo Biome.js

## 🤝 Contribuindo

1. Siga as convenções de código
2. Escreva testes para novas funcionalidades
3. Execute `pnpm lint` antes de commitar
4. Mantenha cobertura de testes > 80%
5. Abra pull requests descritivos
