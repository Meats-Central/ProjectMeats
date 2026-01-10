/**
 * Payables Purchase Orders Page
 * 
 * Accounting view of purchase orders showing payment status and outstanding balances.
 * This is a specialized view focused on payables accounting rather than procurement.
 * 
 * Features:
 * - View all purchase orders from accounting perspective
 * - Filter by payment status (unpaid, partial, paid)
 * - Track outstanding amounts and due dates
 * - Side panel with order details and activity feed
 * - Record payment functionality with modal
 * 
 * Pattern: Follows Invoices.tsx architecture with side panel integration
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ActivityFeed, RecordPaymentModal, PaymentHistoryList } from '../../components/Shared';
import { apiClient } from '../../services/apiService';
import { formatCurrency } from '../../shared/utils';
import { formatDateLocal } from '../../utils/formatters';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface PurchaseOrder {
  id: number;
  tenant: string;
  order_number: string;
  supplier: number;
  supplier_name?: string;
  order_date: string;
  delivery_date: string | null;
  status: string;
  payment_status?: 'unpaid' | 'partial' | 'paid';
  total_amount: string;
  paid_amount?: string;
  outstanding_amount?: string;
  notes: string;
  created_on: string;
}

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

const ContentContainer = styled.div<{ hasSidePanel?: boolean }>`
  display: grid;
  grid-template-columns: ${props => props.hasSidePanel ? '1fr 400px' : '1fr'};
  gap: 1.5rem;
  transition: grid-template-columns 0.3s ease;
  flex: 1;
  overflow: hidden;
  
  /* Stack layout on tablets and mobile */
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
`;

const FilterBar = styled.div`
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
`;

const FilterButton = styled.button<{ active?: boolean }>`
  padding: 0.5rem 1rem;
  background: ${props => props.active ? 'rgb(var(--color-primary))' : 'rgb(var(--color-surface))'};
  color: ${props => props.active ? 'white' : 'rgb(var(--color-text-primary))'};
  border: 1px solid ${props => props.active ? 'rgb(var(--color-primary))' : 'rgb(var(--color-border))'};
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    opacity: 0.9;
  }
`;

const TableContainer = styled.div`
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  overflow: hidden;
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const TableWrapper = styled.div`
  overflow-y: auto;
  flex: 1;

  /* Only enable horizontal scroll on small screens when truly needed */
  @media (max-width: 768px) {
    overflow-x: auto;
  }

  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgb(var(--color-background));
  }

  &::-webkit-scrollbar-thumb {
    background: rgb(var(--color-border));
    border-radius: 4px;
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  
  /* Allow table to shrink on smaller screens */
  @media (max-width: 768px) {
    min-width: 600px; /* Minimum width to prevent column squashing */
  }
`;

const TableHeader = styled.thead`
  background: rgb(var(--color-background));
  border-bottom: 1px solid rgb(var(--color-border));
  position: sticky;
  top: 0;
  z-index: 10;
`;

const TableRow = styled.tr<{ clickable?: boolean; selected?: boolean }>`
  border-bottom: 1px solid rgb(var(--color-border));
  cursor: ${props => props.clickable ? 'pointer' : 'default'};
  background: ${props => props.selected ? 'rgba(var(--color-primary), 0.05)' : 'transparent'};
  transition: background 0.15s ease;

  &:hover {
    background: ${props => props.clickable ? 'rgba(var(--color-primary), 0.08)' : 'transparent'};
  }

  &:last-child {
    border-bottom: none;
  }
`;

const TableHead = styled.th`
  padding: 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgb(var(--color-text-secondary));
`;

const TableCell = styled.td`
  padding: 1rem;
  font-size: 0.875rem;
  color: rgb(var(--color-text-primary));
`;

const StatusBadge = styled.span<{ status: string }>`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  ${props => {
    switch (props.status) {
      case 'paid':
        return 'background: rgba(34, 197, 94, 0.15); color: rgba(34, 197, 94, 1);';
      case 'partial':
        return 'background: rgba(234, 179, 8, 0.15); color: rgba(234, 179, 8, 1);';
      case 'unpaid':
      default:
        return 'background: rgba(239, 68, 68, 0.15); color: rgba(239, 68, 68, 1);';
    }
  }}
`;

