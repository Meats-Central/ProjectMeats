import React from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/suppliers', label: 'Suppliers', icon: '🏭' },
    { path: '/customers', label: 'Customers', icon: '👥' },
    { path: '/purchase-orders', label: 'Purchase Orders', icon: '📋' },
    { path: '/accounts-receivables', label: 'Accounts Receivables', icon: '💰' },
    { path: '/contacts', label: 'Contacts', icon: '📞' },
    { path: '/plants', label: 'Plants', icon: '🏢' },
    { path: '/carriers', label: 'Carriers', icon: '🚛' },
    { path: '/ai-assistant', label: 'AI Assistant', icon: '🤖' },
  ];

  return (
    <SidebarContainer $isOpen={isOpen}>
      <SidebarHeader>
        <Logo>
          <LogoIcon>🥩</LogoIcon>
          {isOpen && <LogoText>ProjectMeats</LogoText>}
        </Logo>
        <ToggleButton onClick={onToggle}>
          {isOpen ? '◀' : '▶'}
        </ToggleButton>
      </SidebarHeader>
      
      <Navigation>
        {menuItems.map((item) => (
          <NavItem key={item.path}>
            <StyledNavLink to={item.path}>
              <NavIcon>{item.icon}</NavIcon>
              {isOpen && <NavLabel>{item.label}</NavLabel>}
            </StyledNavLink>
          </NavItem>
        ))}
      </Navigation>
    </SidebarContainer>
  );
};

const SidebarContainer = styled.div<{ $isOpen: boolean }>`
  width: ${props => props.$isOpen ? '250px' : '60px'};
  height: 100vh;
  background: #2c3e50;
  color: white;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
`;

const SidebarHeader = styled.div`
  padding: 20px 15px;
  border-bottom: 1px solid #34495e;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const LogoIcon = styled.span`
  font-size: 24px;
`;

const LogoText = styled.h2`
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #34495e;
  }
`;

const Navigation = styled.nav`
  flex: 1;
  padding-top: 20px;
`;

const NavItem = styled.li`
  list-style: none;
  margin-bottom: 2px;
`;

const StyledNavLink = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 20px;
  color: #bdc3c7;
  text-decoration: none;
  transition: all 0.2s ease;

  &:hover {
    background-color: #34495e;
    color: white;
  }

  &.active {
    background-color: #3498db;
    color: white;
    border-right: 3px solid #2980b9;
  }
`;

const NavIcon = styled.span`
  font-size: 20px;
  min-width: 20px;
  display: flex;
  justify-content: center;
`;

const NavLabel = styled.span`
  font-weight: 500;
  white-space: nowrap;
`;

export default Sidebar;
