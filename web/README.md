# 🎨 RepairChat - Frontend

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

### Instalação

```bash
# Instalar dependências
pnpm install
```

### Desenvolvimento

```bash
# Iniciar servidor de desenvolvimento (porta 5173)
pnpm dev

# A aplicação estará disponível em:
# http://localhost:5173
```

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
│   └── test/           # Setup de testes
├── public/             # Arquivos estáticos
└── package.json
```

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
