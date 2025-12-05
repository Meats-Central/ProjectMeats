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

// Pin icon SVG component
const PinIcon: React.FC<{ isPinned: boolean }> = ({ isPinned }) => (
  <svg 
    width="16" 
    height="16" 
    viewBox="0 0 24 24" 
    fill={isPinned ? "currentColor" : "none"}
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    style={{ transform: isPinned ? 'rotate(45deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}
  >
    <line x1="12" y1="17" x2="12" y2="22" />
    <path d="M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24Z" />
  </svg>
);

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle, onHoverChange }) => {
  const { theme, tenantBranding } = useTheme();
  const location = useLocation();
  const [isHovered, setIsHovered] = useState(false);
  const [keepOpen, setKeepOpen] = useState(() => {
    // Load keep open preference from localStorage
    return localStorage.getItem('sidebarKeepOpen') === 'true';
  });

  // Check if we're on desktop (for pin functionality)
  // Using function to safely access window for SSR compatibility
  const getIsDesktop = () => typeof window !== 'undefined' && window.innerWidth >= 768;
  const [isDesktop, setIsDesktop] = useState(getIsDesktop);
  
  useEffect(() => {
    const handleResize = () => {
      setIsDesktop(getIsDesktop());
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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
      <SidebarHeader $theme={theme} $isExpanded={isExpanded}>
        <Logo>
          {tenantBranding?.logoUrl ? (
            <LogoImage src={tenantBranding.logoUrl} alt={tenantBranding.tenantName} />
          ) : (
            <LogoIcon>🥩</LogoIcon>
          )}
          {isExpanded && <LogoText>{tenantBranding?.tenantName || 'ProjectMeats'}</LogoText>}
        </Logo>
        {isExpanded && isDesktop && (
          <PinButton 
            onClick={handleKeepOpenToggle} 
            $theme={theme} 
            $active={keepOpen} 
            title={keepOpen ? "Unpin sidebar" : "Pin sidebar open"}
            aria-label={keepOpen ? "Unpin sidebar" : "Pin sidebar open"}
          >
            <PinIcon isPinned={keepOpen} />
          </PinButton>
        )}
      </SidebarHeader>

      <NavigationSection>
        <NavigationMenu items={navigation} isExpanded={isExpanded} />
      </NavigationSection>

      <SidebarFooter $isExpanded={isExpanded}>
        {isExpanded && (
          <FooterText>
            © 2025 ProjectMeats
          </FooterText>
        )}
      </SidebarFooter>
    </SidebarContainer>
  );
};

const SidebarContainer = styled.div<{ $isOpen: boolean; $theme: Theme }>`
  width: ${(props) => (props.$isOpen ? '260px' : '64px')};
  height: 100vh;
  background: #0f172a; /* Dark mode per architecture */
  color: #ffffff;
  transition: width 0.25s ease;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
`;

const SidebarHeader = styled.div<{ $theme: Theme; $isExpanded: boolean }>`
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 64px;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const LogoIcon = styled.span`
  font-size: 28px;
  line-height: 1;
`;

const LogoImage = styled.img`
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 6px;
`;

const LogoText = styled.h2`
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  color: #ffffff;
  letter-spacing: 0.01em;
`;

const PinButton = styled.button<{ $theme: Theme; $active: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: ${(props) => props.$active ? 'rgba(102, 126, 234, 0.2)' : 'transparent'};
  border: none;
  border-radius: 6px;
  color: ${(props) => props.$active ? '#667eea' : 'rgba(255, 255, 255, 0.6)'};
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    background: ${(props) => props.$active ? 'rgba(102, 126, 234, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
    color: ${(props) => props.$active ? '#667eea' : '#ffffff'};
  }

  &:focus-visible {
    outline: 2px solid #667eea;
    outline-offset: 2px;
  }
`;

const NavigationSection = styled.nav`
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;

    &:hover {
      background: rgba(255, 255, 255, 0.25);
    }
  }
`;

const SidebarFooter = styled.div<{ $isExpanded: boolean }>`
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  min-height: ${(props) => props.$isExpanded ? '48px' : '0'};
  display: ${(props) => props.$isExpanded ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
`;

const FooterText = styled.span`
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 0.02em;
`;

export default Sidebar;
