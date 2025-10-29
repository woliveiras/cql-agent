import { useEffect, useState } from 'react';
import { Container, Status, Icon, Text, QueueInfo } from './OfflineIndicator.styles';

interface OfflineIndicatorProps {
  isOnline: boolean;
  queuedMessages: number;
}

export function OfflineIndicator({ isOnline, queuedMessages }: OfflineIndicatorProps) {
  const [visible, setVisible] = useState(!isOnline);
  const [showQueue, setShowQueue] = useState(false);

  useEffect(() => {
    if (!isOnline) {
      setVisible(true);
    } else {
      // Quando voltar online, mostrar por mais 3 segundos
      setTimeout(() => setVisible(false), 3000);
    }
  }, [isOnline]);

  useEffect(() => {
    setShowQueue(queuedMessages > 0);
  }, [queuedMessages]);

  if (!visible && !showQueue) return null;

  return (
    <Container $isOnline={isOnline}>
      <Status>
        <Icon>{isOnline ? '✓' : '📡'}</Icon>
        <Text>{isOnline ? 'Conectado' : 'Sem conexão'}</Text>
      </Status>

      {showQueue && (
        <QueueInfo>
          {queuedMessages} mensage{queuedMessages === 1 ? 'm' : 'ns'} aguardando envio
        </QueueInfo>
      )}
    </Container>
  );
}

export default OfflineIndicator;
