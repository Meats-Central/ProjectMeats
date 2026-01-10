/**
 * Sales Orders Page
 * 
 * Comprehensive sales order management with customer tracking and activity logging.
 * 
 * Features:
 * - View all sales orders with status filtering
 * - Search by customer, order number, or date range
 * - Side panel with order details and activity feed
 * - Theme-compliant styling (32px headers, color variables)
 * - Timezone-aware date formatting
 * 
 * Pattern: Follows Claims.tsx architecture for consistency
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ActivityFeed, CreateOrderModal } from '../../components/Shared';
import { apiClient } from '../../services/apiService';
import { formatCurrency } from '../../shared/utils';
import { formatDateLocal, formatToLocal } from '../../utils/formatters';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface SalesOrder {
  id: number;
  tenant: string;
  order_number: string;
  customer: number;
  customer_name?: string;
  order_date: string;
  delivery_date: string | null;
  status: 'draft' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total_amount: string;
  notes: string;
  created_by: number | null;
  created_by_name: string;
  created_on: string;
  updated_on: string;
}

type OrderStatus = 'draft' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

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

const HeaderActions = styled.div`
  display: flex;
  gap: 0.75rem;
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
  
  /* Stack layout on tablets and mobile */
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    height: auto;
  }
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  overflow: hidden;
`;

const FilterBar = styled.div`
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: rgb(var(--color-surface));
  border-bottom: 1px solid rgb(var(--color-border));
  flex-wrap: wrap;
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

const SearchBar = styled.input`
  flex: 1;
  min-width: 250px;
  padding: 0.5rem 1rem;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-text-primary));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-sm);
  font-size: 0.875rem;

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }

  &::placeholder {
    color: rgb(var(--color-text-secondary));
  }
`;

const TableContainer = styled.div`
  flex: 1;
  overflow-y: auto;

  /* Only enable horizontal scroll on small screens when truly needed */
  @media (max-width: 768px) {
    overflow-x: auto;
  }

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
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
  
  /* Reduce minimum width on smaller screens */
  @media (min-width: 769px) {
    min-width: 800px;
  }
  
  @media (max-width: 768px) {
    min-width: 600px;
  }
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
  white-space: nowrap;
`;

const TableCell = styled.td`
  padding: 1rem 1.5rem;
  font-size: 0.875rem;
  color: rgb(var(--color-text-primary));
  white-space: nowrap;
`;

const StatusBadge = styled.span<{ status: OrderStatus }>`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;

  ${props => {
    switch (props.status) {
      case 'draft':
        return `
          background: rgba(107, 114, 128, 0.1);
          color: rgb(107, 114, 128);
        `;
      case 'confirmed':
        return `
          background: rgba(59, 130, 246, 0.1);
          color: rgb(59, 130, 246);
        `;
      case 'processing':
        return `
          background: rgba(251, 191, 36, 0.1);
          color: rgb(251, 191, 36);
        `;
      case 'shipped':
        return `
          background: rgba(139, 92, 246, 0.1);
          color: rgb(139, 92, 246);
        `;
      case 'delivered':
        return `
          background: rgba(34, 197, 94, 0.1);
          color: rgb(34, 197, 94);
        `;
      case 'cancelled':
        return `
          background: rgba(239, 68, 68, 0.1);
          color: rgb(239, 68, 68);
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
  position: relative;
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

// ============================================================================
// Component
// ============================================================================

