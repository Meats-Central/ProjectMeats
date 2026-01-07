/**
 * ProfileDropdown component for user profile actions.
 */
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { config } from '../../config/runtime';
import { Theme } from '../../config/theme';

interface ProfileDropdownProps {
  // No props needed currently
}

const ProfileDropdown: React.FC<ProfileDropdownProps> = () => {
  const { user, logout, isAdmin, loading } = useAuth();
  const { theme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      // Redirect to login page or refresh
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleProfileClick = () => {
    navigate('/profile');
    setIsOpen(false);
  };

  const handleSettingsClick = () => {
    navigate('/settings');
    setIsOpen(false);
  };

  const handleAdminClick = () => {
    // Open Django admin in new tab
    // In deployed environments, admin is proxied through the same domain as the frontend
    // In local dev (localhost), use the API base URL
    
    const hostname = window.location.hostname;
    let adminUrl: string;
    
    if (hostname.includes('localhost')) {
      // Local dev: use backend directly
      const baseBackendUrl = config.API_BASE_URL.replace('/api/v1', '');
      adminUrl = `${baseBackendUrl}/admin/`;
    } else {
      // Deployed environments: admin is proxied through same domain
      const protocol = window.location.protocol;
      adminUrl = `${protocol}//${hostname}/admin/`;
    }
    
    // Use window.location.href for more reliable navigation
    window.location.href = adminUrl;
    setIsOpen(false);
  };

  const handleLoginClick = () => {
    navigate('/login');
    setIsOpen(false);
  };

  const handleSignUpClick = () => {
    navigate('/signup');
    setIsOpen(false);
  };

  if (loading) {
    return (
      <DropdownContainer ref={dropdownRef}>
        <UserMenu onClick={() => setIsOpen(!isOpen)} $isOpen={isOpen} $theme={theme}>
          <UserAvatar $theme={theme}>⏳</UserAvatar>
          <UserName $theme={theme}>Loading...</UserName>
          <DropdownArrow $isOpen={isOpen} $theme={theme}>▼</DropdownArrow>
        </UserMenu>
      </DropdownContainer>
    );
  }

  if (!user) {
    return (
      <DropdownContainer ref={dropdownRef}>
        <UserMenu onClick={() => setIsOpen(!isOpen)} $isOpen={isOpen} $theme={theme}>
          <UserAvatar $theme={theme}>👤</UserAvatar>
          <UserName $theme={theme}>Guest</UserName>
          <DropdownArrow $isOpen={isOpen} $theme={theme}>▼</DropdownArrow>
        </UserMenu>

        {isOpen && (
          <DropdownMenu $theme={theme}>
            <DropdownItem onClick={handleLoginClick} $theme={theme}>
              <ItemIcon>🔐</ItemIcon>
              Login
            </DropdownItem>

            <DropdownDivider $theme={theme} />

            <DropdownItem onClick={handleSignUpClick} $theme={theme}>
              <ItemIcon>📝</ItemIcon>
              Sign Up
            </DropdownItem>
          </DropdownMenu>
        )}
      </DropdownContainer>
    );
  }

  const displayName =
    user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.username;

  return (
    <DropdownContainer ref={dropdownRef}>
      <UserMenu onClick={() => setIsOpen(!isOpen)} $isOpen={isOpen} $theme={theme}>
        <UserAvatar $theme={theme}>👤</UserAvatar>
        <UserName $theme={theme}>{displayName}</UserName>
        <DropdownArrow $isOpen={isOpen} $theme={theme}>▼</DropdownArrow>
      </UserMenu>

      {isOpen && (
        <DropdownMenu $theme={theme}>
          <DropdownItem onClick={handleProfileClick} $theme={theme}>
            <ItemIcon>👤</ItemIcon>
            View Profile
          </DropdownItem>

          <DropdownItem onClick={handleSettingsClick} $theme={theme}>
            <ItemIcon>⚙️</ItemIcon>
            Settings
          </DropdownItem>

          {isAdmin && (
            <DropdownItem onClick={handleAdminClick} $theme={theme}>
              <ItemIcon>🔧</ItemIcon>
              View as Admin
            </DropdownItem>
          )}

          <DropdownDivider $theme={theme} />

          <DropdownItem onClick={handleLogout} $isLogout $theme={theme}>
            <ItemIcon>🚪</ItemIcon>
            Logout
          </DropdownItem>
        </DropdownMenu>
      )}
    </DropdownContainer>
  );
};

const DropdownContainer = styled.div`
  position: relative;
`;

const UserMenu = styled.div<{ $isOpen?: boolean; $theme: Theme }>`
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
  background-color: ${(props) => (props.$isOpen ? props.$theme.colors.surfaceHover : 'transparent')};

  &:hover {
    background-color: ${(props) => props.$theme.colors.surfaceHover};
  }
`;

const UserAvatar = styled.div<{ $theme: Theme }>`
  font-size: 20px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${(props) => props.$theme.colors.borderLight};
  border-radius: 50%;
`;

const UserName = styled.span<{ $theme: Theme }>`
  font-weight: 500;
  color: ${(props) => props.$theme.colors.textPrimary};
  font-size: 14px;
`;

const DropdownArrow = styled.span<{ $isOpen: boolean; $theme: Theme }>`
  font-size: 10px;
  color: ${(props) => props.$theme.colors.textSecondary};
  transform: ${(props) => (props.$isOpen ? 'rotate(180deg)' : 'rotate(0deg)')};
  transition: transform 0.2s ease;
`;

const DropdownMenu = styled.div<{ $theme: Theme }>`
  position: absolute;
  top: 100%;
  right: 0;
  background: ${(props) => props.$theme.colors.surface};
  border: 1px solid ${(props) => props.$theme.colors.border};
  border-radius: 8px;
  box-shadow: 0 4px 12px ${(props) => props.$theme.colors.shadowMedium};
  min-width: 180px;
  z-index: 1000;
  padding: 8px 0;
  margin-top: 4px;

  &::before {
    content: '';
    position: absolute;
    top: -6px;
    right: 16px;
    width: 12px;
    height: 12px;
    background: ${(props) => props.$theme.colors.surface};
    border: 1px solid ${(props) => props.$theme.colors.border};
    border-bottom: none;
    border-right: none;
    transform: rotate(45deg);
  }
`;

const DropdownItem = styled.button<{ $isLogout?: boolean; $theme: Theme }>`
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: ${(props) => (props.$isLogout ? props.$theme.colors.error : props.$theme.colors.textPrimary)};
  transition: background-color 0.2s ease;

  &:hover {
    background-color: ${(props) => props.$theme.colors.surfaceHover};
  }

  &:focus {
    outline: none;
    background-color: ${(props) => props.$theme.colors.surfaceHover};
  }
`;

const ItemIcon = styled.span`
  font-size: 16px;
  width: 16px;
  text-align: center;
`;

const DropdownDivider = styled.hr<{ $theme: Theme }>`
  border: none;
  border-top: 1px solid ${(props) => props.$theme.colors.border};
  margin: 8px 0;
`;

export default ProfileDropdown;
