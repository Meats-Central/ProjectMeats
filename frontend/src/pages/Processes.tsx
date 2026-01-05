import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useTheme } from '../contexts/ThemeContext';
import { Theme } from '../config/theme';
import { apiService, PurchaseOrder } from '../services/apiService';

const Processes: React.FC = () => {
  const { theme } = useTheme();
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProcesses();
  }, []);

  const fetchProcesses = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPurchaseOrders();
      setPurchaseOrders(data);
    } catch (err) {
      console.error('Error fetching processes:', err);
      setError('Failed to load process data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      pending: '#ffc107',
      approved: '#28a745',
      delivered: '#17a2b8',
      cancelled: '#dc3545',
    };
    return statusColors[status] || '#6c757d';
  };

  if (loading) {
    return (
      <Container>
        <LoadingMessage $theme={theme}>Loading processes...</LoadingMessage>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorMessage $theme={theme}>⚠️ {error}</ErrorMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title $theme={theme}>⚙️ Processes - Workflow Management</Title>
        <Subtitle $theme={theme}>
          Track and manage all business processes
        </Subtitle>
      </Header>

      <TableContainer $theme={theme}>
        <Table>
          <thead>
            <TableRow $theme={theme}>
              <TableHeader $theme={theme}>Order #</TableHeader>
              <TableHeader $theme={theme}>Supplier</TableHeader>
              <TableHeader $theme={theme}>Order Date</TableHeader>
              <TableHeader $theme={theme}>Status</TableHeader>
              <TableHeader $theme={theme}>Weight (lbs)</TableHeader>
              <TableHeader $theme={theme}>Amount</TableHeader>
            </TableRow>
          </thead>
          <tbody>
            {purchaseOrders.length === 0 ? (
              <TableRow $theme={theme}>
                <TableCell $theme={theme} colSpan={6}>
                  <EmptyState>
                    <EmptyIcon>📋</EmptyIcon>
                    <EmptyText $theme={theme}>
                      No processes to display
                    </EmptyText>
                  </EmptyState>
                </TableCell>
              </TableRow>
            ) : (
              purchaseOrders.map((order) => (
                <TableRow key={order.id} $theme={theme}>
                  <TableCell $theme={theme}>{order.order_number}</TableCell>
                  <TableCell $theme={theme}>
                    Supplier #{order.supplier}
                  </TableCell>
                  <TableCell $theme={theme}>
                    {new Date(order.order_date).toLocaleDateString()}
                  </TableCell>
                  <TableCell $theme={theme}>
                    <StatusBadge color={getStatusBadge(order.status)}>
                      {order.status}
                    </StatusBadge>
                  </TableCell>
                  <TableCell $theme={theme}>
                    {order.total_weight?.toLocaleString() || 'N/A'}
                  </TableCell>
                  <TableCell $theme={theme}>
                    ${order.total_amount.toLocaleString()}
                  </TableCell>
                </TableRow>
              ))
            )}
          </tbody>
        </Table>
      </TableContainer>
    </Container>
  );
};

const Container = styled.div`
  max-width: 1200px;
  padding: 20px;
`;

const Header = styled.div`
  margin-bottom: 30px;
`;

const Title = styled.h1<{ $theme: Theme }>`
  font-size: 32px;
  font-weight: 700;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p<{ $theme: Theme }>`
  font-size: 16px;
  color: ${(props) => props.$theme.colors.textSecondary};
  margin: 0;
`;

const LoadingMessage = styled.div<{ $theme: Theme }>`
  text-align: center;
  padding: 60px;
  font-size: 18px;
  color: ${(props) => props.$theme.colors.textSecondary};
`;

const ErrorMessage = styled.div<{ $theme: Theme }>`
  text-align: center;
  padding: 60px;
  font-size: 18px;
  color: ${(props) => props.$theme.colors.error};
`;

const TableContainer = styled.div<{ $theme: Theme }>`
  background: ${(props) => props.$theme.colors.surface};
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px ${(props) => props.$theme.colors.shadow};
  overflow-x: auto;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableRow = styled.tr<{ $theme: Theme }>`
  border-bottom: 1px solid ${(props) => props.$theme.colors.border};

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: ${(props) => props.$theme.colors.surfaceHover};
  }
`;

const TableHeader = styled.th<{ $theme: Theme }>`
  text-align: left;
  padding: 12px;
  font-weight: 600;
  color: ${(props) => props.$theme.colors.textPrimary};
  background: ${(props) => props.$theme.colors.background};
`;

const TableCell = styled.td<{ $theme: Theme }>`
  padding: 12px;
  color: ${(props) => props.$theme.colors.textPrimary};
`;

const StatusBadge = styled.span<{ color: string }>`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  background: ${(props) => props.color};
  color: white;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
`;

const EmptyIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
`;

const EmptyText = styled.p<{ $theme: Theme }>`
  font-size: 16px;
  color: ${(props) => props.$theme.colors.textSecondary};
  margin: 0;
`;

export default Processes;
