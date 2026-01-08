/**
 * LocationSelector Component - RLS-Protected Location Dropdown
 * 
 * Features:
 * - Fetches locations from backend (filtered by RLS tenant isolation)
 * - Handles loading states and errors gracefully
 * - Supports optional type filtering (plant, warehouse, distribution center)
 * - Theme-aware styling
 * - Error handling for 403 Forbidden (RLS rejection) and token expiration
 * 
 * Phase 4: Frontend Integration & UX Alignment
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Theme } from '../../config/theme';
import { useTheme } from '../../contexts/ThemeContext';
import { Location } from '../../types/index';
import axios from 'axios';
import { config } from '../../config/runtime';

export interface LocationSelectorProps {
  value: string | null;
  onChange: (id: string | null) => void;
  type?: 'plant' | 'warehouse' | 'distribution_center' | null;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  placeholder?: string;
  'aria-label'?: string;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({
  value,
  onChange,
  type = null,
  label = 'Location',
  required = false,
  disabled = false,
  error,
  placeholder = 'Select a location',
  'aria-label': ariaLabel,
}) => {
  const { theme } = useTheme();
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  useEffect(() => {
    fetchLocations();
  }, [type]);

  const fetchLocations = async () => {
    try {
      setLoading(true);
      setFetchError(null);

      const token = localStorage.getItem('authToken');
      const tenantId = localStorage.getItem('tenantId');

      if (!token) {
        setFetchError('Authentication required');
        setLoading(false);
        return;
      }

      // Build API URL with optional type filter
      let url = `${config.API_BASE_URL}/locations/`;
      if (type) {
        url += `?type=${type}`;
      }

      const response = await axios.get<Location[]>(url, {
        headers: {
          Authorization: `Token ${token}`,
          ...(tenantId && { 'X-Tenant-ID': tenantId }),
        },
        timeout: 10000,
      });

      // Handle both paginated and non-paginated responses
      const data = Array.isArray(response.data) 
        ? response.data 
        : (response.data as any).results || [];

      setLocations(data);
    } catch (err: any) {
      // Graceful error handling for RLS and auth failures
      if (err.response?.status === 403) {
        setFetchError('Access denied - insufficient permissions');
        console.error('[LocationSelector] RLS policy rejected request:', err);
      } else if (err.response?.status === 401) {
        setFetchError('Session expired - please log in again');
        console.error('[LocationSelector] Token expired:', err);
        // Optionally trigger logout
        localStorage.removeItem('authToken');
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else if (err.code === 'ECONNABORTED') {
        setFetchError('Request timeout - please try again');
      } else {
        setFetchError('Failed to load locations');
        console.error('[LocationSelector] Error fetching locations:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;
    onChange(selectedValue === '' ? null : selectedValue);
  };

  return (
    <Container>
      {label && <Label $theme={theme}>{label}{required && ' *'}</Label>}
      
      <StyledSelect
        value={value || ''}
        onChange={handleChange}
        disabled={disabled || loading}
        required={required}
        aria-label={ariaLabel || label}
        $theme={theme}
        $hasError={!!error || !!fetchError}
      >
        <option value="" disabled hidden>
          {loading ? 'Loading locations...' : placeholder}
        </option>
        
        {!loading && !fetchError && locations.length === 0 && (
          <option value="" disabled>
            No locations available
          </option>
        )}
        
        {!loading && fetchError && (
          <option value="" disabled>
            {fetchError}
          </option>
        )}
        
        {!loading && !fetchError && locations.map((location) => (
          <option key={location.id} value={location.id}>
            {location.name} - {location.location_type} ({location.city}, {location.state_province})
          </option>
        ))}
      </StyledSelect>
      
      {(error || fetchError) && (
        <ErrorMessage $theme={theme}>
          {error || fetchError}
          {fetchError && (
            <RetryButton onClick={fetchLocations} type="button">
              Retry
            </RetryButton>
          )}
        </ErrorMessage>
      )}
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
`;

const Label = styled.label<{ $theme: Theme }>`
  font-size: 14px;
  font-weight: 500;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin-bottom: 2px;
`;

const StyledSelect = styled.select<{ $theme: Theme; $hasError: boolean }>`
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  border: 1px solid ${(props) => 
    props.$hasError 
      ? props.$theme.colors.danger 
      : props.$theme.colors.border
  };
  border-radius: 6px;
  background-color: ${(props) => props.$theme.colors.surface};
  color: ${(props) => props.$theme.colors.textPrimary};
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover:not(:disabled) {
    border-color: ${(props) => props.$theme.colors.primary};
  }

  &:focus {
    outline: none;
    border-color: ${(props) => props.$theme.colors.primary};
    box-shadow: 0 0 0 3px ${(props) => props.$theme.colors.primary}20;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: ${(props) => props.$theme.colors.surfaceHover};
  }

  option {
    background-color: ${(props) => props.$theme.colors.surface};
    color: ${(props) => props.$theme.colors.textPrimary};
    padding: 8px;
  }
`;

const ErrorMessage = styled.div<{ $theme: Theme }>`
  color: ${(props) => props.$theme.colors.danger};
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RetryButton = styled.button`
  background: none;
  border: none;
  color: rgb(var(--color-primary));
  text-decoration: underline;
  cursor: pointer;
  font-size: 12px;
  padding: 0;

  &:hover {
    color: rgb(var(--color-primary-hover));
  }
`;

export default LocationSelector;
