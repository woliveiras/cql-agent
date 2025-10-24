import styled from '@emotion/styled';
import { useTheme } from '@emotion/react';
import type { Theme } from '../../styles/types';
import { Button } from '../../components/Button';
import { Input, Textarea } from '../../components/Input';
import { Card } from '../../components/Card';
import { Avatar } from '../../components/Avatar';

const Container = styled.div<{ theme?: Theme }>`
  max-width: 1200px;
  margin: 0 auto;
  padding: ${(props) => props.theme?.spacing['2xl'] || '3rem'};
`;

const Header = styled.header<{ theme?: Theme }>`
  margin-bottom: ${(props) => props.theme?.spacing['3xl'] || '4rem'};
`;

const Title = styled.h1<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize['4xl'] || '2.25rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.bold || 700};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  margin-bottom: ${(props) => props.theme?.spacing.md || '1rem'};
`;

const Subtitle = styled.p<{ theme?: Theme}>`
  font-size: ${(props) => props.theme?.typography.fontSize.lg || '1.125rem'};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
`;

const Section = styled.section<{ theme?: Theme }>`
  margin-bottom: ${(props) => props.theme?.spacing['3xl'] || '4rem'};
`;

const SectionTitle = styled.h2<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize['2xl'] || '1.5rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.semibold || 600};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  margin-bottom: ${(props) => props.theme?.spacing.lg || '1.5rem'};
  padding-bottom: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  border-bottom: 2px solid ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'};
`;

const ComponentCard = styled.div<{ theme?: Theme }>`
  padding: ${(props) => props.theme?.spacing.xl || '2rem'};
  background: ${(props) => props.theme?.colors.background.paper || '#F8FAFC'};
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  box-shadow: ${(props) => props.theme?.shadows.md || '0 4px 6px -1px rgba(0, 0, 0, 0.1)'};
  margin-bottom: ${(props) => props.theme?.spacing.xl || '2rem'};
`;

const ComponentName = styled.h3<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.xl || '1.25rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.medium || 500};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  margin-bottom: ${(props) => props.theme?.spacing.md || '1rem'};
`;

const ComponentDescription = styled.p<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.sm || '0.875rem'};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
  margin-bottom: ${(props) => props.theme?.spacing.lg || '1.5rem'};
`;

const ComponentDemo = styled.div<{ theme?: Theme }>`
  display: flex;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  flex-wrap: wrap;
  align-items: center;
`;

const ColorGrid = styled.div<{ theme?: Theme }>`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
`;

const ColorCard = styled.div<{ color: string; theme?: Theme }>`
  height: 100px;
  background: ${(props) => props.color};
  border-radius: ${(props) => props.theme?.borderRadius.md || '0.5rem'};
  display: flex;
  align-items: flex-end;
  padding: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  box-shadow: ${(props) => props.theme?.shadows.sm || '0 1px 2px 0 rgba(0, 0, 0, 0.05)'};
`;

const ColorName = styled.span<{ isDark?: boolean; theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.xs || '0.75rem'};
  font-family: ${(props) => props.theme?.typography.fontFamily.mono || 'monospace'};
  color: ${(props) => (props.isDark ? '#FFFFFF' : '#000000')};
  font-weight: ${(props) => props.theme?.typography.fontWeight.medium || 500};
