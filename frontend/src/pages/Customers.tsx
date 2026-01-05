import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTheme } from '../contexts/ThemeContext';
import { Theme } from '../config/theme';
import { apiService, Customer } from '../services/apiService';
import { PhoneInput, Select } from '../components/ui';
import { US_STATES } from '../utils/constants/states';

const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    country: '',
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const data = await apiService.getCustomers();
      setCustomers(data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingCustomer) {
        await apiService.updateCustomer(editingCustomer.id, formData);
      } else {
        await apiService.createCustomer(formData);
      }
      setShowForm(false);
      setEditingCustomer(null);
      resetForm();
      fetchCustomers();
    } catch (error: unknown) {
      // Log detailed error information
      const err = error as Error & { response?: { status: number; data: unknown }; stack?: string };
      console.error('Error saving customer:', {
        message: err.message || 'Unknown error',
        stack: err.stack || 'No stack trace available',
        response: err.response ? {
          status: err.response.status,
          data: err.response.data
        } : 'No response data'
      });
      // Display user-friendly error to the UI
      alert(`Failed to save customer: ${err.message || 'Please try again later'}`);
    }
  };

  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setFormData({
      name: customer.name,
      contact_person: customer.contact_person || '',
      email: customer.email || '',
      phone: customer.phone || '',
      address: customer.address || '',
      city: customer.city || '',
      state: customer.state || '',
      zip_code: customer.zip_code || '',
      country: customer.country || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        await apiService.deleteCustomer(id);
        alert('Customer deleted successfully!');
        await fetchCustomers(); // Re-fetch to update the list
      } catch (error: unknown) {
        // Type-safe error handling: Use 'unknown' instead of 'any' and assert expected structure
        console.error('Error deleting customer:', error);
        const err = error as { response?: { data?: { detail?: string; message?: string } }; message?: string };
        const errorMessage = err?.response?.data?.detail 
          || err?.response?.data?.message 
          || err?.message 
          || 'Failed to delete customer';
        alert(`Error: ${errorMessage}`);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      contact_person: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      country: '',
    });
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingCustomer(null);
    resetForm();
  };

  if (loading) {
    return <LoadingContainer $theme={theme}>Loading customers...</LoadingContainer>;
  }

  return (
    <>
      <Header>
        <Title $theme={theme}>Customers</Title>
        <AddButton onClick={() => setShowForm(true)}>+ Add Customer</AddButton>
      </Header>

      {showForm && (
        <FormOverlay>
          <FormContainer $theme={theme}>
            <FormHeader $theme={theme}>
              <FormTitle $theme={theme}>{editingCustomer ? 'Edit Customer' : 'Add New Customer'}</FormTitle>
              <CloseButton $theme={theme} onClick={handleCancel}>×</CloseButton>
            </FormHeader>

            <Form onSubmit={handleSubmit}>
              <FormGrid>
                <FormGroup>
                  <Label $theme={theme}>Company Name *</Label>
                  <Input $theme={theme}
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>Contact Person</Label>
                  <Input $theme={theme}
                    type="text"
                    value={formData.contact_person}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        contact_person: e.target.value,
                      })
                    }
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>Email</Label>
                  <Input $theme={theme}
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>Phone</Label>
                  <PhoneInput
                    value={formData.phone}
                    onChange={(value) => setFormData({ ...formData, phone: value })}
                    placeholder="(XXX) XXX-XXXX"
                    aria-label="Phone number"
                  />
                </FormGroup>

                <FormGroup $fullWidth>
                  <Label $theme={theme}>Address</Label>
                  <Input $theme={theme}
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>City</Label>
                  <Input $theme={theme}
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>State</Label>
                  <Select
                    value={formData.state}
                    onChange={(value) => setFormData({ ...formData, state: value })}
                    options={US_STATES}
                    placeholder="Select state"
                    aria-label="State"
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>ZIP Code</Label>
                  <Input $theme={theme}
                    type="text"
                    value={formData.zip_code}
                    onChange={(e) => {
                      // Only allow digits, max 5 characters
                      const value = e.target.value.replace(/\D/g, '').slice(0, 5);
                      setFormData({ ...formData, zip_code: value });
                    }}
                    maxLength={5}
                    pattern="^\d{5}$"
                    placeholder="12345"
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>Country</Label>
                  <Input $theme={theme}
                    type="text"
                    value={formData.country}
                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  />
                </FormGroup>
              </FormGrid>

              <FormActions>
                <CancelButton type="button" onClick={handleCancel}>
                  Cancel
                </CancelButton>
                <SubmitButton type="submit">
                  {editingCustomer ? 'Update' : 'Create'} Customer
                </SubmitButton>
              </FormActions>
            </Form>
          </FormContainer>
        </FormOverlay>
      )}

      <TableContainer $theme={theme}>
        {customers.length === 0 ? (
          <EmptyState>
            <EmptyIcon>👥</EmptyIcon>
            <EmptyText $theme={theme}>No customers found</EmptyText>
            <EmptySubText $theme={theme}>Add your first customer to get started</EmptySubText>
          </EmptyState>
        ) : (
          <Table>
            <TableHeader $theme={theme}>
              <TableRow $theme={theme}>
                <TableHeaderCell $theme={theme}>Company Name</TableHeaderCell>
                <TableHeaderCell $theme={theme}>Contact Person</TableHeaderCell>
                <TableHeaderCell $theme={theme}>Email</TableHeaderCell>
                <TableHeaderCell $theme={theme}>Phone</TableHeaderCell>
                <TableHeaderCell $theme={theme}>Location</TableHeaderCell>
                <TableHeaderCell $theme={theme}>Actions</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {customers.map((customer) => (
                <TableRow $theme={theme} key={customer.id}>
                  <TableCell $theme={theme}>
                    <CompanyName $theme={theme}>{customer.name}</CompanyName>
                  </TableCell>
                  <TableCell $theme={theme}>{customer.contact_person || '-'}</TableCell>
                  <TableCell $theme={theme}>{customer.email || '-'}</TableCell>
                  <TableCell $theme={theme}>{customer.phone || '-'}</TableCell>
                  <TableCell $theme={theme}>
                    {customer.city && customer.state
                      ? `${customer.city}, ${customer.state}`
                      : customer.city || customer.state || '-'}
                  </TableCell>
                  <TableCell $theme={theme}>
                    <ActionButton onClick={() => handleEdit(customer)}>Edit</ActionButton>
                    <DeleteButton onClick={() => handleDelete(customer.id)}>Delete</DeleteButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </TableContainer>
    </>
  );
};

// Styled Components (reusing from Suppliers with customer theme colors)
const LoadingContainer = styled.div<{ $theme: Theme }>`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 18px;
  color: ${(props) => props.$theme.colors.textSecondary};
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
`;

const Title = styled.h1<{ $theme: Theme }>`
  font-size: 32px;
  font-weight: 700;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin: 0;
`;

const AddButton = styled.button`
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
  }
`;

const FormOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const FormContainer = styled.div<{ $theme: Theme }>`
  background: ${(props) => props.$theme.colors.surface};
  border-radius: 12px;
  padding: 0;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
`;

const FormHeader = styled.div<{ $theme: Theme }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid ${(props) => props.$theme.colors.border};
`;

const FormTitle = styled.h2<{ $theme: Theme }>`
  margin: 0;
  color: ${(props) => props.$theme.colors.textPrimary};
`;

const CloseButton = styled.button<{ $theme: Theme }>`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: ${(props) => props.$theme.colors.textSecondary};

  &:hover {
    color: ${(props) => props.$theme.colors.textPrimary};
  }
`;

const Form = styled.form`
  padding: 30px;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
`;

const FormGroup = styled.div<{ $fullWidth?: boolean }>`
  grid-column: ${(props) => (props.$fullWidth ? '1 / -1' : 'auto')};
`;

const Label = styled.label<{ $theme: Theme }>`
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: ${(props) => props.$theme.colors.textPrimary};
`;

const Input = styled.input<{ $theme: Theme }>`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid ${(props) => props.$theme.colors.border};
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #e74c3c;
  }
`;

const FormActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 10px;
`;

const CancelButton = styled.button`
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background: #5a6268;
  }
`;

const SubmitButton = styled.button`
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
  }
`;

const TableContainer = styled.div<{ $theme: Theme }>`
  background: ${(props) => props.$theme.colors.surface};
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px ${(props) => props.$theme.colors.shadow};
`;

const EmptyState = styled.div`
  padding: 60px 20px;
  text-align: center;
`;

const EmptyIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
`;

const EmptyText = styled.div<{ $theme: Theme }>`
  font-size: 18px;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const EmptySubText = styled.div<{ $theme: Theme }>`
  color: ${(props) => props.$theme.colors.textSecondary};
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead<{ $theme: Theme }>`
  background: ${(props) => props.$theme.colors.background};
`;

const TableBody = styled.tbody``;

const TableRow = styled.tr<{ $theme: Theme }>`
  border-bottom: 1px solid ${(props) => props.$theme.colors.border};

  &:hover {
    background: ${(props) => props.$theme.colors.background};
  }
`;

const TableHeaderCell = styled.th<{ $theme: Theme }>`
  padding: 15px 20px;
  text-align: left;
  font-weight: 600;
  color: ${(props) => props.$theme.colors.textPrimary};
`;

const TableCell = styled.td<{ $theme: Theme }>`
  padding: 15px 20px;
`;

const CompanyName = styled.div<{ $theme: Theme }>`
  font-weight: 600;
  color: ${(props) => props.$theme.colors.textPrimary};
`;

const ActionButton = styled.button`
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  margin-right: 8px;
  transition: background-color 0.2s ease;

  &:hover {
    background: #2980b9;
  }
`;

const DeleteButton = styled.button`
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background: #c0392b;
  }
`;

export default Customers;
