import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiService, PurchaseOrder, Supplier } from '../services/apiService';
import { LocationSelector } from '../components/Shared';
import PurchaseOrderWorkflow from '../components/Workflow/PurchaseOrderWorkflow';

// Styled Components
const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
`;

const AddButton = styled.button`
  background: rgb(var(--color-primary));
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgb(var(--color-primary-hover));
    transform: translateY(-1px);
  }
`;

const StatsCards = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: rgb(var(--color-surface));
  color: rgb(var(--color-surface-foreground));
  padding: 24px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  text-align: center;
  border: 1px solid rgb(var(--color-border));
  transition: box-shadow 0.2s ease, background-color 0.3s ease;
`;

const StatNumber = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: rgb(var(--color-primary));
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 60px 20px;
  font-size: 18px;
  color: #6c757d;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
`;

const EmptyIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
`;

const EmptyTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
`;

const EmptyDescription = styled.p`
  color: #6c757d;
  font-size: 16px;
`;

const Table = styled.table`
  width: 100%;
  background: rgb(var(--color-surface));
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid rgb(var(--color-border));
`;

const TableHeader = styled.thead`
  background: rgb(var(--color-surface-hover));
`;

const TableBody = styled.tbody``;

const TableRow = styled.tr`
  border-bottom: 1px solid rgb(var(--color-border));

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background-color: rgb(var(--color-surface-hover));
  }
`;

const TableHeaderCell = styled.th`
  text-align: left;
  padding: 16px 20px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
`;

const TableCell = styled.td`
  padding: 16px 20px;
  color: #495057;
  font-size: 14px;
`;

const StatusBadge = styled.span<{ $color: string }>`
  background: ${(props) => props.$color};
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
`;

const ActionButton = styled.button`
  background: #28a745;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  margin-right: 8px;
  transition: background 0.2s;

  &:hover {
    background: #218838;
  }
`;

const DeleteButton = styled.button`
  background: #dc3545;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #c82333;
  }
`;

const FormOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const FormContainer = styled.div`
  background: rgb(var(--color-surface));
  color: rgb(var(--color-surface-foreground));
  border-radius: 12px;
  padding: 0;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid rgb(var(--color-border));
`;

const FormHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e9ecef;
`;

const FormTitle = styled.h2`
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: #2c3e50;
  }
`;

const Form = styled.form`
  padding: 24px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }

  /* Hide number input spinner buttons */
  &[type='number']::-webkit-inner-spin-button,
  &[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  &[type='number'] {
    -moz-appearance: textfield;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }
`;

const FieldHint = styled.div`
  margin-top: 6px;
  font-size: 12px;
  color: #6c757d;
  font-style: italic;
`;

const FormActions = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
`;

const CancelButton = styled.button`
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #5a6268;
  }
`;

const SubmitButton = styled.button`
  background: rgb(var(--color-primary));
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: rgb(var(--color-primary-hover));
  }
