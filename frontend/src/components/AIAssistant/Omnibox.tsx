import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import Modal from '../Modal/Modal';

interface OmniboxProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (command: string) => void;
}

const Omnibox: React.FC<OmniboxProps> = ({ isOpen, onClose, onSubmit }) => {
  const [command, setCommand] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);

  const sampleCommands = [
    'Create a purchase order for ABC Meats',
    'Show me supplier performance for this month',
    'Generate a customer report',
    'Set pricing rule for premium cuts',
    'Update inventory levels',
    'Send payment reminder to overdue customers',
    'Schedule delivery for order #12345',
    'Compare supplier prices for beef products',
  ];

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (command.length > 2) {
      const filtered = sampleCommands.filter((cmd) =>
        cmd.toLowerCase().includes(command.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 5));
    } else {
      setSuggestions([]);
    }
    setSelectedSuggestionIndex(-1);
    // sampleCommands is static and doesn't need to be in dependencies
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [command]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedSuggestionIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedSuggestionIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedSuggestionIndex >= 0) {
        handleSubmit(suggestions[selectedSuggestionIndex]);
      } else if (command.trim()) {
        handleSubmit(command);
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  const handleSubmit = (commandToSubmit: string) => {
    onSubmit(commandToSubmit);
    setCommand('');
    setSuggestions([]);
    setSelectedSuggestionIndex(-1);
    onClose();
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSubmit(suggestion);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="AI Command Center" maxWidth="700px">
      <OmniboxContainer>
        <CommandInput
          ref={inputRef}
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your command (e.g., 'Create purchase order for ABC Meats')"
        />

        {suggestions.length > 0 && (
          <SuggestionsList>
            {suggestions.map((suggestion, index) => (
              <SuggestionItem
                key={suggestion}
                isSelected={index === selectedSuggestionIndex}
                onClick={() => handleSuggestionClick(suggestion)}
              >
                <SuggestionIcon>💡</SuggestionIcon>
                <SuggestionText>{suggestion}</SuggestionText>
              </SuggestionItem>
            ))}
          </SuggestionsList>
        )}

        <HelpText>
          <HelpTitle>🤖 AI Assistant Commands</HelpTitle>
          <HelpSection>
            <HelpSubtitle>Sample Commands:</HelpSubtitle>
            <HelpList>
              <HelpItem>"Create purchase order for [supplier name]"</HelpItem>
              <HelpItem>"Show supplier performance for [time period]"</HelpItem>
              <HelpItem>"Set pricing rule for [product type]"</HelpItem>
              <HelpItem>"Generate report for [entity type]"</HelpItem>
            </HelpList>
          </HelpSection>
          <TipText>💡 Tip: Use natural language - the AI will interpret your intent</TipText>
        </HelpText>
      </OmniboxContainer>
    </Modal>
  );
};

const OmniboxContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const CommandInput = styled.input`
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 16px;
  font-family: inherit;
  transition: border-color 0.2s;
  background: #f8f9fa;

  &:focus {
    outline: none;
    border-color: #3498db;
    background: white;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  }

  &::placeholder {
    color: #6c757d;
  }
`;

const SuggestionsList = styled.div`
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const SuggestionItem = styled.div<{ isSelected: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  background: ${(props) => (props.isSelected ? '#e3f2fd' : 'white')};
  border-bottom: 1px solid #f1f3f4;
  transition: background-color 0.2s;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: #f8f9fa;
  }
`;

const SuggestionIcon = styled.span`
  font-size: 16px;
  opacity: 0.7;
`;

const SuggestionText = styled.span`
  font-size: 14px;
  color: #2c3e50;
`;

const HelpText = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 10px;
`;

const HelpTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #2c3e50;
`;

const HelpSection = styled.div`
  margin-bottom: 16px;
`;

const HelpSubtitle = styled.h4`
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #495057;
`;

const HelpList = styled.ul`
  margin: 0;
  padding-left: 20px;
`;

const HelpItem = styled.li`
  font-size: 13px;
  color: #6c757d;
  margin-bottom: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
`;

const TipText = styled.div`
  font-size: 13px;
  color: #6c757d;
  font-style: italic;
  padding: 12px;
  background: rgba(52, 152, 219, 0.1);
  border-radius: 6px;
  border-left: 3px solid #3498db;
`;

export default Omnibox;
