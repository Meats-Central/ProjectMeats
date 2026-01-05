import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useTheme } from '../contexts/ThemeContext';
import { Theme } from '../config/theme';
import { apiService } from '../services/apiService';

interface SummaryStats {
  totalPurchaseOrders: number;
  totalWeight: number;
  activeDeliveries: number;
  pendingOrders: number;
  totalSuppliers: number;
  totalCustomers: number;
}

const Cockpit: React.FC = () => {
  const { theme } = useTheme();
  const [stats, setStats] = useState<SummaryStats>({
    totalPurchaseOrders: 0,
    totalWeight: 0,
    activeDeliveries: 0,
    pendingOrders: 0,
    totalSuppliers: 0,
    totalCustomers: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSummaryStats();
  }, []);

  const fetchSummaryStats = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch data from all endpoints
      const [purchaseOrders, suppliers, customers] = await Promise.all([
        apiService.getPurchaseOrders().catch(() => []),
        apiService.getSuppliers().catch(() => []),
        apiService.getCustomers().catch(() => []),
      ]);

      // Calculate summary statistics
      const totalWeight = purchaseOrders.reduce(
        (sum, po) => sum + (Number(po.total_weight) || 0),
        0
      );
      const pendingOrders = purchaseOrders.filter(
        (po) => po.status === 'pending'
      ).length;
      const activeDeliveries = purchaseOrders.filter(
        (po) => po.status === 'approved' || po.status === 'delivered'
      ).length;

      setStats({
        totalPurchaseOrders: purchaseOrders.length,
        totalWeight: Math.round(totalWeight),
        activeDeliveries,
        pendingOrders,
        totalSuppliers: suppliers.length,
        totalCustomers: customers.length,
      });
    } catch (err) {
      console.error('Error fetching cockpit stats:', err);
      setError('Failed to load cockpit data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <LoadingMessage $theme={theme}>Loading cockpit data...</LoadingMessage>
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
        <Title $theme={theme}>📊 Cockpit - Command Center</Title>
        <Subtitle $theme={theme}>
          Real-time business operations dashboard
        </Subtitle>
      </Header>

      <StatsGrid>
        <StatCard $theme={theme}>
          <StatIcon>📋</StatIcon>
          <StatContent>
            <StatValue $theme={theme}>{stats.totalPurchaseOrders}</StatValue>
            <StatLabel $theme={theme}>Total P.O.s</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard $theme={theme}>
          <StatIcon>⚖️</StatIcon>
          <StatContent>
            <StatValue $theme={theme}>
              {stats.totalWeight.toLocaleString()} lbs
            </StatValue>
            <StatLabel $theme={theme}>Total Weight</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard $theme={theme}>
          <StatIcon>🚚</StatIcon>
          <StatContent>
            <StatValue $theme={theme}>{stats.activeDeliveries}</StatValue>
            <StatLabel $theme={theme}>Active Deliveries</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard $theme={theme}>
          <StatIcon>⏳</StatIcon>
          <StatContent>
            <StatValue $theme={theme}>{stats.pendingOrders}</StatValue>
            <StatLabel $theme={theme}>Pending Orders</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard $theme={theme}>
          <StatIcon>🏭</StatIcon>
          <StatContent>
            <StatValue $theme={theme}>{stats.totalSuppliers}</StatValue>
            <StatLabel $theme={theme}>Suppliers</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard $theme={theme}>
          <StatIcon>👥</StatIcon>
          <StatContent>
            <StatValue $theme={theme}>{stats.totalCustomers}</StatValue>
            <StatLabel $theme={theme}>Customers</StatLabel>
          </StatContent>
        </StatCard>
      </StatsGrid>

      <Section $theme={theme}>
        <SectionTitle $theme={theme}>Quick Insights</SectionTitle>
        <InsightsList>
          <InsightItem $theme={theme}>
            <InsightIcon>✅</InsightIcon>
            <InsightText $theme={theme}>
              All systems operational - {stats.totalPurchaseOrders} orders tracked
            </InsightText>
          </InsightItem>
          <InsightItem $theme={theme}>
            <InsightIcon>📈</InsightIcon>
            <InsightText $theme={theme}>
              {stats.activeDeliveries} deliveries in progress
            </InsightText>
          </InsightItem>
          <InsightItem $theme={theme}>
            <InsightIcon>⚠️</InsightIcon>
            <InsightText $theme={theme}>
              {stats.pendingOrders} orders awaiting approval
            </InsightText>
          </InsightItem>
        </InsightsList>
      </Section>
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

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div<{ $theme: Theme }>`
  background: ${(props) => props.$theme.colors.surface};
  border-radius: 12px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 10px ${(props) => props.$theme.colors.shadow};
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px ${(props) => props.$theme.colors.shadowMedium};
  }
`;

const StatIcon = styled.div`
  font-size: 40px;
  opacity: 0.8;
`;

const StatContent = styled.div`
  display: flex;
  flex-direction: column;
`;

const StatValue = styled.div<{ $theme: Theme }>`
  font-size: 28px;
  font-weight: 700;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin-bottom: 4px;
`;

const StatLabel = styled.div<{ $theme: Theme }>`
  font-size: 14px;
  color: ${(props) => props.$theme.colors.textSecondary};
  font-weight: 500;
`;

const Section = styled.div<{ $theme: Theme }>`
  background: ${(props) => props.$theme.colors.surface};
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 10px ${(props) => props.$theme.colors.shadow};
`;

const SectionTitle = styled.h2<{ $theme: Theme }>`
  font-size: 20px;
  font-weight: 600;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin: 0 0 20px 0;
`;

const InsightsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const InsightItem = styled.div<{ $theme: Theme }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: ${(props) => props.$theme.colors.background};
  border-radius: 8px;
`;

const InsightIcon = styled.div`
  font-size: 24px;
`;

const InsightText = styled.div<{ $theme: Theme }>`
  font-size: 14px;
  color: ${(props) => props.$theme.colors.textPrimary};
`;

export default Cockpit;
