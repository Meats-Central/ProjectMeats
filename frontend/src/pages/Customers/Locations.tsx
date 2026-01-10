/**
 * Customer Locations Management Page - Table View
 * 
 * Features:
 * - Table layout with sorting, pagination, and search
 * - Full CRUD operations (Create, Read, Update, Delete)
 * - Contextual customer selection (state-based navigation)
 * - Links to customer details
 * - Theme-compliant styling with antd Table
 * - Multi-tenancy support
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useLocation, useNavigate } from 'react-router-dom';
import { Table, Input, Button, Modal, Form, Select, message, Tag, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { SearchOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiClient } from '../../services/apiService';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface Location {
  id: number;
  name: string;
  code?: string;
  customer: number | null;
  customer_name?: string;
  location_type?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  contact_name?: string;
  is_active?: boolean;
}

interface Customer {
  id: number;
  name: string;
}

interface FormErrors {
  [key: string]: string[];
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

const TableControls = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const StyledTable = styled(Table)`
  .ant-table {
    background: rgb(var(--color-surface));
    border: 1px solid rgb(var(--color-border));
    border-radius: var(--radius-lg);
  }
  
  .ant-table-thead > tr > th {
    background: rgb(var(--color-surface));
    color: rgb(var(--color-text-primary));
    font-weight: 600;
    border-bottom: 1px solid rgb(var(--color-border));
  }
  
  .ant-table-tbody > tr > td {
    color: rgb(var(--color-text-primary));
    border-bottom: 1px solid rgb(var(--color-border));
  }
  
  .ant-table-tbody > tr:hover > td {
    background: rgb(var(--color-surface-hover));
  }
  
  .ant-pagination {
    margin-top: 1rem;
  }
  
  .ant-pagination-item-active {
    border-color: rgb(var(--color-primary));
    
    a {
      color: rgb(var(--color-primary));
    }
  }
`;

const CustomerLink = styled.a`
  color: rgb(var(--color-primary));
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    text-decoration: underline;
  }
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: rgb(var(--color-text-primary));
`;

const RequiredMark = styled.span`
  color: rgb(239, 68, 68);
  margin-left: 4px;
`;

const ErrorMessage = styled.div`
  color: rgb(239, 68, 68);
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

// ============================================================================
// Main Component
// ============================================================================

const CustomerLocations: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  
  // State
  const [locations, setLocations] = useState<Location[]>([]);
  const [filteredLocations, setFilteredLocations] = useState<Location[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [contextCustomerId, setContextCustomerId] = useState<number | null>(null);
  const [searchText, setSearchText] = useState('');
  const [formErrors, setFormErrors] = useState<FormErrors>({});

  // Detect context from navigation state (Phase 4 pattern)
  useEffect(() => {
    const state = location.state as any;
    if (state?.customerId) {
      setContextCustomerId(state.customerId);
    }
  }, [location]);

  useEffect(() => {
    loadLocations();
    loadCustomers();
  }, []);

  useEffect(() => {
    filterLocations();
  }, [locations, searchText, contextCustomerId]);

  const loadLocations = async () => {
    try {
      setLoading(true);
      // Try multiple possible endpoints
      let response;
      try {
        response = await apiClient.get('locations/');
      } catch (err: any) {
        if (err.response?.status === 404) {
          // Try alternative endpoint
          response = await apiClient.get('api/v1/locations/');
        } else {
          throw err;
        }
      }
      setLocations(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading locations:', error);
      message.warning('Locations API not yet implemented. Using empty dataset.');
      setLocations([]);
    } finally {
      setLoading(false);
    }
  };

  const loadCustomers = async () => {
    try {
      const response = await apiClient.get('customers/');
      setCustomers(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading customers:', error);
    }
  };

  const filterLocations = () => {
    let filtered = [...locations];
    
    // Filter by context customer
    if (contextCustomerId) {
      filtered = filtered.filter(l => l.customer === contextCustomerId);
    }
    
    // Filter by search text
    if (searchText) {
      const search = searchText.toLowerCase();
      filtered = filtered.filter(l => 
        l.name.toLowerCase().includes(search) ||
        l.code?.toLowerCase().includes(search) ||
        l.customer_name?.toLowerCase().includes(search) ||
        l.city?.toLowerCase().includes(search) ||
        l.state?.toLowerCase().includes(search)
      );
    }
    
    setFilteredLocations(filtered);
  };

  const handleAdd = () => {
    setEditingLocation(null);
    setFormErrors({});
    form.resetFields();
    
    // Pre-fill customer if context exists
    if (contextCustomerId) {
      form.setFieldsValue({ customer: contextCustomerId });
    }
    
    setShowModal(true);
  };

  const handleEdit = (loc: Location) => {
    setEditingLocation(loc);
    setFormErrors({});
    form.setFieldsValue({
      name: loc.name,
      code: loc.code || '',
      customer: loc.customer,
      location_type: loc.location_type || 'warehouse',
      address: loc.address || '',
      city: loc.city || '',
      state: loc.state || '',
      zip_code: loc.zip_code || '',
      country: loc.country || 'USA',
      phone: loc.phone || '',
      email: loc.email || '',
      contact_name: loc.contact_name || '',
    });
    setShowModal(true);
  };

  const handleDelete = (loc: Location) => {
    Modal.confirm({
      title: 'Delete Location',
      content: `Are you sure you want to delete ${loc.name}?`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await apiClient.delete(`locations/${loc.id}/`);
          message.success('Location deleted successfully');
          loadLocations();
        } catch (error: any) {
          console.error('Error deleting location:', error);
          message.error('Failed to delete location');
        }
      },
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setFormErrors({});
      
      if (editingLocation) {
        await apiClient.patch(`locations/${editingLocation.id}/`, values);
        message.success('Location updated successfully');
      } else {
        await apiClient.post('locations/', values);
        message.success('Location created successfully');
      }
      
      setShowModal(false);
      loadLocations();
    } catch (error: any) {
      if (error.response?.status === 400) {
        setFormErrors(error.response.data);
      } else if (error.errorFields) {
        // Ant Design form validation errors
        return;
      } else {
        message.error('Failed to save location');
      }
    }
  };

  const handleCustomerClick = (customerId: number) => {
    navigate(`/customers/${customerId}`);
  };

  // Table columns
  const columns: ColumnsType<Location> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
      width: 200,
    },
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
      sorter: (a, b) => (a.customer_name || '').localeCompare(b.customer_name || ''),
      render: (text, record) => (
        record.customer ? (
          <CustomerLink onClick={() => handleCustomerClick(record.customer!)}>
            {text || 'Unknown'}
          </CustomerLink>
        ) : '-'
      ),
      width: 180,
    },
    {
      title: 'Type',
      dataIndex: 'location_type',
      key: 'location_type',
      filters: [
        { text: 'Warehouse', value: 'warehouse' },
        { text: 'Store', value: 'store' },
        { text: 'Distribution Center', value: 'distribution_center' },
        { text: 'Office', value: 'office' },
      ],
      onFilter: (value, record) => record.location_type === value,
      render: (type) => {
        const colors: { [key: string]: string } = {
          warehouse: 'blue',
          store: 'green',
          distribution_center: 'orange',
          office: 'purple',
        };
        return type ? <Tag color={colors[type] || 'default'}>{type}</Tag> : '-';
      },
      width: 150,
    },
    {
      title: 'Address',
      dataIndex: 'address',
      key: 'address',
      width: 200,
      render: (text) => text || '-',
    },
    {
      title: 'City/State',
      key: 'location',
      render: (_, record) => {
        if (record.city && record.state) {
          return `${record.city}, ${record.state}`;
        }
        return '-';
      },
      width: 160,
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <PageContainer>
      <PageHeader>
        <TitleSection>
          <PageTitle>Customer Locations</PageTitle>
          <PageSubtitle>Manage customer delivery addresses and facilities</PageSubtitle>
        </TitleSection>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="large"
          onClick={handleAdd}
        >
          Add Location
        </Button>
      </PageHeader>

      {contextCustomerId && (
        <ContextBanner>
          <span>📍 Context: Showing locations for selected customer</span>
        </ContextBanner>
      )}

      <TableControls>
        <Input
          placeholder="Search locations by name, customer, or address..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ maxWidth: 400 }}
          allowClear
        />
      </TableControls>

      <StyledTable
        columns={columns}
        dataSource={filteredLocations}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} locations`,
        }}
        scroll={{ x: 'max-content' }}
      />

      {/* Form Modal */}
      <Modal
        title={editingLocation ? 'Edit Location' : 'Add New Location'}
        open={showModal}
        onOk={handleSubmit}
        onCancel={() => setShowModal(false)}
        width={700}
        okText={editingLocation ? 'Update' : 'Create'}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label={<><Label>Name<RequiredMark>*</RequiredMark></Label></>}
            rules={[{ required: true, message: 'Location name is required' }]}
            validateStatus={formErrors.name ? 'error' : ''}
            help={formErrors.name && <ErrorMessage>⚠ {formErrors.name[0]}</ErrorMessage>}
          >
            <Input placeholder="Location Name" />
          </Form.Item>

          <Form.Item
            name="code"
            label={<Label>Code</Label>}
            validateStatus={formErrors.code ? 'error' : ''}
            help={formErrors.code && <ErrorMessage>⚠ {formErrors.code[0]}</ErrorMessage>}
          >
            <Input placeholder="Location Code (optional)" />
          </Form.Item>

          <Form.Item
            name="customer"
            label={<Label>Customer</Label>}
            validateStatus={formErrors.customer ? 'error' : ''}
            help={formErrors.customer && <ErrorMessage>⚠ {formErrors.customer[0]}</ErrorMessage>}
          >
            <Select
              placeholder="Select Customer"
              disabled={!!contextCustomerId}
              allowClear
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={customers.map(c => ({ label: c.name, value: c.id }))}
            />
          </Form.Item>

          <Form.Item
            name="location_type"
            label={<Label>Location Type</Label>}
          >
            <Select placeholder="Select Type">
              <Select.Option value="warehouse">Warehouse</Select.Option>
              <Select.Option value="store">Store</Select.Option>
              <Select.Option value="distribution_center">Distribution Center</Select.Option>
              <Select.Option value="office">Office</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="address" label={<Label>Address</Label>}>
            <Input placeholder="Street Address" />
          </Form.Item>

          <Form.Item name="city" label={<Label>City</Label>}>
            <Input placeholder="City" />
          </Form.Item>

          <Form.Item name="state" label={<Label>State</Label>}>
            <Input placeholder="State" />
          </Form.Item>

          <Form.Item name="zip_code" label={<Label>ZIP Code</Label>}>
            <Input placeholder="ZIP Code" />
          </Form.Item>

          <Form.Item name="country" label={<Label>Country</Label>}>
            <Input placeholder="Country" />
          </Form.Item>

          <Form.Item name="phone" label={<Label>Phone</Label>}>
            <Input placeholder="Phone Number" />
          </Form.Item>

          <Form.Item name="email" label={<Label>Email</Label>}>
            <Input type="email" placeholder="Email Address" />
          </Form.Item>

          <Form.Item name="contact_name" label={<Label>Contact Name</Label>}>
            <Input placeholder="Primary Contact Name" />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default CustomerLocations;
