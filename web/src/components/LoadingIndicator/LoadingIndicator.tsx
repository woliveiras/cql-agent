import { Container, Dot } from './LoadingIndicator.styles';

export function LoadingIndicator() {
  return (
    <Container>
      <Dot delay={0} />
      <Dot delay={0.2} />
      <Dot delay={0.4} />
    </Container>
  );
}
