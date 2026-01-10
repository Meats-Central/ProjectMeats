# CallLog Professional Scheduling Upgrade Guide

## Overview
This document outlines the comprehensive upgrade to CallLog.tsx to support professional scheduling with calendar views, drag-and-drop, and full CRUD operations.

## ✅ Completed: ScheduleCallModal.tsx

### Enhanced Features
1. **Edit Mode Support** - Pass `initialData` prop to edit existing calls
2. **Create Mode** - Works as before for new calls  
3. **Outcome Field** - Shows for completed calls in edit mode
4. **Better Validation** - Enhanced error messages
5. **Loading States** - Shows "Updating..." vs "Scheduling..."

### Usage
```tsx
// Create new call
<ScheduleCallModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  onSuccess={() => fetchCalls()}
/>

// Edit existing call
<ScheduleCallModal
  isOpen={showEditModal}
  initialData={selectedCall}
  onClose={() => setShowEditModal(false)}
  onSuccess={() => fetchCalls()}
/>
```

## 📋 TODO: CallLog.tsx Enhancements

### 1. Add Edit & Delete Functionality

#### Edit Logic
```typescript
const [editingCall, setEditingCall] = useState<ScheduledCall | null>(null);

const handleEditCall = (call: ScheduledCall, e: React.MouseEvent) => {
  e.stopPropagation();
  setEditingCall(call);
};

// In render:
<ScheduleCallModal
  isOpen={!!editingCall}
  initialData={editingCall}
  onClose={() => setEditingCall(null)}
  onSuccess={() => {
    fetchScheduledCalls();
    setEditingCall(null);
  }}
/>
```

#### Delete Logic
```typescript
const handleDeleteCall = async (callId: number, e: React.MouseEvent) => {
  e.stopPropagation();
  
  if (!confirm('Are you sure you want to delete this call?')) {
    return;
  }
  
  try {
    await apiClient.delete(\`cockpit/scheduled-calls/\${callId}/\`);
    await fetchScheduledCalls();
  } catch (err: any) {
    console.error('Failed to delete call:', err);
    alert('Failed to delete call');
  }
};

// Add to CallActions:
<SecondaryButton onClick={(e) => handleEditCall(call, e)}>
  ✏️ Edit
</SecondaryButton>
<SecondaryButton onClick={(e) => handleDeleteCall(call.id, e)}>
  🗑️ Delete
</SecondaryButton>
```

### 2. Calendar UI Transformation

#### Install Additional Dependencies
```bash
npm install @ant-design/icons
npm install dayjs
```

#### Calendar Component Structure
```tsx
import { Calendar, Badge, Segmented } from 'antd';
import { LeftOutlined, RightOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';

type ViewMode = 'agenda' | 'day' | 'week' | 'month';

const [viewMode, setViewMode] = useState<ViewMode>('month');
const [currentDate, setCurrentDate] = useState<Dayjs>(dayjs());

const CalendarControls = styled.div\`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
\`;

const NavigationButtons = styled.div\`
  display: flex;
  gap: 0.5rem;
\`;

const NavButton = styled.button\`
  padding: 0.5rem 1rem;
  background: rgb(var(--color-surface));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  cursor: pointer;
  color: rgb(var(--color-text-primary));
  
  &:hover {
    background: rgb(var(--color-surface-hover));
  }
\`;

// In render:
<CalendarControls>
  <Segmented
    options={['Agenda', 'Day', 'Week', 'Month']}
    value={viewMode}
    onChange={(value) => setViewMode(value.toLowerCase() as ViewMode)}
  />
  <NavigationButtons>
    <NavButton onClick={() => setCurrentDate(currentDate.subtract(1, viewMode === 'month' ? 'month' : viewMode === 'week' ? 'week' : 'day'))}>
      <LeftOutlined /> Previous
    </NavButton>
    <NavButton onClick={() => setCurrentDate(dayjs())}>
      Today
    </NavButton>
    <NavButton onClick={() => setCurrentDate(currentDate.add(1, viewMode === 'month' ? 'month' : viewMode === 'week' ? 'week' : 'day'))}>
      Next <RightOutlined />
    </NavButton>
  </NavigationButtons>
</CalendarControls>

{viewMode === 'month' && (
  <Calendar
    value={currentDate}
    onChange={setCurrentDate}
    dateCellRender={dateCellRender}
  />
)}
```

