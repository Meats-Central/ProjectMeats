/**
 * Activity Feed Component
 * 
 * Universal widget for displaying activity logs/notes for any entity.
 * Used in Cockpit Call Log, Supplier pages, Customer pages, Order details, etc.
 * 
 * Features:
 * - Fetches activity logs from backend API
 * - Displays in chronological timeline format
 * - Shows metadata (created by, timestamp)
 * - Supports adding new activity logs
 * - Fully theme-compliant (no hardcoded colors)
 * 
 * Usage:
 *   <ActivityFeed entityType="supplier" entityId={123} />
 *   <ActivityFeed entityType="customer" entityId={456} showCreateForm />
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { formatToLocal } from '../../utils/formatters';
import { apiClient } from '../../services/apiService';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface ActivityLog {
  id: number;
  tenant: string;
  entity_type: string;
  entity_id: number;
  title: string;
  content: string;
  created_by: number | null;
  created_by_name: string;
  created_on: string;
  updated_on: string;
}

interface ActivityFeedProps {
  entityType: 'supplier' | 'customer' | 'plant' | 'purchase_order' | 'sales_order' | 'carrier' | 'product' | 'invoice' | 'contact';
  entityId: number;
  showCreateForm?: boolean;
  maxHeight?: string;
}

// ============================================================================
// Styled Components (Theme-Compliant)
// ============================================================================

const FeedContainer = styled.div`
  width: 100%;
`;

const FeedHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const FeedTitle = styled.h3`
  font-size: 24px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0;
`;

const AddButton = styled.button`
  padding: 0.5rem 1rem;
  background: rgb(var(--color-primary));
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const TimelineContainer = styled.div<{ maxHeight?: string }>`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: ${props => props.maxHeight || 'none'};
  overflow-y: auto;
  padding-right: 0.5rem;

  /* Custom scrollbar for dark mode compatibility */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgb(var(--color-surface));
  }

  &::-webkit-scrollbar-thumb {
    background: rgb(var(--color-border));
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgb(var(--color-text-secondary));
  }
`;

const ActivityCard = styled.div`
  position: relative;
  padding: 1rem;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  transition: border-color 0.2s ease;

  &:hover {
    border-color: rgb(var(--color-primary));
  }

  /* Timeline connector */
  &:not(:last-child)::after {
    content: '';
    position: absolute;
    left: -12px;
    top: 50%;
    width: 2px;
    height: calc(100% + 1rem);
    background: rgb(var(--color-border));
  }
`;

const ActivityHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
`;

const ActivityTitle = styled.h4`
  font-size: 1rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0;
`;

const ActivityMeta = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
`;

const MetaText = styled.span`
  font-size: 0.75rem;
  color: rgb(var(--color-text-secondary));
`;

const ActivityContent = styled.p`
  font-size: 0.875rem;
  line-height: 1.6;
  color: rgb(var(--color-text-primary));
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
`;

const CreateForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
`;

const FormInput = styled.input`
  padding: 0.5rem;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-text-primary));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-sm);
  font-size: 0.875rem;

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }
`;

const FormTextarea = styled.textarea`
  padding: 0.5rem;
  background: rgb(var(--color-surface));
  color: rgb(var(--color-text-primary));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  min-height: 100px;
  resize: vertical;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: rgb(var(--color-primary));
  }
`;

const FormActions = styled.div`
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
`;

const SubmitButton = styled.button`
  padding: 0.5rem 1rem;
  background: rgb(var(--color-primary));
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const CancelButton = styled.button`
  padding: 0.5rem 1rem;
  background: transparent;
  color: rgb(var(--color-text-secondary));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgb(var(--color-surface-hover));
    border-color: rgb(var(--color-text-secondary));
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem 1rem;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const LoadingState = styled.div`
  text-align: center;
  padding: 2rem 1rem;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const ErrorState = styled.div`
  padding: 1rem;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: var(--radius-md);
  color: rgb(220, 38, 38);
  font-size: 0.875rem;
`;

// ============================================================================
// Component
// ============================================================================

export const ActivityFeed: React.FC<ActivityFeedProps> = ({
  entityType,
  entityId,
  showCreateForm = false,
  maxHeight = '600px'
}) => {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ title: '', content: '' });
  const [submitting, setSubmitting] = useState(false);

  // Fetch activity logs on mount and when entity changes
  useEffect(() => {
    fetchActivities();
  }, [entityType, entityId]);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get('cockpit/activity-logs/', {
        params: {
          entity_type: entityType,
          entity_id: entityId,
        },
      });

      setActivities(response.data.results || response.data);
    } catch (err: any) {
      console.error('Failed to fetch activity logs:', err);
      setError(err.response?.data?.detail || 'Failed to load activity logs');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.content.trim()) {
      return;
    }

    try {
      setSubmitting(true);
      
      const response = await apiClient.post('cockpit/activity-logs/', {
        entity_type: entityType,
        entity_id: entityId,
        title: formData.title.trim() || 'Note',
        content: formData.content.trim(),
      });

      // Add new activity to the top of the list
      setActivities([response.data, ...activities]);
      
      // Reset form
      setFormData({ title: '', content: '' });
      setShowForm(false);
    } catch (err: any) {
      console.error('Failed to create activity log:', err);
      setError(err.response?.data?.detail || 'Failed to create activity log');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    setFormData({ title: '', content: '' });
    setShowForm(false);
  };

  return (
    <FeedContainer>
      <FeedHeader>
        <FeedTitle>Activity Log</FeedTitle>
        {showCreateForm && !showForm && (
          <AddButton onClick={() => setShowForm(true)}>
            + Add Note
          </AddButton>
        )}
      </FeedHeader>

      {/* Create Form */}
      {showForm && (
        <CreateForm onSubmit={handleSubmit}>
          <FormInput
            type="text"
            placeholder="Title (optional)"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            disabled={submitting}
          />
          <FormTextarea
            placeholder="Enter your note..."
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            disabled={submitting}
            required
          />
          <FormActions>
            <CancelButton type="button" onClick={handleCancel} disabled={submitting}>
              Cancel
            </CancelButton>
            <SubmitButton type="submit" disabled={submitting || !formData.content.trim()}>
              {submitting ? 'Saving...' : 'Save Note'}
            </SubmitButton>
          </FormActions>
        </CreateForm>
      )}

      {/* Loading State */}
      {loading && (
        <LoadingState>Loading activity logs...</LoadingState>
      )}

      {/* Error State */}
      {error && (
        <ErrorState>{error}</ErrorState>
      )}

      {/* Timeline */}
      {!loading && !error && (
        <TimelineContainer maxHeight={maxHeight}>
          {activities.length === 0 ? (
            <EmptyState>
              No activity logs yet.
              {showCreateForm && ' Click "Add Note" to create the first one.'}
            </EmptyState>
          ) : (
            activities.map((activity) => (
              <ActivityCard key={activity.id}>
                <ActivityHeader>
                  <ActivityTitle>
                    {activity.title || 'Note'}
                  </ActivityTitle>
                  <ActivityMeta>
                    <MetaText>
                      {activity.created_by_name || 'Unknown User'}
                    </MetaText>
                    <MetaText>
                      {formatToLocal(activity.created_on)}
                    </MetaText>
                  </ActivityMeta>
                </ActivityHeader>
                <ActivityContent>{activity.content}</ActivityContent>
              </ActivityCard>
            ))
          )}
        </TimelineContainer>
      )}
    </FeedContainer>
  );
};

export default ActivityFeed;
