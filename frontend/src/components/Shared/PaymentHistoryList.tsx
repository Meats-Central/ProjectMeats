/**
 * Payment History List Component
 * 
 * Displays a chronological list of payment transactions for an order or invoice.
 * Shows date, reference number, amount, and payment method.
 * 
 * Features:
 * - Fetches payment history from API based on entity type and ID
 * - Shows empty state when no payments exist
 * - Clean, readable design matching theme
 * - Automatic formatting of dates and currency
 * 
 * Usage:
 * <PaymentHistoryList 
 *   entityType="purchase_order"
 *   entityId={123}
 * />
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiClient } from '../../services/apiService';
import { formatCurrency } from '../../shared/utils';
import { formatDateLocal } from '../../utils/formatters';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface PaymentTransaction {
  id: number;
  amount: string;
  payment_date: string;
  payment_method: string;
  reference_number: string;
  notes: string;
  created_by_name: string;
  created_on: string;
}

interface PaymentHistoryListProps {
  entityType: 'purchase_order' | 'sales_order' | 'invoice';
  entityId: number;
}

// ============================================================================
// Styled Components
// ============================================================================

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const PaymentItem = styled.div`
  padding: 12px;
  background: var(--color-bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const PaymentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const PaymentDate = styled.span`
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
`;

const PaymentAmount = styled.span`
  font-size: 16px;
  font-weight: 700;
  color: var(--color-success);
`;

const PaymentDetails = styled.div`
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
`;

const DetailItem = styled.div`
  display: flex;
  gap: 4px;
`;

const DetailLabel = styled.span`
  font-weight: 500;
`;

const DetailValue = styled.span`
  color: var(--color-text-primary);
`;

const EmptyState = styled.div`
  padding: 24px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
  background: var(--color-bg-secondary);
  border-radius: 6px;
  border: 1px dashed var(--color-border);
`;

const LoadingState = styled.div`
  padding: 24px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
`;

const ErrorState = styled.div`
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
  border-radius: 6px;
  font-size: 14px;
`;

// ============================================================================
// Component
// ============================================================================

export const PaymentHistoryList: React.FC<PaymentHistoryListProps> = ({ 
  entityType, 
  entityId 
}) => {
  const [payments, setPayments] = useState<PaymentTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPaymentHistory();
  }, [entityType, entityId]);

  const fetchPaymentHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get('payments/', {
        params: { [entityType]: entityId }
      });
      
      // Sort by payment date (newest first)
      const sortedPayments = response.data.sort((a: PaymentTransaction, b: PaymentTransaction) => {
        return new Date(b.payment_date).getTime() - new Date(a.payment_date).getTime();
      });
      
      setPayments(sortedPayments);
    } catch (err: any) {
      console.error('Error fetching payment history:', err);
      setError('Failed to load payment history');
    } finally {
      setLoading(false);
    }
  };

  const getPaymentMethodLabel = (method: string): string => {
    const labels: Record<string, string> = {
      'check': 'Check',
      'wire_transfer': 'Wire Transfer',
      'ach': 'ACH',
      'credit_card': 'Credit Card',
      'cash': 'Cash',
      'other': 'Other'
    };
    return labels[method] || method;
  };

  if (loading) {
    return <LoadingState>Loading payment history...</LoadingState>;
  }

  if (error) {
    return <ErrorState>{error}</ErrorState>;
  }

  if (payments.length === 0) {
    return (
      <EmptyState>
        No payment history yet
      </EmptyState>
    );
  }

  return (
    <Container>
      {payments.map(payment => (
        <PaymentItem key={payment.id}>
          <PaymentHeader>
            <PaymentDate>{formatDateLocal(payment.payment_date)}</PaymentDate>
            <PaymentAmount>{formatCurrency(parseFloat(payment.amount))}</PaymentAmount>
          </PaymentHeader>
          
          <PaymentDetails>
            <DetailItem>
              <DetailLabel>Method:</DetailLabel>
              <DetailValue>{getPaymentMethodLabel(payment.payment_method)}</DetailValue>
            </DetailItem>
            
            {payment.reference_number && (
              <DetailItem>
                <DetailLabel>Ref:</DetailLabel>
                <DetailValue>{payment.reference_number}</DetailValue>
              </DetailItem>
            )}
            
            <DetailItem>
              <DetailLabel>By:</DetailLabel>
              <DetailValue>{payment.created_by_name}</DetailValue>
            </DetailItem>
          </PaymentDetails>
          
          {payment.notes && (
            <DetailItem style={{ fontSize: '12px', marginTop: '4px' }}>
              <DetailLabel>Note:</DetailLabel>
              <DetailValue>{payment.notes}</DetailValue>
            </DetailItem>
          )}
        </PaymentItem>
      ))}
    </Container>
  );
};

export default PaymentHistoryList;
