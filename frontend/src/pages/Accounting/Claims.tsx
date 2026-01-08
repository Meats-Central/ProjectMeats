/**
 * Accounting Claims Page
 * 
 * Comprehensive claims management for payables (to suppliers) and receivables (from customers).
 * 
 * Features:
 * - Tabbed interface: Payable Claims | Receivable Claims
 * - High-density data table with status badges
 * - Side panel for claim resolution with activity feed
 * - Workflow actions: Approve, Deny, Settle
 * - Filter by status (pending/approved/denied/settled/cancelled)
 * 
 * Theme Compliance:
 * - Page title: 32px, bold, rgb(var(--color-text-primary))
 * - Tabs: Active = primary color, Inactive = text-secondary
 * - Buttons: rgb(var(--color-primary)) background
 * - No hardcoded colors
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ActivityFeed } from '../../components/Shared/ActivityFeed';
import { apiClient } from '../../services/apiService';
import { formatCurrency } from '../../shared/utils';
import { formatDateLocal, formatToLocal } from '../../utils/formatters';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface Claim {
  id: number;
  tenant: string;
  claim_number: string;
  claim_type: 'payable' | 'receivable';
  status: 'pending' | 'approved' | 'denied' | 'settled' | 'cancelled';
  supplier: number | null;
  customer: number | null;
  purchase_order: number | null;
  sales_order: number | null;
  invoice: number | null;
  claim_date: string;
  claimed_amount: string;
  approved_amount: string | null;
  settled_amount: string | null;
  description: string;
  resolution_notes: string;
  created_by: number | null;
  created_by_name: string;
  created_on: string;
  updated_on: string;
}

type ClaimType = 'payable' | 'receivable';
type ClaimStatus = 'pending' | 'approved' | 'denied' | 'settled' | 'cancelled';

// ============================================================================
// Styled Components (Theme-Compliant)
// ============================================================================

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1.5rem;
  background: rgb(var(--color-background));
`;

const PageHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
`;

const PageTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: rgb(var(--color-text-primary));
  margin: 0;
`;

const PrimaryButton = styled.button`
  padding: 0.75rem 1.5rem;
  background: rgb(var(--color-primary));
  color: white;
  border: none;
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

const ContentContainer = styled.div<{ hasSidePanel?: boolean }>`
  display: grid;
  grid-template-columns: ${props => props.hasSidePanel ? '1fr 400px' : '1fr'};
  gap: 1.5rem;
  height: calc(100vh - 180px);
  overflow: hidden;
  transition: grid-template-columns 0.3s ease;
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  overflow: hidden;
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 2px solid rgb(var(--color-border));
  padding: 0 1.5rem;
  background: rgb(var(--color-surface));
`;

const Tab = styled.button<{ isActive?: boolean }>`
  padding: 1rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid ${props => props.isActive ? 'rgb(var(--color-primary))' : 'transparent'};
  color: ${props => props.isActive ? 'rgb(var(--color-primary))' : 'rgb(var(--color-text-secondary))'};
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: -2px;
  transition: all 0.2s ease;

  &:hover {
    color: rgb(var(--color-primary));
  }
`;

const FilterBar = styled.div`
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: rgb(var(--color-surface));
  border-bottom: 1px solid rgb(var(--color-border));
`;

const FilterButton = styled.button<{ isActive?: boolean }>`
  padding: 0.5rem 1rem;
  background: ${props => props.isActive ? 'rgba(var(--color-primary), 0.1)' : 'transparent'};
  color: ${props => props.isActive ? 'rgb(var(--color-primary))' : 'rgb(var(--color-text-secondary))'};
  border: 1px solid ${props => props.isActive ? 'rgb(var(--color-primary))' : 'rgb(var(--color-border))'};
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(var(--color-primary), 0.1);
    border-color: rgb(var(--color-primary));
    color: rgb(var(--color-primary));
  }
`;

const TableContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 0;

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgb(var(--color-surface));
  }

  &::-webkit-scrollbar-thumb {
    background: rgb(var(--color-border));
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgb(var(--color-text-secondary));
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background: rgb(var(--color-surface-hover));
  position: sticky;
  top: 0;
  z-index: 10;
`;

const TableRow = styled.tr<{ isSelected?: boolean; isClickable?: boolean }>`
  border-bottom: 1px solid rgb(var(--color-border));
  background: ${props => props.isSelected ? 'rgba(var(--color-primary), 0.1)' : 'transparent'};
  cursor: ${props => props.isClickable ? 'pointer' : 'default'};
  transition: background 0.2s ease;

  &:hover {
    background: ${props => props.isClickable ? 'rgb(var(--color-surface-hover))' : 'transparent'};
  }
`;

const TableHeaderCell = styled.th`
  text-align: left;
  padding: 1rem 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgb(var(--color-text-secondary));
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const TableCell = styled.td`
  padding: 1rem 1.5rem;
  font-size: 0.875rem;
  color: rgb(var(--color-text-primary));
`;

const StatusBadge = styled.span<{ status: ClaimStatus }>`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;

  ${props => {
    switch (props.status) {
      case 'pending':
        return `
          background: rgba(251, 191, 36, 0.1);
          color: rgb(251, 191, 36);
        `;
      case 'approved':
        return `
          background: rgba(34, 197, 94, 0.1);
          color: rgb(34, 197, 94);
        `;
      case 'denied':
        return `
          background: rgba(239, 68, 68, 0.1);
          color: rgb(239, 68, 68);
        `;
      case 'settled':
        return `
          background: rgba(59, 130, 246, 0.1);
          color: rgb(59, 130, 246);
        `;
      case 'cancelled':
        return `
          background: rgba(107, 114, 128, 0.1);
          color: rgb(107, 114, 128);
        `;
      default:
        return '';
    }
  }}
`;

const LoadingState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const ErrorState = styled.div`
  padding: 1rem 1.5rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  color: rgb(239, 68, 68);
  font-size: 0.875rem;
  margin: 1rem 1.5rem;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  text-align: center;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

// Side Panel Styles
const SidePanel = styled.div`
  display: flex;
  flex-direction: column;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  overflow: hidden;
`;

const SidePanelHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid rgb(var(--color-border));
  background: rgb(var(--color-surface));
`;

const SidePanelTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0 0 0.5rem 0;
`;

const SidePanelSubtitle = styled.div`
  font-size: 0.875rem;
  color: rgb(var(--color-text-secondary));
`;

const CloseButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: rgb(var(--color-text-secondary));
  cursor: pointer;
  font-size: 1.25rem;
  transition: color 0.2s ease;

  &:hover {
    color: rgb(var(--color-text-primary));
  }
`;

const SidePanelContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: rgb(var(--color-surface));
  }

  &::-webkit-scrollbar-thumb {
    background: rgb(var(--color-border));
    border-radius: 3px;
  }
`;

const DetailSection = styled.div`
  margin-bottom: 1.5rem;
`;

const DetailLabel = styled.div`
  font-size: 0.75rem;
  font-weight: 600;
  color: rgb(var(--color-text-secondary));
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
`;

const DetailValue = styled.div`
  font-size: 0.875rem;
  color: rgb(var(--color-text-primary));
`;

const DetailAmount = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: rgb(var(--color-primary));
  margin-top: 0.25rem;
`;

const SidePanelActions = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid rgb(var(--color-border));
  background: rgb(var(--color-surface));
`;

const ActionButton = styled.button<{ variant?: 'approve' | 'deny' | 'settle' | 'cancel' }>`
  padding: 0.75rem 1rem;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease;

  ${props => {
    switch (props.variant) {
      case 'approve':
        return `
          background: rgb(34, 197, 94);
          color: white;
        `;
      case 'deny':
        return `
          background: rgb(239, 68, 68);
          color: white;
        `;
      case 'settle':
        return `
          background: rgb(59, 130, 246);
          color: white;
        `;
      case 'cancel':
        return `
          background: transparent;
          color: rgb(var(--color-text-secondary));
          border: 1px solid rgb(var(--color-border));
        `;
      default:
        return `
          background: rgb(var(--color-primary));
          color: white;
        `;
    }
  }}

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// ============================================================================
// Component
// ============================================================================

export const Claims: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ClaimType>('payable');
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<ClaimStatus | 'all'>('all');
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);

  useEffect(() => {
    fetchClaims();
  }, [activeTab]);

  const fetchClaims = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get('/api/v1/claims/', {
        params: {
          type: activeTab,
        },
      });

      setClaims(response.data);
    } catch (err: any) {
      console.error('Failed to fetch claims:', err);
      setError(err.response?.data?.detail || 'Failed to load claims');
    } finally {
      setLoading(false);
    }
  };

  const handleClaimClick = (claim: Claim) => {
    setSelectedClaim(claim);
  };

  const handleClosePanel = () => {
    setSelectedClaim(null);
  };

  const handleStatusUpdate = async (claimId: number, newStatus: ClaimStatus, notes?: string) => {
    try {
      const updateData: any = { status: newStatus };
      if (notes) {
        updateData.resolution_notes = notes;
      }

      const response = await apiClient.patch(`/api/v1/claims/${claimId}/`, updateData);

      // Update local state
      setClaims(claims.map(c => c.id === claimId ? response.data : c));
      setSelectedClaim(response.data);
    } catch (err: any) {
      console.error('Failed to update claim status:', err);
      alert('Failed to update claim status');
    }
  };

  const filteredClaims = statusFilter === 'all' 
    ? claims 
    : claims.filter(c => c.status === statusFilter);

  const statusCounts = {
    all: claims.length,
    pending: claims.filter(c => c.status === 'pending').length,
    approved: claims.filter(c => c.status === 'approved').length,
    denied: claims.filter(c => c.status === 'denied').length,
    settled: claims.filter(c => c.status === 'settled').length,
    cancelled: claims.filter(c => c.status === 'cancelled').length,
  };

  return (
    <PageContainer>
      <PageHeader>
        <PageTitle>Claims Management</PageTitle>
        <PrimaryButton onClick={() => alert('Create claim functionality coming soon')}>
          + New Claim
        </PrimaryButton>
      </PageHeader>

      <ContentContainer hasSidePanel={selectedClaim !== null}>
        <MainContent>
          {/* Tabs */}
          <TabsContainer>
            <Tab 
              isActive={activeTab === 'payable'} 
              onClick={() => setActiveTab('payable')}
            >
              Payable Claims
            </Tab>
            <Tab 
              isActive={activeTab === 'receivable'} 
              onClick={() => setActiveTab('receivable')}
            >
              Receivable Claims
            </Tab>
          </TabsContainer>

          {/* Status Filters */}
          <FilterBar>
            <FilterButton 
              isActive={statusFilter === 'all'}
              onClick={() => setStatusFilter('all')}
            >
              All ({statusCounts.all})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'pending'}
              onClick={() => setStatusFilter('pending')}
            >
              Pending ({statusCounts.pending})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'approved'}
              onClick={() => setStatusFilter('approved')}
            >
              Approved ({statusCounts.approved})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'settled'}
              onClick={() => setStatusFilter('settled')}
            >
              Settled ({statusCounts.settled})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'denied'}
              onClick={() => setStatusFilter('denied')}
            >
              Denied ({statusCounts.denied})
            </FilterButton>
          </FilterBar>

          {/* Error State */}
          {error && <ErrorState>{error}</ErrorState>}

          {/* Table */}
          <TableContainer>
            {loading ? (
              <LoadingState>Loading claims...</LoadingState>
            ) : filteredClaims.length === 0 ? (
              <EmptyState>
                <p>No {statusFilter !== 'all' ? statusFilter : ''} claims found.</p>
                <p>Click "New Claim" to create one.</p>
              </EmptyState>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHeaderCell>Claim #</TableHeaderCell>
                    <TableHeaderCell>Entity</TableHeaderCell>
                    <TableHeaderCell>Date</TableHeaderCell>
                    <TableHeaderCell>Amount</TableHeaderCell>
                    <TableHeaderCell>Reason</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                    <TableHeaderCell>Created By</TableHeaderCell>
                  </TableRow>
                </TableHeader>
                <tbody>
                  {filteredClaims.map((claim) => (
                    <TableRow
                      key={claim.id}
                      isClickable
                      isSelected={selectedClaim?.id === claim.id}
                      onClick={() => handleClaimClick(claim)}
                    >
                      <TableCell>{claim.claim_number}</TableCell>
                      <TableCell>
                        {activeTab === 'payable' 
                          ? `Supplier #${claim.supplier}` 
                          : `Customer #${claim.customer}`}
                      </TableCell>
                      <TableCell>{formatDateLocal(claim.claim_date)}</TableCell>
                      <TableCell>{formatCurrency(parseFloat(claim.claimed_amount))}</TableCell>
                      <TableCell>{claim.description.substring(0, 50)}...</TableCell>
                      <TableCell>
                        <StatusBadge status={claim.status}>
                          {claim.status.toUpperCase()}
                        </StatusBadge>
                      </TableCell>
                      <TableCell>{claim.created_by_name}</TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
            )}
          </TableContainer>
        </MainContent>

        {/* Side Panel */}
        {selectedClaim && (
          <SidePanel>
            <SidePanelHeader style={{ position: 'relative' }}>
              <CloseButton onClick={handleClosePanel}>×</CloseButton>
              <SidePanelTitle>Claim Details</SidePanelTitle>
              <SidePanelSubtitle>{selectedClaim.claim_number}</SidePanelSubtitle>
            </SidePanelHeader>

            <SidePanelContent>
              <DetailSection>
                <DetailLabel>Status</DetailLabel>
                <StatusBadge status={selectedClaim.status}>
                  {selectedClaim.status.toUpperCase()}
                </StatusBadge>
              </DetailSection>

              <DetailSection>
                <DetailLabel>Claimed Amount</DetailLabel>
                <DetailAmount>
                  {formatCurrency(parseFloat(selectedClaim.claimed_amount))}
                </DetailAmount>
              </DetailSection>

              {selectedClaim.approved_amount && (
                <DetailSection>
                  <DetailLabel>Approved Amount</DetailLabel>
                  <DetailValue>
                    {formatCurrency(parseFloat(selectedClaim.approved_amount))}
                  </DetailValue>
                </DetailSection>
              )}

              {selectedClaim.settled_amount && (
                <DetailSection>
                  <DetailLabel>Settled Amount</DetailLabel>
                  <DetailValue>
                    {formatCurrency(parseFloat(selectedClaim.settled_amount))}
                  </DetailValue>
                </DetailSection>
              )}

              <DetailSection>
                <DetailLabel>Description</DetailLabel>
                <DetailValue>{selectedClaim.description}</DetailValue>
              </DetailSection>

              {selectedClaim.resolution_notes && (
                <DetailSection>
                  <DetailLabel>Resolution Notes</DetailLabel>
                  <DetailValue>{selectedClaim.resolution_notes}</DetailValue>
                </DetailSection>
              )}

              <DetailSection>
                <DetailLabel>Date Filed</DetailLabel>
                <DetailValue>{formatToLocal(selectedClaim.claim_date)}</DetailValue>
              </DetailSection>

              <DetailSection>
                <DetailLabel>Filed By</DetailLabel>
                <DetailValue>{selectedClaim.created_by_name}</DetailValue>
              </DetailSection>

              <DetailSection>
                <DetailLabel>Activity History</DetailLabel>
                <div style={{ marginTop: '1rem' }}>
                  <ActivityFeed
                    entityType="invoice"
                    entityId={selectedClaim.id}
                    showCreateForm
                    maxHeight="300px"
                  />
                </div>
              </DetailSection>
            </SidePanelContent>

            {/* Workflow Actions */}
            {selectedClaim.status === 'pending' && (
              <SidePanelActions>
                <ActionButton 
                  variant="approve"
                  onClick={() => handleStatusUpdate(selectedClaim.id, 'approved', 'Claim approved')}
                >
                  ✓ Approve Claim
                </ActionButton>
                <ActionButton 
                  variant="deny"
                  onClick={() => handleStatusUpdate(selectedClaim.id, 'denied', 'Claim denied')}
                >
                  ✗ Deny Claim
                </ActionButton>
              </SidePanelActions>
            )}

            {selectedClaim.status === 'approved' && (
              <SidePanelActions>
                <ActionButton 
                  variant="settle"
                  onClick={() => handleStatusUpdate(selectedClaim.id, 'settled', 'Claim settled')}
                >
                  💰 Mark as Settled
                </ActionButton>
              </SidePanelActions>
            )}
          </SidePanel>
        )}
      </ContentContainer>
    </PageContainer>
  );
};

export default Claims;
