/**
 * PhoneInput Component - Masked phone input with (XXX) XXX-XXXX format
 * 
 * Features:
 * - Auto-formatting as user types
 * - Theme-aware styling
 * - Error state support
 * - Full accessibility
 */

import React from 'react';
import InputMask from 'react-input-mask';
import styled from 'styled-components';
import { Theme } from '../../config/theme';
import { useTheme } from '../../contexts/ThemeContext';

export interface PhoneInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  'aria-label'?: string;
  id?: string;
}

export const PhoneInput: React.FC<PhoneInputProps> = ({
  value,
  onChange,
  placeholder = '(XXX) XXX-XXXX',
  error,
  disabled = false,
  required = false,
  'aria-label': ariaLabel = 'Phone number',
  id,
}) => {
  const { theme } = useTheme();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Strip formatting and pass raw digits
    const rawValue = e.target.value.replace(/\D/g, '');
    onChange(rawValue);
  };

  return (
    <PhoneInputContainer>
      <StyledInputMask
        mask="(999) 999-9999"
        value={value}
        onChange={handleChange}
        disabled={disabled}
        placeholder={placeholder}
        aria-label={ariaLabel}
        required={required}
        id={id}
        $theme={theme}
        $hasError={!!error}
      />
      {error && <ErrorMessage $theme={theme}>{error}</ErrorMessage>}
    </PhoneInputContainer>
  );
};

const PhoneInputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
`;

const StyledInputMask = styled(InputMask)<{ $theme: Theme; $hasError: boolean }>`
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  border: 1px solid ${(props) => 
    props.$hasError 
      ? props.$theme.colors.danger 
      : props.$theme.colors.border
  };
  border-radius: 6px;
  background-color: ${(props) => props.$theme.colors.surface};
  color: ${(props) => props.$theme.colors.textPrimary};
  transition: all 0.2s ease;

  &::placeholder {
    color: ${(props) => props.$theme.colors.textSecondary};
    opacity: 0.6;
  }

  &:hover:not(:disabled) {
    border-color: ${(props) => props.$theme.colors.primary};
  }

  &:focus {
    outline: none;
    border-color: ${(props) => props.$theme.colors.primary};
    box-shadow: 0 0 0 3px ${(props) => props.$theme.colors.primary}20;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: ${(props) => props.$theme.colors.surfaceHover};
  }
`;

const ErrorMessage = styled.span<{ $theme: Theme }>`
  color: ${(props) => props.$theme.colors.danger};
  font-size: 12px;
  margin-top: 2px;
`;

export default PhoneInput;
