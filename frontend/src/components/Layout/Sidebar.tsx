import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useTheme } from '../../contexts/ThemeContext';
import { Theme } from '../../config/theme';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onHoverChange?: (isHovered: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle, onHoverChange }) => {
  const { theme, tenantBranding } = useTheme();
  const location = useLocation();
  const [isHovered, setIsHovered] = useState(false);
  const [keepOpen, setKeepOpen] = useState(() => {
    // Load keep open preference from localStorage
    return localStorage.getItem('sidebarKeepOpen') === 'true';
  });
  
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

  // Sync keepOpen with parent isOpen state when keepOpen changes
  useEffect(() => {
    if (keepOpen && !isOpen) {
      onToggle();
    } else if (!keepOpen && isOpen) {
      onToggle();
    }
  }, [keepOpen, isOpen, onToggle]);

  // Auto-close on route change unless keepOpen is enabled
  useEffect(() => {
    if (!keepOpen && isOpen) {
      onToggle();
    }
  }, [location.pathname, keepOpen, isOpen, onToggle]);

  // Notify parent of hover state changes
  useEffect(() => {
    if (onHoverChange) {
      onHoverChange(isHovered);
    }
  }, [isHovered, onHoverChange]);

  const handleKeepOpenToggle = () => {
    const newKeepOpen = !keepOpen;
    setKeepOpen(newKeepOpen);
    localStorage.setItem('sidebarKeepOpen', String(newKeepOpen));
  };

  // Sidebar is expanded if: keepOpen is true, OR it's being hovered (when not kept open)
  const isExpanded = keepOpen || isHovered;

  return (
    <SidebarContainer
      $isOpen={isExpanded}
      $theme={theme}
      onMouseEnter={() => !keepOpen && setIsHovered(true)}
      onMouseLeave={() => !keepOpen && setIsHovered(false)}
    >
      <SidebarHeader $theme={theme}>
        <Logo>
          {tenantBranding?.logoUrl ? (
            <LogoImage src={tenantBranding.logoUrl} alt={tenantBranding.tenantName} />
          ) : (
            <LogoIcon>🥩</LogoIcon>
          )}
          {isExpanded && <LogoText>{tenantBranding?.tenantName || 'ProjectMeats'}</LogoText>}
        </Logo>
        <KeepOpenToggle onClick={handleKeepOpenToggle} $theme={theme} $active={keepOpen} title={keepOpen ? "Auto-close sidebar" : "Keep sidebar open"}>
          📌
        </KeepOpenToggle>
      </SidebarHeader>

      <Navigation>
        {menuItems.map((item) => (
          <NavItem key={item.path}>
            <StyledNavLink to={item.path} $theme={theme}>
              <NavIcon $theme={theme}>{item.icon}</NavIcon>
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

const LogoImage = styled.img`
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 4px;
`;

const LogoText = styled.h2`
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
`;

const KeepOpenToggle = styled.button<{ $theme: Theme; $active: boolean }>`
  background: ${(props) => props.$active ? props.$theme.colors.primary : 'none'};
  border: none;
  color: ${(props) => props.$active ? 'white' : props.$theme.colors.sidebarText};
  cursor: pointer;
  font-size: 16px;
  padding: 5px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  opacity: ${(props) => props.$active ? 1 : 0.6};

  &:hover {
    opacity: 1;
    background-color: ${(props) => props.$active ? props.$theme.colors.primaryHover : props.$theme.colors.surfaceHover};
    color: ${(props) => props.$active ? 'white' : props.$theme.colors.sidebarTextHover};
    transform: scale(1.1);
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

const NavIcon = styled.span<{ $theme: Theme }>`
  font-size: 20px;
  min-width: 20px;
  display: flex;
  justify-content: center;
  filter: ${(props) => props.$theme.name === 'dark' ? 'grayscale(100%) brightness(1.5)' : 'grayscale(100%) brightness(0.7)'};
  opacity: 0.9;
`;

const NavLabel = styled.span`
  font-weight: 500;
  white-space: nowrap;
`;

export default Sidebar;
