/**
 * Select Component - Reusable dropdown with semantic design system
 * 
 * Features:
 * - Theme-aware styling
 * - Full keyboard navigation
 * - ARIA labels for accessibility
 * - Error state support
 * - Optional placeholder
 */

import React from 'react';
import styled from 'styled-components';
import { Theme } from '../../config/theme';
import { useTheme } from '../../contexts/ThemeContext';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  'aria-label'?: string;
  id?: string;
}

export const Select: React.FC<SelectProps> = ({
  value,
  onChange,
  options,
  placeholder = 'Select an option',
  error,
  disabled = false,
  required = false,
  'aria-label': ariaLabel,
  id,
}) => {
  const { theme } = useTheme();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value);
  };

  return (
    <SelectContainer>
      <StyledSelect
        id={id}
        value={value}
        onChange={handleChange}
        disabled={disabled}
        required={required}
        aria-label={ariaLabel}
        $theme={theme}
        $hasError={!!error}
      >
        <option value="" disabled hidden>
          {placeholder}
        </option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </StyledSelect>
      {error && <ErrorMessage $theme={theme}>{error}</ErrorMessage>}
    </SelectContainer>
  );
};

const SelectContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
`;

const StyledSelect = styled.select<{ $theme: Theme; $hasError: boolean }>`
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
  cursor: pointer;

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

  option {
    background-color: ${(props) => props.$theme.colors.surface};
    color: ${(props) => props.$theme.colors.textPrimary};
    padding: 8px;
  }
`;

const ErrorMessage = styled.span<{ $theme: Theme }>`
  color: ${(props) => props.$theme.colors.danger};
  font-size: 12px;
  margin-top: 2px;
`;

export default Select;
