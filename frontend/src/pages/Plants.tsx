/**
 * Plants Management Page - Phase 4 Complete
 * 
 * Features:
 * - Full CRUD operations (Create, Read, Update, Delete)
 * - Contextual supplier selection (state-based navigation)
 * - Edit and Delete operations with confirmation
 * - View plant details
 * - Theme-compliant styling
 * - Multi-tenancy support
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useLocation } from 'react-router-dom';
import { apiClient } from '../services/apiService';

interface Plant {
  id: number;
  name: string;
  code: string;
  supplier: number | null;
  supplier_name?: string;
  plant_type?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  manager?: string;
  capacity?: number;
  is_active?: boolean;
}

interface Supplier {
  id: number;
  name: string;
}

const Plants: React.FC = () => {
  const location = useLocation();
  const [plants, setPlants] = useState<Plant[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingPlant, setEditingPlant] = useState<Plant | null>(null);
  const [deletingPlant, setDeletingPlant] = useState<Plant | null>(null);
  const [contextSupplierId, setContextSupplierId] = useState<number | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string[]>>({});
  
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    supplier: '',
    plant_type: 'processing',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'USA',
    phone: '',
    email: '',
    manager: '',
    capacity: '',
  });

  // Detect context from navigation state (Phase 4 pattern)
  useEffect(() => {
    const state = location.state as any;
    if (state?.supplierId) {
      setContextSupplierId(state.supplierId);
    }
  }, [location]);

  useEffect(() => {
    loadPlants();
    loadSuppliers();
  }, []);

  const loadPlants = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('plants/');
      setPlants(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading plants:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSuppliers = async () => {
    try {
      const response = await apiClient.get('suppliers/');
      setSuppliers(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading suppliers:', error);
    }
  };

  const handleAddPlant = () => {
    setEditingPlant(null);
    setFormErrors({});
    setFormData({
      name: '',
      code: '',
      supplier: contextSupplierId ? String(contextSupplierId) : '',
      plant_type: 'processing',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'USA',
      phone: '',
      email: '',
      manager: '',
      capacity: '',
    });
    setShowForm(true);
  };

  const handleEditPlant = (plant: Plant) => {
    setEditingPlant(plant);
    setFormErrors({});
    setFormData({
      name: plant.name,
      code: plant.code,
      supplier: plant.supplier ? String(plant.supplier) : '',
      plant_type: plant.plant_type || 'processing',
      address: plant.address || '',
      city: plant.city || '',
      state: plant.state || '',
      zip_code: plant.zip_code || '',
      country: plant.country || 'USA',
      phone: plant.phone || '',
      email: plant.email || '',
      manager: plant.manager || '',
      capacity: plant.capacity ? String(plant.capacity) : '',
    });
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormErrors({}); // Clear previous errors
    
    try {
      const payload = {
        ...formData,
        supplier: formData.supplier ? parseInt(formData.supplier) : null,
        capacity: formData.capacity ? parseInt(formData.capacity) : null,
      };

      if (editingPlant) {
        // Update existing plant
        await apiClient.patch(`plants/${editingPlant.id}/`, payload);
      } else {
        // Create new plant
        await apiClient.post('plants/', payload);
      }
      
      await loadPlants();
      setShowForm(false);
      setEditingPlant(null);
      setFormErrors({});
    } catch (error: any) {
      console.error('Error saving plant:', error);
      
      // Handle validation errors from backend
      if (error.response?.status === 400 && error.response?.data) {
        const errors = error.response.data;
        setFormErrors(errors);
        
        // Don't show alert if we have field-specific errors
        if (Object.keys(errors).length === 0) {
          const errorMessage = error.response?.data?.error 
            || error.response?.data?.detail
            || 'Failed to save plant';
          alert(`Error: ${errorMessage}`);
        }
      } else {
        // Show generic error for non-validation errors
        const errorMessage = error.response?.data?.error 
          || error.response?.data?.detail
          || error.response?.data?.details
          || 'Failed to save plant';
        alert(`Error: ${errorMessage}`);
      }
    }
  };

  const handleDeleteClick = (plant: Plant) => {
    setDeletingPlant(plant);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingPlant) return;

    try {
      await apiClient.delete(`plants/${deletingPlant.id}/`);
      await loadPlants();
      setDeletingPlant(null);
    } catch (error) {
      console.error('Error deleting plant:', error);
      alert('Failed to delete plant');
    }
  };

  if (loading) {
    return (
      <Container>
        <LoadingMessage>Loading plants...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Plants & Facilities</Title>
          <Subtitle>Manage supplier processing facilities and locations</Subtitle>
        </div>
        <AddButton onClick={handleAddPlant}>+ Add Plant</AddButton>
      </Header>

      {contextSupplierId && (
        <ContextBanner>
          <span>📍 Context: Adding plant for selected supplier</span>
        </ContextBanner>
      )}

      {plants.length === 0 ? (
        <EmptyState>
          <EmptyIcon>🏢</EmptyIcon>
          <EmptyTitle>No Plants Yet</EmptyTitle>
          <EmptyDescription>Add your first processing facility</EmptyDescription>
        </EmptyState>
      ) : (
        <Grid>
          {plants.map(plant => (
            <PlantCard key={plant.id}>
              <CardHeader>
                <PlantName>{plant.name}</PlantName>
                <CardActions>
                  <ActionButton onClick={() => handleEditPlant(plant)} title="Edit">
                    ✏️
                  </ActionButton>
                  <ActionButton 
                    onClick={() => handleDeleteClick(plant)} 
                    title="Delete"
                    className="delete"
                  >
                    🗑️
                  </ActionButton>
                </CardActions>
              </CardHeader>
              
              <PlantCode>Code: {plant.code}</PlantCode>
              
              {plant.supplier_name && (
                <PlantDetail>
                  <strong>Supplier:</strong> {plant.supplier_name}
                </PlantDetail>
              )}
              
              {plant.plant_type && (
                <PlantDetail>
                  <strong>Type:</strong> {plant.plant_type}
                </PlantDetail>
              )}
              
              {plant.city && plant.state && (
                <PlantDetail>
                  📍 {plant.city}, {plant.state}
                </PlantDetail>
              )}
              
              {plant.phone && (
                <PlantDetail>
                  📞 {plant.phone}
                </PlantDetail>
              )}
              
              {plant.manager && (
                <PlantDetail>
                  👤 Manager: {plant.manager}
                </PlantDetail>
              )}
            </PlantCard>
          ))}
        </Grid>
      )}

      {/* Form Modal */}
      {showForm && (
        <FormOverlay onClick={() => setShowForm(false)}>
          <FormContainer onClick={(e) => e.stopPropagation()}>
            <FormHeader>
              <FormTitle>{editingPlant ? 'Edit Plant' : 'Add New Plant'}</FormTitle>
              <CloseButton onClick={() => setShowForm(false)}>×</CloseButton>
            </FormHeader>
            
            <Form onSubmit={handleSubmit}>
              <FormRow>
                <FormGroup>
                  <Label>Plant Name <RequiredMark>*</RequiredMark></Label>
                  <Input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Main Processing Facility"
                    required
                    className={formErrors.name ? 'error' : ''}
                  />
                  {formErrors.name && <ErrorMessage>{formErrors.name[0]}</ErrorMessage>}
                </FormGroup>

                <FormGroup>
                  <Label>Plant Code <RequiredMark>*</RequiredMark></Label>
                  <Input
                    type="text"
                    value={formData.code}
                    onChange={(e) => setFormData(prev => ({ ...prev, code: e.target.value }))}
                    placeholder="e.g., PLANT-001"
                    required
                    className={formErrors.code ? 'error' : ''}
                  />
                  {formErrors.code && <ErrorMessage>{formErrors.code[0]}</ErrorMessage>}
                </FormGroup>
              </FormRow>

              <FormGroup>
                <Label>
                  Supplier {contextSupplierId && '(Pre-selected from context)'}
                </Label>
                <Select
                  value={formData.supplier}
                  onChange={(e) => setFormData(prev => ({ ...prev, supplier: e.target.value }))}
                  disabled={!!contextSupplierId}
                  className={formErrors.supplier ? 'error' : ''}
                >
                  <option value="">Select Supplier (Optional)</option>
                  {suppliers.map(supplier => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </option>
                  ))}
                </Select>
                {contextSupplierId && (
                  <HelpText>Supplier automatically selected based on your navigation context</HelpText>
                )}
                {formErrors.supplier && <ErrorMessage>{formErrors.supplier[0]}</ErrorMessage>}
              </FormGroup>

              <FormGroup>
                <Label>Plant Type</Label>
                <Select
                  value={formData.plant_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, plant_type: e.target.value }))}
                  className={formErrors.plant_type ? 'error' : ''}
                >
                  <option value="processing">Processing Plant</option>
                  <option value="distribution">Distribution Center</option>
                  <option value="warehouse">Warehouse</option>
                  <option value="retail">Retail Location</option>
                  <option value="other">Other</option>
                </Select>
                {formErrors.plant_type && <ErrorMessage>{formErrors.plant_type[0]}</ErrorMessage>}
              </FormGroup>

              <FormGroup>
                <Label>Address</Label>
                <Input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
                  placeholder="Street address"
                  className={formErrors.address ? 'error' : ''}
                />
                {formErrors.address && <ErrorMessage>{formErrors.address[0]}</ErrorMessage>}
              </FormGroup>

              <FormRow>
                <FormGroup>
                  <Label>City</Label>
                  <Input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                    className={formErrors.city ? 'error' : ''}
                  />
                  {formErrors.city && <ErrorMessage>{formErrors.city[0]}</ErrorMessage>}
                </FormGroup>
                <FormGroup>
                  <Label>State</Label>
                  <Input
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                    maxLength={2}
                    placeholder="e.g., CA"
                    className={formErrors.state ? 'error' : ''}
                  />
                  {formErrors.state && <ErrorMessage>{formErrors.state[0]}</ErrorMessage>}
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup>
                  <Label>ZIP Code</Label>
                  <Input
                    type="text"
                    value={formData.zip_code}
                    onChange={(e) => setFormData(prev => ({ ...prev, zip_code: e.target.value }))}
                    className={formErrors.zip_code ? 'error' : ''}
                  />
                  {formErrors.zip_code && <ErrorMessage>{formErrors.zip_code[0]}</ErrorMessage>}
                </FormGroup>
                <FormGroup>
                  <Label>Country</Label>
                  <Input
                    type="text"
                    value={formData.country}
                    onChange={(e) => setFormData(prev => ({ ...prev, country: e.target.value }))}
                    className={formErrors.country ? 'error' : ''}
                  />
                  {formErrors.country && <ErrorMessage>{formErrors.country[0]}</ErrorMessage>}
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup>
                  <Label>Phone</Label>
                  <Input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                    className={formErrors.phone ? 'error' : ''}
                  />
                  {formErrors.phone && <ErrorMessage>{formErrors.phone[0]}</ErrorMessage>}
                </FormGroup>
                <FormGroup>
                  <Label>Email</Label>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    className={formErrors.email ? 'error' : ''}
                  />
                  {formErrors.email && <ErrorMessage>{formErrors.email[0]}</ErrorMessage>}
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup>
                  <Label>Manager</Label>
                  <Input
                    type="text"
                    value={formData.manager}
                    onChange={(e) => setFormData(prev => ({ ...prev, manager: e.target.value }))}
                    placeholder="Facility manager name"
                    className={formErrors.manager ? 'error' : ''}
                  />
                  {formErrors.manager && <ErrorMessage>{formErrors.manager[0]}</ErrorMessage>}
                </FormGroup>
                <FormGroup>
                  <Label>Capacity</Label>
                  <Input
                    type="number"
                    value={formData.capacity}
                    onChange={(e) => setFormData(prev => ({ ...prev, capacity: e.target.value }))}
                    placeholder="Units"
                    className={formErrors.capacity ? 'error' : ''}
                  />
                  {formErrors.capacity && <ErrorMessage>{formErrors.capacity[0]}</ErrorMessage>}
                </FormGroup>
              </FormRow>

              <FormActions>
                <CancelButton type="button" onClick={() => setShowForm(false)}>
                  Cancel
                </CancelButton>
                <SubmitButton type="submit">
                  {editingPlant ? 'Update Plant' : 'Create Plant'}
                </SubmitButton>
              </FormActions>
            </Form>
          </FormContainer>
        </FormOverlay>
      )}

      {/* Delete Confirmation Modal */}
      {deletingPlant && (
        <FormOverlay onClick={() => setDeletingPlant(null)}>
          <ConfirmDialog onClick={(e) => e.stopPropagation()}>
            <ConfirmTitle>Delete Plant?</ConfirmTitle>
            <ConfirmMessage>
              Are you sure you want to delete <strong>{deletingPlant.name}</strong>?
              This action cannot be undone.
            </ConfirmMessage>
            <ConfirmActions>
              <CancelButton onClick={() => setDeletingPlant(null)}>
                Cancel
              </CancelButton>
              <DeleteButton onClick={handleDeleteConfirm}>
                Delete Plant
              </DeleteButton>
            </ConfirmActions>
          </ConfirmDialog>
        </FormOverlay>
      )}
    </Container>
  );
};

