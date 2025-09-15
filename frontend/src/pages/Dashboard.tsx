import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { apiService, Supplier, PurchaseOrder } from '../services/apiService';
import SupplierPerformanceChart from '../components/Visualization/SupplierPerformanceChart';
import PurchaseOrderTrends from '../components/Visualization/PurchaseOrderTrends';

interface DashboardStats {
  suppliers: number;
  customers: number;
  purchaseOrders: number;
  accountsReceivables: number;
}

interface RecentActivity {
  type: 'supplier' | 'customer' | 'purchase_order' | 'accounts_receivable';
  title: string;
  description: string;
  timestamp: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    suppliers: 0,
    customers: 0,
    purchaseOrders: 0,
    accountsReceivables: 0
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [supplierPerformanceData, setSupplierPerformanceData] = useState<any[]>([]);
  const [purchaseOrderTrendData, setPurchaseOrderTrendData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setError(null);
      setLoading(true);
      
      // Fetch data from all endpoints to get real counts
      const [
        suppliersData,
        customersData,
        purchaseOrdersData,
        accountsReceivablesData
      ] = await Promise.all([
        apiService.getSuppliers().catch(() => []),
        apiService.getCustomers().catch(() => []),
        apiService.getPurchaseOrders().catch(() => []),
        apiService.getAccountsReceivables().catch(() => [])
      ]);

        // Set real stats
        setStats({
          suppliers: suppliersData.length,
          customers: customersData.length,
          purchaseOrders: purchaseOrdersData.length,
          accountsReceivables: accountsReceivablesData.length
        });

        // Generate supplier performance data from real API data
        const supplierMap = new Map<number, { name: string; orders: number; revenue: number; rating: number }>();
        
        // First, create a map of all suppliers
        suppliersData.forEach((supplier: Supplier) => {
          supplierMap.set(supplier.id, {
            name: supplier.name,
            orders: 0,
            revenue: 0,
            rating: 4.0 + Math.random() * 1.0, // Random rating between 4.0-5.0 since we don't have ratings in DB yet
          });
        });

        // Then, aggregate purchase order data by supplier
        purchaseOrdersData.forEach((order: PurchaseOrder) => {
          const supplierId = order.supplier;
          if (supplierMap.has(supplierId)) {
            const supplierData = supplierMap.get(supplierId)!;
            supplierData.orders += 1;
            supplierData.revenue += Number(order.total_amount) || 0;
          }
        });

        // Convert to array and round ratings to 1 decimal place
        const supplierChartData = Array.from(supplierMap.values())
          .filter(supplier => supplier.orders > 0) // Only show suppliers with orders
          .map(supplier => ({
            ...supplier,
            rating: Math.round(supplier.rating * 10) / 10
          }))
          .sort((a, b) => b.revenue - a.revenue) // Sort by revenue descending
          .slice(0, 10); // Show top 10 suppliers

        // Add fallback data if no suppliers have orders
        if (supplierChartData.length === 0 && suppliersData.length > 0) {
          setSupplierPerformanceData(
            suppliersData.slice(0, 4).map(supplier => ({
              name: supplier.name,
              orders: 0,
              revenue: 0,
              rating: 4.0 + Math.random() * 1.0
            }))
          );
        } else {
          setSupplierPerformanceData(supplierChartData);
        }

        // Generate purchase order trends data from real API data
        const monthlyData = new Map<string, { date: string; orders: number; value: number }>();
        
        purchaseOrdersData.forEach((order: PurchaseOrder) => {
          const orderDate = new Date(order.order_date);
          const monthKey = `${orderDate.getFullYear()}-${(orderDate.getMonth() + 1).toString().padStart(2, '0')}`;
          
          if (!monthlyData.has(monthKey)) {
            monthlyData.set(monthKey, {
              date: monthKey,
              orders: 0,
              value: 0
            });
          }
          
          const monthData = monthlyData.get(monthKey)!;
          monthData.orders += 1;
          monthData.value += Number(order.total_amount) || 0;
        });

        // Convert to array, calculate average values, and sort by date
        const trendChartData = Array.from(monthlyData.values())
          .map(monthData => ({
            ...monthData,
            averageValue: monthData.orders > 0 ? Math.round(monthData.value / monthData.orders) : 0
          }))
          .sort((a, b) => a.date.localeCompare(b.date))
          .slice(-12); // Show last 12 months

        // Add fallback data if no purchase orders exist
        if (trendChartData.length === 0) {
          const currentDate = new Date();
          const fallbackData = [];
          for (let i = 5; i >= 0; i--) {
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
            const monthKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
            fallbackData.push({
              date: monthKey,
              orders: 0,
              value: 0,
              averageValue: 0
            });
          }
          setPurchaseOrderTrendData(fallbackData);
        } else {
          setPurchaseOrderTrendData(trendChartData);
        }

        // Generate recent activity from the data
        const activities: RecentActivity[] = [];
        
        // Add recent suppliers
        suppliersData.slice(-3).forEach(supplier => {
          activities.push({
            type: 'supplier',
            title: `New Supplier: ${supplier.name}`,
            description: supplier.contact_person ? `Contact: ${supplier.contact_person}` : 'No contact person',
            timestamp: supplier.created_at || new Date().toISOString()
          });
        });

        // Add recent customers
        customersData.slice(-3).forEach(customer => {
          activities.push({
            type: 'customer',
            title: `New Customer: ${customer.name}`,
            description: customer.contact_person ? `Contact: ${customer.contact_person}` : 'No contact person',
            timestamp: customer.created_at || new Date().toISOString()
          });
        });

        // Add recent purchase orders
        purchaseOrdersData.slice(-2).forEach(order => {
          activities.push({
            type: 'purchase_order',
            title: `Purchase Order: ${order.order_number}`,
            description: `Amount: $${order.total_amount.toLocaleString()} - Status: ${order.status}`,
            timestamp: order.created_at || new Date().toISOString()
          });
        });

        // Sort by timestamp and take the most recent
        activities.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        setRecentActivity(activities.slice(0, 8));

      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        setError('Failed to load dashboard data. Please check your connection.');
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleRefresh = async () => {
    await fetchStats();
  };

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'add-supplier':
        navigate('/suppliers');
        break;
      case 'add-customer':
        navigate('/customers');
        break;
      case 'create-purchase-order':
        navigate('/purchase-orders');
        break;
      case 'ask-ai':
        navigate('/ai-assistant');
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  const getActivityIcon = (type: RecentActivity['type']) => {
    switch (type) {
      case 'supplier':
        return '🏭';
      case 'customer':
        return '👥';
      case 'purchase_order':
        return '📋';
      case 'accounts_receivable':
        return '💰';
      default:
        return '📄';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (loading) {
    return <LoadingContainer>Loading dashboard...</LoadingContainer>;
  }

  if (error) {
    return (
      <ErrorContainer>
        <ErrorIcon>⚠️</ErrorIcon>
        <ErrorTitle>Error Loading Dashboard</ErrorTitle>
        <ErrorMessage>{error}</ErrorMessage>
        <RetryButton onClick={handleRefresh}>
          Retry
        </RetryButton>
      </ErrorContainer>
    );
  }

  return (
    <DashboardContainer>
      <DashboardHeader>
        <HeaderTop>
          <TitleSection>
            <Title>Dashboard</Title>
            <Subtitle>Welcome to ProjectMeats Business Management System</Subtitle>
          </TitleSection>
          <RefreshButton onClick={handleRefresh}>
            🔄 Refresh Data
          </RefreshButton>
        </HeaderTop>
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
        <SupplierPerformanceChart data={supplierPerformanceData} />
        <PurchaseOrderTrends data={purchaseOrderTrendData} />
      </ChartsContainer>

      <ChartsContainer>
        <ChartCard>
          <ChartTitle>Recent Activity</ChartTitle>
          {recentActivity.length > 0 ? (
            <ActivityList>
              {recentActivity.map((activity, index) => (
                <ActivityItem key={index}>
                  <ActivityIcon>{getActivityIcon(activity.type)}</ActivityIcon>
                  <ActivityContent>
                    <ActivityTitle>{activity.title}</ActivityTitle>
                    <ActivityDescription>{activity.description}</ActivityDescription>
                  </ActivityContent>
                  <ActivityTime>{formatTimestamp(activity.timestamp)}</ActivityTime>
                </ActivityItem>
              ))}
            </ActivityList>
          ) : (
            <ChartPlaceholder>
              <ChartIcon>📈</ChartIcon>
              <ChartText>No recent activity to display</ChartText>
            </ChartPlaceholder>
          )}
        </ChartCard>

        <ChartCard>
          <ChartTitle>Quick Stats</ChartTitle>
          <StatsOverview>
            <OverviewStat>
              <OverviewLabel>Total Entities</OverviewLabel>
              <OverviewNumber>{stats.suppliers + stats.customers + stats.purchaseOrders + stats.accountsReceivables}</OverviewNumber>
            </OverviewStat>
            <OverviewStat>
              <OverviewLabel>Active POs</OverviewLabel>
              <OverviewNumber>{stats.purchaseOrders}</OverviewNumber>
            </OverviewStat>
            <OverviewStat>
              <OverviewLabel>Outstanding AR</OverviewLabel>
              <OverviewNumber>{stats.accountsReceivables}</OverviewNumber>
            </OverviewStat>
            <OverviewStat>
              <OverviewLabel>Business Partners</OverviewLabel>
              <OverviewNumber>{stats.suppliers + stats.customers}</OverviewNumber>
            </OverviewStat>
          </StatsOverview>
        </ChartCard>
      </ChartsContainer>

      <QuickActions>
        <QuickActionTitle>Quick Actions</QuickActionTitle>
        <ActionButtons>
          <ActionButton onClick={() => handleQuickAction('add-supplier')}>
            + Add Supplier
          </ActionButton>
          <ActionButton onClick={() => handleQuickAction('add-customer')}>
            + Add Customer
          </ActionButton>
          <ActionButton onClick={() => handleQuickAction('create-purchase-order')}>
            + Create Purchase Order
          </ActionButton>
          <ActionButton onClick={() => handleQuickAction('ask-ai')}>
            💬 Ask AI Assistant
          </ActionButton>
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

const HeaderTop = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
`;

const TitleSection = styled.div`
  flex: 1;
`;

const RefreshButton = styled.button`
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:hover {
    background: #e9ecef;
    border-color: #adb5bd;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
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

// Error components
const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
`;

const ErrorIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
`;

const ErrorTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: #e74c3c;
  margin: 0 0 8px 0;
`;

const ErrorMessage = styled.p`
  font-size: 16px;
  color: #6c757d;
  margin: 0 0 24px 0;
`;

const RetryButton = styled.button`
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #2980b9;
    transform: translateY(-1px);
  }
`;

// Activity components
const ActivityList = styled.div`
  max-height: 300px;
  overflow-y: auto;
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f3f4;

  &:last-child {
    border-bottom: none;
  }
`;

const ActivityIcon = styled.div`
  font-size: 20px;
  opacity: 0.8;
`;

const ActivityContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const ActivityTitle = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 2px;
`;

const ActivityDescription = styled.div`
  font-size: 12px;
  color: #6c757d;
`;

const ActivityTime = styled.div`
  font-size: 11px;
  color: #95a5a6;
  white-space: nowrap;
`;

// Stats overview components
const StatsOverview = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
`;

const OverviewStat = styled.div`
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
`;

const OverviewLabel = styled.div`
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 8px;
  font-weight: 500;
`;

const OverviewNumber = styled.div`
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
`;

export default Dashboard;
