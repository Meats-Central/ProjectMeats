import type { Meta, StoryObj } from '@storybook/react';
import SupplierPerformanceChart from '../components/Visualization/SupplierPerformanceChart';

const meta: Meta<typeof SupplierPerformanceChart> = {
  title: 'Visualization/SupplierPerformanceChart',
  component: SupplierPerformanceChart,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A bar chart component that displays supplier performance metrics including orders, revenue, and ratings.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    height: {
      control: { type: 'number', min: 200, max: 800, step: 50 },
      description: 'Height of the chart in pixels',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

const sampleData = [
  { name: 'ABC Meats', orders: 24, revenue: 125000, rating: 4.2 },
  { name: 'Prime Cuts', orders: 18, revenue: 98000, rating: 4.8 },
  { name: 'Quality Foods', orders: 32, revenue: 167000, rating: 3.9 },
  { name: 'Farm Fresh', orders: 15, revenue: 75000, rating: 4.5 },
];

export const Default: Story = {
  args: {
    data: sampleData,
    height: 300,
  },
};

export const TallChart: Story = {
  args: {
    data: sampleData,
    height: 500,
  },
};

export const SingleSupplier: Story = {
  args: {
    data: [{ name: 'ABC Meats', orders: 24, revenue: 125000, rating: 4.2 }],
    height: 300,
  },
};

export const ManySuppliers: Story = {
  args: {
    data: [
      { name: 'ABC Meats', orders: 24, revenue: 125000, rating: 4.2 },
      { name: 'Prime Cuts', orders: 18, revenue: 98000, rating: 4.8 },
      { name: 'Quality Foods', orders: 32, revenue: 167000, rating: 3.9 },
      { name: 'Farm Fresh', orders: 15, revenue: 75000, rating: 4.5 },
      { name: 'Mountain Beef', orders: 28, revenue: 142000, rating: 4.3 },
      { name: 'Ocean Meats', orders: 21, revenue: 89000, rating: 4.0 },
    ],
    height: 350,
  },
};