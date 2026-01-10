/**
 * Create Claim Modal
 * 
 * Production-ready modal for creating payable/receivable claims.
 * 
 * Features:
 * - Claim type (Payable/Receivable)
 * - Dynamic entity selector (PO/SO/Invoice based on type)
 * - Claimed amount and reason inputs
 * - Claim date (defaults to today)
 * - Form validation (required fields)
 * - Submits to claims/ endpoint
 * - Auto-refreshes parent table on success
 * 
 * Usage:
 * ```tsx
 * <CreateClaimModal
 *   isOpen={showModal}
 *   onClose={() => setShowModal(false)}
 *   onSuccess={() => fetchClaims()}
 *   defaultClaimType="payable"  // Optional: pre-select claim type
 * />
 * ```
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiClient } from '../../services/apiService';
import { SearchableSelect } from './SearchableSelect';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface CreateClaimModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  defaultClaimType?: 'payable' | 'receivable';
}

interface LinkedEntity {
  id: number;
  reference: string; // PO number, SO number, or Invoice number
}

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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
`;

const ModalHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid rgb(var(--color-border));
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ModalTitle = styled.h2`
  font-size: 32px;
  font-weight: 700;
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

const Required = styled.span`
  color: rgba(239, 68, 68, 1);
  margin-left: 0.25rem;
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
  min-height: 100px;
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

export const CreateClaimModal: React.FC<CreateClaimModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  defaultClaimType = 'payable',
}) => {
  const [linkedEntities, setLinkedEntities] = useState<LinkedEntity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    claim_type: defaultClaimType,
    linked_entity: '',
    claimed_amount: '',
    reason: '',
    description: '',
    claim_date: new Date().toISOString().split('T')[0],
  });

  // Load linked entities when claim type changes
  useEffect(() => {
    if (isOpen && formData.claim_type) {
      loadLinkedEntities(formData.claim_type);
    }
  }, [isOpen, formData.claim_type]);

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setFormData({
        claim_type: defaultClaimType,
        linked_entity: '',
        claimed_amount: '',
        reason: '',
        description: '',
        claim_date: new Date().toISOString().split('T')[0],
      });
      setError(null);
    }
  }, [isOpen, defaultClaimType]);

  const loadLinkedEntities = async (claimType: string) => {
    try {
      let endpoint = '';
      
      if (claimType === 'payable') {
        // Payable claims link to Purchase Orders
        endpoint = 'purchase-orders/';
      } else {
        // Receivable claims link to Sales Orders or Invoices
        // For now, load sales orders
        endpoint = 'sales-orders/';
      }

      const response = await apiClient.get(endpoint);
      const data = response.data.results || response.data || [];
      
      // Transform to unified format
      const entities = data.map((item: any) => ({
        id: item.id,
        reference: item.order_number || item.invoice_number || `#${item.id}`,
      }));

      setLinkedEntities(entities);
    } catch (err: any) {
      console.error('Failed to load linked entities:', err);
      setError('Failed to load available entities. Please try again.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSelectChange = (name: string, value: string | number) => {
    setFormData(prev => ({ ...prev, [name]: String(value) }));
    setError(null);
  };

  const handleClaimTypeChange = (name: string, value: string | number) => {
    setFormData(prev => ({ ...prev, [name]: String(value), linked_entity: '' }));
    setError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.claim_type) {
      setError('Claim type is required');
      return false;
    }
    if (!formData.linked_entity) {
      setError('Linked entity is required');
      return false;
    }
    if (!formData.claimed_amount || parseFloat(formData.claimed_amount) <= 0) {
      setError('Claimed amount must be greater than zero');
      return false;
    }
    if (!formData.reason) {
      setError('Reason is required');
      return false;
    }
    if (!formData.description) {
      setError('Description is required');
      return false;
    }
    if (!formData.claim_date) {
      setError('Claim date is required');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const payload: any = {
        claim_type: formData.claim_type,
        claimed_amount: parseFloat(formData.claimed_amount),
        reason: formData.reason,
        description: formData.description,
        claim_date: formData.claim_date,
      };

      // Set the appropriate linked entity field based on claim type
      if (formData.claim_type === 'payable') {
        payload.purchase_order = parseInt(formData.linked_entity);
      } else {
        payload.sales_order = parseInt(formData.linked_entity);
      }

      await apiClient.post('claims/', payload);

      // Success!
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Failed to create claim:', err);
      setError(err.response?.data?.message || err.response?.data?.detail || 'Failed to create claim');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getEntityLabel = () => {
    if (formData.claim_type === 'payable') {
      return 'Purchase Order';
    }
    return 'Sales Order / Invoice';
  };

  return (
    <Overlay isOpen={isOpen} onClick={onClose}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>Create Claim</ModalTitle>
          <CloseButton onClick={onClose}>×</CloseButton>
        </ModalHeader>

        <form onSubmit={handleSubmit}>
          <ModalBody>
            {error && <ErrorText style={{ marginBottom: '1rem' }}>{error}</ErrorText>}

            <FormGroup>
              <SearchableSelect
                label="Claim Type"
                value={formData.claim_type}
                options={[
                  { id: 'payable', name: 'Payable (to Supplier)' },
                  { id: 'receivable', name: 'Receivable (from Customer)' },
                ]}
                onChange={(value) => handleClaimTypeChange('claim_type', value)}
                placeholder="Select Claim Type"
                required
              />
              <HelpText>
                Payable: Money we owe | Receivable: Money owed to us
              </HelpText>
            </FormGroup>

            <FormGroup>
              <SearchableSelect
                label={getEntityLabel()}
                value={formData.linked_entity}
                options={linkedEntities}
                onChange={(value) => handleSelectChange('linked_entity', value)}
                placeholder={`Select ${getEntityLabel()}`}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="claimed_amount">
                Claimed Amount<Required>*</Required>
              </Label>
              <Input
                id="claimed_amount"
                name="claimed_amount"
                type="number"
                step="0.01"
                min="0.01"
                value={formData.claimed_amount}
                onChange={handleChange}
                placeholder="0.00"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="reason">
                Reason<Required>*</Required>
              </Label>
              <Input
                id="reason"
                name="reason"
                type="text"
                value={formData.reason}
                onChange={handleChange}
                placeholder="e.g., Damaged goods, Late delivery, Pricing discrepancy"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="description">
                Description<Required>*</Required>
              </Label>
              <TextArea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Provide detailed description of the claim..."
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="claim_date">
                Claim Date<Required>*</Required>
              </Label>
              <Input
                id="claim_date"
                name="claim_date"
                type="date"
                value={formData.claim_date}
                onChange={handleChange}
                max={new Date().toISOString().split('T')[0]}
                required
              />
            </FormGroup>
          </ModalBody>

          <ModalFooter>
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Claim'}
            </Button>
          </ModalFooter>
        </form>
      </Modal>
    </Overlay>
  );
};

export default CreateClaimModal;
