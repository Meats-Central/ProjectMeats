/**
 * Invoices Page (Receivables)
 * 
 * Customer invoice management with payment tracking and activity logging.
 * 
 * Features:
 * - View all customer invoices with status filtering
 * - Filter by status: Draft | Sent | Paid | Overdue | Cancelled
 * - Side panel with invoice details and activity feed
 * - Payment tracking with outstanding amounts
 * - Theme-compliant styling (32px headers, color variables)
 * 
 * Pattern: Follows Claims.tsx/SalesOrders.tsx architecture for consistency
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

interface Invoice {
  id: number;
  tenant: string;
  invoice_number: string;
  customer: number;
  customer_name?: string;
  sales_order: number | null;
  our_sales_order_num: string;
  date_time_stamp: string;
  due_date: string | null;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  total_amount: string;
  paid_amount?: string;
  outstanding_amount?: string;
  notes: string;
  created_by: number | null;
  created_by_name: string;
  created_on: string;
  updated_on: string;
}

type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';

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
  transition: grid-template-columns 0.3s ease;
  flex: 1;
  overflow: hidden;
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

const SearchInput = styled.input`
  padding: 0.5rem 1rem;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  min-width: 250px;

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }

  &::placeholder {
    color: rgb(var(--color-text-secondary));
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
  overflow-x: auto;
  overflow-y: auto;
  flex: 1;

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

  &::-webkit-scrollbar-thumb:hover {
    background: rgb(var(--color-text-secondary));
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
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

const StatusBadge = styled.span<{ status: InvoiceStatus }>`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  ${props => {
    switch (props.status) {
      case 'paid':
        return 'background: rgba(34, 197, 94, 0.15); color: rgba(34, 197, 94, 1);';
      case 'sent':
        return 'background: rgba(59, 130, 246, 0.15); color: rgba(59, 130, 246, 1);';
      case 'overdue':
        return 'background: rgba(239, 68, 68, 0.15); color: rgba(239, 68, 68, 1);';
      case 'cancelled':
        return 'background: rgba(107, 114, 128, 0.15); color: rgba(107, 114, 128, 1);';
      case 'draft':
      default:
        return 'background: rgba(234, 179, 8, 0.15); color: rgba(234, 179, 8, 1);';
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

const Invoices: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<InvoiceStatus | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);

  // Fetch invoices
  const fetchInvoices = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      const response = await apiClient.get('/api/v1/invoices/', { params });
      const invoicesData = response.data.results || response.data;
      
      // Calculate outstanding amounts (mocked for now - backend enhancement needed)
      const invoicesWithOutstanding = invoicesData.map((invoice: Invoice) => ({
        ...invoice,
        outstanding_amount: invoice.outstanding_amount || 
                          (invoice.status === 'paid' ? '0.00' : invoice.total_amount),
      }));
      
      setInvoices(invoicesWithOutstanding);
    } catch (err: any) {
      console.error('Failed to fetch invoices:', err);
      setError(err.response?.data?.message || 'Failed to load invoices');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, [statusFilter]);

  // Filter invoices by search query
  const filteredInvoices = invoices.filter(invoice => {
    if (!searchQuery) return true;
    
    const query = searchQuery.toLowerCase();
    return (
      invoice.invoice_number.toLowerCase().includes(query) ||
      invoice.customer_name?.toLowerCase().includes(query) ||
      invoice.our_sales_order_num.toLowerCase().includes(query)
    );
  });

  // Count invoices by status
  const counts = {
    all: invoices.length,
    draft: invoices.filter(i => i.status === 'draft').length,
    sent: invoices.filter(i => i.status === 'sent').length,
    paid: invoices.filter(i => i.status === 'paid').length,
    overdue: invoices.filter(i => i.status === 'overdue').length,
    cancelled: invoices.filter(i => i.status === 'cancelled').length,
  };

  return (
    <PageContainer>
      <PageHeader>
        <PageTitle>Receivables - Invoices</PageTitle>
        <HeaderActions>
          <PrimaryButton onClick={() => alert('Create Invoice feature coming soon')}>
            + Create Invoice
          </PrimaryButton>
        </HeaderActions>
      </PageHeader>

      <ContentContainer hasSidePanel={!!selectedInvoice}>
        <MainContent>
          <FilterBar>
            <FilterButton active={statusFilter === 'all'} onClick={() => setStatusFilter('all')}>
              All ({counts.all})
            </FilterButton>
            <FilterButton active={statusFilter === 'draft'} onClick={() => setStatusFilter('draft')}>
              Draft ({counts.draft})
            </FilterButton>
            <FilterButton active={statusFilter === 'sent'} onClick={() => setStatusFilter('sent')}>
              Sent ({counts.sent})
            </FilterButton>
            <FilterButton active={statusFilter === 'paid'} onClick={() => setStatusFilter('paid')}>
              Paid ({counts.paid})
            </FilterButton>
            <FilterButton active={statusFilter === 'overdue'} onClick={() => setStatusFilter('overdue')}>
              Overdue ({counts.overdue})
            </FilterButton>
            <FilterButton active={statusFilter === 'cancelled'} onClick={() => setStatusFilter('cancelled')}>
              Cancelled ({counts.cancelled})
            </FilterButton>
            <SearchInput
              type="text"
              placeholder="Search invoices..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </FilterBar>

          <TableContainer>
            {loading ? (
              <LoadingMessage>Loading invoices...</LoadingMessage>
            ) : error ? (
              <ErrorMessage>{error}</ErrorMessage>
            ) : filteredInvoices.length === 0 ? (
              <EmptyMessage>
                {searchQuery ? 'No invoices match your search' : 'No invoices found'}
              </EmptyMessage>
            ) : (
              <TableWrapper>
                <Table>
                  <TableHeader>
                    <tr>
                      <TableHead>Invoice #</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>SO Reference</TableHead>
                      <TableHead>Invoice Date</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Total Amount</TableHead>
                      <TableHead>Outstanding</TableHead>
                      <TableHead>Status</TableHead>
                    </tr>
                  </TableHeader>
                  <tbody>
                    {filteredInvoices.map(invoice => (
                      <TableRow
                        key={invoice.id}
                        clickable
                        selected={selectedInvoice?.id === invoice.id}
                        onClick={() => setSelectedInvoice(invoice)}
                      >
                        <TableCell>{invoice.invoice_number}</TableCell>
                        <TableCell>{invoice.customer_name || `Customer #${invoice.customer}`}</TableCell>
                        <TableCell>{invoice.our_sales_order_num || '-'}</TableCell>
                        <TableCell>{formatDateLocal(invoice.date_time_stamp)}</TableCell>
                        <TableCell>{invoice.due_date ? formatDateLocal(invoice.due_date) : '-'}</TableCell>
                        <TableCell>{formatCurrency(parseFloat(invoice.total_amount))}</TableCell>
                        <TableCell>
                          {formatCurrency(parseFloat(invoice.outstanding_amount || invoice.total_amount))}
                        </TableCell>
                        <TableCell>
                          <StatusBadge status={invoice.status}>
                            {invoice.status.toUpperCase()}
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

        {selectedInvoice && (
          <SidePanel>
            <SidePanelHeader>
              <SidePanelTitle>{selectedInvoice.invoice_number}</SidePanelTitle>
              <CloseButton onClick={() => setSelectedInvoice(null)}>×</CloseButton>
            </SidePanelHeader>

            <DetailSection>
              <DetailLabel>Customer</DetailLabel>
              <DetailValue>
                {selectedInvoice.customer_name || `Customer #${selectedInvoice.customer}`}
              </DetailValue>
            </DetailSection>

            <DetailSection>
              <DetailLabel>Sales Order</DetailLabel>
              <DetailValue>{selectedInvoice.our_sales_order_num || 'N/A'}</DetailValue>
            </DetailSection>

            <DetailSection>
              <DetailLabel>Invoice Date</DetailLabel>
              <DetailValue>{formatDateLocal(selectedInvoice.date_time_stamp)}</DetailValue>
            </DetailSection>

            <DetailSection>
              <DetailLabel>Due Date</DetailLabel>
              <DetailValue>
                {selectedInvoice.due_date ? formatDateLocal(selectedInvoice.due_date) : 'Not set'}
              </DetailValue>
            </DetailSection>

            <DetailSection>
              <DetailLabel>Financial Summary</DetailLabel>
              <DetailValue>
                <div>Total: {formatCurrency(parseFloat(selectedInvoice.total_amount))}</div>
                <div>
                  Outstanding: {formatCurrency(parseFloat(selectedInvoice.outstanding_amount || selectedInvoice.total_amount))}
                </div>
              </DetailValue>
            </DetailSection>

            <DetailSection>
              <DetailLabel>Status</DetailLabel>
              <DetailValue>
                <StatusBadge status={selectedInvoice.status}>
                  {selectedInvoice.status.toUpperCase()}
                </StatusBadge>
              </DetailValue>
            </DetailSection>

            {selectedInvoice.notes && (
              <DetailSection>
                <DetailLabel>Notes</DetailLabel>
                <DetailValue>{selectedInvoice.notes}</DetailValue>
              </DetailSection>
            )}

            <DetailSection>
              <DetailLabel>Activity Log</DetailLabel>
              <ActivityFeed
                entityType="invoice"
                entityId={selectedInvoice.id}
                showCreateForm={true}
                maxHeight="400px"
              />
            </DetailSection>
          </SidePanel>
        )}
      </ContentContainer>
    </PageContainer>
  );
};

export default Invoices;
