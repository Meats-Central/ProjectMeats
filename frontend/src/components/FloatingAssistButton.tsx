/**
 * Floating Assistance Button (FAB)
 * 
 * Fixed-position action button in bottom-right corner providing quick access to:
 * - Support: FAQ
 * - Support: Create Ticket
 * - User Profile
 * 
 * Features:
 * - Responsive design
 * - Theme-aware styling
 * - ARIA accessible
 * - z-index: 1000 (above tables, below modals)
 */
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useTheme } from '../contexts/ThemeContext';
import { Theme } from '../config/theme';

const FloatingAssistButton: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const { theme } = useTheme();
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        buttonRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setMenuOpen(false);
      }
    };

    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuOpen]);

  const handleMenuItemClick = (path: string) => {
    setMenuOpen(false);
    navigate(path);
  };

  const menuItems = [
    { label: 'Support: Questions (FAQ)', path: '/faq', icon: '❓' },
    { label: 'Support: Create Ticket', path: '/support/ticket', icon: '🎫' },
    { label: 'Profile', path: '/profile', icon: '👤' },
  ];

  return (
    <Container>
      <FAB
        ref={buttonRef}
        onClick={() => setMenuOpen(!menuOpen)}
        $theme={theme}
        $isOpen={menuOpen}
        aria-label="Assistance Menu"
        aria-expanded={menuOpen}
        aria-haspopup="true"
      >
        {menuOpen ? '✕' : '?'}
      </FAB>

      {menuOpen && (
        <Menu ref={menuRef} $theme={theme} role="menu">
          {menuItems.map((item, index) => (
            <MenuItem
              key={index}
              onClick={() => handleMenuItemClick(item.path)}
              $theme={theme}
              role="menuitem"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleMenuItemClick(item.path);
                }
              }}
            >
              <MenuItemIcon>{item.icon}</MenuItemIcon>
              <MenuItemText>{item.label}</MenuItemText>
            </MenuItem>
          ))}
        </Menu>
      )}
    </Container>
  );
};

const Container = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;

  @media (max-width: 768px) {
    bottom: 15px;
    right: 15px;
  }
`;

const FAB = styled.button<{ $theme: Theme; $isOpen: boolean }>`
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: ${(props) =>
    props.$theme.name === 'dark'
      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: white;
  border: none;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
  }

  &:active {
    transform: scale(0.95);
  }

  &:focus {
    outline: 2px solid ${(props) => (props.$theme.name === 'dark' ? '#fff' : '#667eea')};
    outline-offset: 2px;
  }

  @media (max-width: 768px) {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
`;

const Menu = styled.div<{ $theme: Theme }>`
  position: absolute;
  bottom: 70px;
  right: 0;
  background: ${(props) => (props.$theme.name === 'dark' ? '#2d2d2d' : '#ffffff')};
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  min-width: 240px;
  overflow: hidden;
  animation: slideUp 0.2s ease-out;

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @media (max-width: 768px) {
    min-width: 200px;
    bottom: 60px;
  }
`;

const MenuItem = styled.div<{ $theme: Theme }>`
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: ${(props) => (props.$theme.name === 'dark' ? '#e0e0e0' : '#333333')};
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid
    ${(props) => (props.$theme.name === 'dark' ? '#404040' : '#e0e0e0')};

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background-color: ${(props) =>
      props.$theme.name === 'dark' ? '#404040' : '#f5f5f5'};
  }

  &:focus {
    outline: none;
    background-color: ${(props) =>
      props.$theme.name === 'dark' ? '#404040' : '#f5f5f5'};
    box-shadow: inset 0 0 0 2px
      ${(props) => (props.$theme.name === 'dark' ? '#667eea' : '#667eea')};
  }
`;

const MenuItemIcon = styled.span`
  font-size: 20px;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
`;

const MenuItemText = styled.span`
  font-size: 14px;
  font-weight: 500;
`;

export default FloatingAssistButton;
