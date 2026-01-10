/**
 * Searchable Select Component
 * 
 * A searchable dropdown with filtering for foreign key selection.
 * Users can type to filter options and see display names instead of IDs.
 * 
 * Features:
 * - Text input for search/filter
 * - Dropdown shows filtered results
 * - Click-outside to close
 * - Keyboard navigation (up/down arrows, enter to select, escape to close)
 * - Shows display name, not ID
 * - Theme-compliant styling
 * 
 * Usage:
 * ```tsx
 * <SearchableSelect
 *   label="Customer"
 *   value={selectedCustomerId}
 *   options={customers}
 *   onChange={(id) => setSelectedCustomerId(id)}
 *   placeholder="Select Customer"
 *   required
 * />
 * ```
 */
import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

export interface SearchableSelectOption {
  id: number | string;
  name: string;
  [key: string]: any; // Allow additional fields
}

interface SearchableSelectProps {
  label?: string;
  value: string | number;
  options?: SearchableSelectOption[]; // Make optional to handle undefined
  onChange: (value: string | number, option?: SearchableSelectOption) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  loading?: boolean; // Add loading state
}

// ============================================================================
// Styled Components (Theme-Compliant)
// ============================================================================

const Container = styled.div`
  position: relative;
  width: 100%;
`;

const Label = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(var(--color-text-primary));
  margin-bottom: 0.5rem;
`;

const Required = styled.span`
  color: rgba(239, 68, 68, 1);
  margin-left: 0.25rem;
`;

const InputWrapper = styled.div<{ isOpen: boolean; hasError?: boolean }>`
  position: relative;
  width: 100%;
`;

const Input = styled.input<{ hasError?: boolean }>`
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 0.75rem;
  background: rgb(var(--color-background));
  border: 1px solid ${props => props.hasError ? 'rgba(239, 68, 68, 1)' : 'rgb(var(--color-border))'};
  border-radius: var(--radius-md);
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: ${props => props.hasError ? 'rgba(239, 68, 68, 1)' : 'rgb(var(--color-primary))'};
  }
  
  &::placeholder {
    color: rgb(var(--color-text-secondary));
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const DropdownIcon = styled.div<{ isOpen: boolean }>`
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%) ${props => props.isOpen ? 'rotate(180deg)' : 'rotate(0deg)'};
  transition: transform 0.2s ease;
  pointer-events: none;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const DropdownList = styled.ul<{ isOpen: boolean }>`
  display: ${props => props.isOpen ? 'block' : 'none'};
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 250px;
  overflow-y: auto;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 100;
  margin: 0;
  padding: 0;
  list-style: none;

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgb(var(--color-background));
  }

  &::-webkit-scrollbar-thumb {
    background: rgb(var(--color-border));
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgb(var(--color-text-secondary));
  }
`;

const DropdownItem = styled.li<{ isSelected: boolean; isFocused: boolean }>`
  padding: 0.75rem;
  cursor: pointer;
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  background: ${props => {
    if (props.isSelected) return 'rgba(var(--color-primary), 0.1)';
    if (props.isFocused) return 'rgb(var(--color-surface-hover))';
    return 'transparent';
  }};
  transition: background 0.15s ease;

  &:hover {
    background: rgb(var(--color-surface-hover));
  }

  ${props => props.isSelected && `
    font-weight: 600;
    color: rgb(var(--color-primary));
  `}
`;

const EmptyState = styled.div`
  padding: 1rem 0.75rem;
  text-align: center;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const LoadingState = styled.div`
  padding: 1rem 0.75rem;
  text-align: center;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
`;

const Spinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid rgb(var(--color-border));
  border-top-color: rgb(var(--color-primary));
  border-radius: 50%;
  animation: spin 0.6s linear infinite;

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const ErrorText = styled.div`
  font-size: 0.75rem;
  color: rgba(239, 68, 68, 1);
  margin-top: 0.25rem;
`;

// ============================================================================
// Main Component
// ============================================================================

export const SearchableSelect: React.FC<SearchableSelectProps> = ({
  label,
  value,
  options = [], // Default to empty array if undefined
  onChange,
  placeholder = 'Select an option',
  required = false,
  disabled = false,
  error,
  loading = false, // Default to false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [focusedIndex, setFocusedIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Safely handle options with null checks
  const safeOptions = options || [];

  // Get the display name for the selected value
  const selectedOption = safeOptions.find(opt => opt && String(opt.id) === String(value));
  const displayValue = selectedOption ? selectedOption.name : '';

  // Filter options based on search query with null checks
  const filteredOptions = safeOptions.filter(option => 
    option && 
    option.name && 
    typeof option.name === 'string' &&
    option.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown') {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex(prev => 
          prev < filteredOptions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex(prev => prev > 0 ? prev - 1 : prev);
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredOptions[focusedIndex]) {
          handleSelect(filteredOptions[focusedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        setSearchQuery('');
        break;
    }
  };

  const handleSelect = (option: SearchableSelectOption) => {
    onChange(option.id, option);
    setIsOpen(false);
    setSearchQuery('');
    setFocusedIndex(0);
  };

  const handleInputClick = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
      if (!isOpen) {
        setSearchQuery('');
        setFocusedIndex(0);
      }
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setIsOpen(true);
    setFocusedIndex(0);
  };

  return (
    <Container ref={containerRef}>
      {label && (
        <Label>
          {label}
          {required && <Required>*</Required>}
        </Label>
      )}
      
      <InputWrapper isOpen={isOpen} hasError={!!error}>
        <Input
          ref={inputRef}
          type="text"
          value={isOpen ? searchQuery : displayValue}
          onChange={handleSearchChange}
          onClick={handleInputClick}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          hasError={!!error}
          autoComplete="off"
        />
        <DropdownIcon isOpen={isOpen}>▼</DropdownIcon>
      </InputWrapper>

      <DropdownList isOpen={isOpen && !disabled}>
        {loading ? (
          <LoadingState>
            <Spinner />
            Loading options...
          </LoadingState>
        ) : filteredOptions.length === 0 ? (
          <EmptyState>
            {searchQuery ? 'No matching results' : safeOptions.length === 0 ? 'No options available' : 'No matching results'}
          </EmptyState>
        ) : (
          filteredOptions.map((option, index) => (
            <DropdownItem
              key={option.id}
              isSelected={String(option.id) === String(value)}
              isFocused={index === focusedIndex}
              onClick={() => handleSelect(option)}
              onMouseEnter={() => setFocusedIndex(index)}
            >
              {option.name}
            </DropdownItem>
          ))
        )}
      </DropdownList>

      {error && <ErrorText>{error}</ErrorText>}
    </Container>
  );
};

export default SearchableSelect;
