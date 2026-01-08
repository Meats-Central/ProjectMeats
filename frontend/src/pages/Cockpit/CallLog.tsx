/**
 * Cockpit Call Log Page
 * 
 * Split-pane layout for managing scheduled calls and activity tracking.
 * 
 * Layout:
 * - Left Pane (40%): Calendar view of scheduled calls
 * - Right Pane (60%): Activity feed filtered by selected entity
 * 
 * Features:
 * - View and create scheduled calls
 * - Mark calls as completed
 * - View activity logs for any entity
 * - Add notes after calls
 * 
 * Theme Compliance:
 * - Page title: 32px, bold, rgb(var(--color-text-primary))
 * - Buttons: rgb(var(--color-primary)) background
 * - No hardcoded colors (#007bff, #2c3e50, etc.)
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ActivityFeed } from '../../components/Shared/ActivityFeed';
import { ScheduleCallModal } from '../../components/Shared/ScheduleCallModal';
import { apiClient } from '../../services/apiService';
import { formatToLocal, formatDateLocal } from '../../utils/formatters';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface ScheduledCall {
  id: number;
  tenant: string;
  entity_type: string;
  entity_id: number;
  title: string;
  description: string;
  scheduled_for: string;
  duration_minutes: number;
  call_purpose: string;
  outcome: string;
  is_completed: boolean;
  created_by: number | null;
  created_by_name: string;
  created_on: string;
  updated_on: string;
}

interface EntityFilter {
  entityType: 'supplier' | 'customer' | 'plant' | 'purchase_order' | 'sales_order' | 'carrier' | 'product' | 'invoice' | 'contact';
  entityId: number;
  entityName?: string;
}

// ============================================================================
// Styled Components (Theme-Compliant)
// ============================================================================

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1.5rem;
  background: rgb(var(--color-background));
`;

const PageHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
`;

const PageTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: rgb(var(--color-text-primary));
  margin: 0;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 0.75rem;
`;

const PrimaryButton = styled.button`
  padding: 0.75rem 1.5rem;
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

const SplitPaneContainer = styled.div`
  display: grid;
  grid-template-columns: 40% 60%;
  gap: 1.5rem;
  height: calc(100vh - 180px);
  overflow: hidden;
`;

const LeftPane = styled.div`
  display: flex;
  flex-direction: column;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  overflow: hidden;
`;

const RightPane = styled.div`
  display: flex;
  flex-direction: column;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  overflow: hidden;
`;

const PaneTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0 0 1rem 0;
`;

const CallsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  overflow-y: auto;
  padding-right: 0.5rem;

  /* Custom scrollbar */
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

const CallCard = styled.div<{ isCompleted?: boolean; isSelected?: boolean }>`
  padding: 1rem;
  background: rgb(var(--color-surface));
  border: 2px solid ${props => 
    props.isSelected 
      ? 'rgb(var(--color-primary))' 
      : 'rgb(var(--color-border))'
  };
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: ${props => props.isCompleted ? 0.6 : 1};

  &:hover {
    border-color: rgb(var(--color-primary));
    box-shadow: var(--shadow-sm);
  }
`;

const CallHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
`;

const CallTitle = styled.h3`
  font-size: 1rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  margin: 0;
  flex: 1;
`;

const CallBadge = styled.span<{ type: 'upcoming' | 'completed' | 'overdue' }>`
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  white-space: nowrap;
  
  ${props => {
    switch (props.type) {
      case 'completed':
        return `
          background: rgba(34, 197, 94, 0.1);
          color: rgb(34, 197, 94);
        `;
      case 'overdue':
        return `
          background: rgba(239, 68, 68, 0.1);
          color: rgb(239, 68, 68);
        `;
      default: // upcoming
        return `
          background: rgba(59, 130, 246, 0.1);
          color: rgb(59, 130, 246);
        `;
    }
  }}
`;

const CallDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
`;

const CallMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: rgb(var(--color-text-secondary));
`;

const CallIcon = styled.span`
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
`;

const CallActions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgb(var(--color-border));
`;

const SecondaryButton = styled.button`
  padding: 0.375rem 0.75rem;
  background: transparent;
  color: rgb(var(--color-text-secondary));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgb(var(--color-surface-hover));
    border-color: rgb(var(--color-text-secondary));
    color: rgb(var(--color-text-primary));
  }
`;

const CompleteButton = styled(SecondaryButton)`
  color: rgb(34, 197, 94);
  border-color: rgb(34, 197, 94);

  &:hover {
    background: rgba(34, 197, 94, 0.1);
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const LoadingState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  color: rgb(var(--color-text-secondary));
  font-size: 0.875rem;
`;

const ErrorState = styled.div`
  padding: 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  color: rgb(239, 68, 68);
  font-size: 0.875rem;
  margin-bottom: 1rem;
`;

const FilterInfo = styled.div`
  padding: 1rem;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: var(--radius-md);
  color: rgb(59, 130, 246);
  font-size: 0.875rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const ClearButton = styled.button`
  padding: 0.25rem 0.5rem;
  background: transparent;
  color: rgb(59, 130, 246);
  border: 1px solid rgb(59, 130, 246);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(59, 130, 246, 0.2);
  }
