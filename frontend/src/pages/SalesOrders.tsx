/**
 * Sales Orders Page
 * 
 * Manages outbound sales orders to customers
 */
import React from 'react';
import { ComingSoon } from './ComingSoon';

const SalesOrders: React.FC = () => {
  return (
    <ComingSoon 
      title="Sales Orders"
      description="Manage sales orders (S.O.'s) to customers. This feature will include order creation, tracking, fulfillment status, and customer delivery management."
    />
  );
};

export default SalesOrders;
