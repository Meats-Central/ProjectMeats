/**
 * Semantic Page Container Component
 * 
 * Provides consistent page layout with responsive padding and header section.
 * Uses CSS variables for colors.
 * 
 * Usage:
 *   <PageContainer title="Dashboard" actions={<Button>New Item</Button>}>
 *     <Card>Your content</Card>
 *   </PageContainer>
 */
import React from 'react';
import styled from 'styled-components';

interface PageContainerProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
  actions?: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

const Container = styled.div<{ maxWidth?: string }>`
  flex: 1;
  padding: 1rem;
  background-color: rgb(var(--color-background));
  min-height: 100vh;

  @media (min-width: 768px) {
    padding: 2rem;
  }

  ${({ maxWidth }) => {
    switch (maxWidth) {
      case 'sm':
        return 'max-width: 640px; margin: 0 auto;';
      case 'md':
        return 'max-width: 768px; margin: 0 auto;';
      case 'lg':
        return 'max-width: 1024px; margin: 0 auto;';
      case 'xl':
        return 'max-width: 1280px; margin: 0 auto;';
      default:
        return 'width: 100%;';
    }
  }}
`;

const HeaderSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;

  @media (min-width: 768px) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
`;

const HeaderContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
`;

const Title = styled.h1`
  font-size: 1.875rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: rgb(var(--color-text-primary));
  margin: 0;

  @media (min-width: 768px) {
    font-size: 2.25rem;
  }
`;

const Description = styled.p`
  font-size: 0.875rem;
  color: rgb(var(--color-text-secondary));
  margin: 0;

  @media (min-width: 768px) {
    font-size: 1rem;
  }
`;

const ActionsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
`;

const Content = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

export const PageContainer: React.FC<PageContainerProps> = ({ 
  children, 
  title, 
  description,
  actions,
  maxWidth = 'full'
}) => {
  return (
    <Container maxWidth={maxWidth}>
      {(title || actions) && (
        <HeaderSection>
          <HeaderContent>
            {title && <Title>{title}</Title>}
            {description && <Description>{description}</Description>}
          </HeaderContent>
          {actions && <ActionsContainer>{actions}</ActionsContainer>}
        </HeaderSection>
      )}
      <Content>{children}</Content>
    </Container>
  );
};