const SidePanel = styled.div`
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
  max-height: calc(100vh - 8rem);

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgb(var(--color-background));
  }

  &::-webkit-scrollbar-thumb {
    background: rgb(var(--color-border));
    border-radius: 4px;
  }
`;

const SidePanelHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgb(var(--color-border));
`;

const SidePanelTitle = styled.h2`
  font-size: 1.25rem;
  font-weight: 600;
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

const RecordPaymentButton = styled.button`
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: rgb(34, 197, 94);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(34, 197, 94, 0.15);
    border-color: rgba(34, 197, 94, 0.5);
  }
  
  &:active {
    transform: scale(0.98);
  }
`;

const DetailSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const DetailLabel = styled.div`
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgb(var(--color-text-secondary));
`;

const DetailValue = styled.div`
  font-size: 0.875rem;
  color: rgb(var(--color-text-primary));
`;

const LoadingMessage = styled.div`
  padding: 3rem;
  text-align: center;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const ErrorMessage = styled.div`
  padding: 3rem;
  text-align: center;
  color: rgba(239, 68, 68, 1);
  font-size: 0.875rem;
`;

const EmptyMessage = styled.div`
  padding: 3rem;
  text-align: center;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

// ============================================================================
// Main Component
// ============================================================================

const PayablePOs: React.FC = () => {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<'all' | 'unpaid' | 'partial' | 'paid'>('all');
  const [selectedOrder, setSelectedOrder] = useState<PurchaseOrder | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  // Fetch purchase orders with accounting focus
  const fetchOrders = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = {};
      if (statusFilter !== 'all') {
        params.payment_status = statusFilter;
      }
      
      const response = await apiClient.get('purchase-orders/', { params });
      
      // Transform orders to include payment status (mocked for now - backend enhancement needed)
      const ordersWithPaymentStatus = response.data.results || response.data;
      setOrders(ordersWithPaymentStatus.map((order: PurchaseOrder) => ({
        ...order,
        payment_status: order.payment_status || 'unpaid', // Default to unpaid if not provided
        outstanding_amount: order.outstanding_amount || order.total_amount,
      })));
    } catch (err: any) {
      console.error('Failed to fetch purchase orders:', err);
      setError(err.response?.data?.message || 'Failed to load purchase orders');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [statusFilter]);

  // Count orders by status
  const counts = {
    all: orders.length,
    unpaid: orders.filter(o => o.payment_status === 'unpaid').length,
    partial: orders.filter(o => o.payment_status === 'partial').length,
    paid: orders.filter(o => o.payment_status === 'paid').length,
  };

  return (
    <PageContainer>
      <PageHeader>
        <PageTitle>Payables - Purchase Orders</PageTitle>
      </PageHeader>

      <ContentContainer hasSidePanel={!!selectedOrder}>
        <MainContent>
          <FilterBar>
            <FilterButton active={statusFilter === 'all'} onClick={() => setStatusFilter('all')}>
              All ({counts.all})
            </FilterButton>
            <FilterButton active={statusFilter === 'unpaid'} onClick={() => setStatusFilter('unpaid')}>
              Unpaid ({counts.unpaid})
            </FilterButton>
            <FilterButton active={statusFilter === 'partial'} onClick={() => setStatusFilter('partial')}>
              Partial ({counts.partial})
            </FilterButton>
            <FilterButton active={statusFilter === 'paid'} onClick={() => setStatusFilter('paid')}>
              Paid ({counts.paid})
            </FilterButton>
          </FilterBar>

          <TableContainer>
            {loading ? (
              <LoadingMessage>Loading purchase orders...</LoadingMessage>
            ) : error ? (
              <ErrorMessage>{error}</ErrorMessage>
            ) : orders.length === 0 ? (
              <EmptyMessage>No purchase orders found</EmptyMessage>
            ) : (
              <TableWrapper>
                <Table>
                  <TableHeader>
                    <tr>
                      <TableHead>PO Number</TableHead>
                      <TableHead>Supplier</TableHead>
                      <TableHead>Order Date</TableHead>
                      <TableHead>Total Amount</TableHead>
                      <TableHead>Outstanding</TableHead>
                      <TableHead>Payment Status</TableHead>
                    </tr>
                  </TableHeader>
                  <tbody>
                    {orders.map(order => (
                      <TableRow
                        key={order.id}
                        clickable
                        selected={selectedOrder?.id === order.id}
                        onClick={() => setSelectedOrder(order)}
                      >
                        <TableCell>{order.order_number}</TableCell>
                        <TableCell>{order.supplier_name || `Supplier #${order.supplier}`}</TableCell>
                        <TableCell>{formatDateLocal(order.order_date)}</TableCell>
                        <TableCell>{formatCurrency(parseFloat(order.total_amount))}</TableCell>
                        <TableCell>{formatCurrency(parseFloat(order.outstanding_amount || order.total_amount))}</TableCell>
                        <TableCell>
                          <StatusBadge status={order.payment_status || 'unpaid'}>
                            {(order.payment_status || 'unpaid').toUpperCase()}
                          </StatusBadge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </tbody>
                </Table>
              </TableWrapper>
            )}
          </TableContainer>
        </MainContent>

        {selectedOrder && (
          <SidePanel>
            <SidePanelHeader>
              <SidePanelTitle>{selectedOrder.order_number}</SidePanelTitle>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                {selectedOrder.payment_status !== 'paid' && (
                  <RecordPaymentButton onClick={() => setShowPaymentModal(true)}>
                    💰 Record Payment
                  </RecordPaymentButton>
                )}
                <CloseButton onClick={() => setSelectedOrder(null)}>×</CloseButton>
              </div>
            </SidePanelHeader>

            <DetailSection>
              <DetailLabel>Supplier</DetailLabel>
              <DetailValue>
                {selectedOrder.supplier_name || `Supplier #${selectedOrder.supplier}`}
              </DetailValue>
            </DetailSection>

            <DetailSection>
              <DetailLabel>Order Date</DetailLabel>
              <DetailValue>{formatDateLocal(selectedOrder.order_date)}</DetailValue>
            </DetailSection>

            {selectedOrder.delivery_date && (
              <DetailSection>
                <DetailLabel>Delivery Date</DetailLabel>
                <DetailValue>{formatDateLocal(selectedOrder.delivery_date)}</DetailValue>
              </DetailSection>
            )}

            <DetailSection>
              <DetailLabel>Financial Summary</DetailLabel>
              <DetailValue>
                <div>Total: {formatCurrency(parseFloat(selectedOrder.total_amount))}</div>
                <div>
                  Outstanding: {formatCurrency(parseFloat(selectedOrder.outstanding_amount || selectedOrder.total_amount))}
                </div>
              </DetailValue>
            </DetailSection>

            <DetailSection>
              <DetailLabel>Payment Status</DetailLabel>
              <DetailValue>
                <StatusBadge status={selectedOrder.payment_status || 'unpaid'}>
                  {(selectedOrder.payment_status || 'unpaid').toUpperCase()}
                </StatusBadge>
              </DetailValue>
            </DetailSection>

            {selectedOrder.notes && (
              <DetailSection>
                <DetailLabel>Notes</DetailLabel>
                <DetailValue>{selectedOrder.notes}</DetailValue>
              </DetailSection>
            )}

            <DetailSection>
              <DetailLabel>Payment History</DetailLabel>
              <PaymentHistoryList
                entityType="purchase_order"
                entityId={selectedOrder.id}
              />
            </DetailSection>

            <DetailSection>
              <DetailLabel>Activity Log</DetailLabel>
              <ActivityFeed
                entityType="purchase_order"
                entityId={selectedOrder.id}
                showCreateForm={true}
                maxHeight="400px"
              />
            </DetailSection>

            <RecordPaymentModal
              isOpen={showPaymentModal}
              onClose={() => setShowPaymentModal(false)}
              entityType="purchase_order"
              entityId={selectedOrder.id}
              entityReference={selectedOrder.order_number}
              outstandingAmount={parseFloat(selectedOrder.outstanding_amount || selectedOrder.total_amount || '0')}
              onSuccess={() => {
                fetchOrders();
                setShowPaymentModal(false);
              }}
            />
          </SidePanel>
        )}
      </ContentContainer>
    </PageContainer>
  );
};

export default PayablePOs;
