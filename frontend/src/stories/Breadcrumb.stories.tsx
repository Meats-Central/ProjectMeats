import type { Meta, StoryObj } from '@storybook/react';
import { BrowserRouter } from 'react-router-dom';
import { ComponentType } from 'react';
import Breadcrumb from '../components/Navigation/Breadcrumb';

const meta: Meta<typeof Breadcrumb> = {
  title: 'Navigation/Breadcrumb',
  component: Breadcrumb,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'A breadcrumb navigation component that shows the current page path with clickable links.',
      },
    },
  },
  tags: ['autodocs'],
  decorators: [
    (Story: ComponentType) => (
      <BrowserRouter>
        <Story />
      </BrowserRouter>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof meta>;

// Note: The breadcrumb component reads from the current location
// In Storybook, we can't easily change the route, so we'll show
// how it would look in different scenarios through documentation

export const Dashboard: Story = {
  parameters: {
    docs: {
      description: {
        story: 'How the breadcrumb appears on the dashboard (root path).',
      },
    },
  },
};

export const SingleLevel: Story = {
  parameters: {
    docs: {
      description: {
        story: 'How the breadcrumb would appear on a single level path like /suppliers.',
      },
    },
  },
};

export const MultiLevel: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'How the breadcrumb would appear on a multi-level path like /purchase-orders/123/edit.',
      },
    },
  },
};
