/**
 * MessageList Component
 *
 * Displays a list of chat messages with proper formatting and styling.
 * Enhanced to support retry functionality for failed messages.
 */
import React from 'react';
import styled from 'styled-components';
import { ChatMessage } from '../../types';

interface MessageListProps {
  messages: ChatMessage[];
  onRetry?: (message: ChatMessage) => void;
}

interface MessageMetadataType {
  model?: string;
  processing_time?: number;
  tokens_used?: number;
}

const MessageList: React.FC<MessageListProps> = ({ messages, onRetry }) => {
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    return date.toLocaleDateString();
  };

  const getMessageIcon = (type: string): string => {
    switch (type) {
      case 'user':
        return '👤';
      case 'assistant':
        return '🤖';
      case 'system':
        return '⚙️';
      case 'document':
        return '📄';
      default:
        return '💬';
    }
  };

  const getStatusIcon = (status?: string): string | null => {
    switch (status) {
      case 'sending':
        return '⏳';
      case 'failed':
        return '❌';
      default:
        return null;
    }
  };

  const handleRetry = (message: ChatMessage) => {
    if (onRetry) {
      onRetry(message);
    }
  };

  return (
    <MessageContainer>
      {messages.map((message) => (
        <MessageItem key={message.id} messageType={message.message_type} $status={message.status}>
          <MessageHeader>
            <MessageTypeIcon>{getMessageIcon(message.message_type)}</MessageTypeIcon>
            <MessageInfo>
              <MessageType>
                {message.message_type === 'user'
                  ? 'You'
                  : message.message_type === 'assistant'
                    ? 'AI Assistant'
                    : message.message_type === 'system'
                      ? 'System'
                      : 'Document'}
              </MessageType>
              <MessageTime>{formatTimestamp(message.created_on)}</MessageTime>
              {getStatusIcon(message.status) && (
                <StatusIndicator $status={message.status}>
                  {getStatusIcon(message.status)}
                </StatusIndicator>
              )}
            </MessageInfo>
          </MessageHeader>

          <MessageContent>{message.content}</MessageContent>

          {/* Show retry button for failed messages */}
          {message.status === 'failed' && onRetry && (
            <RetryContainer>
              <RetryMessage>Failed to send message</RetryMessage>
              <RetryButton onClick={() => handleRetry(message)}>
                <RetryIcon>🔄</RetryIcon>
                Try Again
              </RetryButton>
            </RetryContainer>
          )}

          {message.metadata && Object.keys(message.metadata).length > 0 && (
            <MessageMetadata>
              {(message.metadata as MessageMetadataType).model && (
                <MetadataItem>
                  Model: {(message.metadata as MessageMetadataType).model}
                </MetadataItem>
              )}
              {(message.metadata as MessageMetadataType).processing_time && (
                <MetadataItem>
                  Processing: {(message.metadata as MessageMetadataType).processing_time}s
                </MetadataItem>
              )}
              {(message.metadata as MessageMetadataType).tokens_used && (
                <MetadataItem>
                  Tokens: {(message.metadata as MessageMetadataType).tokens_used}
                </MetadataItem>
              )}
            </MessageMetadata>
          )}
        </MessageItem>
      ))}
    </MessageContainer>
  );
};

// Styled Components
const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MessageItem = styled.div<{ messageType: string; $status?: string }>`
  padding: 16px;
  border-radius: 12px;
  background: ${(props) =>
    props.$status === 'failed'
      ? '#fef2f2'
      : props.messageType === 'user'
        ? '#e0f2fe'
        : props.messageType === 'assistant'
          ? '#f8fafc'
          : '#fff7ed'};
  border: 1px solid
    ${(props) =>
      props.$status === 'failed'
        ? '#fecaca'
        : props.messageType === 'user'
          ? '#b3e5fc'
          : props.messageType === 'assistant'
            ? '#e2e8f0'
            : '#fed7aa'};
  opacity: ${(props) => (props.$status === 'sending' ? 0.7 : 1)};

  ${(props) =>
    props.messageType === 'user' &&
    `
    margin-left: 20%;
  `}

  ${(props) =>
    props.messageType === 'assistant' &&
    `
    margin-right: 20%;
  `}
`;

const MessageHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

const MessageTypeIcon = styled.span`
  font-size: 16px;
`;

const MessageInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
`;

const MessageType = styled.span`
  font-weight: 600;
  font-size: 14px;
  color: #374151;
`;

const MessageTime = styled.span`
  font-size: 12px;
  color: #9ca3af;
`;

const StatusIndicator = styled.span<{ $status?: string }>`
  font-size: 12px;
  margin-left: 4px;
`;

const MessageContent = styled.div`
  font-size: 14px;
  line-height: 1.6;
  color: #111827;
  white-space: pre-wrap;
  word-wrap: break-word;
`;

const RetryContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #fecaca;
`;

const RetryMessage = styled.span`
  font-size: 12px;
  color: #dc2626;
`;

const RetryButton = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #b91c1c;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0) scale(0.98);
  }
`;

const RetryIcon = styled.span`
  font-size: 12px;
`;

const MessageMetadata = styled.div`
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
`;

const MetadataItem = styled.span`
  font-size: 11px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
`;

export default MessageList;
