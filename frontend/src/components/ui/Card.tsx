/**
 * Semantic Card Component
 * 
 * Uses CSS variables for colors, allowing tenant-specific branding
 * without component changes.
 * 
 * Usage:
 *   <Card>
 *     <CardHeader title="Dashboard" description="Welcome back!" />
 *     <CardContent>Your content here</CardContent>
 *   </Card>
 */
import React from 'react';
import styled from 'styled-components';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const StyledCard = styled.div<{ padding?: string }>`
  background-color: rgb(var(--color-surface));
  color: rgb(var(--color-surface-foreground));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease;

  ${({ padding }) => {
    switch (padding) {
      case 'none':
        return 'padding: 0;';
      case 'sm':
        return 'padding: 1rem;';
      case 'lg':
        return 'padding: 2rem;';
      default: // 'md'
        return 'padding: 1.5rem;';
    }
  }}

  &:hover {
    box-shadow: var(--shadow-md);
  }
`;

const CardHeaderContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-bottom: 1rem;
`;

const CardTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.025em;
  color: rgb(var(--color-text-primary));
  margin: 0;
`;

const CardDescription = styled.p`
  font-size: 0.875rem;
  color: rgb(var(--color-text-secondary));
  margin: 0;
`;

const CardContentContainer = styled.div`
  width: 100%;
`;

const CardFooterContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgb(var(--color-border));
`;

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  padding = 'md' 
}) => {
  return (
    <StyledCard className={className} padding={padding}>
      {children}
    </StyledCard>
  );
};

interface CardHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ 
  title, 
  description, 
  actions 
}) => (
  <CardHeaderContainer>
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <CardTitle>{title}</CardTitle>
      {actions}
    </div>
    {description && <CardDescription>{description}</CardDescription>}
  </CardHeaderContainer>
);

export const CardContent: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <CardContentContainer>{children}</CardContentContainer>
);

export const CardFooter: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <CardFooterContainer>{children}</CardFooterContainer>
);
