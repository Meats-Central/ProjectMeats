/**
 * Main App Component
 * 
 * ProjectMeats3 React Application
 * Enhanced AI Assistant with Copilot-style UI
 */
import React, { useState } from 'react';
import styled from 'styled-components';
import ChatWindow from './components/ChatInterface/ChatWindow';
import { ChatSession } from './types';

const App: React.FC = () => {
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);

  return (
    <AppContainer>
      <Header>
        <Logo>
          <LogoIcon>🥩</LogoIcon>
          <LogoText>ProjectMeats3 test</LogoText>
        </Logo>
        <HeaderSubtitle>AI-Powered Meat Market Operations</HeaderSubtitle>
      </Header>
      
      <MainContent>
        <ChatWindow 
          sessionId={currentSession?.id}
          onSessionChange={setCurrentSession}
        />
      </MainContent>
    </AppContainer>
  );
};

// Styled Components
const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f9fafb;
`;

const Header = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
`;

const LogoIcon = styled.span`
  font-size: 28px;
`;

const LogoText = styled.h1`
  font-size: 24px;
  font-weight: 700;
  margin: 0;
`;

const HeaderSubtitle = styled.p`
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
  color: rgba(255, 255, 255, 0.9);
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  overflow: hidden;
`;

export default App;