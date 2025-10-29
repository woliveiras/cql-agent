import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  align-items: center;
`;

export const ChatContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
  max-width: 1200px;
`;

export const ErrorBanner = styled.div<{ theme?: Theme }>`
  padding: ${(props) => props.theme?.spacing.lg || '1.5rem'} ${(props) => props.theme?.spacing.xl || '2rem'};
  margin: ${(props) => props.theme?.spacing.lg || '1.5rem'} ${(props) => props.theme?.spacing.md || '1rem'} 0;
  background-color: ${(props) => props.theme?.colors.error.light || '#EF4444'};
  color: #FFFFFF;
  text-align: center;
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.medium || 500};
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  box-shadow: ${(props) => props.theme?.shadows.lg || '0 10px 15px -3px rgba(0, 0, 0, 0.1)'};
  animation: slideDown 0.3s ease-out;
  max-width: 900px;
  width: calc(100% - 2rem);
  margin-left: auto;
  margin-right: auto;

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding: ${(props) => props.theme?.spacing.md || '1rem'};
    font-size: ${(props) => props.theme?.typography.fontSize.sm || '0.875rem'};
    margin: ${(props) => props.theme?.spacing.md || '1rem'} ${(props) => props.theme?.spacing.sm || '0.5rem'} 0;
  }
`;

export const ErrorMessage = styled.span<{ theme?: Theme }>`
  flex: 1;
  text-align: center;
`;

export const CloseButton = styled.button<{ theme?: Theme }>`
  background: none;
  border: none;
  color: #FFFFFF;
  cursor: pointer;
  padding: ${(props) => props.theme?.spacing.xs || '0.25rem'};
  font-size: 1.25rem;
  line-height: 1;
  opacity: 0.8;
  transition: opacity ${(props) => props.theme?.transitions.fast || '0.15s'};

  &:hover {
    opacity: 1;
  }
`;

export const NewConsultationContainer = styled.div<{ theme?: Theme }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${(props) => props.theme?.spacing.xl || '2rem'};
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  background: ${(props) => props.theme?.colors.background.paper || '#F8FAFC'};
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  margin: ${(props) => props.theme?.spacing.md || '1rem'};
`;

export const NewConsultationText = styled.p<{ theme?: Theme }>`
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  text-align: center;
  margin: 0;
`;

export const NewConsultationButton = styled.button<{ theme?: Theme }>`
  padding: ${(props) => props.theme?.spacing.md || '1rem'} ${(props) => props.theme?.spacing.xl || '2rem'};
  background-color: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
  color: ${(props) => props.theme?.colors.primary.contrast || '#FFFFFF'};
  border: none;
  border-radius: ${(props) => props.theme?.borderRadius.md || '0.5rem'};
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.semibold || 600};
  cursor: pointer;
  transition: all ${(props) => props.theme?.transitions.normal || '0.25s'};
  box-shadow: ${(props) => props.theme?.shadows.md || '0 4px 6px -1px rgba(0, 0, 0, 0.1)'};

  &:hover {
    background-color: ${(props) => props.theme?.colors.primary.dark || '#B91C1C'};
    transform: translateY(-2px);
    box-shadow: ${(props) => props.theme?.shadows.lg || '0 10px 15px -3px rgba(0, 0, 0, 0.1)'};
  }

  &:active {
    transform: translateY(0);
  }
`;
