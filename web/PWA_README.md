# PWA - Progressive Web App

## 📱 Funcionalidades

### ✅ Funciona Offline
- O aplicativo continua funcionando mesmo sem conexão com a internet
- Assets estáticos (HTML, CSS, JS, imagens) são cacheados automaticamente
- Páginas já visitadas ficam disponíveis offline

### 📤 Fila de Mensagens Offline
- Mensagens enviadas enquanto offline são **automaticamente salvas** em uma fila
- Quando a conexão voltar, as mensagens são **sincronizadas automaticamente**
- IndexedDB é usado para armazenamento persistente e confiável
- Nenhuma mensagem é perdida!

### 🔄 Background Sync
- Sincronização automática em segundo plano quando voltar online
- Funciona mesmo se o aplicativo estiver fechado (em navegadores compatíveis)
- Retry automático em caso de falha

### 📲 Instalável
- Pode ser instalado na tela inicial do dispositivo
- Funciona como um app nativo
- Ícone próprio e splash screen
- Experiência standalone (sem barra de navegação do navegador)

### 🎯 Indicadores Visuais
- **OfflineIndicator**: mostra status da conexão (online/offline)
- **InstallPrompt**: prompt para instalar o PWA
- Contador de mensagens na fila
- Feedback visual quando mensagens são sincronizadas

---

## 🏗️ Arquitetura

### Service Worker
**Arquivo**: `public/service-worker.js`

O Service Worker intercepta todas as requisições e implementa diferentes estratégias:

#### 1. Cache First (Assets Estáticos)
```
Requisição → Cache → Se não tem → Network → Cachear
```
Usado para: HTML, CSS, JS, imagens, fonts

#### 2. Network First com Queue (Mensagens de Chat)
```
Requisição → Network → Se falhar → Adicionar à fila offline
```
Usado para: POST /api/v1/chat/message

#### 3. Network Only (Outras requisições)
```
Requisição → Network
```
Usado para: Outras APIs

### IndexedDB
O IndexedDB armazena as mensagens offline de forma persistente:

```javascript
Database: vicente-offline-queue
Store: messages
Schema: {
  timestamp: number (chave primária)
  url: string
  method: string
  headers: array
  body: string
}
```

### React Hook
**Arquivo**: `src/hooks/usePWA.ts`

Hook personalizado que gerencia todo o estado do PWA:

```typescript
const pwa = usePWA();

// Status
pwa.isOnline          // boolean - está online?
pwa.isInstalled       // boolean - app está instalado?
pwa.canInstall        // boolean - pode instalar?
pwa.queuedMessages    // number - mensagens na fila
pwa.swRegistration    // ServiceWorkerRegistration | null

// Métodos
pwa.install()         // Instalar PWA
pwa.clearQueue()      // Limpar fila manualmente
pwa.updateQueueStatus() // Atualizar contador
```

---

## 🚀 Como Funciona

### 1. Instalação do Service Worker
```typescript
// Automaticamente registrado no usePWA hook
navigator.serviceWorker.register('/service-worker.js')
```

### 2. Envio de Mensagem Offline
```mermaid
User → Chat Component → API POST
                         ↓
                    Network Falha
                         ↓
                Service Worker intercepta
                         ↓
                Salva no IndexedDB
                         ↓
                Retorna 202 Accepted
                         ↓
            UI mostra "mensagem enfileirada"
```

### 3. Sincronização quando Voltar Online
```mermaid
Network Online
    ↓
Background Sync triggered
    ↓
Service Worker processa fila
    ↓
Para cada mensagem:
  → Tenta enviar
  → Se sucesso: remove da fila
  → Se falha: mantém na fila
    ↓
Notifica cliente (UI)
```

---

## 📦 Estrutura de Arquivos

```
web/
├── public/
│   ├── manifest.json           # Configuração do PWA
│   ├── service-worker.js       # Service Worker
│   ├── offline.html            # Página offline
│   └── icons/                  # Ícones do app
│       ├── icon-72x72.png
│       ├── icon-96x96.png
│       ├── icon-128x128.png
│       ├── icon-144x144.png
│       ├── icon-152x152.png
│       ├── icon-192x192.png
│       ├── icon-384x384.png
│       └── icon-512x512.png
│
└── src/
    ├── hooks/
    │   └── usePWA.ts           # Hook React para PWA
    │
    └── components/
        ├── OfflineIndicator/   # Indicador de status
        │   ├── OfflineIndicator.tsx
        │   ├── OfflineIndicator.styles.ts
        │   └── index.ts
        │
        └── InstallPrompt/      # Prompt de instalação
            ├── InstallPrompt.tsx
            ├── InstallPrompt.styles.ts
            └── index.ts
```

