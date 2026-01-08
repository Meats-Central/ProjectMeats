/**
 * Receivables Sales Orders Page
 * 
 * Accounting view of sales orders showing payment status and outstanding balances.
 * This is a specialized view focused on receivables accounting rather than sales.
 * 
 * Features:
 * - View all sales orders from accounting perspective
 * - Filter by payment status (unpaid, partial, paid)
 * - Track outstanding amounts and due dates
 * - Quick access to customer information
 * 
 * Pattern: Uses DataTable pattern similar to SalesOrders but with accounting focus
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiClient } from '../../services/apiService';
import { formatCurrency } from '../../shared/utils';
import { formatDateLocal } from '../../utils/formatters';

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

const FilterBar = styled.div`
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
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
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background: rgb(var(--color-background));
  border-bottom: 1px solid rgb(var(--color-border));
  position: sticky;
  top: 0;
  z-index: 10;
`;

const TableRow = styled.tr`
  border-bottom: 1px solid rgb(var(--color-border));
  cursor: pointer;
  transition: background 0.15s ease;

  &:hover {
    background: rgba(var(--color-primary), 0.05);
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

const ReceivableSOs: React.FC = () => {
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<'all' | 'unpaid' | 'partial' | 'paid'>('all');

  // Fetch sales orders with accounting focus
  const fetchOrders = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = {};
      if (statusFilter !== 'all') {
        params.payment_status = statusFilter;
      }
      
      const response = await apiClient.get('/api/v1/sales-orders/', { params });
      
      // Transform orders to include payment status (mocked for now - backend enhancement needed)
      const ordersWithPaymentStatus = response.data.results || response.data;
      setOrders(ordersWithPaymentStatus.map((order: SalesOrder) => ({
        ...order,
        payment_status: order.payment_status || 'unpaid', // Default to unpaid if not provided
        outstanding_amount: order.outstanding_amount || order.total_amount,
      })));
    } catch (err: any) {
      console.error('Failed to fetch sales orders:', err);
      setError(err.response?.data?.message || 'Failed to load sales orders');
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
        <PageTitle>Receivables - Sales Orders</PageTitle>
      </PageHeader>

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
          <LoadingMessage>Loading sales orders...</LoadingMessage>
        ) : error ? (
          <ErrorMessage>{error}</ErrorMessage>
        ) : orders.length === 0 ? (
          <EmptyMessage>No sales orders found</EmptyMessage>
        ) : (
          <Table>
            <TableHeader>
              <tr>
                <TableHead>SO Number</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Order Date</TableHead>
                <TableHead>Total Amount</TableHead>
                <TableHead>Outstanding</TableHead>
                <TableHead>Payment Status</TableHead>
              </tr>
            </TableHeader>
            <tbody>
              {orders.map(order => (
                <TableRow key={order.id}>
                  <TableCell>{order.order_number}</TableCell>
                  <TableCell>{order.customer_name || `Customer #${order.customer}`}</TableCell>
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
        )}
      </TableContainer>
    </PageContainer>
  );
};

export default ReceivableSOs;
