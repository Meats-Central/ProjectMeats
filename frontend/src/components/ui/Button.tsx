/**
 * Semantic Button Component
 * 
 * Uses CSS variables for colors, allowing tenant-specific branding
 * without component changes.
 * 
 * Usage:
 *   <Button variant="primary">Save</Button>
 *   <Button variant="secondary" size="lg">Cancel</Button>
 */
import React from 'react';
import styled from 'styled-components';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

const StyledButton = styled.button<ButtonProps>`
  /* Base styles */
  display: inline-flex;
  align-items: center;
  justify-center: center;
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  font-family: var(--font-sans);
  
  /* Disable effects */
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }

  /* Focus ring */
  &:focus-visible {
    outline: 2px solid rgb(var(--color-primary));
    outline-offset: 2px;
  }

  /* Size variants */
  ${({ size }) => {
    switch (size) {
      case 'sm':
        return `
          height: 2rem;
          padding: 0 0.75rem;
          font-size: 0.875rem;
        `;
      case 'lg':
        return `
          height: 3rem;
          padding: 0 2rem;
          font-size: 1.125rem;
        `;
      default: // 'md'
        return `
          height: 2.5rem;
          padding: 0 1rem;
          font-size: 1rem;
        `;
    }
  }}

  /* Width */
  ${({ fullWidth }) => fullWidth && 'width: 100%;'}

  /* Variant styles - using semantic CSS variables */
  ${({ variant }) => {
    switch (variant) {
      case 'primary':
        return `
          background-color: rgb(var(--color-primary));
          color: rgb(var(--color-primary-foreground));
          box-shadow: var(--shadow-sm);

          &:hover:not(:disabled) {
            background-color: rgb(var(--color-primary-hover));
          }

          &:active:not(:disabled) {
            background-color: rgb(var(--color-primary-active));
          }
        `;
      
      case 'secondary':
        return `
          background-color: rgb(var(--color-secondary));
          color: rgb(var(--color-secondary-foreground));
          box-shadow: var(--shadow-sm);

          &:hover:not(:disabled) {
            background-color: rgb(var(--color-secondary-hover));
          }
        `;
      
      case 'outline':
        return `
          background-color: transparent;
          color: rgb(var(--color-text-primary));
          border: 1px solid rgb(var(--color-border));

          &:hover:not(:disabled) {
            background-color: rgb(var(--color-surface-hover));
          }
        `;
      
      case 'ghost':
        return `
          background-color: transparent;
          color: rgb(var(--color-text-primary));

          &:hover:not(:disabled) {
            background-color: rgb(var(--color-surface-hover));
          }
        `;
      
      case 'danger':
        return `
          background-color: rgb(var(--color-danger));
          color: white;
          box-shadow: var(--shadow-sm);

          &:hover:not(:disabled) {
            opacity: 0.9;
          }
        `;
      
      default:
        return '';
    }
  }}
`;

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  fullWidth = false,
  ...props 
}) => {
  return (
    <StyledButton 
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      {...props}
    >
      {children}
    </StyledButton>
  );
};
