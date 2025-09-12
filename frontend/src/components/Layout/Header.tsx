import React from 'react';
import styled from 'styled-components';
import ProfileDropdown from '../ProfileDropdown';

interface HeaderProps {
  // No props needed currently
}

const Header: React.FC<HeaderProps> = () => {
  return (
    <HeaderContainer>
      <HeaderTitle>Business Management System</HeaderTitle>
      <HeaderActions>
        <NotificationButton>🔔</NotificationButton>
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

export default Header;
