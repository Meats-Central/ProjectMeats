import React, { useState } from 'react';
import styled from 'styled-components';
import ProfileDropdown from '../ProfileDropdown';
import { useTheme } from '../../contexts/ThemeContext';
import { useNavigate } from 'react-router-dom';
import { Theme } from '../../config/theme';

interface HeaderProps {
  // No props needed currently
}

// Search icon SVG component
const SearchIcon: React.FC = () => (
  <svg 
    width="16" 
    height="16" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
  >
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.3-4.3" />
  </svg>
);

const Header: React.FC<HeaderProps> = () => {
  const { theme, themeName, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showQuickMenu, setShowQuickMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Get tenant name from localStorage
  const tenantName = localStorage.getItem('tenantName') || 'Meats Central';

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

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // TODO: Implement global search functionality
      console.log('Search query:', searchQuery);
      // Navigate to search results page or filter current page
      // navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <HeaderContainer $theme={theme}>
      <HeaderTitle $theme={theme}>{tenantName}</HeaderTitle>
      
      {/* Global Search */}
      <SearchForm onSubmit={handleSearchSubmit}>
        <SearchInputWrapper $theme={theme}>
          <SearchIconWrapper $theme={theme}>
            <SearchIcon />
          </SearchIconWrapper>
          <SearchInput
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            $theme={theme}
            aria-label="Global search"
          />
        </SearchInputWrapper>
      </SearchForm>
      
      <HeaderActions>
        {/* Quick Menu */}
        <QuickMenuContainer>
          <QuickMenuButton
            onClick={() => setShowQuickMenu(!showQuickMenu)}
            $theme={theme}
            title="Quick Actions"
            aria-label="Quick Actions Menu"
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
          aria-label={`Switch to ${themeName === 'light' ? 'dark' : 'light'} mode`}
        >
          {themeName === 'light' ? '🌙' : '☀️'}
        </ThemeToggleButton>

        {/* Notifications */}
        <NotificationButton $theme={theme} title="Notifications" aria-label="Notifications">
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
  gap: 20px;
`;

const HeaderTitle = styled.h1<{ $theme: Theme }>`
  font-size: 20px;
  font-weight: 600;
  color: ${(props) => props.$theme.colors.headerText};
  margin: 0;
  white-space: nowrap;
`;

const SearchForm = styled.form`
  flex: 1;
  max-width: 500px;
  display: flex;
  align-items: center;
`;

const SearchInputWrapper = styled.div<{ $theme: Theme }>`
  display: flex;
  align-items: center;
  width: 100%;
  background: ${(props) => props.$theme.colors.surface};
  border-radius: 8px;
  padding: 8px 12px;
  gap: 8px;
  border: 1px solid ${(props) => props.$theme.colors.border};
  transition: all 0.2s ease;

  &:focus-within {
    border-color: ${(props) => props.$theme.colors.primary};
    box-shadow: 0 0 0 3px ${(props) => props.$theme.colors.primary}20;
  }
`;

const SearchIconWrapper = styled.div<{ $theme: Theme }>`
  color: ${(props) => props.$theme.colors.textSecondary};
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SearchInput = styled.input<{ $theme: Theme }>`
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: ${(props) => props.$theme.colors.textPrimary};
  
  &::placeholder {
    color: ${(props) => props.$theme.colors.textSecondary};
  }
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
