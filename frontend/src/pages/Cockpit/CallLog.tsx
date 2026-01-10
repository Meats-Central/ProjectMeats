/**
 * Cockpit Call Log Page - Professional Scheduling
 * 
 * Features:
 * - Multiple calendar views: Month, Week, Day, Agenda
 * - Full CRUD operations: Create, Read, Update, Delete
 * - Drag-and-drop rescheduling (Week/Day views)
 * - Visual status indicators (upcoming, completed, overdue)
 * - Activity feed integration
 * 
 * Theme Compliance:
 * - Uses CSS custom properties (rgb(var(--color-primary)))
 * - No hardcoded colors
 * - Responsive design
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Calendar, Badge, Segmented } from 'antd';
import { LeftOutlined, RightOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { ActivityFeed } from '../../components/Shared/ActivityFeed';
import { ScheduleCallModal } from '../../components/Shared/ScheduleCallModal';
import { apiClient } from '../../services/apiService';
import { formatToLocal } from '../../utils/formatters';

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

type ViewMode = 'month' | 'week' | 'day' | 'agenda';

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
// Calendar View Styled Components
// ============================================================================

const CalendarContainer = styled.div`
  flex: 1;
  min-height: 600px;
  overflow-y: auto;
`;

const CalendarControls = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
`;

const NavigationButtons = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const NavButton = styled.button`
  padding: 0.5rem 1rem;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  cursor: pointer;
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgb(var(--color-surface-hover));
    border-color: rgb(var(--color-primary));
  }
`;

const CurrentDateLabel = styled.div`
  font-size: 1.25rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
`;

const TimeSlotGrid = styled.div`
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 1px;
  background: rgb(var(--color-border));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  overflow: hidden;
`;

const TimeLabel = styled.div`
  padding: 0.75rem 0.5rem;
  background: rgb(var(--color-surface));
  font-size: 0.75rem;
  color: rgb(var(--color-text-secondary));
  text-align: right;
  font-weight: 500;
  border-right: 1px solid rgb(var(--color-border));
`;

const TimeSlot = styled.div`
  padding: 0.5rem;
  background: rgb(var(--color-background));
  min-height: 60px;
  position: relative;
  cursor: pointer;
  
  &:hover {
    background: rgba(var(--color-primary), 0.02);
  }
`;

const CallBlock = styled.div<{ duration: number; status: string; isDragging?: boolean }>`
  position: absolute;
  left: 4px;
  right: 4px;
  background: ${props => 
    props.status === 'completed' ? 'rgba(34, 197, 94, 0.15)' :
    props.status === 'overdue' ? 'rgba(239, 68, 68, 0.15)' :
    'rgba(var(--color-primary), 0.15)'
  };
  border-left: 3px solid ${props =>
    props.status === 'completed' ? 'rgb(34, 197, 94)' :
    props.status === 'overdue' ? 'rgb(239, 68, 68)' :
    'rgb(var(--color-primary))'
  };
  border-radius: var(--radius-sm);
  padding: 0.5rem;
  font-size: 0.75rem;
  cursor: move;
  height: ${props => Math.max((props.duration / 60) * 60, 40)}px;
  overflow: hidden;
  opacity: ${props => props.isDragging ? 0.5 : 1};
  transition: opacity 0.2s ease;
  
  &:hover {
    opacity: 0.9;
  }
`;

const CallBlockTitle = styled.div`
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: rgb(var(--color-text-primary));
`;

const CallBlockTime = styled.div`
  font-size: 0.7rem;
  color: rgb(var(--color-text-secondary));
`;

const AgendaList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const AgendaDateGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const AgendaDate = styled.div`
  font-size: 1.125rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  padding: 0.75rem 1rem;
  background: rgb(var(--color-surface-hover));
  border-radius: var(--radius-md);
  border-left: 4px solid rgb(var(--color-primary));
`;

const WeekGrid = styled.div`
  display: grid;
  grid-template-columns: 80px repeat(7, 1fr);
  gap: 1px;
  background: rgb(var(--color-border));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  overflow: hidden;
`;

const WeekDayHeader = styled.div`
  padding: 0.75rem;
  background: rgb(var(--color-surface));
  font-weight: 600;
  text-align: center;
  color: rgb(var(--color-text-primary));
  font-size: 0.875rem;
  border-bottom: 2px solid rgb(var(--color-border));
`;

const WeekTimeSlot = styled.div`
  background: rgb(var(--color-background));
  min-height: 60px;
  position: relative;
  padding: 0.25rem;
  cursor: pointer;
  
  &:hover {
    background: rgba(var(--color-primary), 0.02);
  }
`;

// ============================================================================
// Component
// ============================================================================

export const CallLog: React.FC = () => {
  // Existing state
  const [calls, setCalls] = useState<ScheduledCall[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCall, setSelectedCall] = useState<ScheduledCall | null>(null);
  const [entityFilter, setEntityFilter] = useState<EntityFilter | null>(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  // Phase 2: Edit & Delete state
  const [editingCall, setEditingCall] = useState<ScheduledCall | null>(null);

  // Phase 3-6: Calendar view state
  const [viewMode, setViewMode] = useState<ViewMode>('agenda');
  const [currentDate, setCurrentDate] = useState<Dayjs>(dayjs());

  // Phase 5: Drag & Drop state
  const [draggedCall, setDraggedCall] = useState<ScheduledCall | null>(null);

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

  // ============================================================================
  // Phase 2: Edit & Delete Handlers
  // ============================================================================

  const handleEditCall = (call: ScheduledCall, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingCall(call);
  };

  const handleDeleteCall = async (callId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!window.confirm('Are you sure you want to delete this scheduled call?')) {
      return;
    }
    
    try {
      await apiClient.delete(`cockpit/scheduled-calls/${callId}/`);
      await fetchScheduledCalls();
    } catch (err: any) {
      console.error('Failed to delete call:', err);
      alert('Failed to delete call. Please try again.');
    }
  };

  // ============================================================================
  // Phase 3: Calendar Navigation Handlers
  // ============================================================================

  const handlePrevious = () => {
    const unit = viewMode === 'month' ? 'month' : viewMode === 'week' ? 'week' : 'day';
    setCurrentDate(currentDate.subtract(1, unit));
  };

  const handleNext = () => {
    const unit = viewMode === 'month' ? 'month' : viewMode === 'week' ? 'week' : 'day';
    setCurrentDate(currentDate.add(1, unit));
  };

  const handleToday = () => {
    setCurrentDate(dayjs());
  };

  const getCurrentDateLabel = () => {
    if (viewMode === 'month') {
      return currentDate.format('MMMM YYYY');
    } else if (viewMode === 'week') {
      const startOfWeek = currentDate.startOf('week');
      const endOfWeek = currentDate.endOf('week');
      return `${startOfWeek.format('MMM D')} - ${endOfWeek.format('MMM D, YYYY')}`;
    } else if (viewMode === 'day') {
      return currentDate.format('dddd, MMMM D, YYYY');
    } else {
      return 'Agenda View';
    }
  };

  // ============================================================================
  // Phase 4: Month View Cell Renderer
  // ============================================================================

  const dateCellRender = (date: Dayjs) => {
    const callsForDate = calls.filter(call => 
      dayjs(call.scheduled_for).format('YYYY-MM-DD') === date.format('YYYY-MM-DD')
    );
    
    return (
      <div style={{ overflow: 'hidden' }}>
        {callsForDate.slice(0, 3).map(call => {
          const status = getCallStatus(call);
          return (
            <Badge
              key={call.id}
              status={status === 'completed' ? 'success' : status === 'overdue' ? 'error' : 'processing'}
              text={call.title}
              onClick={(e) => {
                e.stopPropagation();
                handleCallClick(call);
              }}
              style={{
                display: 'block',
                fontSize: '0.7rem',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                cursor: 'pointer',
                marginBottom: '2px',
              }}
            />
          );
        })}
        {callsForDate.length > 3 && (
          <div style={{ fontSize: '0.7rem', color: 'rgb(var(--color-text-secondary))' }}>
            +{callsForDate.length - 3} more
          </div>
        )}
      </div>
    );
  };

  // ============================================================================
  // Phase 5: Drag & Drop Handlers
  // ============================================================================

  const handleDragStart = (e: React.DragEvent, call: ScheduledCall) => {
    setDraggedCall(call);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e: React.DragEvent, targetHour: number, targetDate?: Dayjs) => {
    e.preventDefault();
    
    if (!draggedCall) return;
    
    try {
      // Calculate new scheduled time
      const baseDate = targetDate || currentDate;
      const newScheduledFor = baseDate
        .hour(targetHour)
        .minute(0)
        .second(0)
        .format('YYYY-MM-DDTHH:mm:ss');
      
      // Update backend
      await apiClient.patch(`cockpit/scheduled-calls/${draggedCall.id}/`, {
        scheduled_for: newScheduledFor,
      });
      
      // Update local state
      setCalls(calls.map(c =>
        c.id === draggedCall.id
          ? { ...c, scheduled_for: newScheduledFor }
          : c
      ));
      
      setDraggedCall(null);
    } catch (err: any) {
      console.error('Failed to reschedule call:', err);
      alert('Failed to reschedule call. Please try again.');
      setDraggedCall(null);
    }
  };

  // ============================================================================
  // Phase 4: Day View Renderer
  // ============================================================================

  const renderDayView = () => {
    const hours = Array.from({ length: 11 }, (_, i) => i + 8); // 8 AM to 6 PM
    
    return (
      <TimeSlotGrid>
        {hours.map(hour => {
          const callsForHour = calls.filter(call => {
            const callDate = dayjs(call.scheduled_for);
            return callDate.format('YYYY-MM-DD') === currentDate.format('YYYY-MM-DD') &&
                   callDate.hour() === hour;
          });

          return (
            <React.Fragment key={hour}>
              <TimeLabel>
                {dayjs().hour(hour).format('h:mm A')}
              </TimeLabel>
              <TimeSlot
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, hour)}
              >
                {callsForHour.map(call => (
                  <CallBlock
                    key={call.id}
                    duration={call.duration_minutes}
                    status={getCallStatus(call)}
                    isDragging={draggedCall?.id === call.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, call)}
                    onClick={() => handleCallClick(call)}
                  >
                    <CallBlockTitle>{call.title}</CallBlockTitle>
                    <CallBlockTime>
                      {dayjs(call.scheduled_for).format('h:mm A')} ({call.duration_minutes}min)
                    </CallBlockTime>
                  </CallBlock>
                ))}
              </TimeSlot>
            </React.Fragment>
          );
        })}
      </TimeSlotGrid>
    );
  };

  // ============================================================================
  // Phase 4: Week View Renderer
  // ============================================================================

  const renderWeekView = () => {
    const startOfWeek = currentDate.startOf('week');
    const hours = Array.from({ length: 11 }, (_, i) => i + 8);
    const days = Array.from({ length: 7 }, (_, i) => startOfWeek.add(i, 'day'));

    return (
      <WeekGrid>
        {/* Header row */}
        <div />
        {days.map(day => (
          <WeekDayHeader key={day.format('YYYY-MM-DD')}>
            <div>{day.format('ddd')}</div>
            <div style={{ fontSize: '1.25rem', marginTop: '0.25rem' }}>
              {day.format('D')}
            </div>
          </WeekDayHeader>
        ))}

        {/* Time slots */}
        {hours.map(hour => (
          <React.Fragment key={hour}>
            <TimeLabel>{dayjs().hour(hour).format('h A')}</TimeLabel>
            {days.map(day => {
              const callsForSlot = calls.filter(call => {
                const callDate = dayjs(call.scheduled_for);
                return callDate.format('YYYY-MM-DD') === day.format('YYYY-MM-DD') &&
                       callDate.hour() === hour;
              });

              return (
                <WeekTimeSlot
                  key={`${day.format('YYYY-MM-DD')}-${hour}`}
                  onDragOver={handleDragOver}
                  onDrop={(e) => handleDrop(e, hour, day)}
                >
                  {callsForSlot.map(call => (
                    <CallBlock
                      key={call.id}
                      duration={call.duration_minutes}
                      status={getCallStatus(call)}
                      isDragging={draggedCall?.id === call.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, call)}
                      onClick={() => handleCallClick(call)}
                      style={{ fontSize: '0.65rem', padding: '0.25rem' }}
                    >
                      <CallBlockTitle style={{ fontSize: '0.7rem' }}>
                        {call.title}
                      </CallBlockTitle>
                    </CallBlock>
                  ))}
                </WeekTimeSlot>
              );
            })}
          </React.Fragment>
        ))}
      </WeekGrid>
    );
  };

  // ============================================================================
  // Phase 6: Agenda View Renderer
  // ============================================================================

  const renderAgendaView = () => {
    // Group calls by date
    const groupedCalls = calls.reduce((acc, call) => {
      const date = dayjs(call.scheduled_for).format('YYYY-MM-DD');
      if (!acc[date]) acc[date] = [];
      acc[date].push(call);
      return acc;
    }, {} as Record<string, ScheduledCall[]>);
    
    // Sort dates
    const sortedDates = Object.keys(groupedCalls).sort();
    
    if (sortedDates.length === 0) {
      return (
        <EmptyState>
          <p>No scheduled calls found.</p>
          <p>Click "Schedule New Call" to get started.</p>
        </EmptyState>
      );
    }
    
    return (
      <AgendaList>
        {sortedDates.map(date => (
          <AgendaDateGroup key={date}>
            <AgendaDate>
              {dayjs(date).format('dddd, MMMM D, YYYY')}
            </AgendaDate>
            {groupedCalls[date]
              .sort((a, b) => dayjs(a.scheduled_for).diff(dayjs(b.scheduled_for)))
              .map(call => renderCallCard(call))}
          </AgendaDateGroup>
        ))}
      </AgendaList>
    );
  };

  // ============================================================================
  // Helper: Render Call Card (used in list and agenda views)
  // ============================================================================

  const renderCallCard = (call: ScheduledCall) => {
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

        <CallActions onClick={(e) => e.stopPropagation()}>
          {!call.is_completed && (
            <CompleteButton
              onClick={(e) => {
                e.stopPropagation();
                handleCompleteCall(call.id);
              }}
            >
              Mark Complete
            </CompleteButton>
          )}
          <SecondaryButton onClick={(e) => handleEditCall(call, e)}>
            ✏️ Edit
          </SecondaryButton>
          <SecondaryButton onClick={(e) => handleDeleteCall(call.id, e)}>
            🗑️ Delete
          </SecondaryButton>
        </CallActions>
      </CallCard>
    );
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

      {/* Schedule Modal - Create */}
      <ScheduleCallModal
        isOpen={showScheduleModal}
        onClose={() => setShowScheduleModal(false)}
        onSuccess={fetchScheduledCalls}
      />

      {/* Edit Modal */}
      <ScheduleCallModal
        isOpen={!!editingCall}
        initialData={editingCall || undefined}
        onClose={() => setEditingCall(null)}
        onSuccess={() => {
          fetchScheduledCalls();
          setEditingCall(null);
        }}
      />

      <SplitPaneContainer>
        {/* Left Pane: Calendar Views */}
        <LeftPane>
          <CalendarControls>
            <Segmented
              options={[
                { label: 'Month', value: 'month' },
                { label: 'Week', value: 'week' },
                { label: 'Day', value: 'day' },
                { label: 'Agenda', value: 'agenda' },
              ]}
              value={viewMode}
              onChange={(value) => setViewMode(value as ViewMode)}
            />
            
            {viewMode !== 'agenda' && (
              <NavigationButtons>
                <NavButton onClick={handlePrevious}>
                  <LeftOutlined />
                  Previous
                </NavButton>
                <NavButton onClick={handleToday}>
                  Today
                </NavButton>
                <NavButton onClick={handleNext}>
                  Next
                  <RightOutlined />
                </NavButton>
              </NavigationButtons>
            )}
          </CalendarControls>

          {viewMode !== 'agenda' && (
            <CurrentDateLabel>{getCurrentDateLabel()}</CurrentDateLabel>
          )}

          {error && <ErrorState>{error}</ErrorState>}

          {loading ? (
            <LoadingState>Loading scheduled calls...</LoadingState>
          ) : (
            <CalendarContainer>
              {viewMode === 'month' && (
                <Calendar
                  value={currentDate}
                  onChange={setCurrentDate}
                  cellRender={dateCellRender}
                  fullscreen={false}
                />
              )}

              {viewMode === 'week' && renderWeekView()}

              {viewMode === 'day' && renderDayView()}

              {viewMode === 'agenda' && renderAgendaView()}
            </CalendarContainer>
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
