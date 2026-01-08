/**
 * Cold Storage Page
 * 
 * Manages cold storage inventory and locations
 */
import React from 'react';
import { ComingSoon } from './ComingSoon';

const ColdStorage: React.FC = () => {
  return (
    <ComingSoon 
      title="Cold Storage"
      description="Track inventory in cold storage facilities, manage temperatures, and monitor stock levels across multiple locations."
    />
  );
};

export default ColdStorage;