---

## 🧪 Testando

### Testar Offline

#### Chrome DevTools
1. Abra DevTools (F12)
2. Aba **Application** → **Service Workers**
3. Marque "Offline"
4. Tente enviar mensagens - devem ser enfileiradas
5. Desmarque "Offline" - mensagens devem sincronizar

#### Network Tab
1. Abra DevTools (F12)
2. Aba **Network**
3. Dropdown do throttling → "Offline"
4. Teste o app

### Testar Instalação

#### Desktop (Chrome/Edge)
1. Ícone de instalação aparece na barra de endereços (➕)
2. Ou: Menu → "Instalar Vicente"
3. Ou: Prompt aparece automaticamente no rodapé

#### Mobile
1. Chrome: Menu → "Adicionar à tela inicial"
2. Safari: Botão de compartilhar → "Adicionar à tela de início"

### Verificar Cache
1. DevTools → Application → Cache Storage
2. Deve ver: `vicente-pwa-v1`
3. Expandir para ver assets cacheados

### Verificar Fila Offline
1. DevTools → Application → IndexedDB
2. Deve ver: `vicente-offline-queue`
3. Expandir → `messages` → Ver mensagens na fila

---

## 🔧 Configuração

### Manifest (manifest.json)
```json
{
  "name": "Vicente - Assistente de Reparos",
  "short_name": "Vicente",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#FFFFFF",
  "theme_color": "#DC2626"
}
```

### Vite Config (vite.config.ts)
```typescript
VitePWA({
  strategies: 'injectManifest',
  srcDir: 'public',
  filename: 'service-worker.js'
})
```

---

## 🎨 Ícones

### Gerando Ícones
Use ferramentas online para gerar todos os tamanhos:
- https://realfavicongenerator.net/
- https://www.pwabuilder.com/imageGenerator

### Tamanhos Necessários
- 72×72 (Android Chrome)
- 96×96 (Android Chrome)
- 128×128 (Android Chrome)
- 144×144 (iOS)
- 152×152 (iOS)
- 192×192 (Android, iOS)
- 384×384 (Android)
- 512×512 (Android, Splash)

### Formato
- PNG com fundo transparente ou sólido
- Purpose: `any maskable` (funciona em todos os devices)

---

## 📊 Compatibilidade

### Service Worker
✅ Chrome/Edge 40+
✅ Firefox 44+
✅ Safari 11.1+
✅ Opera 27+

### Background Sync
✅ Chrome/Edge 49+
⚠️ Firefox - Não suportado
⚠️ Safari - Não suportado
✅ Opera 36+

> **Nota**: Em navegadores sem Background Sync, a sincronização acontece quando o app é aberto novamente.

### IndexedDB
✅ Chrome/Edge 24+
✅ Firefox 16+
✅ Safari 10+
✅ Opera 15+

---

## 🐛 Troubleshooting

### Service Worker não registra
- Verificar console do navegador
- Certificar que está servindo via HTTPS (ou localhost)
- Limpar cache e recarregar

### Mensagens não sincronizam
- Verificar se IndexedDB tem as mensagens
- Console do Service Worker: `chrome://serviceworker-internals/`
- Tentar sync manual: `pwa.updateQueueStatus()`

### App não instala
- Verificar `manifest.json` está acessível
- Verificar todos os ícones existem
- Chrome requer HTTPS
- Verificar console para erros

### Cache não atualiza
- Incrementar `CACHE_VERSION` no service-worker.js
- Ou limpar manualmente: DevTools → Application → Clear Storage

---

## 🚀 Build para Produção

```bash
# Build
pnpm build

# Preview do build
pnpm preview

# Arquivos gerados em dist/
dist/
├── index.html
├── manifest.json
├── service-worker.js
├── offline.html
├── assets/
└── icons/
```

---

## 📚 Recursos

- [MDN - Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web.dev - PWA](https://web.dev/progressive-web-apps/)
- [Workbox](https://developers.google.com/web/tools/workbox)
- [Can I Use - Service Workers](https://caniuse.com/serviceworkers)
