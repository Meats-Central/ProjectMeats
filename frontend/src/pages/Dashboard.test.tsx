/**
 * Unit tests for Dashboard component
 * Tests real data integration, quick actions, recent activity, and error handling
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

// Mock axios to avoid ESM issues
jest.mock('axios');

// Mock the API service
jest.mock('../services/apiService', () => ({
  apiService: {
    getSuppliers: jest.fn(),
    getCustomers: jest.fn(),
    getPurchaseOrders: jest.fn(),
    getAccountsReceivables: jest.fn(),
  },
}));

// Mock ThemeContext
jest.mock('../contexts/ThemeContext', () => ({
  useTheme: () => ({
    theme: {
      colors: {
        primary: '#1890ff',
        textPrimary: '#000000',
        textSecondary: '#666666',
        textDisabled: '#999999',
        surface: '#ffffff',
        surfaceHover: '#f5f5f5',
        background: '#f0f0f0',
        border: '#d9d9d9',
        borderLight: '#e8e8e8',
        shadow: 'rgba(0, 0, 0, 0.1)',
        shadowMedium: 'rgba(0, 0, 0, 0.2)',
        error: '#ff4d4f',
      },
    },
  }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock visualization components
jest.mock('../components/Visualization/SupplierPerformanceChart', () => {
  return function MockSupplierPerformanceChart() {
    return <div data-testid="supplier-performance-chart">Supplier Performance Chart</div>;
  };
});

jest.mock('../components/Visualization/PurchaseOrderTrends', () => {
  return function MockPurchaseOrderTrends() {
    return <div data-testid="purchase-order-trends">Purchase Order Trends</div>;
  };
});

// Mock data
const mockSuppliers = [
  { id: 1, name: 'Supplier 1', contact_person: 'John Doe', created_at: '2024-11-01T10:00:00Z' },
  { id: 2, name: 'Supplier 2', contact_person: 'Jane Smith', created_at: '2024-11-15T10:00:00Z' },
];

const mockCustomers = [
  { id: 1, name: 'Customer 1', contact_person: 'Bob Johnson', created_at: '2024-11-05T10:00:00Z' },
  { id: 2, name: 'Customer 2', contact_person: 'Alice Brown', created_at: '2024-11-20T10:00:00Z' },
];

const mockPurchaseOrders = [
  {
    id: 1,
    order_number: 'PO-001',
    supplier: 1,
    total_amount: 5000,
    status: 'pending',
    order_date: '2024-11-01',
    created_at: '2024-11-01T10:00:00Z',
  },
  {
    id: 2,
    order_number: 'PO-002',
    supplier: 2,
    total_amount: 7500,
    status: 'approved',
    order_date: '2024-11-15',
    created_at: '2024-11-15T10:00:00Z',
  },
];

const mockAccountsReceivables = [
  { id: 1, amount: 1000, status: 'pending' },
  { id: 2, amount: 2000, status: 'paid' },
];

// Helper function to render Dashboard with providers
const renderDashboard = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        <Dashboard />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();

    // Setup default mock implementations
    (apiService.getSuppliers as jest.Mock).mockResolvedValue(mockSuppliers);
    (apiService.getCustomers as jest.Mock).mockResolvedValue(mockCustomers);
    (apiService.getPurchaseOrders as jest.Mock).mockResolvedValue(mockPurchaseOrders);
    (apiService.getAccountsReceivables as jest.Mock).mockResolvedValue(mockAccountsReceivables);
  });

  describe('Real Data Integration', () => {
    it('should fetch and display real data from all API endpoints', async () => {
      renderDashboard();

      // Wait for API calls to complete
      await waitFor(() => {
        expect(apiService.getSuppliers).toHaveBeenCalled();
        expect(apiService.getCustomers).toHaveBeenCalled();
        expect(apiService.getPurchaseOrders).toHaveBeenCalled();
        expect(apiService.getAccountsReceivables).toHaveBeenCalled();
      });

      // Verify stats are displayed correctly
      await waitFor(() => {
        expect(screen.getByText('2')).toBeInTheDocument(); // Suppliers count
        expect(screen.getByText('Suppliers')).toBeInTheDocument();
        expect(screen.getByText('Customers')).toBeInTheDocument();
        expect(screen.getByText('Purchase Orders')).toBeInTheDocument();
        expect(screen.getByText('Accounts Receivables')).toBeInTheDocument();
      });
    });

    it('should display correct counts for each entity type', async () => {
      renderDashboard();

      await waitFor(() => {
        const stats = screen.getAllByText('2');
        expect(stats.length).toBeGreaterThan(0); // Multiple stats with count 2
      });
    });

    it('should handle empty data gracefully', async () => {
      (apiService.getSuppliers as jest.Mock).mockResolvedValue([]);
      (apiService.getCustomers as jest.Mock).mockResolvedValue([]);
      (apiService.getPurchaseOrders as jest.Mock).mockResolvedValue([]);
      (apiService.getAccountsReceivables as jest.Mock).mockResolvedValue([]);

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('0')).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading state while fetching data', () => {
      // Make API calls take longer to resolve
      (apiService.getSuppliers as jest.Mock).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockSuppliers), 100))
      );

      renderDashboard();

      expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
    });

    it('should hide loading state after data is fetched', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.queryByText('Loading dashboard...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when API calls fail', async () => {
      (apiService.getSuppliers as jest.Mock).mockRejectedValue(new Error('API Error'));

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Error Loading Dashboard')).toBeInTheDocument();
      });
    });

    it('should show retry button on error', async () => {
      (apiService.getSuppliers as jest.Mock).mockRejectedValue(new Error('API Error'));

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
    });

    it('should retry fetching data when retry button is clicked', async () => {
      // First call fails, second succeeds
      (apiService.getSuppliers as jest.Mock)
        .mockRejectedValueOnce(new Error('API Error'))
        .mockResolvedValueOnce(mockSuppliers);

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Retry'));

      await waitFor(() => {
        expect(apiService.getSuppliers).toHaveBeenCalledTimes(2);
        expect(screen.queryByText('Error Loading Dashboard')).not.toBeInTheDocument();
      });
    });

    it('should handle partial API failures gracefully', async () => {
      // Some APIs succeed, some fail
      (apiService.getSuppliers as jest.Mock).mockResolvedValue(mockSuppliers);
      (apiService.getCustomers as jest.Mock).mockRejectedValue(new Error('Customers API Error'));
      (apiService.getPurchaseOrders as jest.Mock).mockResolvedValue(mockPurchaseOrders);
      (apiService.getAccountsReceivables as jest.Mock).mockResolvedValue(
        mockAccountsReceivables
      );

      renderDashboard();

      // Should still render with partial data
      await waitFor(() => {
        expect(screen.queryByText('Loading dashboard...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Quick Actions', () => {
    beforeEach(async () => {
      renderDashboard();
      await waitFor(() => {
        expect(screen.queryByText('Loading dashboard...')).not.toBeInTheDocument();
      });
    });

    it('should render all quick action buttons', () => {
      expect(screen.getByText('+ Add Supplier')).toBeInTheDocument();
      expect(screen.getByText('+ Add Customer')).toBeInTheDocument();
      expect(screen.getByText('+ Create Purchase Order')).toBeInTheDocument();
      expect(screen.getByText('💬 Ask AI Assistant')).toBeInTheDocument();
    });

    it('should navigate to suppliers page when Add Supplier is clicked', () => {
      fireEvent.click(screen.getByText('+ Add Supplier'));
      expect(mockNavigate).toHaveBeenCalledWith('/suppliers');
    });

    it('should navigate to customers page when Add Customer is clicked', () => {
      fireEvent.click(screen.getByText('+ Add Customer'));
      expect(mockNavigate).toHaveBeenCalledWith('/customers');
    });

    it('should navigate to purchase orders page when Create Purchase Order is clicked', () => {
      fireEvent.click(screen.getByText('+ Create Purchase Order'));
      expect(mockNavigate).toHaveBeenCalledWith('/purchase-orders');
    });

    it('should navigate to AI assistant page when Ask AI Assistant is clicked', () => {
      fireEvent.click(screen.getByText('💬 Ask AI Assistant'));
      expect(mockNavigate).toHaveBeenCalledWith('/ai-assistant');
    });
  });

  describe('Recent Activity', () => {
    it('should display recent activity section', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Recent Activity')).toBeInTheDocument();
      });
    });

    it('should display recent suppliers in activity feed', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText(/New Supplier: Supplier 1/)).toBeInTheDocument();
        expect(screen.getByText(/New Supplier: Supplier 2/)).toBeInTheDocument();
      });
    });

    it('should display recent customers in activity feed', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText(/New Customer: Customer 1/)).toBeInTheDocument();
        expect(screen.getByText(/New Customer: Customer 2/)).toBeInTheDocument();
      });
    });

    it('should display recent purchase orders in activity feed', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText(/Purchase Order: PO-001/)).toBeInTheDocument();
        expect(screen.getByText(/Purchase Order: PO-002/)).toBeInTheDocument();
      });
    });

    it('should show "No recent activity" when there is no data', async () => {
      (apiService.getSuppliers as jest.Mock).mockResolvedValue([]);
      (apiService.getCustomers as jest.Mock).mockResolvedValue([]);
      (apiService.getPurchaseOrders as jest.Mock).mockResolvedValue([]);
      (apiService.getAccountsReceivables as jest.Mock).mockResolvedValue([]);

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('No recent activity to display')).toBeInTheDocument();
      });
    });
  });

  describe('Visualization Components', () => {
    it('should render supplier performance chart', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByTestId('supplier-performance-chart')).toBeInTheDocument();
      });
    });

    it('should render purchase order trends chart', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByTestId('purchase-order-trends')).toBeInTheDocument();
      });
    });
  });

  describe('Refresh Functionality', () => {
    it('should render refresh button', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('🔄 Refresh Data')).toBeInTheDocument();
      });
    });

    it('should refetch data when refresh button is clicked', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('🔄 Refresh Data')).toBeInTheDocument();
      });

      // Clear previous calls
      jest.clearAllMocks();

      // Click refresh
      fireEvent.click(screen.getByText('🔄 Refresh Data'));

      await waitFor(() => {
        expect(apiService.getSuppliers).toHaveBeenCalled();
        expect(apiService.getCustomers).toHaveBeenCalled();
        expect(apiService.getPurchaseOrders).toHaveBeenCalled();
        expect(apiService.getAccountsReceivables).toHaveBeenCalled();
      });
    });
  });

  describe('Quick Stats', () => {
    it('should display quick stats section', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Quick Stats')).toBeInTheDocument();
      });
    });

    it('should calculate and display total entities correctly', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Total Entities')).toBeInTheDocument();
        // Total: 2 suppliers + 2 customers + 2 purchase orders + 2 accounts receivables = 8
        const totalEntities = screen.getByText('Total Entities')
          .closest('div')
          ?.querySelector('[class*="OverviewNumber"]');
        expect(totalEntities).toHaveTextContent('8');
      });
    });

    it('should display active purchase orders count', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Active POs')).toBeInTheDocument();
      });
    });

    it('should display outstanding accounts receivables count', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Outstanding AR')).toBeInTheDocument();
      });
    });

    it('should display business partners count', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Business Partners')).toBeInTheDocument();
        // Business partners = suppliers + customers = 2 + 2 = 4
        const businessPartners = screen.getByText('Business Partners')
          .closest('div')
          ?.querySelector('[class*="OverviewNumber"]');
        expect(businessPartners).toHaveTextContent('4');
      });
    });
  });

  describe('Dashboard Header', () => {
    it('should display dashboard title', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
      });
    });

    it('should display welcome message', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(
          screen.getByText('Welcome to ProjectMeats Business Management System')
        ).toBeInTheDocument();
      });
    });
  });
});