export const SalesOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<OrderStatus | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get('sales-orders/');
      setOrders(response.data.results || response.data);
    } catch (err: any) {
      console.error('Failed to fetch sales orders:', err);
      setError(err.response?.data?.detail || 'Failed to load sales orders');
    } finally {
      setLoading(false);
    }
  };

  const handleOrderClick = (order: SalesOrder) => {
    setSelectedOrder(order);
  };

  const handleClosePanel = () => {
    setSelectedOrder(null);
  };

  // Filter and search logic
  const filteredOrders = orders.filter(order => {
    // Status filter
    if (statusFilter !== 'all' && order.status !== statusFilter) {
      return false;
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        order.order_number.toLowerCase().includes(query) ||
        order.customer_name?.toLowerCase().includes(query) ||
        order.notes.toLowerCase().includes(query)
      );
    }

    return true;
  });

  const statusCounts = {
    all: orders.length,
    draft: orders.filter(o => o.status === 'draft').length,
    confirmed: orders.filter(o => o.status === 'confirmed').length,
    processing: orders.filter(o => o.status === 'processing').length,
    shipped: orders.filter(o => o.status === 'shipped').length,
    delivered: orders.filter(o => o.status === 'delivered').length,
    cancelled: orders.filter(o => o.status === 'cancelled').length,
  };

  return (
    <PageContainer>
      <PageHeader>
        <PageTitle>Sales Orders</PageTitle>
        <HeaderActions>
          <PrimaryButton onClick={() => setIsModalOpen(true)}>
            + New Sales Order
          </PrimaryButton>
        </HeaderActions>
      </PageHeader>

      <ContentContainer hasSidePanel={selectedOrder !== null}>
        <MainContent>
          {/* Filters and Search */}
          <FilterBar>
            <FilterButton 
              isActive={statusFilter === 'all'}
              onClick={() => setStatusFilter('all')}
            >
              All ({statusCounts.all})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'draft'}
              onClick={() => setStatusFilter('draft')}
            >
              Draft ({statusCounts.draft})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'confirmed'}
              onClick={() => setStatusFilter('confirmed')}
            >
              Confirmed ({statusCounts.confirmed})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'processing'}
              onClick={() => setStatusFilter('processing')}
            >
              Processing ({statusCounts.processing})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'shipped'}
              onClick={() => setStatusFilter('shipped')}
            >
              Shipped ({statusCounts.shipped})
            </FilterButton>
            <FilterButton 
              isActive={statusFilter === 'delivered'}
              onClick={() => setStatusFilter('delivered')}
            >
              Delivered ({statusCounts.delivered})
            </FilterButton>
            <SearchBar
              type="text"
              placeholder="Search orders, customers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </FilterBar>

          {/* Error State */}
          {error && <ErrorState>{error}</ErrorState>}

          {/* Table */}
          <TableContainer>
            {loading ? (
              <LoadingState>Loading sales orders...</LoadingState>
            ) : filteredOrders.length === 0 ? (
              <EmptyState>
                <p>No sales orders found.</p>
                <p>Click "New Sales Order" to create your first order.</p>
              </EmptyState>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHeaderCell>Order #</TableHeaderCell>
                    <TableHeaderCell>Customer</TableHeaderCell>
                    <TableHeaderCell>Order Date</TableHeaderCell>
                    <TableHeaderCell>Delivery Date</TableHeaderCell>
                    <TableHeaderCell>Amount</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                  </TableRow>
                </TableHeader>
                <tbody>
                  {filteredOrders.map((order) => (
                    <TableRow
                      key={order.id}
                      isClickable
                      isSelected={selectedOrder?.id === order.id}
                      onClick={() => handleOrderClick(order)}
                    >
                      <TableCell>{order.order_number}</TableCell>
                      <TableCell>{order.customer_name || `Customer #${order.customer}`}</TableCell>
                      <TableCell>{formatDateLocal(order.order_date)}</TableCell>
                      <TableCell>{order.delivery_date ? formatDateLocal(order.delivery_date) : 'Not scheduled'}</TableCell>
                      <TableCell>{formatCurrency(parseFloat(order.total_amount))}</TableCell>
                      <TableCell>
                        <StatusBadge status={order.status}>
                          {order.status.toUpperCase()}
                        </StatusBadge>
                      </TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
            )}
          </TableContainer>
        </MainContent>

        {/* Side Panel */}
        {selectedOrder && (
          <SidePanel>
            <SidePanelHeader>
              <CloseButton onClick={handleClosePanel}>×</CloseButton>
              <SidePanelTitle>Order Details</SidePanelTitle>
              <SidePanelSubtitle>{selectedOrder.order_number}</SidePanelSubtitle>
            </SidePanelHeader>

            <SidePanelContent>
              <DetailSection>
                <DetailLabel>Status</DetailLabel>
                <StatusBadge status={selectedOrder.status}>
                  {selectedOrder.status.toUpperCase()}
                </StatusBadge>
              </DetailSection>

              <DetailSection>
                <DetailLabel>Total Amount</DetailLabel>
                <DetailAmount>
                  {formatCurrency(parseFloat(selectedOrder.total_amount))}
                </DetailAmount>
              </DetailSection>

              <DetailSection>
                <DetailLabel>Customer</DetailLabel>
                <DetailValue>
                  {selectedOrder.customer_name || `Customer #${selectedOrder.customer}`}
                </DetailValue>
              </DetailSection>

              <DetailSection>
                <DetailLabel>Order Date</DetailLabel>
                <DetailValue>{formatToLocal(selectedOrder.order_date)}</DetailValue>
              </DetailSection>

              {selectedOrder.delivery_date && (
                <DetailSection>
                  <DetailLabel>Delivery Date</DetailLabel>
                  <DetailValue>{formatToLocal(selectedOrder.delivery_date)}</DetailValue>
                </DetailSection>
              )}

              {selectedOrder.notes && (
                <DetailSection>
                  <DetailLabel>Notes</DetailLabel>
                  <DetailValue>{selectedOrder.notes}</DetailValue>
                </DetailSection>
              )}

              <DetailSection>
                <DetailLabel>Created By</DetailLabel>
                <DetailValue>{selectedOrder.created_by_name}</DetailValue>
              </DetailSection>

              <DetailSection>
                <DetailLabel>Activity History</DetailLabel>
                <div style={{ marginTop: '1rem' }}>
                  <ActivityFeed
                    entityType="sales_order"
                    entityId={selectedOrder.id}
                    showCreateForm
                    maxHeight="300px"
                  />
                </div>
              </DetailSection>
            </SidePanelContent>
          </SidePanel>
        )}
      </ContentContainer>

      <CreateOrderModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchOrders}
      />
    </PageContainer>
  );
};

export default SalesOrdersPage;
