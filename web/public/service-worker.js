/* eslint-disable no-restricted-globals */
/**
 * Service Worker para PWA com suporte offline
 * - Cache de assets estáticos
 * - Fila de mensagens offline
 * - Background Sync para envio quando voltar online
 */

const CACHE_VERSION = 'v1';
const CACHE_NAME = `vicente-pwa-${CACHE_VERSION}`;
const OFFLINE_QUEUE_DB = 'vicente-offline-queue';
const OFFLINE_QUEUE_STORE = 'messages';

// Assets para cache (estratégia Cache First)
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
];

// ============================================================================
// INSTALAÇÃO DO SERVICE WORKER
// ============================================================================

self.addEventListener('install', (event) => {
  console.log('[SW] Instalando service worker...');

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Cache aberto');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.error('[SW] Erro ao adicionar assets ao cache:', err);
        // Não falhar a instalação se alguns assets não carregarem
        return Promise.resolve();
      });
    })
  );

  // Ativar imediatamente sem esperar
  self.skipWaiting();
});

// ============================================================================
// ATIVAÇÃO DO SERVICE WORKER
// ============================================================================

self.addEventListener('activate', (event) => {
  console.log('[SW] Ativando service worker...');

  event.waitUntil(
    Promise.all([
      // Limpar caches antigos
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('[SW] Deletando cache antigo:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Tomar controle de todas as páginas imediatamente
      self.clients.claim(),
    ])
  );
});

// ============================================================================
// INTERCEPTAÇÃO DE REQUISIÇÕES (FETCH)
// ============================================================================

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignora requisições de extensões do navegador
  if (url.protocol === 'chrome-extension:' || url.protocol === 'moz-extension:') {
    return;
  }

  // Estratégia de cache baseada no tipo de requisição
  if (request.method === 'GET') {
    // GET: Cache First com fallback para network
    event.respondWith(cacheFirstStrategy(request));
  } else if (request.method === 'POST' && url.pathname.includes('/api/v1/chat/message')) {
    // POST para chat: Network First com fila offline
    event.respondWith(networkFirstWithQueue(request));
  } else {
    // Outras requisições: Network Only
    event.respondWith(fetch(request));
  }
});

/**
 * Estratégia Cache First
 * Tenta buscar do cache primeiro, se não encontrar busca da rede
 */
async function cacheFirstStrategy(request) {
  try {
    // Tentar buscar do cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('[SW] Servindo do cache:', request.url);
      return cachedResponse;
    }

    // Se não está no cache, buscar da rede
    const networkResponse = await fetch(request);

    // Cachear assets estáticos
    if (networkResponse.ok && shouldCache(request)) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('[SW] Erro em cacheFirstStrategy:', error);

    // Se falhar, tentar retornar página offline
    if (request.mode === 'navigate') {
      const offlineResponse = await caches.match('/offline.html');
      if (offlineResponse) {
        return offlineResponse;
      }
    }

    throw error;
  }
}

/**
 * Estratégia Network First com fila offline para mensagens de chat
 */
