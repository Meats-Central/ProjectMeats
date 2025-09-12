/**
 * ProfileDropdown component for user profile actions.
 */
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../../contexts/AuthContext';

interface ProfileDropdownProps {
  // No props needed currently
}

const ProfileDropdown: React.FC<ProfileDropdownProps> = () => {
  const { user, logout, isAdmin } = useAuth();
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
    const adminUrl = window.location.origin.replace(':3001', ':8000') + '/admin/';
    window.open(adminUrl, '_blank');
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

  if (!user) {
    return (
      <DropdownContainer ref={dropdownRef}>
        <UserMenu onClick={() => setIsOpen(!isOpen)} $isOpen={isOpen}>
          <UserAvatar>👤</UserAvatar>
          <UserName>Guest</UserName>
          <DropdownArrow $isOpen={isOpen}>▼</DropdownArrow>
        </UserMenu>

        {isOpen && (
          <DropdownMenu>
            <DropdownItem onClick={handleLoginClick}>
              <ItemIcon>🔐</ItemIcon>
              Login
            </DropdownItem>
            
            <DropdownDivider />
            
            <DropdownItem onClick={handleSignUpClick}>
              <ItemIcon>📝</ItemIcon>
              Sign Up
            </DropdownItem>
          </DropdownMenu>
        )}
      </DropdownContainer>
    );
  }

  const displayName = user.first_name && user.last_name 
    ? `${user.first_name} ${user.last_name}` 
    : user.username;

  return (
    <DropdownContainer ref={dropdownRef}>
      <UserMenu onClick={() => setIsOpen(!isOpen)} $isOpen={isOpen}>
        <UserAvatar>👤</UserAvatar>
        <UserName>{displayName}</UserName>
        <DropdownArrow $isOpen={isOpen}>▼</DropdownArrow>
      </UserMenu>

      {isOpen && (
        <DropdownMenu>
          <DropdownItem onClick={handleProfileClick}>
            <ItemIcon>👤</ItemIcon>
            View Profile
          </DropdownItem>
          
          <DropdownItem onClick={handleSettingsClick}>
            <ItemIcon>⚙️</ItemIcon>
            Settings
          </DropdownItem>

          {isAdmin && (
            <DropdownItem onClick={handleAdminClick}>
              <ItemIcon>🔧</ItemIcon>
              View as Admin
            </DropdownItem>
          )}

          <DropdownDivider />

          <DropdownItem onClick={handleLogout} $isLogout>
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

const UserMenu = styled.div<{ $isOpen?: boolean }>`
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
  background-color: ${props => props.$isOpen ? '#f8f9fa' : 'transparent'};

  &:hover {
    background-color: #f8f9fa;
  }
`;

const UserAvatar = styled.div`
  font-size: 20px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e9ecef;
  border-radius: 50%;
`;

const UserName = styled.span`
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
`;

const DropdownArrow = styled.span<{ $isOpen: boolean }>`
  font-size: 10px;
  color: #6c757d;
  transform: ${props => props.$isOpen ? 'rotate(180deg)' : 'rotate(0deg)'};
  transition: transform 0.2s ease;
`;

const DropdownMenu = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
    background: white;
    border: 1px solid #e9ecef;
    border-bottom: none;
    border-right: none;
    transform: rotate(45deg);
  }
`;

const DropdownItem = styled.button<{ $isLogout?: boolean }>`
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: ${props => props.$isLogout ? '#dc3545' : '#2c3e50'};
  transition: background-color 0.2s ease;

  &:hover {
    background-color: ${props => props.$isLogout ? '#fff5f5' : '#f8f9fa'};
  }

  &:focus {
    outline: none;
    background-color: ${props => props.$isLogout ? '#fff5f5' : '#f8f9fa'};
  }
`;

const ItemIcon = styled.span`
  font-size: 16px;
  width: 16px;
  text-align: center;
`;

const DropdownDivider = styled.hr`
  border: none;
  border-top: 1px solid #e9ecef;
  margin: 8px 0;
`;

export default ProfileDropdown;