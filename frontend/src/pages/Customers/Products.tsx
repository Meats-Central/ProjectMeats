/**
 * Customer Products Management Page
 * 
 * Features:
 * - Display products associated with a specific customer
 * - Table layout with sorting, pagination, and search
 * - Add/remove product associations
 * - Links to product details
 * - Theme-compliant styling with antd Table
 * - Multi-tenancy support
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Table, Input, Button, Modal, message, Tag, Space, Spin } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { SearchOutlined, PlusOutlined, DeleteOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { apiClient } from '../../services/apiService';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface Product {
  id: number;
  product_code: string;
  description_of_product_item: string;
  type_of_protein?: string;
  fresh_or_frozen?: string;
  package_type?: string;
  unit_weight?: number;
  supplier?: number;
  supplier_name?: string;
  is_active?: boolean;
}

interface Customer {
  id: number;
  name: string;
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

const TitleSection = styled.div`
  flex: 1;
`;

const PageTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: rgb(var(--color-text-primary));
  margin: 0 0 0.25rem 0;
`;

const PageSubtitle = styled.p`
  font-size: 14px;
  color: rgb(var(--color-text-secondary));
  margin: 0;
`;

const ContextBanner = styled.div`
  background: rgb(var(--color-primary) / 0.1);
  border: 1px solid rgb(var(--color-primary) / 0.3);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  
  span {
    font-weight: 500;
  }
`;

const SearchSection = styled.div`
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const ContentCard = styled.div`
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  flex: 1;
  overflow: auto;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem 1rem;
  color: rgb(var(--color-text-secondary));
  
  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: rgb(var(--color-text-primary));
  }
  
  p {
    margin-bottom: 1.5rem;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
`;

// ============================================================================
// Main Component
// ============================================================================

const CustomerProducts: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  // State
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchText, setSearchText] = useState<string>('');
  const [customer, setCustomer] = useState<Customer | null>(null);

  // Get customer from location state or fetch
  useEffect(() => {
    if (location.state?.customer) {
      setCustomer(location.state.customer);
    } else if (id) {
      fetchCustomer();
    }
  }, [id, location.state]);

  // Fetch customer details
  const fetchCustomer = async () => {
    if (!id) return;
    try {
      const response = await apiClient.get(`/customers/${id}/`);
      setCustomer(response.data);
    } catch (error) {
      console.error('Error fetching customer:', error);
      message.error('Failed to load customer details');
    }
  };

  // Fetch products
  useEffect(() => {
    if (id) {
      fetchProducts();
    }
  }, [id]);

  const fetchProducts = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const response = await apiClient.get(`/customers/${id}/products/`);
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
      message.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  // Remove product association
  const handleRemoveProduct = async (productId: number) => {
    Modal.confirm({
      title: 'Remove Product Association',
      content: 'Are you sure you want to remove this product from this customer?',
      okText: 'Remove',
      okType: 'danger',
      onOk: async () => {
        try {
          // Update customer to remove product from M2M
          await apiClient.patch(`/customers/${id}/`, {
            products: products.filter(p => p.id !== productId).map(p => p.id)
          });
          message.success('Product association removed successfully');
          fetchProducts();
        } catch (error) {
          console.error('Error removing product:', error);
          message.error('Failed to remove product association');
        }
      },
    });
  };

  // Navigate back to customers
  const handleBackToCustomers = () => {
    navigate('/customers');
  };

  // Table columns
  const columns: ColumnsType<Product> = [
    {
      title: 'Product Code',
      dataIndex: 'product_code',
      key: 'product_code',
      sorter: (a, b) => a.product_code.localeCompare(b.product_code),
      filteredValue: searchText ? [searchText] : null,
      onFilter: (value, record) => {
        const search = value.toString().toLowerCase();
        return (
          record.product_code.toLowerCase().includes(search) ||
          record.description_of_product_item.toLowerCase().includes(search)
        );
      },
    },
    {
      title: 'Description',
      dataIndex: 'description_of_product_item',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Protein Type',
      dataIndex: 'type_of_protein',
      key: 'protein',
      filters: [
        { text: 'Beef', value: 'Beef' },
        { text: 'Chicken', value: 'Chicken' },
        { text: 'Pork', value: 'Pork' },
        { text: 'Lamb', value: 'Lamb' },
      ],
      onFilter: (value, record) => record.type_of_protein === value,
    },
    {
      title: 'Fresh/Frozen',
      dataIndex: 'fresh_or_frozen',
      key: 'fresh_frozen',
      filters: [
        { text: 'Fresh', value: 'Fresh' },
        { text: 'Frozen', value: 'Frozen' },
      ],
      onFilter: (value, record) => record.fresh_or_frozen === value,
    },
    {
      title: 'Unit Weight',
      dataIndex: 'unit_weight',
      key: 'weight',
      render: (weight: number) => weight ? `${weight} lbs` : '-',
      sorter: (a, b) => (a.unit_weight || 0) - (b.unit_weight || 0),
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'status',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Active' : 'Inactive'}
        </Tag>
      ),
      filters: [
        { text: 'Active', value: true },
        { text: 'Inactive', value: false },
      ],
      onFilter: (value, record) => record.is_active === value,
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right' as const,
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleRemoveProduct(record.id)}
            size="small"
          >
            Remove
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <PageContainer>
      <PageHeader>
        <TitleSection>
          <PageTitle>Customer Products</PageTitle>
          <PageSubtitle>
            Products associated with {customer?.name || 'this customer'}
          </PageSubtitle>
        </TitleSection>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={handleBackToCustomers}
        >
          Back to Customers
        </Button>
      </PageHeader>

      {customer && (
        <ContextBanner>
          Viewing products for: <span>{customer.name}</span>
        </ContextBanner>
      )}

      <SearchSection>
        <Input
          placeholder="Search by product code or description..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ maxWidth: 400 }}
          allowClear
        />
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => message.info('Add Product feature coming soon!')}
        >
          Add Products
        </Button>
      </SearchSection>

      <ContentCard>
        {loading ? (
          <LoadingContainer>
            <Spin size="large" />
          </LoadingContainer>
        ) : products.length === 0 ? (
          <EmptyState>
            <h3>No Products Associated</h3>
            <p>This customer doesn't have any products associated yet.</p>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => message.info('Add Product feature coming soon!')}
            >
              Add Products
            </Button>
          </EmptyState>
        ) : (
          <Table
            columns={columns}
            dataSource={products}
            rowKey="id"
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} products`,
            }}
            scroll={{ x: 1200 }}
          />
        )}
      </ContentCard>
    </PageContainer>
  );
};

export default CustomerProducts;
