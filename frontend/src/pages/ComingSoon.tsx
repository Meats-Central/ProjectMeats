/**
 * ComingSoon Component
 * 
 * Placeholder page for features in development
 */
import React from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

interface ComingSoonProps {
  title: string;
  description?: string;
}

export const ComingSoon: React.FC<ComingSoonProps> = ({ 
  title, 
  description = 'This feature is currently under development and will be available soon.' 
}) => {
  const navigate = useNavigate();

  return (
    <Container>
      <Content>
        <Icon>🚧</Icon>
        <Title>{title}</Title>
        <Description>{description}</Description>
        <BackButton onClick={() => navigate(-1)}>
          ← Go Back
        </BackButton>
      </Content>
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 2rem;
`;

const Content = styled.div`
  text-align: center;
  max-width: 500px;
`;

const Icon = styled.div`
  font-size: 80px;
  margin-bottom: 1.5rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin-bottom: 1rem;
`;

const Description = styled.p`
  font-size: 1.125rem;
  color: rgb(var(--color-text-secondary));
  margin-bottom: 2rem;
  line-height: 1.6;
`;

const BackButton = styled.button`
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: rgb(var(--color-primary-foreground));
  background-color: rgb(var(--color-primary));
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: rgb(var(--color-primary-hover));
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

export default ComingSoon;
