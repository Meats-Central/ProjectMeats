import React, { useState } from 'react';
import styled from 'styled-components';
import ProfileDropdown from '../ProfileDropdown';
import { useTheme } from '../../contexts/ThemeContext';
import { useNavigate } from 'react-router-dom';
import { Theme } from '../../config/theme';

interface HeaderProps {
  // No props needed currently
}

const Header: React.FC<HeaderProps> = () => {
  const { theme, themeName, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showQuickMenu, setShowQuickMenu] = useState(false);

  const quickMenuItems = [
    { label: 'New Supplier', path: '/suppliers/new', icon: '🏭' },
    { label: 'New Customer', path: '/customers/new', icon: '👥' },
    { label: 'New Purchase Order', path: '/purchase-orders/new', icon: '📋' },
    { label: 'View Dashboard', path: '/', icon: '📊' },
  ];

  const handleQuickMenuClick = (path: string) => {
    navigate(path);
    setShowQuickMenu(false);
  };

  return (
    <HeaderContainer $theme={theme}>
      <HeaderTitle $theme={theme}>Business Management System</HeaderTitle>
      <HeaderActions>
        {/* Quick Menu */}
        <QuickMenuContainer>
          <QuickMenuButton
            onClick={() => setShowQuickMenu(!showQuickMenu)}
            $theme={theme}
            title="Quick Actions"
          >
            ⚡
          </QuickMenuButton>
          {showQuickMenu && (
            <QuickMenuDropdown $theme={theme}>
              {quickMenuItems.map((item) => (
                <QuickMenuItem
                  key={item.path}
                  onClick={() => handleQuickMenuClick(item.path)}
                  $theme={theme}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </QuickMenuItem>
              ))}
            </QuickMenuDropdown>
          )}
        </QuickMenuContainer>

        {/* Theme Toggle */}
        <ThemeToggleButton
          onClick={toggleTheme}
          $theme={theme}
          title={`Switch to ${themeName === 'light' ? 'dark' : 'light'} mode`}
        >
          {themeName === 'light' ? '🌙' : '☀️'}
        </ThemeToggleButton>

        {/* Notifications */}
        <NotificationButton $theme={theme} title="Notifications">
          🔔
        </NotificationButton>

        {/* Profile */}
        <ProfileDropdown />
      </HeaderActions>
    </HeaderContainer>
  );
};

const HeaderContainer = styled.header<{ $theme: Theme }>`
  height: 60px;
  background: ${(props) => props.$theme.colors.headerBackground};
  border-bottom: 1px solid ${(props) => props.$theme.colors.headerBorder};
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  box-shadow: 0 2px 4px ${(props) => props.$theme.colors.shadow};
  transition: all 0.3s ease;
`;

const HeaderTitle = styled.h1<{ $theme: Theme }>`
  font-size: 20px;
  font-weight: 600;
  color: ${(props) => props.$theme.colors.headerText};
  margin: 0;
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const QuickMenuContainer = styled.div`
  position: relative;
`;

const QuickMenuButton = styled.button<{ $theme: Theme }>`
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
  color: ${(props) => props.$theme.colors.textPrimary};

  &:hover {
    background-color: ${(props) => props.$theme.colors.surfaceHover};
  }
`;

const QuickMenuDropdown = styled.div<{ $theme: Theme }>`
  position: absolute;
  top: 45px;
  right: 0;
  min-width: 220px;
  background: ${(props) => props.$theme.colors.surface};
  border: 1px solid ${(props) => props.$theme.colors.border};
  border-radius: 8px;
  box-shadow: 0 4px 12px ${(props) => props.$theme.colors.shadowMedium};
  z-index: 1000;
  overflow: hidden;
`;

const QuickMenuItem = styled.button<{ $theme: Theme }>`
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: none;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  color: ${(props) => props.$theme.colors.textPrimary};
  font-size: 14px;
  transition: background-color 0.2s;

  &:hover {
    background-color: ${(props) => props.$theme.colors.surfaceHover};
  }

  span:first-child {
    font-size: 18px;
  }
`;

const ThemeToggleButton = styled.button<{ $theme: Theme }>`
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
  color: ${(props) => props.$theme.colors.textPrimary};

  &:hover {
    background-color: ${(props) => props.$theme.colors.surfaceHover};
    transform: scale(1.1);
  }
`;

const NotificationButton = styled.button<{ $theme: Theme }>`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
  color: ${(props) => props.$theme.colors.textPrimary};

  &:hover {
    background-color: ${(props) => props.$theme.colors.surfaceHover};
  }
`;

export default Header;
