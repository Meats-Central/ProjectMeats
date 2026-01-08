import React, { useState } from 'react';
import styled from 'styled-components';
import ChatWindow from '../components/ChatInterface/ChatWindow';
import { ChatSession } from '../types';

const AIAssistant: React.FC = () => {
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);

  return (
    <Container>
      <Header>
        <Title>AI Assistant</Title>
        <Subtitle>
          Get help with your business operations, ask questions, and receive intelligent insights
        </Subtitle>
      </Header>

      <ChatContainer>
        <ChatWindow sessionId={currentSession?.id} onSessionChange={setCurrentSession} />
      </ChatContainer>
    </Container>
  );
};

const Container = styled.div`
  max-width: 1200px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  margin-bottom: 20px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: rgb(var(--color-text-primary));
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: #6c757d;
  margin: 0;
`;

const ChatContainer = styled.div`
  flex: 1;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-surface-foreground));
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  overflow: hidden;
`;

export default AIAssistant;
