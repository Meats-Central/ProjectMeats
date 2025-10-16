import React, { useState } from 'react';
import styled from 'styled-components';
import ProfileDropdown from '../ProfileDropdown';
import { useTheme } from '../../contexts/ThemeContext';

interface HeaderProps {
  // No props needed currently
}

const Header: React.FC<HeaderProps> = () => {
  const { theme, toggleTheme } = useTheme();
  const [showQuickMenu, setShowQuickMenu] = useState(false);

  const quickMenuItems = [
    { label: 'New Supplier', path: '/suppliers/new', icon: '🏭' },
    { label: 'New Customer', path: '/customers/new', icon: '👥' },
    { label: 'New PO', path: '/purchase-orders/new', icon: '📋' },
    { label: 'New Contact', path: '/contacts/new', icon: '📞' },
  ];

  return (
    <HeaderContainer>
      <HeaderTitle>Business Management System</HeaderTitle>
      <HeaderActions>
        <QuickMenuContainer>
          <QuickMenuButton
            onClick={() => setShowQuickMenu(!showQuickMenu)}
            title="Quick actions"
          >
            ➕
          </QuickMenuButton>
          {showQuickMenu && (
            <QuickMenuDropdown>
              {quickMenuItems.map((item) => (
                <QuickMenuItem
                  key={item.path}
                  onClick={() => {
                    window.location.href = item.path;
                    setShowQuickMenu(false);
                  }}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </QuickMenuItem>
              ))}
            </QuickMenuDropdown>
          )}
        </QuickMenuContainer>
        <ThemeToggleButton onClick={toggleTheme} title="Toggle dark/light mode">
          {theme === 'light' ? '🌙' : '☀️'}
        </ThemeToggleButton>
        <NotificationButton title="Notifications">🔔</NotificationButton>
        <ProfileDropdown />
      </HeaderActions>
    </HeaderContainer>
  );
};

const HeaderContainer = styled.header`
  height: 60px;
  background: white;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
`;

const HeaderTitle = styled.h1`
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const NotificationButton = styled.button`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #f8f9fa;
  }
`;

const ThemeToggleButton = styled.button`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #f8f9fa;
  }
`;

const QuickMenuContainer = styled.div`
  position: relative;
`;

const QuickMenuButton = styled.button`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #f8f9fa;
  }
`;

const QuickMenuDropdown = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  z-index: 1000;
  overflow: hidden;
`;

const QuickMenuItem = styled.button`
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #2c3e50;
  transition: background-color 0.2s;

  &:hover {
    background-color: #f8f9fa;
  }

  span:first-child {
    font-size: 18px;
  }
`;

export default Header;