async function networkFirstWithQueue(request) {
  try {
    // Tentar enviar pela rede
    const networkResponse = await fetch(request.clone());

    if (networkResponse.ok) {
      console.log('[SW] Mensagem enviada com sucesso');
      return networkResponse;
    }

    throw new Error(`HTTP ${networkResponse.status}`);
  } catch (error) {
    console.warn('[SW] Falha ao enviar mensagem, adicionando à fila offline:', error);

    // Adicionar à fila offline
    await addToOfflineQueue(request);

    // Registrar background sync
    if ('sync' in self.registration) {
      await self.registration.sync.register('sync-offline-messages');
    }

    // Retornar resposta indicando que a mensagem foi enfileirada
    return new Response(
      JSON.stringify({
        queued: true,
        message: 'Mensagem salva. Será enviada quando a conexão voltar.',
      }),
      {
        status: 202, // Accepted
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}

/**
 * Verifica se a requisição deve ser cacheada
 */
function shouldCache(request) {
  const url = new URL(request.url);

  // Cachear apenas assets do próprio domínio
  if (url.origin !== self.location.origin) {
    return false;
  }

  // Cachear JS, CSS, fonts, imagens
  return /\.(js|css|woff2?|ttf|eot|svg|png|jpg|jpeg|gif|ico)$/.test(url.pathname);
}

// ============================================================================
// GERENCIAMENTO DA FILA OFFLINE (IndexedDB)
// ============================================================================

/**
 * Adiciona mensagem à fila offline usando IndexedDB
 */
async function addToOfflineQueue(request) {
  try {
    const body = await request.clone().text();
    const message = {
      url: request.url,
      method: request.method,
      headers: Array.from(request.headers.entries()),
      body: body,
      timestamp: Date.now(),
    };

    const db = await openDatabase();
    const tx = db.transaction(OFFLINE_QUEUE_STORE, 'readwrite');
    const store = tx.objectStore(OFFLINE_QUEUE_STORE);
    await store.add(message);

    console.log('[SW] Mensagem adicionada à fila offline:', message.timestamp);

    // Notificar cliente que mensagem foi enfileirada
    await notifyClients({ type: 'OFFLINE_MESSAGE_QUEUED', data: message });
  } catch (error) {
    console.error('[SW] Erro ao adicionar mensagem à fila offline:', error);
  }
}

/**
 * Processa fila offline quando voltar online
 */
async function processOfflineQueue() {
  try {
    const db = await openDatabase();
    const tx = db.transaction(OFFLINE_QUEUE_STORE, 'readonly');
    const store = tx.objectStore(OFFLINE_QUEUE_STORE);
    const messages = await store.getAll();

    if (messages.length === 0) {
      console.log('[SW] Fila offline vazia');
      return;
    }

    console.log(`[SW] Processando ${messages.length} mensagens da fila offline`);

    for (const message of messages) {
      try {
        // Recriar requisição
        const headers = new Headers(message.headers);
        const response = await fetch(message.url, {
          method: message.method,
          headers: headers,
          body: message.body,
        });

        if (response.ok) {
          console.log('[SW] Mensagem sincronizada com sucesso:', message.timestamp);

          // Remover da fila
          const deleteTx = db.transaction(OFFLINE_QUEUE_STORE, 'readwrite');
          const deleteStore = deleteTx.objectStore(OFFLINE_QUEUE_STORE);
          await deleteStore.delete(message.timestamp);

          // Notificar cliente
          await notifyClients({
            type: 'OFFLINE_MESSAGE_SYNCED',
            data: { timestamp: message.timestamp, response: await response.json() },
          });
        } else {
          console.warn('[SW] Falha ao sincronizar mensagem:', response.status);
        }
      } catch (error) {
        console.error('[SW] Erro ao processar mensagem da fila:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Erro ao processar fila offline:', error);
  }
}

/**
 * Abre ou cria banco IndexedDB para fila offline
 */
function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(OFFLINE_QUEUE_DB, 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(OFFLINE_QUEUE_STORE)) {
        db.createObjectStore(OFFLINE_QUEUE_STORE, { keyPath: 'timestamp' });
      }
    };
  });
}

/**
 * Notifica todos os clientes (páginas abertas)
 */
async function notifyClients(message) {
  const clients = await self.clients.matchAll({ type: 'window' });
  clients.forEach((client) => {
    client.postMessage(message);
  });
}

// ============================================================================
// BACKGROUND SYNC (quando voltar online)
// ============================================================================

self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync event:', event.tag);

  if (event.tag === 'sync-offline-messages') {
    event.waitUntil(
      processOfflineQueue()
        .then(() => {
          console.log('[SW] Fila offline processada com sucesso');
        })
        .catch((error) => {
          console.error('[SW] Erro ao processar fila offline:', error);
          // Falhar o sync para tentar novamente
          throw error;
        })
    );
  }
});

// ============================================================================
// MENSAGENS DO CLIENTE
// ============================================================================

self.addEventListener('message', (event) => {
  console.log('[SW] Mensagem recebida:', event.data);

  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data.type === 'GET_QUEUE_STATUS') {
    getQueueStatus().then((status) => {
      event.ports[0].postMessage(status);
    });
  }

  if (event.data.type === 'CLEAR_QUEUE') {
    clearQueue().then(() => {
      event.ports[0].postMessage({ success: true });
    });
  }
});

/**
 * Retorna status da fila offline
 */
async function getQueueStatus() {
  try {
    const db = await openDatabase();
    const tx = db.transaction(OFFLINE_QUEUE_STORE, 'readonly');
    const store = tx.objectStore(OFFLINE_QUEUE_STORE);
    const messages = await store.getAll();

    return {
      count: messages.length,
      messages: messages.map((m) => ({ timestamp: m.timestamp, url: m.url })),
    };
  } catch (error) {
    console.error('[SW] Erro ao obter status da fila:', error);
    return { count: 0, messages: [] };
  }
}

/**
 * Limpa toda a fila offline
 */
async function clearQueue() {
  try {
    const db = await openDatabase();
    const tx = db.transaction(OFFLINE_QUEUE_STORE, 'readwrite');
    const store = tx.objectStore(OFFLINE_QUEUE_STORE);
    await store.clear();
    console.log('[SW] Fila offline limpa');
  } catch (error) {
    console.error('[SW] Erro ao limpar fila:', error);
  }
}

console.log('[SW] Service Worker carregado');
