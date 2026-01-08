/**
 * Record Payment Modal
 * 
 * Universal modal for recording payments against Purchase Orders, Sales Orders, or Invoices.
 * 
 * Features:
 * - Pre-fills amount with outstanding balance
 * - Payment method dropdown (Check, Wire, ACH, Credit Card, Cash)
 * - Reference number input (check#, wire confirmation, etc.)
 * - Date picker (defaults to today)
 * - Notes field
 * - Validates amount doesn't exceed outstanding
 * - Submits to /api/v1/payments/
 * - Auto-refreshes parent data on success
 * 
 * Usage:
 * ```tsx
 * <RecordPaymentModal
 *   isOpen={showModal}
 *   onClose={() => setShowModal(false)}
 *   entityType="purchase_order"
 *   entityId={order.id}
 *   entityReference="PO-2026-001"
 *   outstandingAmount={5000.00}
 *   onSuccess={() => fetchOrders()}
 * />
 * ```
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiClient } from '../../services/apiService';
import { formatCurrency } from '../../shared/utils';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface RecordPaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  entityType: 'purchase_order' | 'sales_order' | 'invoice';
  entityId: number;
  entityReference: string;  // PO-2026-001, SO-2026-001, INV-2026-001
  outstandingAmount: number;
  onSuccess: () => void;
}

type PaymentMethod = 'check' | 'wire' | 'ach' | 'credit_card' | 'cash' | 'other';

// ============================================================================
// Styled Components (Theme-Compliant)
// ============================================================================

const Overlay = styled.div<{ isOpen: boolean }>`
  display: ${props => props.isOpen ? 'flex' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  padding: 1rem;
`;

const Modal = styled.div`
  background: rgb(var(--color-surface));
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
`;

const ModalHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid rgb(var(--color-border));
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const ModalTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0;
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: rgb(var(--color-text-secondary));
  cursor: pointer;
  font-size: 1.5rem;
  line-height: 1;
  padding: 0;
  
  &:hover {
    color: rgb(var(--color-text-primary));
  }
`;

const ModalBody = styled.div`
  padding: 1.5rem;
`;

const EntityInfo = styled.div`
  background: rgba(var(--color-primary), 0.05);
  border: 1px solid rgba(var(--color-primary), 0.2);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1.5rem;
`;

const InfoLabel = styled.div`
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgb(var(--color-text-secondary));
  margin-bottom: 0.25rem;
`;

const InfoValue = styled.div`
  font-size: 1rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
`;

const FormGroup = styled.div`
  margin-bottom: 1.25rem;
`;

const Label = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(var(--color-text-primary));
  margin-bottom: 0.5rem;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  background: rgb(var(--color-background));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  
  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }
  
  &::placeholder {
    color: rgb(var(--color-text-secondary));
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  background: rgb(var(--color-background));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  background: rgb(var(--color-background));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  min-height: 80px;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }
  
  &::placeholder {
    color: rgb(var(--color-text-secondary));
  }
`;

const HelpText = styled.div`
  font-size: 0.75rem;
  color: rgb(var(--color-text-secondary));
  margin-top: 0.25rem;
`;

const ErrorText = styled.div`
  font-size: 0.75rem;
  color: rgba(239, 68, 68, 1);
  margin-top: 0.25rem;
`;

const ModalFooter = styled.div`
  padding: 1.5rem;
  border-top: 1px solid rgb(var(--color-border));
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 0.75rem 1.5rem;
  background: ${props => props.variant === 'primary' ? 'rgb(var(--color-primary))' : 'rgb(var(--color-surface))'};
  color: ${props => props.variant === 'primary' ? 'white' : 'rgb(var(--color-text-primary))'};
  border: 1px solid ${props => props.variant === 'primary' ? 'rgb(var(--color-primary))' : 'rgb(var(--color-border))'};
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// ============================================================================
// Main Component
// ============================================================================

export const RecordPaymentModal: React.FC<RecordPaymentModalProps> = ({
  isOpen,
  onClose,
  entityType,
  entityId,
  entityReference,
  outstandingAmount,
  onSuccess,
}) => {
  const [amount, setAmount] = useState(outstandingAmount.toString());
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split('T')[0]);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('check');
  const [referenceNumber, setReferenceNumber] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setAmount(outstandingAmount.toString());
      setPaymentDate(new Date().toISOString().split('T')[0]);
      setPaymentMethod('check');
      setReferenceNumber('');
      setNotes('');
      setError(null);
    }
  }, [isOpen, outstandingAmount]);

  const validateAmount = () => {
    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      setError('Amount must be greater than zero');
      return false;
    }
    if (amountNum > outstandingAmount) {
      setError(`Amount cannot exceed outstanding balance of ${formatCurrency(outstandingAmount)}`);
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateAmount()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const payload: any = {
        amount: parseFloat(amount),
        payment_date: paymentDate,
        payment_method: paymentMethod,
        reference_number: referenceNumber,
        notes: notes,
      };

      // Set the appropriate entity field
      payload[entityType] = entityId;

      await apiClient.post('/api/v1/payments/', payload);

      // Success!
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Failed to record payment:', err);
      setError(err.response?.data?.message || 'Failed to record payment');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Overlay isOpen={isOpen} onClick={onClose}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>Record Payment</ModalTitle>
          <CloseButton onClick={onClose}>×</CloseButton>
        </ModalHeader>

        <form onSubmit={handleSubmit}>
          <ModalBody>
            <EntityInfo>
              <InfoLabel>Recording payment for:</InfoLabel>
              <InfoValue>{entityReference}</InfoValue>
              <div style={{ marginTop: '0.5rem' }}>
                <InfoLabel>Outstanding Balance:</InfoLabel>
                <InfoValue style={{ color: 'rgba(239, 68, 68, 1)' }}>
                  {formatCurrency(outstandingAmount)}
                </InfoValue>
              </div>
            </EntityInfo>

            <FormGroup>
              <Label htmlFor="amount">Payment Amount *</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                min="0.01"
                max={outstandingAmount}
                value={amount}
                onChange={(e) => {
                  setAmount(e.target.value);
                  setError(null);
                }}
                required
              />
              {error && <ErrorText>{error}</ErrorText>}
            </FormGroup>

            <FormGroup>
              <Label htmlFor="payment_date">Payment Date *</Label>
              <Input
                id="payment_date"
                type="date"
                value={paymentDate}
                onChange={(e) => setPaymentDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="payment_method">Payment Method *</Label>
              <Select
                id="payment_method"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value as PaymentMethod)}
                required
              >
                <option value="check">Check</option>
                <option value="wire">Wire Transfer</option>
                <option value="ach">ACH</option>
                <option value="credit_card">Credit Card</option>
                <option value="cash">Cash</option>
                <option value="other">Other</option>
              </Select>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="reference_number">Reference Number</Label>
              <Input
                id="reference_number"
                type="text"
                placeholder="Check #, Wire confirmation, etc."
                value={referenceNumber}
                onChange={(e) => setReferenceNumber(e.target.value)}
              />
              <HelpText>
                Enter check number, wire confirmation, or transaction ID
              </HelpText>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="notes">Notes</Label>
              <TextArea
                id="notes"
                placeholder="Additional notes about this payment..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </FormGroup>
          </ModalBody>

          <ModalFooter>
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Recording...' : 'Record Payment'}
            </Button>
          </ModalFooter>
        </form>
      </Modal>
    </Overlay>
  );
};

export default RecordPaymentModal;
