import React, { useEffect, useState } from 'react';
import styled from 'styled-components';

interface DashboardStats {
  suppliers: number;
  customers: number;
  purchaseOrders: number;
  accountsReceivables: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    suppliers: 0,
    customers: 0,
    purchaseOrders: 0,
    accountsReceivables: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // In a real app, you'd have a dedicated stats endpoint
        // For now, we'll simulate this
        setStats({
          suppliers: 45,
          customers: 128,
          purchaseOrders: 73,
          accountsReceivables: 32
        });
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <LoadingContainer>Loading dashboard...</LoadingContainer>;
  }

  return (
    <DashboardContainer>
      <DashboardHeader>
        <Title>Dashboard</Title>
        <Subtitle>Welcome to ProjectMeats Business Management System</Subtitle>
      </DashboardHeader>

      <StatsGrid>
        <StatCard>
          <StatIcon>🏭</StatIcon>
          <StatContent>
            <StatNumber>{stats.suppliers}</StatNumber>
            <StatLabel>Suppliers</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon>👥</StatIcon>
          <StatContent>
            <StatNumber>{stats.customers}</StatNumber>
            <StatLabel>Customers</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon>📋</StatIcon>
          <StatContent>
            <StatNumber>{stats.purchaseOrders}</StatNumber>
            <StatLabel>Purchase Orders</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon>💰</StatIcon>
          <StatContent>
            <StatNumber>{stats.accountsReceivables}</StatNumber>
            <StatLabel>Accounts Receivables</StatLabel>
          </StatContent>
        </StatCard>
      </StatsGrid>

      <ChartsContainer>
        <ChartCard>
          <ChartTitle>Recent Activity</ChartTitle>
          <ChartPlaceholder>
            <ChartIcon>📈</ChartIcon>
            <ChartText>Sales trends and analytics coming soon</ChartText>
          </ChartPlaceholder>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Top Suppliers</ChartTitle>
          <ChartPlaceholder>
            <ChartIcon>🏭</ChartIcon>
            <ChartText>Supplier performance metrics coming soon</ChartText>
          </ChartPlaceholder>
        </ChartCard>
      </ChartsContainer>

      <QuickActions>
        <QuickActionTitle>Quick Actions</QuickActionTitle>
        <ActionButtons>
          <ActionButton>+ Add Supplier</ActionButton>
          <ActionButton>+ Add Customer</ActionButton>
          <ActionButton>+ Create Purchase Order</ActionButton>
          <ActionButton>💬 Ask AI Assistant</ActionButton>
        </ActionButtons>
      </QuickActions>
    </DashboardContainer>
  );
};

const DashboardContainer = styled.div`
  max-width: 1200px;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 18px;
  color: #6c757d;
`;

const DashboardHeader = styled.div`
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: #6c757d;
  margin: 0;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
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

const StatNumber = styled.div`
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
`;

const ChartsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
`;

const ChartTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
`;

const ChartPlaceholder = styled.div`
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
`;

const ChartIcon = styled.div`
  font-size: 48px;
  margin-bottom: 10px;
  opacity: 0.5;
`;

const ChartText = styled.div`
  color: #6c757d;
  font-style: italic;
`;

const QuickActions = styled.div`
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
`;

const QuickActionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
`;

const ActionButtons = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
`;

const ActionButton = styled.button`
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 15px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
  }
`;

export default Dashboard;
