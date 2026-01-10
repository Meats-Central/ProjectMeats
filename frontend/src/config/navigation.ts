/**
 * Navigation configuration for ProjectMeats frontend
 * 
 * Defines the main navigation structure for the application.
 * This is the central location for managing navigation items.
 */

export interface NavigationItem {
  label: string;
  path?: string;
  icon?: string;
  children?: NavigationItem[];
  requiresAuth?: boolean;
  roles?: string[];
  onClick?: () => void;
  color?: string;
}

export const navigation: NavigationItem[] = [
  {
    label: 'Workspace',
    icon: '💼',
    children: [
      {
        label: 'Dashboard',
        icon: '📊',
        path: '/',
      },
      {
        label: 'Call Log',
        icon: '📞',
        path: '/call-log',
      },
      {
        label: 'Processes',
        icon: '⚙️',
        path: '/processes',
      },
      {
        label: 'Reports',
        icon: '📈',
        path: '/reports',
      },
    ],
  },
  {
    label: 'Suppliers',
    icon: '🏭',
    path: '/suppliers',
    children: [
      {
        label: 'Plants',
        icon: '🏢',
        path: '/plants',
      },
      {
        label: 'Contacts',
        icon: '📞',
        path: '/suppliers/contacts',
      },
    ],
  },
  {
    label: 'Customers',
    icon: '👥',
    path: '/customers',
    children: [
      {
        label: 'Contacts',
        icon: '📞',
        path: '/customers/contacts',
      },
    ],
  },
  {
    label: 'Orders',
    icon: '📋',
    children: [
      {
        label: "P.O.'s",
        icon: '📦',
        path: '/purchase-orders',
        children: [
          {
            label: 'Attachments',
            icon: '📎',
            path: '/purchase-orders/attachments',
          },
        ],
      },
      {
        label: "S.O.'s",
        icon: '🚚',
        path: '/sales-orders',
        children: [
          {
            label: 'Attachments',
            icon: '📎',
            path: '/sales-orders/attachments',
          },
        ],
      },
    ],
  },
  {
    label: 'Accounting',
    icon: '💰',
    children: [
      {
        label: 'Payables',
        icon: '💸',
        path: '/accounting/payables',
        children: [
          {
            label: 'Claims',
            icon: '📋',
            path: '/accounting/payables/claims',
          },
          {
            label: "P.O.'s",
            icon: '📦',
            path: '/accounting/payables/pos',
          },
        ],
      },
      {
        label: 'Receivables',
        icon: '💵',
        path: '/accounts-receivables',
        children: [
          {
            label: 'Claims',
            icon: '📋',
            path: '/accounting/receivables/claims',
          },
          {
            label: "S.O.'s",
            icon: '🚚',
            path: '/accounting/receivables/sos',
          },
          {
            label: 'Invoices',
            icon: '🧾',
            path: '/accounting/receivables/invoices',
          },
        ],
      },
    ],
  },
  {
    label: 'Cold Storage',
    icon: '❄️',
    path: '/cold-storage',
  },
  {
    label: 'Logistics',
    icon: '🚛',
    path: '/carriers',
  },
];