`;

export function Showcase() {
  const theme = useTheme() as Theme;

  return (
    <Container>
      <Header>
        <Title>🎨 RepairChat - Design System</Title>
        <Subtitle>
          Componentes e estilos da interface de chat para reparos residenciais
        </Subtitle>
      </Header>

      {/* Cores */}
      <Section>
        <SectionTitle>Paleta de Cores</SectionTitle>

        <ComponentCard>
          <ComponentName>Cores Primárias</ComponentName>
          <ComponentDescription>
            Vermelho vibrante representando urgência e ação (ferramentas, emergência)
          </ComponentDescription>
          <ColorGrid>
            <ColorCard color={theme.colors.primary.light}>
              <ColorName isDark>Primary Light</ColorName>
            </ColorCard>
            <ColorCard color={theme.colors.primary.main}>
              <ColorName isDark>Primary Main</ColorName>
            </ColorCard>
            <ColorCard color={theme.colors.primary.dark}>
              <ColorName isDark>Primary Dark</ColorName>
            </ColorCard>
          </ColorGrid>
        </ComponentCard>

        <ComponentCard>
          <ComponentName>Cores Secundárias</ComponentName>
          <ComponentDescription>
            Cinza azulado representando confiança e profissionalismo
          </ComponentDescription>
          <ColorGrid>
            <ColorCard color={theme.colors.secondary.light}>
              <ColorName isDark>Secondary Light</ColorName>
            </ColorCard>
            <ColorCard color={theme.colors.secondary.main}>
              <ColorName isDark>Secondary Main</ColorName>
            </ColorCard>
            <ColorCard color={theme.colors.secondary.dark}>
              <ColorName isDark>Secondary Dark</ColorName>
            </ColorCard>
          </ColorGrid>
        </ComponentCard>

        <ComponentCard>
          <ComponentName>Cores de Status</ComponentName>
          <ComponentDescription>Sucesso, erro e aviso</ComponentDescription>
          <ColorGrid>
            <ColorCard color={theme.colors.success.main}>
              <ColorName isDark>Success</ColorName>
            </ColorCard>
            <ColorCard color={theme.colors.error.main}>
              <ColorName isDark>Error</ColorName>
            </ColorCard>
            <ColorCard color={theme.colors.warning.main}>
              <ColorName isDark>Warning</ColorName>
            </ColorCard>
          </ColorGrid>
        </ComponentCard>
      </Section>

      {/* Tipografia */}
      <Section>
        <SectionTitle>Tipografia</SectionTitle>
        <ComponentCard>
          <ComponentName>Tamanhos de Fonte</ComponentName>
          <ComponentDemo style={{ flexDirection: 'column', alignItems: 'flex-start', width: '100%' }}>
            <div style={{ fontSize: theme.typography.fontSize['4xl'], marginBottom: theme.spacing.sm }}>
              Heading 1 - 36px
            </div>
            <div style={{ fontSize: theme.typography.fontSize['3xl'], marginBottom: theme.spacing.sm }}>
              Heading 2 - 30px
            </div>
            <div style={{ fontSize: theme.typography.fontSize['2xl'], marginBottom: theme.spacing.sm }}>
              Heading 3 - 24px
            </div>
            <div style={{ fontSize: theme.typography.fontSize.xl, marginBottom: theme.spacing.sm }}>Body Large - 20px</div>
            <div style={{ fontSize: theme.typography.fontSize.base, marginBottom: theme.spacing.sm }}>Body - 16px</div>
            <div style={{ fontSize: theme.typography.fontSize.sm, marginBottom: theme.spacing.sm }}>Body Small - 14px</div>
            <div style={{ fontSize: theme.typography.fontSize.xs }}>Caption - 12px</div>
          </ComponentDemo>
        </ComponentCard>
      </Section>

      {/* Espaçamentos */}
      <Section>
        <SectionTitle>Espaçamentos</SectionTitle>
        <ComponentCard>
          <ComponentName>Sistema de Spacing</ComponentName>
          <ComponentDescription>
            Escala consistente de espaçamentos (4px, 8px, 16px, 24px, 32px, 48px, 64px, 96px)
          </ComponentDescription>
          <ComponentDemo style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
            {Object.entries(theme.spacing).map(([key, value]) => (
              <div
                key={key}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: theme.spacing.md,
                  marginBottom: theme.spacing.sm,
                }}
              >
                <code style={{ width: '80px' }}>
                  {key}: {value}
                </code>
                <div
                  style={{
                    height: '20px',
                    width: value,
                    background: theme.colors.primary.main,
                    borderRadius: theme.borderRadius.sm,
                  }}
                />
              </div>
            ))}
          </ComponentDemo>
        </ComponentCard>
      </Section>

      {/* Componentes - Placeholder */}
      {/* Componentes */}
      <Section>
        <SectionTitle>Componentes</SectionTitle>

        <ComponentCard>
          <ComponentName>Button</ComponentName>
          <ComponentDescription>
            Botão com três variantes (primary, secondary, ghost) e três tamanhos (small, medium,
            large)
          </ComponentDescription>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Variantes
            </h4>
            <ComponentDemo>
              <Button variant="primary">Primary Button</Button>
              <Button variant="secondary">Secondary Button</Button>
              <Button variant="ghost">Ghost Button</Button>
            </ComponentDemo>
          </div>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Tamanhos
            </h4>
            <ComponentDemo>
              <Button size="small">Small</Button>
              <Button size="medium">Medium</Button>
              <Button size="large">Large</Button>
            </ComponentDemo>
          </div>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Estados
            </h4>
            <ComponentDemo>
              <Button>Normal</Button>
              <Button disabled>Disabled</Button>
              <Button loading>Loading</Button>
            </ComponentDemo>
          </div>

          <div>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Full Width
            </h4>
            <Button fullWidth>Full Width Button</Button>
          </div>
        </ComponentCard>

        <ComponentCard>
          <ComponentName>Input</ComponentName>
          <ComponentDescription>
            Campo de entrada de texto com label, placeholder, estados de erro e helper text
          </ComponentDescription>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Básico
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
              <Input placeholder="Digite algo..." />
              <Input label="Nome" placeholder="Seu nome completo" />
              <Input
                label="Email"
                type="email"
                placeholder="seu@email.com"
                helperText="Usaremos este email para contato"
              />
            </div>
          </div>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Estados
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
              <Input label="Normal" placeholder="Estado normal" />
              <Input label="Com Erro" error="Este campo é obrigatório" placeholder="Campo com erro" />
              <Input label="Desabilitado" disabled placeholder="Campo desabilitado" />
            </div>
          </div>

          <div>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Full Width
            </h4>
            <Input fullWidth label="Campo Full Width" placeholder="Ocupa toda a largura disponível" />
          </div>
        </ComponentCard>

        <ComponentCard>
          <ComponentName>Textarea</ComponentName>
          <ComponentDescription>
            Campo de texto multilinha para mensagens longas
          </ComponentDescription>

          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
            <Textarea
              label="Mensagem"
              placeholder="Descreva seu problema..."
              helperText="Mínimo 10 caracteres"
            />
            <Textarea
              label="Com Erro"
              error="Mensagem muito curta"
              placeholder="Digite mais caracteres"
              rows={3}
            />
            <Textarea
              fullWidth
              label="Full Width"
              placeholder="Textarea full width com 6 linhas"
              rows={6}
            />
          </div>
        </ComponentCard>

        <ComponentCard>
          <ComponentName>Card</ComponentName>
          <ComponentDescription>
            Container com três variantes (elevated, outlined, filled) e opções de padding
          </ComponentDescription>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Variantes
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: theme.spacing.md }}>
              <Card variant="elevated">
                <h5 style={{ marginBottom: theme.spacing.sm, fontWeight: theme.typography.fontWeight.semibold }}>
                  Elevated
                </h5>
                <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.text.secondary }}>
                  Card com sombra elevada
                </p>
              </Card>
              <Card variant="outlined">
                <h5 style={{ marginBottom: theme.spacing.sm, fontWeight: theme.typography.fontWeight.semibold }}>
                  Outlined
                </h5>
                <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.text.secondary }}>
                  Card com borda
                </p>
              </Card>
              <Card variant="filled">
                <h5 style={{ marginBottom: theme.spacing.sm, fontWeight: theme.typography.fontWeight.semibold }}>
                  Filled
                </h5>
                <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.text.secondary }}>
                  Card com background preenchido
                </p>
              </Card>
            </div>
          </div>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Padding
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
              <Card padding="none" variant="outlined">
                <div style={{ padding: theme.spacing.md, background: theme.colors.neutral[100] }}>
                  Padding: none (0)
                </div>
              </Card>
              <Card padding="small" variant="outlined">
                Padding: small (16px)
              </Card>
              <Card padding="medium" variant="outlined">
                Padding: medium (24px) - Padrão
              </Card>
              <Card padding="large" variant="outlined">
                Padding: large (32px)
              </Card>
            </div>
          </div>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Clickable
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: theme.spacing.md }}>
              <Card clickable onClick={() => alert('Card clicado!')}>
                <h5 style={{ marginBottom: theme.spacing.sm, fontWeight: theme.typography.fontWeight.semibold }}>
                  🖱️ Clique aqui
                </h5>
                <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.text.secondary }}>
                  Card interativo
                </p>
              </Card>
              <Card clickable variant="outlined" onClick={() => alert('Outra opção!')}>
                <h5 style={{ marginBottom: theme.spacing.sm, fontWeight: theme.typography.fontWeight.semibold }}>
                  ✨ Ou aqui
                </h5>
                <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.text.secondary }}>
                  Com hover e animação
                </p>
              </Card>
            </div>
          </div>

          <div>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Exemplo Complexo
            </h4>
            <Card variant="elevated">
              <h3 style={{ marginBottom: theme.spacing.sm, fontSize: theme.typography.fontSize.xl }}>
                Sugestão de Reparo
              </h3>
              <p style={{ marginBottom: theme.spacing.md, color: theme.colors.text.secondary }}>
                Como consertar uma torneira pingando?
              </p>
              <div style={{ display: 'flex', gap: theme.spacing.sm }}>
                <Button size="small" variant="primary">
                  Ver Solução
                </Button>
                <Button size="small" variant="ghost">
                  Ignorar
                </Button>
              </div>
            </Card>
          </div>
        </ComponentCard>

        <ComponentCard>
          <ComponentName>Avatar</ComponentName>
          <ComponentDescription>
            Avatar circular para usuário e assistente, com suporte a imagem, iniciais ou ícone
          </ComponentDescription>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Tamanhos
            </h4>
            <ComponentDemo>
              <Avatar size="small" variant="user" />
              <Avatar size="medium" variant="user" />
              <Avatar size="large" variant="user" />
            </ComponentDemo>
          </div>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Variantes
            </h4>
            <ComponentDemo>
              <div style={{ textAlign: 'center' }}>
                <Avatar variant="user" />
                <div style={{ fontSize: theme.typography.fontSize.xs, marginTop: theme.spacing.xs }}>
                  Usuário
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <Avatar variant="assistant" />
                <div style={{ fontSize: theme.typography.fontSize.xs, marginTop: theme.spacing.xs }}>
                  Assistente
                </div>
              </div>
            </ComponentDemo>
          </div>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Com Iniciais
            </h4>
            <ComponentDemo>
              <Avatar name="William Souza" />
              <Avatar name="João Silva" variant="user" size="large" />
              <Avatar name="Maria" variant="user" size="small" />
            </ComponentDemo>
          </div>

          <div style={{ marginBottom: theme.spacing.lg }}>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Com Imagem
            </h4>
            <ComponentDemo>
              <Avatar
                src="https://i.pravatar.cc/150?img=1"
                alt="User 1"
                size="small"
              />
              <Avatar
                src="https://i.pravatar.cc/150?img=2"
                alt="User 2"
                size="medium"
              />
              <Avatar
                src="https://i.pravatar.cc/150?img=3"
                alt="User 3"
                size="large"
              />
            </ComponentDemo>
          </div>

          <div>
            <h4
              style={{
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing.md,
                color: theme.colors.text.secondary,
              }}
            >
              Exemplo de Uso (Chat)
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
              <div style={{ display: 'flex', gap: theme.spacing.md, alignItems: 'start' }}>
                <Avatar variant="user" name="Você" />
                <Card variant="filled" padding="small" style={{ flex: 1 }}>
                  Como faço para consertar uma torneira pingando?
                </Card>
              </div>
              <div style={{ display: 'flex', gap: theme.spacing.md, alignItems: 'start' }}>
                <Avatar variant="assistant" />
                <Card variant="outlined" padding="small" style={{ flex: 1 }}>
                  Vou te ajudar! Para consertar uma torneira pingando, você precisará...
                </Card>
              </div>
            </div>
          </div>
        </ComponentCard>
      </Section>
    </Container>
  );
}

export default Showcase;
