import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import styled from 'styled-components';
import Sidebar from './Sidebar';
import Header from './Header';
import Breadcrumb from '../Navigation/Breadcrumb';
import Omnibox from '../AIAssistant/Omnibox';
import { useNavigation } from '../../contexts/NavigationContext';

const Layout: React.FC = () => {
  const { sidebarOpen, setSidebarOpen } = useNavigation();
  const [showOmnibox, setShowOmnibox] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Global keyboard shortcut for Omnibox (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowOmnibox(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleOmniboxSubmit = (command: string) => {
    // For now, just log the command. In a real app, this would be sent to the AI service
    console.log('AI Command:', command);
    // You could also show a notification or redirect to a specific page based on the command
  };

  return (
    <LayoutContainer>
      <Sidebar isOpen={sidebarOpen} onToggle={toggleSidebar} />
      <MainArea $sidebarOpen={sidebarOpen}>
        <Header />
        <Content>
          <Breadcrumb />
          <Outlet />
        </Content>
      </MainArea>
      <Omnibox
        isOpen={showOmnibox}
        onClose={() => setShowOmnibox(false)}
        onSubmit={handleOmniboxSubmit}
      />
      <KeyboardShortcutHint>
        Press <kbd>Ctrl+K</kbd> (or <kbd>⌘K</kbd>) to open AI Command Center
      </KeyboardShortcutHint>
    </LayoutContainer>
  );
};

const LayoutContainer = styled.div`
  display: flex;
  height: 100vh;
`;

const MainArea = styled.div<{ $sidebarOpen: boolean }>`
  flex: 1;
  margin-left: ${props => props.$sidebarOpen ? '250px' : '60px'};
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
`;

const Content = styled.main`
  flex: 1;
  padding: 30px;
  background-color: #f8f9fa;
  overflow-y: auto;
`;

const KeyboardShortcutHint = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  opacity: 0.7;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }

  kbd {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 3px;
    padding: 2px 4px;
    font-family: inherit;
    font-size: 11px;
  }
`;

export default Layout;
