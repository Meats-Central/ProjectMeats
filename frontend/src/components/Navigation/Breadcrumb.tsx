import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const Breadcrumb: React.FC = () => {
  const location = useLocation();
  
  // Create breadcrumb items from current path
  const pathnames = location.pathname.split('/').filter(x => x);
  
  const breadcrumbNameMap: { [key: string]: string } = {
    'suppliers': 'Suppliers',
    'customers': 'Customers',
    'purchase-orders': 'Purchase Orders',
    'accounts-receivables': 'Accounts Receivables',
    'contacts': 'Contacts',
    'plants': 'Plants', 
    'carriers': 'Carriers',
    'ai-assistant': 'AI Assistant',
    'profile': 'Profile',
    'settings': 'Settings',
  };

  if (pathnames.length === 0) {
    return (
      <BreadcrumbContainer>
        <BreadcrumbItem>
          <BreadcrumbText>Dashboard</BreadcrumbText>
        </BreadcrumbItem>
      </BreadcrumbContainer>
    );
  }

  return (
    <BreadcrumbContainer>
      <BreadcrumbItem>
        <BreadcrumbLink to="/">Dashboard</BreadcrumbLink>
        <Separator>/</Separator>
      </BreadcrumbItem>
      {pathnames.map((pathname, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;
        const displayName = breadcrumbNameMap[pathname] || pathname;

        return (
          <BreadcrumbItem key={pathname}>
            {isLast ? (
              <BreadcrumbText>{displayName}</BreadcrumbText>
            ) : (
              <>
                <BreadcrumbLink to={routeTo}>{displayName}</BreadcrumbLink>
                <Separator>/</Separator>
              </>
            )}
          </BreadcrumbItem>
        );
      })}
    </BreadcrumbContainer>
  );
};

const BreadcrumbContainer = styled.nav`
  display: flex;
  align-items: center;
  padding: 16px 0;
  font-size: 14px;
`;

const BreadcrumbItem = styled.div`
  display: flex;
  align-items: center;
`;

const BreadcrumbLink = styled(Link)`
  color: #6c757d;
  text-decoration: none;
  transition: color 0.2s;

  &:hover {
    color: #495057;
    text-decoration: underline;
  }
`;

const BreadcrumbText = styled.span`
  color: #495057;
  font-weight: 500;
`;

const Separator = styled.span`
  margin: 0 8px;
  color: #6c757d;
`;

export default Breadcrumb;