`;

const PurchaseOrders: React.FC = () => {
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingPurchaseOrder, setEditingPurchaseOrder] = useState<PurchaseOrder | null>(null);
  const [formData, setFormData] = useState({
    order_number: '',
    supplier: '',
    total_amount: '',
    status: 'pending',
    order_date: '',
    delivery_date: '',
    notes: '',
    logistics_scenario: 'supplier_delivery',
    pick_up_location: null as string | null, // Phase 4: Location integration
    delivery_location: null as string | null, // Phase 4: Location integration
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [posData, suppliersData] = await Promise.all([
        apiService.getPurchaseOrders(),
        apiService.getSuppliers(),
      ]);
      setPurchaseOrders(posData);
      setSuppliers(suppliersData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPurchaseOrders = async () => {
    try {
      const data = await apiService.getPurchaseOrders();
      setPurchaseOrders(data);
    } catch (error) {
      console.error('Error loading purchase orders:', error);
    }
  };

  // Calculate next suggested order number
  const getNextOrderNumber = () => {
    if (purchaseOrders.length === 0) return '1';
    
    // Find highest numeric order number
    let maxNum = 0;
    purchaseOrders.forEach((po) => {
      const num = parseInt(po.order_number);
      if (!isNaN(num) && num > maxNum) {
        maxNum = num;
      }
    });
    
    return String(maxNum + 1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const purchaseOrderData: any = {
        ...formData,
        total_amount: parseFloat(formData.total_amount),
        supplier: parseInt(formData.supplier),
      };
      
      // Remove order_number if empty - let backend auto-generate
      if (!purchaseOrderData.order_number || purchaseOrderData.order_number.trim() === '') {
        purchaseOrderData.order_number = undefined;
      }

      if (editingPurchaseOrder) {
        await apiService.updatePurchaseOrder(editingPurchaseOrder.id, purchaseOrderData);
      } else {
        await apiService.createPurchaseOrder(purchaseOrderData);
      }

      await loadPurchaseOrders();
      setShowForm(false);
      setEditingPurchaseOrder(null);
      setFormData({
        order_number: '',
        supplier: '',
        total_amount: '',
        status: 'pending',
        order_date: '',
        delivery_date: '',
        notes: '',
        logistics_scenario: 'supplier_delivery',
        pick_up_location: null, // Phase 4: Reset location
        delivery_location: null, // Phase 4: Reset location
      });
    } catch (error: unknown) {
      // Log detailed error information
      const err = error as Error & { response?: { status: number; data: unknown }; stack?: string };
      console.error('Error saving purchase order:', {
        message: err.message || 'Unknown error',
        stack: err.stack || 'No stack trace available',
        response: err.response ? {
          status: err.response.status,
          data: err.response.data
        } : 'No response data'
      });
      // Display user-friendly error to the UI
      alert(`Failed to save purchase order: ${err.message || 'Please try again later'}`);
    }
  };

  const handleEdit = (purchaseOrder: PurchaseOrder) => {
    setEditingPurchaseOrder(purchaseOrder);
    setFormData({
      order_number: purchaseOrder.order_number,
      supplier: purchaseOrder.supplier.toString(),
      total_amount: purchaseOrder.total_amount.toString(),
      status: purchaseOrder.status,
      order_date: purchaseOrder.order_date,
      delivery_date: purchaseOrder.delivery_date || '',
      notes: purchaseOrder.notes || '',
      logistics_scenario: purchaseOrder.logistics_scenario || 'supplier_delivery',
      pick_up_location: purchaseOrder.pick_up_location || null, // Phase 4: Populate location
      delivery_location: purchaseOrder.delivery_location || null, // Phase 4: Populate location
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this purchase order?')) {
      try {
        await apiService.deletePurchaseOrder(id);
        alert('Purchase order deleted successfully!');
        await loadPurchaseOrders(); // Re-fetch to update the list
      } catch (error: unknown) {
        // Type-safe error handling: Use 'unknown' instead of 'any' and assert expected structure
        console.error('Error deleting purchase order:', error);
        const err = error as { response?: { data?: { detail?: string; message?: string } }; message?: string };
        const errorMessage = err?.response?.data?.detail 
          || err?.response?.data?.message 
          || err?.message 
          || 'Failed to delete purchase order';
        alert(`Error: ${errorMessage}`);
      }
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return '#ffc107';
      case 'approved':
        return '#28a745';
      case 'delivered':
        return 'rgb(var(--color-primary))';
      case 'cancelled':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  if (loading) {
    return <LoadingMessage>Loading purchase orders...</LoadingMessage>;
  }

  return (
    <>
      <Header>
        <Title>Purchase Orders</Title>
        <AddButton
          onClick={() => {
            setFormData({
              order_number: getNextOrderNumber(),
              supplier: '',
              total_amount: '',
              status: 'pending',
              order_date: '',
              delivery_date: '',
              notes: '',
              logistics_scenario: 'supplier_delivery',
              pick_up_location: null, // Phase 4: Reset location
              delivery_location: null, // Phase 4: Reset location
            });
            setShowForm(true);
          }}
        >
          + Add Purchase Order
        </AddButton>
      </Header>

      <StatsCards>
        <StatCard>
          <StatNumber>{purchaseOrders.length}</StatNumber>
          <StatLabel>Total Orders</StatLabel>
        </StatCard>
        <StatCard>
          <StatNumber>{purchaseOrders.filter((po) => po.status === 'pending').length}</StatNumber>
          <StatLabel>Pending</StatLabel>
        </StatCard>
        <StatCard>
          <StatNumber>{purchaseOrders.filter((po) => po.status === 'approved').length}</StatNumber>
          <StatLabel>Approved</StatLabel>
        </StatCard>
        <StatCard>
          <StatNumber>
            $
            {Array.isArray(purchaseOrders)
              ? purchaseOrders
                  .reduce((sum, po) => sum + (Number(po.total_amount) || 0), 0)
                  .toFixed(2)
              : '0.00'}
          </StatNumber>
          <StatLabel>Total Value</StatLabel>
        </StatCard>
      </StatsCards>

      {/* Sample Workflow Visualization */}
      <PurchaseOrderWorkflow
        stages={[
          {
            id: 'draft',
            label: 'Draft',
            status: 'completed',
            description: 'Order created',
          },
          {
            id: 'approval',
            label: 'Approval',
            status: 'completed',
            description: 'Management review',
          },
          {
            id: 'processing',
            label: 'Processing',
            status: 'active',
            description: 'Supplier processing',
          },
          {
            id: 'shipping',
            label: 'Shipping',
            status: 'pending',
            description: 'In transit',
          },
          {
            id: 'delivered',
            label: 'Delivered',
            status: 'pending',
            description: 'Order complete',
          },
        ]}
      />

      {purchaseOrders.length === 0 ? (
        <EmptyState>
          <EmptyIcon>📋</EmptyIcon>
          <EmptyTitle>No Purchase Orders</EmptyTitle>
          <EmptyDescription>Get started by creating your first purchase order</EmptyDescription>
        </EmptyState>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHeaderCell>Order Number</TableHeaderCell>
              <TableHeaderCell>Supplier</TableHeaderCell>
              <TableHeaderCell>Amount</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Order Date</TableHeaderCell>
              <TableHeaderCell>Delivery Date</TableHeaderCell>
              <TableHeaderCell>Actions</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {purchaseOrders.map((purchaseOrder) => {
              const supplier = suppliers.find((s) => s.id === purchaseOrder.supplier);
              return (
                <TableRow key={purchaseOrder.id}>
                  <TableCell>{purchaseOrder.order_number}</TableCell>
                  <TableCell>{supplier?.name || `ID: ${purchaseOrder.supplier}`}</TableCell>
                  <TableCell>
                    {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'USD',
                    }).format(Number(purchaseOrder.total_amount) || 0)}
                  </TableCell>
                  <TableCell>
                    <StatusBadge $color={getStatusColor(purchaseOrder.status)}>
                      {purchaseOrder.status.toUpperCase()}
                    </StatusBadge>
                  </TableCell>
                  <TableCell>{new Date(purchaseOrder.order_date).toLocaleDateString()}</TableCell>
                  <TableCell>
                    {purchaseOrder.delivery_date
                      ? new Date(purchaseOrder.delivery_date).toLocaleDateString()
                      : 'Not set'}
                  </TableCell>
                  <TableCell>
                    <ActionButton onClick={() => handleEdit(purchaseOrder)}>Edit</ActionButton>
                    <DeleteButton onClick={() => handleDelete(purchaseOrder.id)}>Delete</DeleteButton>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {showForm && (
        <FormOverlay>
          <FormContainer>
            <FormHeader>
              <FormTitle>
                {editingPurchaseOrder ? 'Edit Purchase Order' : 'Add New Purchase Order'}
              </FormTitle>
              <CloseButton onClick={() => setShowForm(false)}>×</CloseButton>
            </FormHeader>
            <Form onSubmit={handleSubmit}>
              <FormGroup>
                <Label>Logistics Scenario</Label>
                <Select 
                  name="logistics_scenario" 
                  value={formData.logistics_scenario} 
                  onChange={handleInputChange}
                  required
                >
                  <option value="customer_pickup">Customer Pickup</option>
                  <option value="supplier_delivery">Supplier Delivery</option>
                  <option value="we_pickup">We Pickup (Our Logistics)</option>
                </Select>
                <FieldHint>
                  {formData.logistics_scenario === 'customer_pickup' && '🚗 Customer handles pickup'}
                  {formData.logistics_scenario === 'supplier_delivery' && '🚚 Supplier delivers to us'}
                  {formData.logistics_scenario === 'we_pickup' && '🚛 We handle logistics'}
                </FieldHint>
              </FormGroup>
              <FormGroup>
                <Label>Order Number {!editingPurchaseOrder && '(Optional - Auto-generated)'}</Label>
                <Input
                  type="text"
                  name="order_number"
                  value={formData.order_number}
                  onChange={handleInputChange}
                  placeholder={editingPurchaseOrder ? '' : `Suggested: ${getNextOrderNumber()}`}
                  readOnly={!editingPurchaseOrder}
                  style={{ 
                    cursor: !editingPurchaseOrder ? 'not-allowed' : 'text'
                  }}
                />
              </FormGroup>
              <FormGroup>
                <Label>Supplier</Label>
                <Select
                  name="supplier"
                  value={formData.supplier}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select a supplier</option>
                  {suppliers.map((supplier) => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              <FormGroup>
                <Label>Total Amount</Label>
                <Input
                  type="number"
                  step="0.01"
                  name="total_amount"
                  value={formData.total_amount}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>
              <FormGroup>
                <Label>Status</Label>
                <Select name="status" value={formData.status} onChange={handleInputChange} required>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="delivered">Delivered</option>
                  <option value="cancelled">Cancelled</option>
                </Select>
              </FormGroup>
              <FormGroup>
                <Label>Order Date</Label>
                <Input
                  type="date"
                  name="order_date"
                  value={formData.order_date}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>
              <FormGroup>
                <Label>Delivery Date</Label>
                <Input
                  type="date"
                  name="delivery_date"
                  value={formData.delivery_date}
                  onChange={handleInputChange}
                />
              </FormGroup>
              <FormGroup>
                <Label>Notes</Label>
                <TextArea
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  rows={3}
                />
              </FormGroup>

              <FormGroup>
                <LocationSelector
                  value={formData.pick_up_location}
                  onChange={(id) => setFormData({ ...formData, pick_up_location: id })}
                  label="Pick-up Location"
                  placeholder="Select pick-up location"
                />
              </FormGroup>

              <FormGroup>
                <LocationSelector
                  value={formData.delivery_location}
                  onChange={(id) => setFormData({ ...formData, delivery_location: id })}
                  label="Delivery Location"
                  placeholder="Select delivery location"
                />
              </FormGroup>

              <FormActions>
                <CancelButton type="button" onClick={() => setShowForm(false)}>
                  Cancel
                </CancelButton>
                <SubmitButton type="submit">
                  {editingPurchaseOrder ? 'Update' : 'Create'} Purchase Order
                </SubmitButton>
              </FormActions>
            </Form>
          </FormContainer>
        </FormOverlay>
      )}
    </>
  );
};

export default PurchaseOrders;
