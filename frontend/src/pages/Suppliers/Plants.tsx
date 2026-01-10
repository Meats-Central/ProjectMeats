/**
 * Plants Management Page - Table View
 * 
 * Features:
 * - Table layout with sorting, pagination, and search
 * - Full CRUD operations (Create, Read, Update, Delete)
 * - Contextual supplier selection (state-based navigation)
 * - Links to supplier details
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

interface Plant {
  id: number;
  name: string;
  code: string;
  supplier: number | null;
  supplier_name?: string;
  plant_type?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  manager?: string;
  capacity?: number;
  is_active?: boolean;
}

interface Supplier {
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

const SupplierLink = styled.a`
  color: rgb(var(--color-primary));
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    text-decoration: underline;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 1rem;
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

const Plants: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  
  // State
  const [plants, setPlants] = useState<Plant[]>([]);
  const [filteredPlants, setFilteredPlants] = useState<Plant[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPlant, setEditingPlant] = useState<Plant | null>(null);
  const [contextSupplierId, setContextSupplierId] = useState<number | null>(null);
  const [searchText, setSearchText] = useState('');
  const [formErrors, setFormErrors] = useState<FormErrors>({});

  // Detect context from navigation state (Phase 4 pattern)
  useEffect(() => {
    const state = location.state as any;
    if (state?.supplierId) {
      setContextSupplierId(state.supplierId);
    }
  }, [location]);

  useEffect(() => {
    loadPlants();
    loadSuppliers();
  }, []);

  useEffect(() => {
    filterPlants();
  }, [plants, searchText, contextSupplierId]);

  const loadPlants = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('plants/');
      setPlants(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading plants:', error);
      message.error('Failed to load plants');
    } finally {
      setLoading(false);
    }
  };

  const loadSuppliers = async () => {
    try {
      const response = await apiClient.get('suppliers/');
      setSuppliers(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading suppliers:', error);
    }
  };

  const filterPlants = () => {
    let filtered = [...plants];
    
    // Filter by context supplier
    if (contextSupplierId) {
      filtered = filtered.filter(p => p.supplier === contextSupplierId);
    }
    
    // Filter by search text
    if (searchText) {
      const search = searchText.toLowerCase();
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(search) ||
        p.code.toLowerCase().includes(search) ||
        p.supplier_name?.toLowerCase().includes(search) ||
        p.city?.toLowerCase().includes(search) ||
        p.state?.toLowerCase().includes(search)
      );
    }
    
    setFilteredPlants(filtered);
  };

  const handleAdd = () => {
    setEditingPlant(null);
    setFormErrors({});
    form.resetFields();
    
    // Pre-fill supplier if context exists
    if (contextSupplierId) {
      form.setFieldsValue({ supplier: contextSupplierId });
    }
    
    setShowModal(true);
  };

  const handleEdit = (plant: Plant) => {
    setEditingPlant(plant);
    setFormErrors({});
    form.setFieldsValue({
      name: plant.name,
      code: plant.code,
      supplier: plant.supplier,
      plant_type: plant.plant_type || 'processing',
      address: plant.address || '',
      city: plant.city || '',
      state: plant.state || '',
      zip_code: plant.zip_code || '',
      country: plant.country || 'USA',
      phone: plant.phone || '',
      email: plant.email || '',
      manager: plant.manager || '',
      capacity: plant.capacity || '',
    });
    setShowModal(true);
  };

  const handleDelete = (plant: Plant) => {
    Modal.confirm({
      title: 'Delete Plant',
      content: `Are you sure you want to delete ${plant.name}?`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await apiClient.delete(`plants/${plant.id}/`);
          message.success('Plant deleted successfully');
          loadPlants();
        } catch (error: any) {
          console.error('Error deleting plant:', error);
          message.error('Failed to delete plant');
        }
      },
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setFormErrors({});
      
      const payload = {
        ...values,
        capacity: values.capacity ? parseInt(values.capacity) : null,
      };
      
      if (editingPlant) {
        await apiClient.patch(`plants/${editingPlant.id}/`, payload);
        message.success('Plant updated successfully');
      } else {
        await apiClient.post('plants/', payload);
        message.success('Plant created successfully');
      }
      
      setShowModal(false);
      loadPlants();
    } catch (error: any) {
      if (error.response?.status === 400) {
        setFormErrors(error.response.data);
      } else if (error.errorFields) {
        // Ant Design form validation errors
        return;
      } else {
        message.error('Failed to save plant');
      }
    }
  };

  const handleSupplierClick = (supplierId: number) => {
    navigate(`/suppliers/${supplierId}`);
  };

  // Table columns
  const columns: ColumnsType<Plant> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
      width: 200,
    },
    {
      title: 'Code',
      dataIndex: 'code',
      key: 'code',
      sorter: (a, b) => a.code.localeCompare(b.code),
      width: 120,
    },
    {
      title: 'Supplier',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      sorter: (a, b) => (a.supplier_name || '').localeCompare(b.supplier_name || ''),
      render: (text, record) => (
        record.supplier ? (
          <SupplierLink onClick={() => handleSupplierClick(record.supplier!)}>
            {text || 'Unknown'}
          </SupplierLink>
        ) : '-'
      ),
      width: 180,
    },
    {
      title: 'Type',
      dataIndex: 'plant_type',
      key: 'plant_type',
      filters: [
        { text: 'Processing', value: 'processing' },
        { text: 'Distribution', value: 'distribution' },
        { text: 'Storage', value: 'storage' },
        { text: 'Mixed', value: 'mixed' },
      ],
      onFilter: (value, record) => record.plant_type === value,
      render: (type) => {
        const colors: { [key: string]: string } = {
          processing: 'blue',
          distribution: 'green',
          storage: 'orange',
          mixed: 'purple',
        };
        return type ? <Tag color={colors[type] || 'default'}>{type}</Tag> : '-';
      },
      width: 130,
    },
    {
      title: 'Location',
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
      title: 'Contact',
      key: 'contact',
      render: (_, record) => (
        <div>
          {record.phone && <div>📞 {record.phone}</div>}
          {record.manager && <div>👤 {record.manager}</div>}
          {!record.phone && !record.manager && '-'}
        </div>
      ),
      width: 180,
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
          <PageTitle>Plants & Facilities</PageTitle>
          <PageSubtitle>Manage supplier processing facilities and locations</PageSubtitle>
        </TitleSection>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="large"
          onClick={handleAdd}
        >
          Add Plant
        </Button>
      </PageHeader>

      {contextSupplierId && (
        <ContextBanner>
          <span>📍 Context: Showing plants for selected supplier</span>
        </ContextBanner>
      )}

      <TableControls>
        <Input
          placeholder="Search plants by name, code, supplier, or location..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ maxWidth: 400 }}
          allowClear
        />
      </TableControls>

      <StyledTable
        columns={columns}
        dataSource={filteredPlants}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} plants`,
        }}
        scroll={{ x: 'max-content' }}
      />

      {/* Form Modal */}
      <Modal
        title={editingPlant ? 'Edit Plant' : 'Add New Plant'}
        open={showModal}
        onOk={handleSubmit}
        onCancel={() => setShowModal(false)}
        width={700}
        okText={editingPlant ? 'Update' : 'Create'}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label={<><Label>Name<RequiredMark>*</RequiredMark></Label></>}
            rules={[{ required: true, message: 'Plant name is required' }]}
            validateStatus={formErrors.name ? 'error' : ''}
            help={formErrors.name && <ErrorMessage>⚠ {formErrors.name[0]}</ErrorMessage>}
          >
            <Input placeholder="Plant Name" />
          </Form.Item>

          <Form.Item
            name="code"
            label={<><Label>Code<RequiredMark>*</RequiredMark></Label></>}
            rules={[{ required: true, message: 'Plant code is required' }]}
            validateStatus={formErrors.code ? 'error' : ''}
            help={formErrors.code && <ErrorMessage>⚠ {formErrors.code[0]}</ErrorMessage>}
          >
            <Input placeholder="Plant Code (e.g., PLT001)" />
          </Form.Item>

          <Form.Item
            name="supplier"
            label={<Label>Supplier</Label>}
            validateStatus={formErrors.supplier ? 'error' : ''}
            help={formErrors.supplier && <ErrorMessage>⚠ {formErrors.supplier[0]}</ErrorMessage>}
          >
            <Select
              placeholder="Select Supplier"
              disabled={!!contextSupplierId}
              allowClear
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={suppliers.map(s => ({ label: s.name, value: s.id }))}
            />
          </Form.Item>

          <Form.Item
            name="plant_type"
            label={<Label>Plant Type</Label>}
          >
            <Select placeholder="Select Type">
              <Select.Option value="processing">Processing</Select.Option>
              <Select.Option value="distribution">Distribution</Select.Option>
              <Select.Option value="storage">Storage</Select.Option>
              <Select.Option value="mixed">Mixed</Select.Option>
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

          <Form.Item name="manager" label={<Label>Manager</Label>}>
            <Input placeholder="Facility Manager Name" />
          </Form.Item>

          <Form.Item name="capacity" label={<Label>Capacity</Label>}>
            <Input type="number" placeholder="Annual Capacity (tons)" />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default Plants;
