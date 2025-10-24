import { ButtonContainer, FeedbackButton } from './FeedbackButtons.styles';

interface FeedbackButtonsProps {
  onFeedback: (feedback: 'sim' | 'não') => void;
  disabled?: boolean;
}

export function FeedbackButtons({ onFeedback, disabled }: FeedbackButtonsProps) {
  return (
    <ButtonContainer>
      <FeedbackButton variant="yes" onClick={() => onFeedback('sim')} disabled={disabled}>
        ✓ Sim
      </FeedbackButton>
      <FeedbackButton variant="no" onClick={() => onFeedback('não')} disabled={disabled}>
        ✗ Não
      </FeedbackButton>
    </ButtonContainer>
  );
}
