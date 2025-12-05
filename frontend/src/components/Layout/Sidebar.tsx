import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useTheme } from '../../contexts/ThemeContext';
import { Theme } from '../../config/theme';
import { navigation } from '../../config/navigation';
import NavigationMenu from '../Navigation/NavigationMenu';

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

  // Sync keepOpen with parent isOpen state when keepOpen changes
  useEffect(() => {
    if (keepOpen && !isOpen) {
      onToggle();
    } else if (!keepOpen && isOpen) {
      onToggle();
    }
  }, [keepOpen, isOpen, onToggle]);

  // Reset hover state when sidebar is pinned (separate effect to avoid dependency issues)
  useEffect(() => {
    if (keepOpen) {
      setIsHovered(false);
    }
  }, [keepOpen]);

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
        {isExpanded && (
          <KeepOpenToggle onClick={handleKeepOpenToggle} $theme={theme} $active={keepOpen} title={keepOpen ? "Auto-close sidebar" : "Keep sidebar open"}>
            📌
          </KeepOpenToggle>
        )}
      </SidebarHeader>

      <Navigation>
        <NavigationMenu items={navigation} isExpanded={isExpanded} />
      </Navigation>
    </SidebarContainer>
  );
};

const SidebarContainer = styled.div<{ $isOpen: boolean; $theme: Theme }>`
  width: ${(props) => (props.$isOpen ? '250px' : '60px')};
  height: 100vh;
  background: #333; /* Consistent dark background regardless of theme */
  color: white; /* Consistent white text */
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.1); /* Consistent border */
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
  color: white; /* Consistent white tenant name */
`;

const KeepOpenToggle = styled.button<{ $theme: Theme; $active: boolean }>`
  background: ${(props) => props.$active ? props.$theme.colors.primary : 'none'};
  border: none;
  color: white; /* Consistent white icon color */
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
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 0;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
`;

export default Sidebar;