#### Date Cell Renderer for Month View
```tsx
const dateCellRender = (date: Dayjs) => {
  const callsForDate = calls.filter(call => 
    dayjs(call.scheduled_for).format('YYYY-MM-DD') === date.format('YYYY-MM-DD')
  );
  
  return (
    <div>
      {callsForDate.map(call => {
        const status = getCallStatus(call);
        return (
          <Badge
            key={call.id}
            status={status === 'completed' ? 'success' : status === 'overdue' ? 'error' : 'processing'}
            text={call.title}
            onClick={() => handleCallClick(call)}
            style={{
              display: 'block',
              fontSize: '0.75rem',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              cursor: 'pointer',
              marginBottom: '2px',
            }}
          />
        );
      })}
    </div>
  );
};
```

### 3. Week/Day View with Time Slots

```tsx
const TimeSlotGrid = styled.div\`
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: 1px;
  background: rgb(var(--color-border));
  border: 1px solid rgb(var(--color-border));
  border-radius: var(--radius-md);
  overflow: hidden;
\`;

const TimeLabel = styled.div\`
  padding: 0.5rem;
  background: rgb(var(--color-surface));
  font-size: 0.75rem;
  color: rgb(var(--color-text-secondary));
  text-align: right;
\`;

const TimeSlot = styled.div<{ hasCall?: boolean }>\`
  padding: 0.5rem;
  background: rgb(var(--color-surface));
  min-height: 60px;
  position: relative;
  cursor: pointer;
  
  &:hover {
    background: rgb(var(--color-surface-hover));
  }
\`;

const CallBlock = styled.div<{ duration: number; status: string }>\`
  position: absolute;
  left: 4px;
  right: 4px;
  background: \${props => 
    props.status === 'completed' ? 'rgba(34, 197, 94, 0.2)' :
    props.status === 'overdue' ? 'rgba(239, 68, 68, 0.2)' :
    'rgba(var(--color-primary), 0.2)'
  };
  border-left: 3px solid \${props =>
    props.status === 'completed' ? 'rgb(34, 197, 94)' :
    props.status === 'overdue' ? 'rgb(239, 68, 68)' :
    'rgb(var(--color-primary))'
  };
  border-radius: var(--radius-sm);
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  cursor: move;
  height: \${props => (props.duration / 60) * 60}px;
\`;

// Render time slots
const renderDayView = () => {
  const hours = Array.from({ length: 11 }, (_, i) => i + 8); // 8 AM to 6 PM
  
  return (
    <TimeSlotGrid>
      {hours.map(hour => (
        <React.Fragment key={hour}>
          <TimeLabel>{hour}:00</TimeLabel>
          <TimeSlot>
            {calls
              .filter(call => dayjs(call.scheduled_for).hour() === hour)
              .map(call => (
                <CallBlock
                  key={call.id}
                  duration={call.duration_minutes}
                  status={getCallStatus(call)}
                  draggable
                  onDragStart={(e) => handleDragStart(e, call)}
                  onDragOver={handleDragOver}
                  onDrop={(e) => handleDrop(e, hour)}
                >
                  {call.title}
                </CallBlock>
              ))}
          </TimeSlot>
        </React.Fragment>
      ))}
    </TimeSlotGrid>
  );
};
```

### 4. Drag and Drop Implementation

```tsx
const [draggedCall, setDraggedCall] = useState<ScheduledCall | null>(null);

const handleDragStart = (e: React.DragEvent, call: ScheduledCall) => {
  setDraggedCall(call);
  e.dataTransfer.effectAllowed = 'move';
};

const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
};

const handleDrop = async (e: React.DragEvent, targetHour: number) => {
  e.preventDefault();
  
  if (!draggedCall) return;
  
  // Calculate new scheduled time
  const currentDate = dayjs(draggedCall.scheduled_for);
  const newScheduledFor = currentDate
    .hour(targetHour)
    .minute(0)
    .second(0)
    .format('YYYY-MM-DDTHH:mm:ss');
  
  try {
    // Update backend immediately
    await apiClient.patch(\`cockpit/scheduled-calls/\${draggedCall.id}/\`, {
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
    alert('Failed to reschedule call');
    setDraggedCall(null);
  }
};
```

### 5. Agenda View

```tsx
const AgendaList = styled.div\`
  display: flex;
  flex-direction: column;
  gap: 1rem;
\`;

const AgendaDate = styled.div\`
  font-size: 1.125rem;
  font-weight: 600;
  color: rgb(var(--color-text-primary));
  padding: 0.75rem;
  background: rgb(var(--color-surface-hover));
  border-radius: var(--radius-md);
  margin-bottom: 0.5rem;
\`;

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
  
  return (
    <AgendaList>
      {sortedDates.map(date => (
        <div key={date}>
          <AgendaDate>
            {dayjs(date).format('dddd, MMMM D, YYYY')}
          </AgendaDate>
          {groupedCalls[date]
            .sort((a, b) => dayjs(a.scheduled_for).diff(dayjs(b.scheduled_for)))
            .map(call => renderCallCard(call))}
        </div>
      ))}
    </AgendaList>
  );
};
```

