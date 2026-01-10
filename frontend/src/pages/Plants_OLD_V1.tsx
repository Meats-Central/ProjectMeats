/**
 * Plants Management Page
 * 
 * Phase 4: Contextual Supplier Selection
 * Demonstrates context-aware parent entity selection
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useLocation } from 'react-router-dom';
import { apiClient } from '../services/apiService';

interface Plant {
  id: number;
  name: string;
  supplier: number;
  supplier_name?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  phone?: string;
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
  const [contextSupplierId, setContextSupplierId] = useState<number | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    supplier: '',
    address: '',
    city: '',
    state: '',
    country: 'USA',
    phone: '',
  });

  // Detect context from URL or state
  useEffect(() => {
    // Check if navigated from a supplier detail page
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('plants/', formData);
      await loadPlants();
      setShowForm(false);
      setFormData({
        name: '',
        supplier: '',
        address: '',
        city: '',
        state: '',
        country: 'USA',
        phone: '',
      });
    } catch (error) {
      console.error('Error creating plant:', error);
      alert('Failed to create plant');
    }
  };

  const handleAddPlant = () => {
    // Pre-fill supplier if context exists
    if (contextSupplierId) {
      setFormData(prev => ({ ...prev, supplier: String(contextSupplierId) }));
    }
    setShowForm(true);
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
          <span>📍 Context: Adding plant for specific supplier</span>
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
              <PlantName>{plant.name}</PlantName>
              <PlantDetail>
                <strong>Supplier:</strong> {plant.supplier_name || `ID: ${plant.supplier}`}
              </PlantDetail>
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
            </PlantCard>
          ))}
        </Grid>
      )}

      {showForm && (
        <FormOverlay>
          <FormContainer>
            <FormHeader>
              <FormTitle>Add New Plant</FormTitle>
              <CloseButton onClick={() => setShowForm(false)}>×</CloseButton>
            </FormHeader>
            <Form onSubmit={handleSubmit}>
              <FormGroup>
                <Label>Plant Name *</Label>
                <Input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Main Processing Facility"
                  required
                />
              </FormGroup>

              <FormGroup>
                <Label>Supplier * {contextSupplierId && '(Pre-selected from context)'}</Label>
                <Select
                  value={formData.supplier}
                  onChange={(e) => setFormData(prev => ({ ...prev, supplier: e.target.value }))}
                  required
                  disabled={!!contextSupplierId}
                >
                  <option value="">Select Supplier</option>
                  {suppliers.map(supplier => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </option>
                  ))}
                </Select>
                {contextSupplierId && (
                  <HelpText>Supplier automatically selected based on your navigation context</HelpText>
                )}
              </FormGroup>

              <FormGroup>
                <Label>Address</Label>
                <Input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
                  placeholder="Street address"
                />
              </FormGroup>

              <FormRow>
                <FormGroup>
                  <Label>City</Label>
                  <Input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                  />
                </FormGroup>
                <FormGroup>
                  <Label>State</Label>
                  <Input
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                    maxLength={2}
                  />
                </FormGroup>
              </FormRow>

              <FormGroup>
                <Label>Phone</Label>
                <Input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                />
              </FormGroup>

              <FormActions>
                <CancelButton type="button" onClick={() => setShowForm(false)}>
                  Cancel
                </CancelButton>
                <SubmitButton type="submit">
                  Create Plant
                </SubmitButton>
              </FormActions>
            </Form>
          </FormContainer>
        </FormOverlay>
      )}
    </Container>
  );
};

// Styled Components
const Container = styled.div`
  padding: 24px;
  max-width: 1200px;
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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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

const PlantName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0 0 12px 0;
`;

const PlantDetail = styled.div`
  font-size: 14px;
  color: rgb(var(--color-text-secondary));
  margin-bottom: 8px;
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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
`;

const FormHeader = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid rgb(var(--color-border));
  display: flex;
  justify-content: space-between;
  align-items: center;
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

export default Plants;