// Styled Components
const Container = styled.div`
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: rgb(var(--color-text-primary));
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: rgb(var(--color-text-secondary));
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
    opacity: 0.9;
    transform: translateY(-1px);
  }
`;

const ContextBanner = styled.div`
  padding: 12px 16px;
  background: rgba(var(--color-primary), 0.1);
  border-left: 4px solid rgb(var(--color-primary));
  border-radius: 6px;
  margin-bottom: 24px;
  font-size: 14px;
  color: rgb(var(--color-text-primary));
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 60px 20px;
  font-size: 18px;
  color: rgb(var(--color-text-secondary));
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 80px 20px;
`;

const EmptyIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
`;

const EmptyTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin-bottom: 10px;
`;

const EmptyDescription = styled.p`
  color: rgb(var(--color-text-secondary));
  font-size: 16px;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
`;

const PlantCard = styled.div`
  background: rgb(var(--color-surface));
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const PlantName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0;
  flex: 1;
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  opacity: 0.7;
  transition: opacity 0.2s, transform 0.2s;

  &:hover {
    opacity: 1;
    transform: scale(1.1);
  }

  &.delete:hover {
    filter: brightness(1.2);
  }
`;

const PlantCode = styled.div`
  font-size: 12px;
  color: rgb(var(--color-text-secondary));
  font-family: monospace;
  margin-bottom: 12px;
  padding: 4px 8px;
  background: rgba(var(--color-border), 0.3);
  border-radius: 4px;
  display: inline-block;
`;

