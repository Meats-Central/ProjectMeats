import React, { useState, useEffect } from 'react';
import { PhoneInput, Select } from '../components/ui';
import { MultiSelect } from '../components/Shared';
import { US_STATES } from '../utils/constants/states';
import { DEPARTMENT_CHOICES } from '../utils/constants/choices';
import styled from 'styled-components';
import { apiService, Supplier } from '../services/apiService';
import { useTheme } from '../contexts/ThemeContext';
import { Theme } from '../config/theme';

const Suppliers: React.FC = () => {
  const { theme } = useTheme();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
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
    departments_array: [] as string[], // Phase 4: ArrayField integration
  });

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    try {
      setLoading(true);
      const data = await apiService.getSuppliers();
      setSuppliers(data);
    } catch (error) {
      console.error('Error fetching suppliers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingSupplier) {
        await apiService.updateSupplier(editingSupplier.id, formData);
      } else {
        await apiService.createSupplier(formData);
      }
      setShowForm(false);
      setEditingSupplier(null);
      resetForm();
      fetchSuppliers();
    } catch (error: unknown) {
      // Extract error message
      const err = error as Error;
      const errorMessage = err.message || 'An unexpected error occurred. Please try again.';
      
      // Log detailed error information for debugging
      // eslint-disable-next-line no-console
      console.error('[Suppliers] Error saving supplier:', {
        message: errorMessage,
        error: err,
        action: editingSupplier ? 'update' : 'create',
      });
      
      // Display user-friendly error to the UI
      alert(errorMessage);
    }
  };

  const handleEdit = (supplier: Supplier) => {
    setEditingSupplier(supplier);
    setFormData({
      name: supplier.name,
      contact_person: supplier.contact_person || '',
      email: supplier.email || '',
      phone: supplier.phone || '',
      address: supplier.address || '',
      city: supplier.city || '',
      state: supplier.state || '',
      zip_code: supplier.zip_code || '',
      country: supplier.country || '',
      departments_array: supplier.departments_array || [], // Phase 4: Populate array
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this supplier?')) {
      try {
        await apiService.deleteSupplier(id);
        alert('Supplier deleted successfully!');
        await fetchSuppliers(); // Re-fetch to update the list
      } catch (error: unknown) {
        // Type-safe error handling: Use 'unknown' instead of 'any' and assert expected structure
        // This ensures we handle errors safely while maintaining type checking
        console.error('Error deleting supplier:', error);
        const err = error as { response?: { data?: { detail?: string; message?: string } }; message?: string };
        const errorMessage = err?.response?.data?.detail 
          || err?.response?.data?.message 
          || err?.message 
          || 'Failed to delete supplier';
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
      departments_array: [], // Phase 4: Reset array
    });
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingSupplier(null);
    resetForm();
  };

  if (loading) {
    return <LoadingContainer $theme={theme}>Loading suppliers...</LoadingContainer>;
  }

  return (
    <>
      <Header>
        <Title $theme={theme}>Suppliers</Title>
        <AddButton onClick={() => setShowForm(true)}>+ Add Supplier</AddButton>
      </Header>

      {showForm && (
        <FormOverlay>
          <FormContainer $theme={theme}>
            <FormHeader $theme={theme}>
              <FormTitle $theme={theme}>{editingSupplier ? 'Edit Supplier' : 'Add New Supplier'}</FormTitle>
              <CloseButton $theme={theme} onClick={handleCancel}>×</CloseButton>
            </FormHeader>

            <Form onSubmit={handleSubmit}>
              <FormGrid>
                <FormGroup>
                  <Label $theme={theme}>Company Name *</Label>
                  <Input
                    $theme={theme}
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>Contact Person</Label>
                  <Input
                    $theme={theme}
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
                  <Input
                    $theme={theme}
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
                  <Input
                    $theme={theme}
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  />
                </FormGroup>

                <FormGroup>
                  <Label $theme={theme}>City</Label>
                  <Input
                    $theme={theme}
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
                  <Input
                    $theme={theme}
                    type="text"
                    value={formData.zip_code}
                    onChange={(e) => {
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
                  <Input
                    $theme={theme}
                    type="text"
                    value={formData.country}
                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  />
                </FormGroup>

                <FormGroup $fullWidth>
                  <MultiSelect
                    value={formData.departments_array}
                    onChange={(values) => setFormData({ ...formData, departments_array: values })}
                    options={DEPARTMENT_CHOICES}
                    label="Departments"
                    placeholder="Select departments (hold Ctrl/Cmd for multiple)"
                  />
                </FormGroup>
              </FormGrid>

              <FormActions>
                <CancelButton type="button" onClick={handleCancel}>
                  Cancel
                </CancelButton>
                <SubmitButton type="submit">
                  {editingSupplier ? 'Update' : 'Create'} Supplier
                </SubmitButton>
              </FormActions>
            </Form>
          </FormContainer>
        </FormOverlay>
      )}

      <TableContainer $theme={theme}>
        {suppliers.length === 0 ? (
          <EmptyState>
            <EmptyIcon>🏭</EmptyIcon>
            <EmptyText $theme={theme}>No suppliers found</EmptyText>
            <EmptySubText $theme={theme}>Add your first supplier to get started</EmptySubText>
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
              {suppliers.map((supplier) => (
                <TableRow key={supplier.id} $theme={theme}>
                  <TableCell $theme={theme}>
                    <CompanyName $theme={theme}>{supplier.name}</CompanyName>
                  </TableCell>
                  <TableCell $theme={theme}>{supplier.contact_person || '-'}</TableCell>
                  <TableCell $theme={theme}>{supplier.email || '-'}</TableCell>
                  <TableCell $theme={theme}>{supplier.phone || '-'}</TableCell>
                  <TableCell $theme={theme}>
                    {supplier.city && supplier.state
                      ? `${supplier.city}, ${supplier.state}`
                      : supplier.city || supplier.state || '-'}
                  </TableCell>
                  <TableCell $theme={theme}>
                    <ActionButton onClick={() => handleEdit(supplier)}>Edit</ActionButton>
                    <DeleteButton onClick={() => handleDelete(supplier.id)}>Delete</DeleteButton>
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

// Styled Components
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
  background: linear-gradient(135deg, #27ae60, #2ecc71);
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
    box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
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
  background: ${(props) => props.$theme.colors.surface};
  color: ${(props) => props.$theme.colors.textPrimary};

  &:focus {
    outline: none;
    border-color: ${(props) => props.$theme.colors.primary};
  }
`;

const FormActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 10px;
`;

const CancelButton = styled.button`
  background: rgb(var(--color-text-secondary));
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
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
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
    background: ${(props) => props.$theme.colors.surfaceHover};
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
  color: ${(props) => props.$theme.colors.textPrimary};
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

export default Suppliers;
