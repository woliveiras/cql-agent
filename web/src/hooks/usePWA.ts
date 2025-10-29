import { useEffect, useState } from 'react';

interface PWAStatus {
  isOnline: boolean;
  isInstalled: boolean;
  canInstall: boolean;
  queuedMessages: number;
  swRegistration: ServiceWorkerRegistration | null;
}

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export function usePWA() {
  const [status, setStatus] = useState<PWAStatus>({
    isOnline: navigator.onLine,
    isInstalled: false,
    canInstall: false,
    queuedMessages: 0,
    swRegistration: null,
  });

  const [installPrompt, setInstallPrompt] =
    useState<BeforeInstallPromptEvent | null>(null);

  // Registra Service Worker
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      registerServiceWorker();
    }
  }, []);

  // Monitora status online/offline
  useEffect(() => {
    const handleOnline = () => {
      console.log('[PWA] Voltou online');
      setStatus((prev) => ({ ...prev, isOnline: true }));

      // Trigger sync manualmente se Background Sync não estiver disponível
      if (status.swRegistration && !('sync' in status.swRegistration)) {
        console.log('[PWA] Background Sync não disponível, sincronizando manualmente');
        status.swRegistration.active?.postMessage({ type: 'SYNC_NOW' });
      }
    };

    const handleOffline = () => {
      console.log('[PWA] Ficou offline');
      setStatus((prev) => ({ ...prev, isOnline: false }));
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [status.swRegistration]);

  // Listener para prompt de instalação
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      const promptEvent = e as BeforeInstallPromptEvent;
      setInstallPrompt(promptEvent);
      setStatus((prev) => ({ ...prev, canInstall: true }));
      console.log('[PWA] Prompt de instalação capturado');
    };

    const handleAppInstalled = () => {
      setStatus((prev) => ({ ...prev, isInstalled: true, canInstall: false }));
      setInstallPrompt(null);
      console.log('[PWA] App instalado');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    // Verificar se já está instalado
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setStatus((prev) => ({ ...prev, isInstalled: true }));
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Mensagens do Service Worker
  useEffect(() => {
    if (!('serviceWorker' in navigator)) return;

    const handleMessage = (event: MessageEvent) => {
      console.log('[PWA] Mensagem do SW:', event.data);

      if (event.data.type === 'OFFLINE_MESSAGE_QUEUED') {
        updateQueueStatus();
      }

      if (event.data.type === 'OFFLINE_MESSAGE_SYNCED') {
        updateQueueStatus();
        // Você pode adicionar um toast/notificação aqui
        console.log('[PWA] Mensagem sincronizada:', event.data.data);
      }
    };

    navigator.serviceWorker.addEventListener('message', handleMessage);

    return () => {
      navigator.serviceWorker.removeEventListener('message', handleMessage);
    };
  }, []);

  // Atualiza status da fila
  const updateQueueStatus = async () => {
    if (!status.swRegistration) return;

    try {
      const channel = new MessageChannel();

      const promise = new Promise<{ count: number }>((resolve) => {
        channel.port1.onmessage = (event) => {
          resolve(event.data);
        };
      });

      status.swRegistration.active?.postMessage(
        { type: 'GET_QUEUE_STATUS' },
        [channel.port2]
      );

      const queueStatus = await promise;
      setStatus((prev) => ({ ...prev, queuedMessages: queueStatus.count }));
    } catch (error) {
      console.error('[PWA] Erro ao obter status da fila:', error);
    }
  };

  // Registra Service Worker
  const registerServiceWorker = async () => {
    try {
      const registration = await navigator.serviceWorker.register(
        '/service-worker.js',
        { scope: '/' }
      );

      console.log('[PWA] Service Worker registrado:', registration.scope);

      setStatus((prev) => ({ ...prev, swRegistration: registration }));

      // Atualizar service worker se houver novo
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        console.log('[PWA] Nova versão do Service Worker encontrada');

        newWorker?.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            console.log('[PWA] Nova versão disponível, por favor recarregue a página');
            // Você pode mostrar uma notificação aqui
          }
        });
      });

      // Atualizar status da fila
      updateQueueStatus();
    } catch (error) {
      console.error('[PWA] Erro ao registrar Service Worker:', error);
    }
  };

  // Instalar PWA
  const install = async () => {
    if (!installPrompt) {
      console.warn('[PWA] Prompt de instalação não disponível');
      return false;
    }

    try {
      await installPrompt.prompt();
      const choiceResult = await installPrompt.userChoice;

      if (choiceResult.outcome === 'accepted') {
        console.log('[PWA] Usuário aceitou instalação');
        setInstallPrompt(null);
        setStatus((prev) => ({ ...prev, canInstall: false }));
        return true;
      } else {
        console.log('[PWA] Usuário recusou instalação');
        return false;
      }
    } catch (error) {
      console.error('[PWA] Erro ao instalar:', error);
      return false;
    }
  };

  // Limpar fila manualmente
  const clearQueue = async () => {
    if (!status.swRegistration) return;

    try {
      const channel = new MessageChannel();

      const promise = new Promise<{ success: boolean }>((resolve) => {
        channel.port1.onmessage = (event) => {
          resolve(event.data);
        };
      });

      status.swRegistration.active?.postMessage(
        { type: 'CLEAR_QUEUE' },
        [channel.port2]
      );

      await promise;
      setStatus((prev) => ({ ...prev, queuedMessages: 0 }));
      console.log('[PWA] Fila limpa');
    } catch (error) {
      console.error('[PWA] Erro ao limpar fila:', error);
    }
  };

  return {
    ...status,
    install,
    clearQueue,
    updateQueueStatus,
  };
}
