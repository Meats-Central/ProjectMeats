import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useTheme } from '../../contexts/ThemeContext';
import { Theme } from '../../config/theme';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const { theme } = useTheme();
  const location = useLocation();
  const [isHovered, setIsHovered] = useState(false);
  
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/suppliers', label: 'Suppliers', icon: '🏭' },
    { path: '/customers', label: 'Customers', icon: '👥' },
    { path: '/purchase-orders', label: 'Purchase Orders', icon: '📋' },
    {
      path: '/accounts-receivables',
      label: 'Accounts Receivables',
      icon: '💰',
    },
    { path: '/contacts', label: 'Contacts', icon: '📞' },
    { path: '/plants', label: 'Plants', icon: '🏢' },
    { path: '/carriers', label: 'Carriers', icon: '🚛' },
    { path: '/ai-assistant', label: 'AI Assistant', icon: '🤖' },
  ];

  // Auto-close on route change (for mobile/tablet)
  useEffect(() => {
    // Only auto-close on small screens when menu is open
    if (isOpen && window.innerWidth < 768) {
      onToggle();
    }
  }, [location.pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  const isExpanded = isOpen || isHovered;

  return (
    <SidebarContainer
      $isOpen={isExpanded}
      $theme={theme}
      onMouseEnter={() => !isOpen && setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <SidebarHeader $theme={theme}>
        <Logo>
          <LogoIcon>🥩</LogoIcon>
          {isExpanded && <LogoText>ProjectMeats</LogoText>}
        </Logo>
        <ToggleButton onClick={onToggle} $theme={theme}>
          {isOpen ? '◀' : '▶'}
        </ToggleButton>
      </SidebarHeader>

      <Navigation>
        {menuItems.map((item) => (
          <NavItem key={item.path}>
            <StyledNavLink to={item.path} $theme={theme}>
              <NavIcon>{item.icon}</NavIcon>
              {isExpanded && <NavLabel>{item.label}</NavLabel>}
            </StyledNavLink>
          </NavItem>
        ))}
      </Navigation>
    </SidebarContainer>
  );
};

const SidebarContainer = styled.div<{ $isOpen: boolean; $theme: Theme }>`
  width: ${(props) => (props.$isOpen ? '250px' : '60px')};
  height: 100vh;
  background: ${(props) => props.$theme.colors.sidebarBackground};
  color: ${(props) => props.$theme.colors.sidebarText};
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 2px 0 10px ${(props) => props.$theme.colors.shadowMedium};
`;

const SidebarHeader = styled.div<{ $theme: Theme }>`
  padding: 20px 15px;
  border-bottom: 1px solid ${(props) => props.$theme.colors.sidebarBorder};
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

const ToggleButton = styled.button<{ $theme: Theme }>`
  background: none;
  border: none;
  color: ${(props) => props.$theme.colors.sidebarText};
  cursor: pointer;
  font-size: 16px;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background-color: ${(props) => props.$theme.colors.surfaceHover};
    color: ${(props) => props.$theme.colors.sidebarTextHover};
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

const StyledNavLink = styled(NavLink)<{ $theme: Theme }>`
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 20px;
  color: ${(props) => props.$theme.colors.sidebarText};
  text-decoration: none;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${(props) => props.$theme.colors.surfaceHover};
    color: ${(props) => props.$theme.colors.sidebarTextHover};
  }

  &.active {
    background-color: ${(props) => props.$theme.colors.sidebarActive};
    color: white;
    border-right: 3px solid ${(props) => props.$theme.colors.primaryActive};
  }
`;

const NavIcon = styled.span`
  font-size: 20px;
  min-width: 20px;
  display: flex;
  justify-center: center;
`;

const NavLabel = styled.span`
  font-weight: 500;
  white-space: nowrap;
`;

export default Sidebar;
