import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useTheme } from '../contexts/ThemeContext';
import { Theme } from '../config/theme';
import { apiService } from '../services/apiService';

interface ReportSummary {
  totalOrders: number;
  totalRevenue: number;
  totalWeight: number;
  averageOrderValue: number;
  supplierCount: number;
  customerCount: number;
}

const Reports: React.FC = () => {
  const { theme } = useTheme();
  const [summary, setSummary] = useState<ReportSummary>({
    totalOrders: 0,
    totalRevenue: 0,
    totalWeight: 0,
    averageOrderValue: 0,
    supplierCount: 0,
    customerCount: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [purchaseOrders, suppliers, customers] = await Promise.all([
        apiService.getPurchaseOrders().catch(() => []),
        apiService.getSuppliers().catch(() => []),
        apiService.getCustomers().catch(() => []),
      ]);

      const totalRevenue = purchaseOrders.reduce(
        (sum, po) => sum + Number(po.total_amount),
        0
      );
      const totalWeight = purchaseOrders.reduce(
        (sum, po) => sum + (Number(po.total_weight) || 0),
        0
      );
      const averageOrderValue =
        purchaseOrders.length > 0 ? totalRevenue / purchaseOrders.length : 0;

      setSummary({
        totalOrders: purchaseOrders.length,
        totalRevenue: Math.round(totalRevenue),
        totalWeight: Math.round(totalWeight),
        averageOrderValue: Math.round(averageOrderValue),
        supplierCount: suppliers.length,
        customerCount: customers.length,
      });
    } catch (err) {
      console.error('Error fetching report data:', err);
      setError('Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <LoadingMessage $theme={theme}>Loading reports...</LoadingMessage>
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
        <Title $theme={theme}>📊 Reports - Business Analytics</Title>
        <Subtitle $theme={theme}>
          Comprehensive business intelligence and reporting
        </Subtitle>
      </Header>

      <ReportGrid>
        <ReportCard $theme={theme}>
          <CardHeader $theme={theme}>
            <CardIcon>📋</CardIcon>
            <CardTitle $theme={theme}>Total Orders</CardTitle>
          </CardHeader>
          <CardValue $theme={theme}>{summary.totalOrders}</CardValue>
          <CardFooter $theme={theme}>All-time purchase orders</CardFooter>
        </ReportCard>

        <ReportCard $theme={theme}>
          <CardHeader $theme={theme}>
            <CardIcon>💰</CardIcon>
            <CardTitle $theme={theme}>Total Revenue</CardTitle>
          </CardHeader>
          <CardValue $theme={theme}>
            ${summary.totalRevenue.toLocaleString()}
          </CardValue>
          <CardFooter $theme={theme}>Cumulative order value</CardFooter>
        </ReportCard>

        <ReportCard $theme={theme}>
          <CardHeader $theme={theme}>
            <CardIcon>⚖️</CardIcon>
            <CardTitle $theme={theme}>Total Weight</CardTitle>
          </CardHeader>
          <CardValue $theme={theme}>
            {summary.totalWeight.toLocaleString()} lbs
          </CardValue>
          <CardFooter $theme={theme}>Total product weight</CardFooter>
        </ReportCard>

        <ReportCard $theme={theme}>
          <CardHeader $theme={theme}>
            <CardIcon>📈</CardIcon>
            <CardTitle $theme={theme}>Avg Order Value</CardTitle>
          </CardHeader>
          <CardValue $theme={theme}>
            ${summary.averageOrderValue.toLocaleString()}
          </CardValue>
          <CardFooter $theme={theme}>Per purchase order</CardFooter>
        </ReportCard>

        <ReportCard $theme={theme}>
          <CardHeader $theme={theme}>
            <CardIcon>🏭</CardIcon>
            <CardTitle $theme={theme}>Suppliers</CardTitle>
          </CardHeader>
          <CardValue $theme={theme}>{summary.supplierCount}</CardValue>
          <CardFooter $theme={theme}>Active supplier network</CardFooter>
        </ReportCard>

        <ReportCard $theme={theme}>
          <CardHeader $theme={theme}>
            <CardIcon>👥</CardIcon>
            <CardTitle $theme={theme}>Customers</CardTitle>
          </CardHeader>
          <CardValue $theme={theme}>{summary.customerCount}</CardValue>
          <CardFooter $theme={theme}>Customer base</CardFooter>
        </ReportCard>
      </ReportGrid>

      <Section $theme={theme}>
        <SectionTitle $theme={theme}>Report Insights</SectionTitle>
        <InsightsList>
          <InsightItem $theme={theme}>
            <InsightBullet>•</InsightBullet>
            <InsightText $theme={theme}>
              Average order value: ${summary.averageOrderValue.toLocaleString()}
            </InsightText>
          </InsightItem>
          <InsightItem $theme={theme}>
            <InsightBullet>•</InsightBullet>
            <InsightText $theme={theme}>
              Total business volume: {summary.totalWeight.toLocaleString()} lbs
              processed
            </InsightText>
          </InsightItem>
          <InsightItem $theme={theme}>
            <InsightBullet>•</InsightBullet>
            <InsightText $theme={theme}>
              Business network: {summary.supplierCount} suppliers serving{' '}
              {summary.customerCount} customers
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

const ReportGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const ReportCard = styled.div<{ $theme: Theme }>`
  background: ${(props) => props.$theme.colors.surface};
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 10px ${(props) => props.$theme.colors.shadow};
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px ${(props) => props.$theme.colors.shadowMedium};
  }
`;

const CardHeader = styled.div<{ $theme: Theme }>`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`;

const CardIcon = styled.div`
  font-size: 32px;
`;

const CardTitle = styled.h3<{ $theme: Theme }>`
  font-size: 16px;
  font-weight: 600;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin: 0;
`;

const CardValue = styled.div<{ $theme: Theme }>`
  font-size: 32px;
  font-weight: 700;
  color: ${(props) => props.$theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const CardFooter = styled.div<{ $theme: Theme }>`
  font-size: 14px;
  color: ${(props) => props.$theme.colors.textSecondary};
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
  gap: 12px;
`;

const InsightItem = styled.div<{ $theme: Theme }>`
  display: flex;
  align-items: flex-start;
  gap: 12px;
`;

const InsightBullet = styled.div`
  font-size: 20px;
  font-weight: bold;
  line-height: 1;
`;

const InsightText = styled.div<{ $theme: Theme }>`
  font-size: 14px;
  color: ${(props) => props.$theme.colors.textPrimary};
  line-height: 1.5;
`;

export default Reports;
