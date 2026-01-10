/**
 * Shared Modal Component - Theme-Compliant
 * 
 * Features:
 * - Uses CSS custom properties for theming
 * - Responsive design (mobile-friendly)
 * - Portal-based rendering
 * - Backdrop click to close
 * - Accessible (ARIA labels, focus management)
 * 
 * Usage:
 * ```tsx
 * <Modal isOpen={show} onClose={handleClose} title="My Modal">
 *   <p>Modal content here</p>
 * </Modal>
 * ```
 */
import React from 'react';
import ReactDOM from 'react-dom';
import styled from 'styled-components';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: string;
  footer?: React.ReactNode; // Optional footer with action buttons
}

const Modal: React.FC<ModalProps> = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  maxWidth = '600px',
  footer 
}) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Handle Escape key
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  return ReactDOM.createPortal(
    <ModalBackdrop onClick={handleBackdropClick} role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <ModalContainer maxWidth={maxWidth}>
        <ModalHeader>
          <ModalTitle id="modal-title">{title}</ModalTitle>
          <CloseButton onClick={onClose} aria-label="Close modal">&times;</CloseButton>
        </ModalHeader>
        <ModalContent>{children}</ModalContent>
        {footer && <ModalFooter>{footer}</ModalFooter>}
      </ModalContainer>
    </ModalBackdrop>,
    document.body
  );
};

const ModalBackdrop = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  
  /* Prevent body scroll when modal is open */
  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }
`;

const ModalContainer = styled.div<{ maxWidth: string }>`
  background: rgb(var(--color-surface));
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: ${(props) => props.maxWidth};
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  /* Responsive: Full width on mobile */
  @media (max-width: 640px) {
    max-width: calc(100vw - 2rem);
    max-height: calc(100vh - 2rem);
  }
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgb(var(--color-border));
  background: rgb(var(--color-surface-hover));
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: rgb(var(--color-text-secondary));
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
  line-height: 1;

  &:hover {
    color: rgb(var(--color-text-primary));
    background: rgba(var(--color-text-primary), 0.1);
  }
  
  &:focus {
    outline: 2px solid rgb(var(--color-primary));
    outline-offset: 2px;
  }
`;

const ModalContent = styled.div`
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  color: rgb(var(--color-text-primary));
  
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
`;

const ModalFooter = styled.div`
  padding: 1.5rem;
  border-top: 1px solid rgb(var(--color-border));
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  background: rgb(var(--color-surface-hover));
  
  /* Stack buttons on mobile */
  @media (max-width: 640px) {
    flex-direction: column-reverse;
    
    button {
      width: 100%;
    }
  }
`;

export default Modal;