### 6. View Completed Call Details

```tsx
interface CallDetailsModalProps {
  call: ScheduledCall | null;
  isOpen: boolean;
  onClose: () => void;
}

const CallDetailsModal: React.FC<CallDetailsModalProps> = ({ call, isOpen, onClose }) => {
  if (!call || !isOpen) return null;
  
  return (
    <Overlay isOpen={isOpen} onClick={onClose}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>{call.title}</ModalTitle>
          <CloseButton onClick={onClose}>&times;</CloseButton>
        </ModalHeader>
        <ModalBody>
          <DetailRow>
            <DetailLabel>Status:</DetailLabel>
            <DetailValue>
              <CallBadge type={getCallStatus(call)}>
                {call.is_completed ? '✓ Completed' : '📅 Upcoming'}
              </CallBadge>
            </DetailValue>
          </DetailRow>
          <DetailRow>
            <DetailLabel>Scheduled:</DetailLabel>
            <DetailValue>{formatToLocal(call.scheduled_for)}</DetailValue>
          </DetailRow>
          <DetailRow>
            <DetailLabel>Duration:</DetailLabel>
            <DetailValue>{call.duration_minutes} minutes</DetailValue>
          </DetailRow>
          <DetailRow>
            <DetailLabel>Purpose:</DetailLabel>
            <DetailValue>{call.call_purpose}</DetailValue>
          </DetailRow>
          {call.description && (
            <DetailRow>
              <DetailLabel>Description:</DetailLabel>
              <DetailValue>{call.description}</DetailValue>
            </DetailRow>
          )}
          {call.outcome && (
            <DetailRow>
              <DetailLabel>Outcome:</DetailLabel>
              <DetailValue>{call.outcome}</DetailValue>
            </DetailRow>
          )}
        </ModalBody>
        <ModalFooter>
          <CancelButton onClick={onClose}>Close</CancelButton>
        </ModalFooter>
      </Modal>
    </Overlay>
  );
};

// Usage
const [viewDetailsCall, setViewDetailsCall] = useState<ScheduledCall | null>(null);

// Click handler for completed calls
const handleViewDetails = (call: ScheduledCall) => {
  if (call.is_completed) {
    setViewDetailsCall(call);
  } else {
    handleCallClick(call);
  }
};
```

## 🎨 Color Standards

### Status Colors
```tsx
const STATUS_COLORS = {
  upcoming: {
    bg: 'rgba(var(--color-primary), 0.1)',
    border: 'rgb(var(--color-primary))',
    text: 'rgb(var(--color-primary))',
  },
  completed: {
    bg: 'rgba(34, 197, 94, 0.1)',
    border: 'rgb(34, 197, 94)',
    text: 'rgb(34, 197, 94)',
  },
  overdue: {
    bg: 'rgba(239, 68, 68, 0.1)',
    border: 'rgb(239, 68, 68)',
    text: 'rgb(239, 68, 68)',
  },
};
```

### Status Icons
- ✓ = Completed
- 📅 = Upcoming  
- ⚠️ = Overdue

## 📦 Final File Structure

```
frontend/src/
├── pages/Cockpit/
│   └── CallLog.tsx (Enhanced with calendar views)
└── components/Shared/
    ├── ScheduleCallModal.tsx ✅ (DONE - Edit/Create support)
    └── CallDetailsModal.tsx (TODO - View completed call details)
```

## 🚀 Implementation Steps

1. ✅ **Phase 1** - Enhanced ScheduleCallModal (COMPLETE)
2. **Phase 2** - Add Edit/Delete to CallLog
3. **Phase 3** - Implement Calendar Controls & Month View
4. **Phase 4** - Add Week/Day views with time slots
5. **Phase 5** - Implement Drag & Drop
6. **Phase 6** - Add Agenda View
7. **Phase 7** - Create CallDetailsModal for completed calls

## 🧪 Testing Checklist

- [ ] Create new call
- [ ] Edit existing call
- [ ] Delete call with confirmation
- [ ] View completed call details
- [ ] Switch between calendar views
- [ ] Navigate dates (Previous/Today/Next)
- [ ] Drag and drop to reschedule (Week/Day views)
- [ ] Month view shows all calls with badges
- [ ] Agenda view groups by date
- [ ] Color coding matches status
- [ ] Theme variables used throughout
- [ ] No hardcoded colors
