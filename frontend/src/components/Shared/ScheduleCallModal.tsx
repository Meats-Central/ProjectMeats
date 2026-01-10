/**
 * Enhanced Schedule Call Modal - CRUD Support
 * 
 * Features:
 * - Create new calls
 * - Edit existing calls (via initialData prop)
 * - Full form validation
 * - Theme-compliant styling
 * 
 * Usage:
 * ```tsx
 * // Create new
 * <ScheduleCallModal isOpen={show} onClose={...} onSuccess={...} />
 * 
 * // Edit existing
 * <ScheduleCallModal 
 *   isOpen={show}
 *   initialData={call}
 *   onClose={...}
 *   onSuccess={...}
 * />
 * ```
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiClient } from '../../services/apiService';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

export interface ScheduledCallData {
  id?: number;
  tenant?: string;
  entity_type: string;
  entity_id: number;
  title: string;
  description: string;
  scheduled_for: string;
  duration_minutes: number;
  call_purpose: string;
  outcome?: string;
  is_completed?: boolean;
  created_by?: number | null;
  created_by_name?: string;
  created_on?: string;
  updated_on?: string;
}

interface ScheduleCallModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  initialData?: ScheduledCallData | null;  // For editing
}

type EntityType = 'supplier' | 'customer' | 'plant' | 'purchase_order' | 'sales_order' | 'carrier' | 'product' | 'invoice' | 'contact';

// ============================================================================
// Styled Components (Theme-Compliant)
// ============================================================================

const Overlay = styled.div<{ isOpen: boolean }>`
  display: \${props => props.isOpen ? 'flex' : 'none'};
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
  max-width: 550px;
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
  padding: 0.625rem;
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-text-primary));
  
  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
    box-shadow: 0 0 0 3px rgba(var(--color-primary), 0.1);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.625rem;
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-text-primary));
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
    box-shadow: 0 0 0 3px rgba(var(--color-primary), 0.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.625rem;
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-text-primary));
  min-height: 80px;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
    box-shadow: 0 0 0 3px rgba(var(--color-primary), 0.1);
  }
`;

const ModalFooter = styled.div`
  padding: 1.5rem;
  border-top: 1px solid rgb(var(--color-border));
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
`;

const CancelButton = styled.button`
  padding: 0.625rem 1.25rem;
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  background: transparent;
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    background: rgba(var(--color-text-primary), 0.05);
  }
`;

const SubmitButton = styled.button`
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: var(--radius-md);
  background: rgb(var(--color-primary));
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  
  &:hover:not(:disabled) {
    opacity: 0.9;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(220, 38, 38, 0.1);
  border-radius: var(--radius-md);
`;

const HelpText = styled.p`
  font-size: 0.75rem;
  color: rgb(var(--color-text-secondary));
  margin-top: 0.25rem;
`;

// ============================================================================
// Component
// ============================================================================

export const ScheduleCallModal: React.FC<ScheduleCallModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialData,
}) => {
  const isEditMode = !!initialData?.id;
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [entityType, setEntityType] = useState<EntityType>('customer');
  const [entityId, setEntityId] = useState('');
  const [scheduledFor, setScheduledFor] = useState('');
  const [durationMinutes, setDurationMinutes] = useState('30');
  const [callPurpose, setCallPurpose] = useState('follow_up');
  const [outcome, setOutcome] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial data for editing
  useEffect(() => {
    if (initialData && isOpen) {
      setTitle(initialData.title || '');
      setDescription(initialData.description || '');
      setEntityType(initialData.entity_type as EntityType || 'customer');
      setEntityId(String(initialData.entity_id || ''));
      setScheduledFor(initialData.scheduled_for || '');
      setDurationMinutes(String(initialData.duration_minutes || 30));
      setCallPurpose(initialData.call_purpose || 'follow_up');
      setOutcome(initialData.outcome || '');
    } else if (isOpen) {
      resetForm();
    }
  }, [initialData, isOpen]);

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setEntityType('customer');
    setEntityId('');
    setScheduledFor('');
    setDurationMinutes('30');
    setCallPurpose('follow_up');
    setOutcome('');
    setError(null);
  };

  const handleClose = () => {
    if (!submitting) {
      resetForm();
      onClose();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (!entityId || isNaN(Number(entityId))) {
      setError('Valid Entity ID is required');
      return;
    }

    if (!scheduledFor) {
      setError('Scheduled date and time is required');
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        title: title.trim(),
        description: description.trim(),
        entity_type: entityType,
        entity_id: Number(entityId),
        scheduled_for: scheduledFor,
        duration_minutes: Number(durationMinutes),
        call_purpose: callPurpose,
        ...(outcome && { outcome: outcome.trim() }),
      };

      if (isEditMode && initialData?.id) {
        // Update existing call
        await apiClient.patch(\`cockpit/scheduled-calls/\${initialData.id}/\`, payload);
      } else {
        // Create new call
        await apiClient.post('cockpit/scheduled-calls/', payload);
      }

      // Success
      resetForm();
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error(\`Failed to \${isEditMode ? 'update' : 'schedule'} call:\`, err);
      setError(err.response?.data?.detail || err.response?.data?.message || \`Failed to \${isEditMode ? 'update' : 'schedule'} call. Please try again.\`);
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Overlay isOpen={isOpen} onClick={handleClose}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <form onSubmit={handleSubmit}>
          <ModalHeader>
            <ModalTitle>{isEditMode ? 'Edit Call' : 'Schedule New Call'}</ModalTitle>
            <CloseButton type="button" onClick={handleClose}>&times;</CloseButton>
          </ModalHeader>

          <ModalBody>
            <FormGroup>
              <Label>Call Title *</Label>
              <Input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Follow-up on order inquiry"
                maxLength={200}
                disabled={submitting}
              />
            </FormGroup>

            <FormGroup>
              <Label>Description</Label>
              <TextArea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add notes about what to discuss..."
                disabled={submitting}
              />
            </FormGroup>

            <FormGroup>
              <Label>Entity Type *</Label>
              <Select
                value={entityType}
                onChange={(e) => setEntityType(e.target.value as EntityType)}
                disabled={submitting}
              >
                <option value="customer">Customer</option>
                <option value="supplier">Supplier</option>
                <option value="contact">Contact</option>
                <option value="sales_order">Sales Order</option>
                <option value="purchase_order">Purchase Order</option>
                <option value="invoice">Invoice</option>
                <option value="plant">Plant</option>
                <option value="carrier">Carrier</option>
                <option value="product">Product</option>
              </Select>
              <HelpText>Who or what is this call about?</HelpText>
            </FormGroup>

            <FormGroup>
              <Label>Entity ID *</Label>
              <Input
                type="number"
                value={entityId}
                onChange={(e) => setEntityId(e.target.value)}
                placeholder="e.g., 123"
                min="1"
                disabled={submitting}
              />
              <HelpText>The database ID of the selected entity</HelpText>
            </FormGroup>

            <FormGroup>
              <Label>Scheduled For *</Label>
              <Input
                type="datetime-local"
                value={scheduledFor}
                onChange={(e) => setScheduledFor(e.target.value)}
                disabled={submitting}
              />
            </FormGroup>

            <FormGroup>
              <Label>Duration (minutes)</Label>
              <Input
                type="number"
                value={durationMinutes}
                onChange={(e) => setDurationMinutes(e.target.value)}
                min="5"
                max="480"
                step="5"
                disabled={submitting}
              />
            </FormGroup>

            <FormGroup>
              <Label>Call Purpose</Label>
              <Select
                value={callPurpose}
                onChange={(e) => setCallPurpose(e.target.value)}
                disabled={submitting}
              >
                <option value="follow_up">Follow-up</option>
                <option value="inquiry">Inquiry</option>
                <option value="complaint">Complaint</option>
                <option value="order">Order</option>
                <option value="support">Support</option>
                <option value="other">Other</option>
              </Select>
            </FormGroup>

            {isEditMode && initialData?.is_completed && (
              <FormGroup>
                <Label>Outcome</Label>
                <TextArea
                  value={outcome}
                  onChange={(e) => setOutcome(e.target.value)}
                  placeholder="What was the outcome of this call?"
                  disabled={submitting}
                />
              </FormGroup>
            )}

            {error && <ErrorMessage>{error}</ErrorMessage>}
          </ModalBody>

          <ModalFooter>
            <CancelButton type="button" onClick={handleClose} disabled={submitting}>
              Cancel
            </CancelButton>
            <SubmitButton type="submit" disabled={submitting}>
              {submitting ? (isEditMode ? 'Updating...' : 'Scheduling...') : (isEditMode ? 'Update Call' : 'Schedule Call')}
            </SubmitButton>
          </ModalFooter>
        </form>
      </Modal>
    </Overlay>
  );
};