`;

// ============================================================================
// Component
// ============================================================================

export const CallLog: React.FC = () => {
  const [calls, setCalls] = useState<ScheduledCall[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCall, setSelectedCall] = useState<ScheduledCall | null>(null);
  const [entityFilter, setEntityFilter] = useState<EntityFilter | null>(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  useEffect(() => {
    fetchScheduledCalls();
  }, []);

  const fetchScheduledCalls = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get('cockpit/scheduled-calls/');
      const callsData = response.data.results || response.data;

      // Sort by scheduled_for (upcoming first)
      callsData.sort((a: ScheduledCall, b: ScheduledCall) => 
        new Date(a.scheduled_for).getTime() - new Date(b.scheduled_for).getTime()
      );

      setCalls(callsData);
    } catch (err: any) {
      console.error('Failed to fetch scheduled calls:', err);
      setError(err.response?.data?.detail || 'Failed to load scheduled calls');
    } finally {
      setLoading(false);
    }
  };

  const handleCallClick = (call: ScheduledCall) => {
    setSelectedCall(call);
    setEntityFilter({
      entityType: call.entity_type as any,
      entityId: call.entity_id,
      entityName: call.title,
    });
  };

  const handleCompleteCall = async (callId: number) => {
    try {
      await apiClient.patch(`cockpit/scheduled-calls/${callId}/`, {
        is_completed: true,
        outcome: 'Completed from call log',
      });

      // Update local state
      setCalls(calls.map(c => 
        c.id === callId ? { ...c, is_completed: true } : c
      ));
    } catch (err: any) {
      console.error('Failed to complete call:', err);
      alert('Failed to mark call as completed');
    }
  };

  const getCallStatus = (call: ScheduledCall): 'upcoming' | 'completed' | 'overdue' => {
    if (call.is_completed) return 'completed';
    
    const scheduledDate = new Date(call.scheduled_for);
    const now = new Date();
    
    return scheduledDate < now ? 'overdue' : 'upcoming';
  };

  const clearFilter = () => {
    setEntityFilter(null);
    setSelectedCall(null);
  };

  return (
    <PageContainer>
      <PageHeader>
        <PageTitle>Call Log & Schedule</PageTitle>
        <HeaderActions>
          <PrimaryButton onClick={() => setShowScheduleModal(true)}>
            + Schedule New Call
          </PrimaryButton>
        </HeaderActions>
      </PageHeader>

      <ScheduleCallModal
        isOpen={showScheduleModal}
        onClose={() => setShowScheduleModal(false)}
        onSuccess={fetchCalls}
      />

      <SplitPaneContainer>
        {/* Left Pane: Scheduled Calls */}
        <LeftPane>
          <PaneTitle>Scheduled Calls</PaneTitle>

          {error && <ErrorState>{error}</ErrorState>}

          {loading ? (
            <LoadingState>Loading scheduled calls...</LoadingState>
          ) : (
            <CallsList>
              {calls.length === 0 ? (
                <EmptyState>
                  <p>No scheduled calls yet.</p>
                  <p>Click "Schedule New Call" to get started.</p>
                </EmptyState>
              ) : (
                calls.map((call) => {
                  const status = getCallStatus(call);
                  
                  return (
                    <CallCard
                      key={call.id}
                      isCompleted={call.is_completed}
                      isSelected={selectedCall?.id === call.id}
                      onClick={() => handleCallClick(call)}
                    >
                      <CallHeader>
                        <CallTitle>{call.title}</CallTitle>
                        <CallBadge type={status}>
                          {status === 'completed' ? '✓ Completed' :
                           status === 'overdue' ? '⚠ Overdue' :
                           '📅 Upcoming'}
                        </CallBadge>
                      </CallHeader>

                      <CallDetails>
                        <CallMeta>
                          <CallIcon>🕐</CallIcon>
                          {formatToLocal(call.scheduled_for)}
                        </CallMeta>
                        <CallMeta>
                          <CallIcon>⏱</CallIcon>
                          {call.duration_minutes} minutes
                        </CallMeta>
                        {call.call_purpose && (
                          <CallMeta>
                            <CallIcon>📋</CallIcon>
                            {call.call_purpose}
                          </CallMeta>
                        )}
                      </CallDetails>

                      {!call.is_completed && (
                        <CallActions>
                          <CompleteButton
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCompleteCall(call.id);
                            }}
                          >
                            Mark Complete
                          </CompleteButton>
                          <SecondaryButton
                            onClick={(e) => {
                              e.stopPropagation();
                              alert('Edit functionality coming soon');
                            }}
                          >
                            Edit
                          </SecondaryButton>
                        </CallActions>
                      )}
                    </CallCard>
                  );
                })
              )}
            </CallsList>
          )}
        </LeftPane>

        {/* Right Pane: Activity Feed */}
        <RightPane>
          <PaneTitle>Activity Log</PaneTitle>

          {entityFilter && (
            <FilterInfo>
              <span>
                Showing activity for: <strong>{entityFilter.entityName || `${entityFilter.entityType} #${entityFilter.entityId}`}</strong>
              </span>
              <ClearButton onClick={clearFilter}>Clear Filter</ClearButton>
            </FilterInfo>
          )}

          {entityFilter ? (
            <ActivityFeed
              entityType={entityFilter.entityType}
              entityId={entityFilter.entityId}
              showCreateForm
              maxHeight="calc(100vh - 380px)"
            />
          ) : (
            <EmptyState>
              <p>Select a scheduled call to view related activity logs.</p>
              <p>Or select an entity from another page to see its history.</p>
            </EmptyState>
          )}
        </RightPane>
      </SplitPaneContainer>
    </PageContainer>
  );
};

export default CallLog;
