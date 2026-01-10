/**
 * Create Sales Order Modal
 * 
 * Production-ready modal for creating new sales orders.
 * 
 * Features:
 * - Customer, Supplier, Product foreign key dropdowns
 * - Total amount and order date inputs
 * - Notes text area
 * - Form validation (required fields)
 * - Submits to sales-orders/ endpoint
 * - Auto-refreshes parent table on success
 * 
 * Usage:
 * ```tsx
 * <CreateOrderModal
 *   isOpen={showModal}
 *   onClose={() => setShowModal(false)}
 *   onSuccess={() => fetchOrders()}
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

interface CreateOrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface Customer {
  id: number;
  name: string;
}

interface Supplier {
  id: number;
  name: string;
}

interface Product {
  id: number;
  name: string;
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
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
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

export const CreateOrderModal: React.FC<CreateOrderModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    customer: '',
    supplier: '',
    product: '',
    total_amount: '',
    order_date: new Date().toISOString().split('T')[0],
    notes: '',
  });

  // Load dropdown data when modal opens
  useEffect(() => {
    if (isOpen) {
      loadDropdownData();
      // Reset form
      setFormData({
        customer: '',
        supplier: '',
        product: '',
        total_amount: '',
        order_date: new Date().toISOString().split('T')[0],
        notes: '',
      });
      setError(null);
    }
  }, [isOpen]);

  const loadDropdownData = async () => {
    try {
      setLoading(true);
      
      const [customersRes, suppliersRes, productsRes] = await Promise.allSettled([
        apiClient.get('customers/'),
        apiClient.get('suppliers/'),
        apiClient.get('products/'),
      ]);

      // Handle customers
      if (customersRes.status === 'fulfilled') {
        setCustomers(customersRes.value.data.results || customersRes.value.data || []);
      } else {
        console.error('Failed to load customers:', customersRes.reason);
        setCustomers([]);
      }

      // Handle suppliers
      if (suppliersRes.status === 'fulfilled') {
        setSuppliers(suppliersRes.value.data.results || suppliersRes.value.data || []);
      } else {
        console.error('Failed to load suppliers:', suppliersRes.reason);
        setSuppliers([]);
      }

      // Handle products with specific 404 check
      if (productsRes.status === 'fulfilled') {
        setProducts(productsRes.value.data.results || productsRes.value.data || []);
      } else {
        const error = productsRes.reason;
        if (error?.response?.status === 404) {
          console.warn('Products endpoint not available (404). Proceeding with empty product list.');
          setError('Products are currently unavailable. You can still create an order and add products later.');
        } else {
          console.error('Failed to load products:', error);
        }
        setProducts([]);
      }
    } catch (err: any) {
      console.error('Unexpected error loading dropdown data:', err);
      setError('Failed to load form options. Some fields may be unavailable.');
    } finally {
      setLoading(false);
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

  const validateForm = (): boolean => {
    if (!formData.customer) {
      setError('Customer is required');
      return false;
    }
    if (!formData.supplier) {
      setError('Supplier is required');
      return false;
    }
    if (!formData.product) {
      setError('Product is required');
      return false;
    }
    if (!formData.total_amount || parseFloat(formData.total_amount) <= 0) {
      setError('Total amount must be greater than zero');
      return false;
    }
    if (!formData.order_date) {
      setError('Order date is required');
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

      const payload = {
        customer: parseInt(formData.customer),
        supplier: parseInt(formData.supplier),
        product: parseInt(formData.product),
        total_amount: parseFloat(formData.total_amount),
        order_date: formData.order_date,
        notes: formData.notes,
      };

      await apiClient.post('sales-orders/', payload);

      // Success!
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Failed to create sales order:', err);
      setError(err.response?.data?.message || err.response?.data?.detail || 'Failed to create sales order');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Overlay isOpen={isOpen} onClick={onClose}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>Create Sales Order</ModalTitle>
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
              <SearchableSelect
                label="Supplier"
                value={formData.supplier}
                options={suppliers}
                onChange={(value) => handleSelectChange('supplier', value)}
                placeholder="Select Supplier"
                required
              />
            </FormGroup>

            <FormGroup>
              <SearchableSelect
                label="Product"
                value={formData.product}
                options={products}
                onChange={(value) => handleSelectChange('product', value)}
                placeholder="Select Product"
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
              <Label htmlFor="order_date">
                Order Date<Required>*</Required>
              </Label>
              <Input
                id="order_date"
                name="order_date"
                type="date"
                value={formData.order_date}
                onChange={handleChange}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="notes">Notes</Label>
              <TextArea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                placeholder="Optional notes about this order..."
              />
            </FormGroup>
          </ModalBody>

          <ModalFooter>
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Order'}
            </Button>
          </ModalFooter>
        </form>
      </Modal>
    </Overlay>
  );
};

export default CreateOrderModal;
