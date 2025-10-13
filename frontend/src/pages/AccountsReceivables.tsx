import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiService, AccountsReceivable } from '../services/apiService';

// Styled Components
const Container = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

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
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #0056b3;
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
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
`;

const StatNumber = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: #007bff;
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
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const TableHeader = styled.thead`
  background: #f8f9fa;
`;

const TableBody = styled.tbody``;

const TableRow = styled.tr`
  border-bottom: 1px solid #e9ecef;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background-color: #f8f9fa;
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
  background: white;
  border-radius: 12px;
  padding: 0;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
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
    border-color: #007bff;
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
    border-color: #007bff;
  }
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
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #0056b3;
  }
`;

const AccountsReceivables: React.FC = () => {
  const [receivables, setReceivables] = useState<AccountsReceivable[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingReceivable, setEditingReceivable] = useState<AccountsReceivable | null>(null);
  const [formData, setFormData] = useState({
    invoice_number: '',
    customer: '',
    amount: '',
    due_date: '',
    status: 'pending',
  });

  useEffect(() => {
    loadReceivables();
  }, []);

  const loadReceivables = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAccountsReceivables();
      setReceivables(data);
    } catch (error) {
      console.error('Error loading accounts receivables:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const receivableData = {
        ...formData,
        amount: parseFloat(formData.amount),
        customer: parseInt(formData.customer),
      };

      if (editingReceivable) {
        await apiService.updateAccountsReceivable(editingReceivable.id, receivableData);
      } else {
        await apiService.createAccountsReceivable(receivableData);
      }

      await loadReceivables();
      setShowForm(false);
      setEditingReceivable(null);
      setFormData({
        invoice_number: '',
        customer: '',
        amount: '',
        due_date: '',
        status: 'pending',
      });
    } catch (error: unknown) {
      // Log detailed error information
      const err = error as Error & { response?: { status: number; data: unknown }; stack?: string };
      console.error('Error saving accounts receivable:', {
        message: err.message || 'Unknown error',
        stack: err.stack || 'No stack trace available',
        response: err.response ? {
          status: err.response.status,
          data: err.response.data
        } : 'No response data'
      });
      // Display user-friendly error to the UI
      alert(`Failed to save accounts receivable: ${err.message || 'Please try again later'}`);
    }
  };

  const handleEdit = (receivable: AccountsReceivable) => {
    setEditingReceivable(receivable);
    setFormData({
      invoice_number: receivable.invoice_number,
      customer: receivable.customer.toString(),
      amount: receivable.amount.toString(),
      due_date: receivable.due_date,
      status: receivable.status,
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this receivable?')) {
      try {
        await apiService.deleteAccountsReceivable(id);
        alert('Accounts receivable deleted successfully!');
        await loadReceivables(); // Re-fetch to update the list
      } catch (error: any) {
        console.error('Error deleting accounts receivable:', error);
        const errorMessage = error?.response?.data?.detail 
          || error?.response?.data?.message 
          || error?.message 
          || 'Failed to delete accounts receivable';
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
      case 'paid':
        return '#28a745';
      case 'overdue':
        return '#dc3545';
      case 'disputed':
        return '#6f42c1';
      default:
        return '#6c757d';
    }
  };

  const getTotalAmount = () =>
    Array.isArray(receivables)
      ? receivables.reduce((sum, r) => sum + (Number(r.amount) || 0), 0)
      : 0;
  const getPendingAmount = () =>
    Array.isArray(receivables)
      ? receivables
          .filter((r) => r.status === 'pending')
          .reduce((sum, r) => sum + (Number(r.amount) || 0), 0)
      : 0;
  const getOverdueAmount = () =>
    Array.isArray(receivables)
      ? receivables
          .filter((r) => r.status === 'overdue')
          .reduce((sum, r) => sum + (Number(r.amount) || 0), 0)
      : 0;

  if (loading) {
    return (
      <Container>
        <LoadingMessage>Loading accounts receivables...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>Accounts Receivables</Title>
        <AddButton onClick={() => setShowForm(true)}>+ Add Receivable</AddButton>
      </Header>

      <StatsCards>
        <StatCard>
          <StatNumber>{receivables.length}</StatNumber>
          <StatLabel>Total Invoices</StatLabel>
        </StatCard>
        <StatCard>
          <StatNumber>${getTotalAmount().toFixed(2)}</StatNumber>
          <StatLabel>Total Amount</StatLabel>
        </StatCard>
        <StatCard>
          <StatNumber>${getPendingAmount().toFixed(2)}</StatNumber>
          <StatLabel>Pending</StatLabel>
        </StatCard>
        <StatCard>
          <StatNumber>${getOverdueAmount().toFixed(2)}</StatNumber>
          <StatLabel>Overdue</StatLabel>
        </StatCard>
      </StatsCards>

      {receivables.length === 0 ? (
        <EmptyState>
          <EmptyIcon>💰</EmptyIcon>
          <EmptyTitle>No Accounts Receivables</EmptyTitle>
          <EmptyDescription>Get started by creating your first receivable</EmptyDescription>
        </EmptyState>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHeaderCell>Invoice #</TableHeaderCell>
              <TableHeaderCell>Customer ID</TableHeaderCell>
              <TableHeaderCell>Amount</TableHeaderCell>
              <TableHeaderCell>Due Date</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Actions</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {receivables.map((receivable) => (
              <TableRow key={receivable.id}>
                <TableCell>{receivable.invoice_number}</TableCell>
                <TableCell>{receivable.customer}</TableCell>
                <TableCell>${(Number(receivable.amount) || 0).toFixed(2)}</TableCell>
                <TableCell>{new Date(receivable.due_date).toLocaleDateString()}</TableCell>
                <TableCell>
                  <StatusBadge $color={getStatusColor(receivable.status)}>
                    {receivable.status.toUpperCase()}
                  </StatusBadge>
                </TableCell>
                <TableCell>
                  <ActionButton onClick={() => handleEdit(receivable)}>Edit</ActionButton>
                  <DeleteButton onClick={() => handleDelete(receivable.id)}>Delete</DeleteButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {showForm && (
        <FormOverlay>
          <FormContainer>
            <FormHeader>
              <FormTitle>{editingReceivable ? 'Edit Receivable' : 'Add New Receivable'}</FormTitle>
              <CloseButton onClick={() => setShowForm(false)}>×</CloseButton>
            </FormHeader>
            <Form onSubmit={handleSubmit}>
              <FormGroup>
                <Label>Invoice Number</Label>
                <Input
                  type="text"
                  name="invoice_number"
                  value={formData.invoice_number}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>
              <FormGroup>
                <Label>Customer ID</Label>
                <Input
                  type="number"
                  name="customer"
                  value={formData.customer}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>
              <FormGroup>
                <Label>Amount</Label>
                <Input
                  type="number"
                  step="0.01"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>
              <FormGroup>
                <Label>Due Date</Label>
                <Input
                  type="date"
                  name="due_date"
                  value={formData.due_date}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>
              <FormGroup>
                <Label>Status</Label>
                <Select name="status" value={formData.status} onChange={handleInputChange} required>
                  <option value="pending">Pending</option>
                  <option value="paid">Paid</option>
                  <option value="overdue">Overdue</option>
                  <option value="disputed">Disputed</option>
                </Select>
              </FormGroup>
              <FormActions>
                <CancelButton type="button" onClick={() => setShowForm(false)}>
                  Cancel
                </CancelButton>
                <SubmitButton type="submit">
                  {editingReceivable ? 'Update' : 'Create'} Receivable
                </SubmitButton>
              </FormActions>
            </Form>
          </FormContainer>
        </FormOverlay>
      )}
    </Container>
  );
};

export default AccountsReceivables;
