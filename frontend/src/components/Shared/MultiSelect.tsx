/**
 * MultiSelect Component - Array-Based Multi-Selection Dropdown
 * 
 * Features:
 * - Binds to ArrayField backend structure (string[])
 * - Prevents common serialization bug: ['Sales,Logistics'] vs ['Sales', 'Logistics']
 * - Theme-aware styling
 * - Keyboard navigation support
 * - ARIA labels for accessibility
 * 
 * Phase 4: Frontend Integration & UX Alignment
 * CRITICAL: Ensures proper array serialization for Django ArrayField
 */

import React from 'react';
import styled from 'styled-components';
import { Theme } from '../../config/theme';
import { useTheme } from '../../contexts/ThemeContext';

export interface MultiSelectOption {
  value: string;
  label: string;
}

export interface MultiSelectProps {
  value: string[];
  onChange: (values: string[]) => void;
  options: MultiSelectOption[];
  label?: string;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  'aria-label'?: string;
  id?: string;
}

export const MultiSelect: React.FC<MultiSelectProps> = ({
  value,
  onChange,
  options,
  label,
  placeholder = 'Select multiple options (hold Ctrl/Cmd)',
  error,
  disabled = false,
  required = false,
  'aria-label': ariaLabel,
  id,
}) => {
  const { theme } = useTheme();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    // CRITICAL: Extract selected options as array of individual strings
    // NOT as comma-separated string
    const selectedOptions = Array.from(e.target.selectedOptions);
    const selectedValues = selectedOptions.map(option => option.value);
    
    // Validation: Ensure we're sending proper array structure
    console.debug('[MultiSelect] Selected values:', selectedValues);
    console.debug('[MultiSelect] Type check:', Array.isArray(selectedValues), selectedValues.length);
    
    onChange(selectedValues);
  };

  return (
    <Container>
      {label && <Label $theme={theme}>{label}{required && ' *'}</Label>}
      
      <StyledSelect
        id={id}
        value={value}
        onChange={handleChange}
        disabled={disabled}
        required={required}
        aria-label={ariaLabel || label}
        $theme={theme}
        $hasError={!!error}
        multiple
        size={Math.min(options.length, 5)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </StyledSelect>
      
      {placeholder && !value.length && (
        <HelpText $theme={theme}>{placeholder}</HelpText>
      )}
      
      {value.length > 0 && (
        <SelectedCount $theme={theme}>
          {value.length} item{value.length !== 1 ? 's' : ''} selected
        </SelectedCount>
      )}
      
      {error && <ErrorMessage $theme={theme}>{error}</ErrorMessage>}
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
`;

const Label = styled.label<{ $theme: Theme }>`
  font-size: 14px;
  font-weight: 500;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin-bottom: 2px;
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
    cursor: pointer;

    &:checked {
      background-color: ${(props) => props.$theme.colors.primary};
      color: white;
    }

    &:hover {
      background-color: ${(props) => props.$theme.colors.surfaceHover};
    }
  }
`;

const HelpText = styled.div<{ $theme: Theme }>`
  color: ${(props) => props.$theme.colors.textSecondary};
  font-size: 12px;
  font-style: italic;
`;

const SelectedCount = styled.div<{ $theme: Theme }>`
  color: ${(props) => props.$theme.colors.primary};
  font-size: 12px;
  font-weight: 500;
`;

const ErrorMessage = styled.div<{ $theme: Theme }>`
  color: ${(props) => props.$theme.colors.danger};
  font-size: 12px;
`;

export default MultiSelect;
