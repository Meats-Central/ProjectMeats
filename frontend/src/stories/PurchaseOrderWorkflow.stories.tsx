import type { Meta, StoryObj } from '@storybook/react';
import PurchaseOrderWorkflow from '../components/Workflow/PurchaseOrderWorkflow';

const meta: Meta<typeof PurchaseOrderWorkflow> = {
  title: 'Workflow/PurchaseOrderWorkflow',
  component: PurchaseOrderWorkflow,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'A workflow visualization component using React Flow to show purchase order stages and their status.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    height: {
      control: { type: 'number', min: 300, max: 800, step: 50 },
      description: 'Height of the workflow diagram',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const InProgress: Story = {
  args: {
    stages: [
      { id: 'draft', label: 'Draft', status: 'completed', description: 'Order created' },
      { id: 'approval', label: 'Approval', status: 'completed', description: 'Management review' },
      {
        id: 'processing',
        label: 'Processing',
        status: 'active',
        description: 'Supplier processing',
      },
      { id: 'shipping', label: 'Shipping', status: 'pending', description: 'In transit' },
      { id: 'delivered', label: 'Delivered', status: 'pending', description: 'Order complete' },
    ],
    height: 400,
  },
};

export const WithException: Story = {
  args: {
    stages: [
      { id: 'draft', label: 'Draft', status: 'completed', description: 'Order created' },
      { id: 'approval', label: 'Approval', status: 'completed', description: 'Management review' },
      {
        id: 'processing',
        label: 'Processing',
        status: 'exception',
        description: 'Supplier issue detected',
      },
      { id: 'shipping', label: 'Shipping', status: 'pending', description: 'In transit' },
      { id: 'delivered', label: 'Delivered', status: 'pending', description: 'Order complete' },
    ],
    height: 400,
  },
};

export const Completed: Story = {
  args: {
    stages: [
      { id: 'draft', label: 'Draft', status: 'completed', description: 'Order created' },
      { id: 'approval', label: 'Approval', status: 'completed', description: 'Management review' },
      {
        id: 'processing',
        label: 'Processing',
        status: 'completed',
        description: 'Supplier processed',
      },
      {
        id: 'shipping',
        label: 'Shipping',
        status: 'completed',
        description: 'Shipped successfully',
      },
      { id: 'delivered', label: 'Delivered', status: 'completed', description: 'Order delivered' },
    ],
    height: 400,
  },
};

export const SimpleWorkflow: Story = {
  args: {
    stages: [
      { id: 'created', label: 'Created', status: 'completed' },
      { id: 'approved', label: 'Approved', status: 'active' },
      { id: 'fulfilled', label: 'Fulfilled', status: 'pending' },
    ],
    height: 300,
  },
};
