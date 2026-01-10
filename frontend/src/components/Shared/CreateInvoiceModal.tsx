/**
 * Create Invoice Modal
 * 
 * Production-ready modal for creating customer invoices.
 * 
 * Features:
 * - Customer foreign key dropdown
 * - Sales order reference text input
 * - Invoice and due date inputs
 * - Total amount input
 * - Payment terms dropdown (Wire/ACH/Check/Credit Card)
 * - Form validation (required fields)
 * - Submits to invoices/ endpoint
 * - Auto-refreshes parent table on success
 * 
 * Usage:
 * ```tsx
 * <CreateInvoiceModal
 *   isOpen={showModal}
 *   onClose={() => setShowModal(false)}
 *   onSuccess={() => fetchInvoices()}
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

interface CreateInvoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface Customer {
  id: number;
  name: string;
}

type PaymentTerms = 'wire' | 'ach' | 'check' | 'credit_card';

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

export const CreateInvoiceModal: React.FC<CreateInvoiceModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    customer: '',
    sales_order_ref: '',
    invoice_date: new Date().toISOString().split('T')[0],
    due_date: '',
    total_amount: '',
    payment_terms: 'wire' as PaymentTerms,
  });

  // Load customers when modal opens
  useEffect(() => {
    if (isOpen) {
      loadCustomers();
      // Reset form
      const today = new Date().toISOString().split('T')[0];
      const thirtyDaysLater = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      setFormData({
        customer: '',
        sales_order_ref: '',
        invoice_date: today,
        due_date: thirtyDaysLater,
        total_amount: '',
        payment_terms: 'wire',
      });
      setError(null);
    }
  }, [isOpen]);

  const loadCustomers = async () => {
    try {
      const response = await apiClient.get('customers/');
      setCustomers(response.data.results || response.data || []);
    } catch (err: any) {
      console.error('Failed to load customers:', err);
      setError('Failed to load customers. Please try again.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSelectChange = (name: string, value: string | number) => {
    setFormData(prev => ({ ...prev, [name]: String(value) }));
    setError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.customer) {
      setError('Customer is required');
      return false;
    }
    if (!formData.invoice_date) {
      setError('Invoice date is required');
      return false;
    }
    if (!formData.due_date) {
      setError('Due date is required');
      return false;
    }
    if (formData.due_date < formData.invoice_date) {
      setError('Due date cannot be before invoice date');
      return false;
    }
    if (!formData.total_amount || parseFloat(formData.total_amount) <= 0) {
      setError('Total amount must be greater than zero');
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
        customer: parseInt(formData.customer),
        date_time_stamp: formData.invoice_date,
        due_date: formData.due_date,
        total_amount: parseFloat(formData.total_amount),
        payment_terms: formData.payment_terms,
      };

      // Include sales order reference if provided
      if (formData.sales_order_ref) {
        payload.our_sales_order_num = formData.sales_order_ref;
      }

      await apiClient.post('invoices/', payload);

      // Success!
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Failed to create invoice:', err);
      setError(err.response?.data?.message || err.response?.data?.detail || 'Failed to create invoice');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Overlay isOpen={isOpen} onClick={onClose}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>Create Invoice</ModalTitle>
          <CloseButton onClick={onClose}>×</CloseButton>
        </ModalHeader>

        <form onSubmit={handleSubmit}>
          <ModalBody>
            {error && <ErrorText style={{ marginBottom: '1rem' }}>{error}</ErrorText>}

            <FormGroup>
              <SearchableSelect
                label="Customer"
                value={formData.customer}
                options={customers}
                onChange={(value) => handleSelectChange('customer', value)}
                placeholder="Select Customer"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="sales_order_ref">Sales Order Reference</Label>
              <Input
                id="sales_order_ref"
                name="sales_order_ref"
                type="text"
                value={formData.sales_order_ref}
                onChange={handleChange}
                placeholder="e.g., SO-2026-001"
              />
              <HelpText>Optional: Link to a sales order</HelpText>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="invoice_date">
                Invoice Date<Required>*</Required>
              </Label>
              <Input
                id="invoice_date"
                name="invoice_date"
                type="date"
                value={formData.invoice_date}
                onChange={handleChange}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="due_date">
                Due Date<Required>*</Required>
              </Label>
              <Input
                id="due_date"
                name="due_date"
                type="date"
                value={formData.due_date}
                onChange={handleChange}
                min={formData.invoice_date}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="total_amount">
                Total Amount<Required>*</Required>
              </Label>
              <Input
                id="total_amount"
                name="total_amount"
                type="number"
                step="0.01"
                min="0.01"
                value={formData.total_amount}
                onChange={handleChange}
                placeholder="0.00"
                required
              />
            </FormGroup>

            <FormGroup>
              <SearchableSelect
                label="Payment Terms"
                value={formData.payment_terms}
                options={[
                  { id: 'wire', name: 'Wire Transfer' },
                  { id: 'ach', name: 'ACH' },
                  { id: 'check', name: 'Check' },
                  { id: 'credit_card', name: 'Credit Card' },
                ]}
                onChange={(value) => handleSelectChange('payment_terms', value)}
                placeholder="Select Payment Terms"
                required
              />
            </FormGroup>
          </ModalBody>

          <ModalFooter>
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Invoice'}
            </Button>
          </ModalFooter>
        </form>
      </Modal>
    </Overlay>
  );
};

export default CreateInvoiceModal;
