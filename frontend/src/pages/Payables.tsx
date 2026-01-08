/**
 * Payables Page
 * 
 * Manages accounts payable to suppliers
 */
import React from 'react';
import { ComingSoon } from './ComingSoon';

const Payables: React.FC = () => {
  return (
    <ComingSoon 
      title="Accounts Payable"
      description="Manage supplier invoices, payment scheduling, claims, and purchase order reconciliation for accounts payable."
    />
  );
};

export default Payables;