const PlantDetail = styled.div`
  font-size: 14px;
  color: rgb(var(--color-text-secondary));
  margin-bottom: 8px;

  strong {
    color: rgb(var(--color-text-primary));
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
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
`;

const FormHeader = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid rgb(var(--color-border));
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: rgb(var(--color-surface));
  z-index: 1;
`;

const FormTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 28px;
  color: rgb(var(--color-text-secondary));
  cursor: pointer;
  line-height: 1;
  padding: 0;

  &:hover {
    color: rgb(var(--color-text-primary));
  }
`;

const Form = styled.form`
  padding: 24px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
`;

const Label = styled.label`
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgb(var(--color-text-primary));
  margin-bottom: 8px;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 2px solid rgb(var(--color-border));
  border-radius: 6px;
  font-size: 14px;
  color: rgb(var(--color-text-primary));
  background: rgb(var(--color-background));

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }

  &.error {
    border-color: #dc3545;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 10px 12px;
  border: 2px solid rgb(var(--color-border));
  border-radius: 6px;
  font-size: 14px;
  color: rgb(var(--color-text-primary));
  background: rgb(var(--color-background));

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }

  &:disabled {
    opacity: 0.6;
    background: rgba(var(--color-border), 0.1);
  }

  &.error {
    border-color: #dc3545;
  }
`;

const RequiredMark = styled.span`
  color: #dc3545;
  margin-left: 2px;
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  
  &:before {
    content: '⚠ ';
    margin-right: 4px;
  }
`;

const HelpText = styled.p`
  font-size: 12px;
  color: rgb(var(--color-text-secondary));
  margin: 6px 0 0 0;
  font-style: italic;
`;

const FormActions = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgb(var(--color-border));
`;

const CancelButton = styled.button`
  background: rgb(var(--color-text-secondary));
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.9;
  }
`;

const SubmitButton = styled.button`
  background: rgb(var(--color-primary));
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.9;
  }
`;

const ConfirmDialog = styled.div`
  background: rgb(var(--color-surface));
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 450px;
`;

const ConfirmTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0 0 16px 0;
`;

const ConfirmMessage = styled.p`
  font-size: 14px;
  color: rgb(var(--color-text-secondary));
  margin: 0 0 24px 0;
  line-height: 1.5;

  strong {
    color: rgb(var(--color-text-primary));
  }
`;

const ConfirmActions = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const DeleteButton = styled.button`
  background: #dc3545;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.9;
  }
`;

export default Plants;
