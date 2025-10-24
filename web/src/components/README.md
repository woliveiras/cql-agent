# Componentes

Esta pasta contém todos os componentes reutilizáveis da aplicação.

## Estrutura

Cada componente deve seguir esta estrutura:

```text
ComponentName/
├── index.tsx          # Componente principal
├── types.ts           # TypeScript types e interfaces
├── ComponentName.test.tsx  # Testes unitários
└── README.md          # Documentação (opcional)
```

## Convenções

### Nomenclatura

- Componentes: PascalCase (ex: `Button`, `ChatInput`)
- Arquivos: PascalCase para componentes, camelCase para utilities
- Types: PascalCase com sufixo Props quando aplicável (ex: `ButtonProps`)

### Types

- Todos os types devem estar em `types.ts`
- Exportar interfaces públicas
- Manter types privados quando possível

### Testes

- Arquivo na mesma pasta do componente
- Sufixo `.test.tsx`
- Testar comportamento, não implementação
- Cobertura mínima: 80%

### Documentação

- Props obrigatórias e opcionais
- Exemplos de uso
- Estados e variantes disponíveis

## Componentes Base

Componentes fundamentais do design system:

- `Button`: Botões com variantes (primary, secondary, ghost)
- `Input`: Campos de entrada de texto
- `Card`: Container com sombra e bordas arredondadas
- `Avatar`: Avatar circular para usuários/assistente
