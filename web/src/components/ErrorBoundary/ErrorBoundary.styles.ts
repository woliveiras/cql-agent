import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const ErrorContainer = styled.div<{ theme?: Theme }>`
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: ${(props) => props.theme?.spacing.xl || '2rem'};
  background: ${(props) => props.theme?.colors.background.default || '#FFFFFF'};
`;

export const ErrorContent = styled.div`
  max-width: 600px;
  width: 100%;
  text-align: center;
`;

export const ErrorTitle = styled.h1<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize['3xl'] || '1.875rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.bold || 700};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  margin-bottom: ${(props) => props.theme?.spacing.md || '1rem'};
`;

export const ErrorMessage = styled.p<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.lg || '1.125rem'};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
  line-height: ${(props) => props.theme?.typography.lineHeight.relaxed || 1.75};
  margin-bottom: ${(props) => props.theme?.spacing.xl || '2rem'};
`;

export const ErrorDetails = styled.details<{ theme?: Theme }>`
  text-align: left;
  background: ${(props) => props.theme?.colors.background.paper || '#F8FAFC'};
  border: 1px solid ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'};
  border-radius: ${(props) => props.theme?.borderRadius.md || '0.5rem'};
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  margin-bottom: ${(props) => props.theme?.spacing.xl || '2rem'};
  cursor: pointer;

  summary {
    font-weight: ${(props) => props.theme?.typography.fontWeight.semibold || 600};
    color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
    margin-bottom: ${(props) => props.theme?.spacing.sm || '0.5rem'};
    user-select: none;

    &:hover {
      color: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
    }
  }

  pre {
    font-family: ${(props) =>
      props.theme?.typography.fontFamily.mono ||
      '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace'};
    font-size: ${(props) => props.theme?.typography.fontSize.sm || '0.875rem'};
    color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    line-height: ${(props) => props.theme?.typography.lineHeight.relaxed || 1.75};
    margin: 0;
  }
`;

export const ButtonGroup = styled.div<{ theme?: Theme }>`
  display: flex;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  justify-content: center;
  flex-wrap: wrap;
`;

const Button = styled.button<{ theme?: Theme }>`
  padding: ${(props) => props.theme?.spacing.md || '1rem'}
    ${(props) => props.theme?.spacing.xl || '2rem'};
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.semibold || 600};
  border-radius: ${(props) => props.theme?.borderRadius.md || '0.5rem'};
  border: none;
  cursor: pointer;
  transition: ${(props) => props.theme?.transitions.fast || '150ms cubic-bezier(0.4, 0, 0.2, 1)'};

  &:hover {
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
  }
`;

export const ReloadButton = styled(Button)<{ theme?: Theme }>`
  background: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
  color: ${(props) => props.theme?.colors.primary.contrast || '#FFFFFF'};

  &:hover {
    background: ${(props) => props.theme?.colors.primary.dark || '#B91C1C'};
  }
`;

export const HomeButton = styled(Button)<{ theme?: Theme }>`
  background: ${(props) => props.theme?.colors.background.paper || '#F8FAFC'};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  border: 1px solid ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'};

  &:hover {
    background: ${(props) => props.theme?.colors.background.hover || '#F1F5F9'};
    border-color: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
  }
`;
