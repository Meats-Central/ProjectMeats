# UI Enhancements Documentation

## Overview

This document describes the UI enhancements implemented for ProjectMeats, including theme system, menu improvements, quick actions, and layout customization.

## Features Implemented

### 1. Theme System (Dark/Light Mode)

#### Architecture
- **Theme Configuration** (`src/config/theme.ts`): Defines light and dark color schemes
- **Theme Context** (`src/contexts/ThemeContext.tsx`): Manages theme state globally
- **Theme Integration**: All layout components use themed styled-components

#### Color Schemes

**Light Theme:**
- Background: #f8f9fa
- Surface: #ffffff
- Sidebar: #2c3e50
- Primary: #3498db

**Dark Theme:**
- Background: #1a1a1a
- Surface: #2d2d2d
- Sidebar: #1f1f1f
- Primary: #3498db

#### Usage

```typescript
import { useTheme } from '../contexts/ThemeContext';

const MyComponent = () => {
  const { theme, themeName, toggleTheme, setTheme } = useTheme();
  
  return (
    <StyledComponent $theme={theme}>
      <button onClick={toggleTheme}>
        Toggle to {themeName === 'light' ? 'dark' : 'light'} mode
      </button>
    </StyledComponent>
  );
};

const StyledComponent = styled.div<{ $theme: Theme }>`
  background: ${props => props.$theme.colors.background};
  color: ${props => props.$theme.colors.textPrimary};
`;
```

#### Persistence
- **localStorage**: Theme preference saved locally
- **Backend API**: Synced to UserPreferences model at `/api/v1/preferences/me/`

### 2. Enhanced Navigation Menu

#### Auto-Close on Route Change
- Sidebar automatically closes on mobile/tablet (< 768px width) when navigating
- Improves mobile UX by preventing menu overlap

#### On-Hover Auto-Open
- When sidebar is collapsed, hovering opens it temporarily
- Smooth transitions with 0.3s easing
- Visual feedback for better UX

#### Implementation
```typescript
const [isHovered, setIsHovered] = useState(false);
const isExpanded = isOpen || isHovered;

<SidebarContainer
  $isOpen={isExpanded}
  onMouseEnter={() => !isOpen && setIsHovered(true)}
  onMouseLeave={() => setIsHovered(false)}
>
```

### 3. Quick Menu (Top Bar)

#### Features
- Lightning bolt icon (⚡) in header for quick access
- Dropdown menu with frequently used actions:
  - New Supplier
  - New Customer
  - New Purchase Order
  - View Dashboard

#### Usage
Click the ⚡ icon in the header to access quick actions. Menu auto-closes after selection.

### 4. Theme Toggle Button

#### Location
Top right header, between quick menu and notifications

#### Icons
- 🌙 Moon icon when in light mode (click to switch to dark)
- ☀️ Sun icon when in dark mode (click to switch to light)

### 5. User Preferences API

#### Backend Model (UserPreferences)

**Fields:**
- `user`: OneToOne relationship with User
- `theme`: Choice field (light/dark/auto)
- `dashboard_layout`: JSONField for widget configurations
- `sidebar_collapsed`: Boolean for default sidebar state
- `quick_menu_items`: JSONField array of favorite routes
- `widget_preferences`: JSONField for widget-specific settings

#### API Endpoints

**Get/Create User Preferences:**
```http
GET /api/v1/preferences/me/
Authorization: Token <user-token>
```

**Update Preferences (Partial):**
```http
PATCH /api/v1/preferences/me/
Authorization: Token <user-token>
Content-Type: application/json

{
  "theme": "dark",
  "sidebar_collapsed": true
}
```

**Update Preferences (Full):**
```http
PUT /api/v1/preferences/me/
Authorization: Token <user-token>
Content-Type: application/json

{
  "theme": "dark",
  "sidebar_collapsed": true,
  "dashboard_layout": {"widgets": ["sales", "inventory"]},
  "quick_menu_items": ["/suppliers", "/customers"],
  "widget_preferences": {"sales": {"period": "month"}}
}
```

## Components Modified

### Layout Components

1. **Layout.tsx**
   - Added ThemeProvider integration
   - Applied theme to container and content
   - Updated keyboard shortcut hint with theme

2. **Sidebar.tsx**
   - Added auto-close on route change
   - Implemented on-hover auto-open
   - Applied theme colors to all elements
   - Added smooth transitions

3. **Header.tsx**
   - Added quick menu dropdown
   - Added theme toggle button
   - Applied theme styling
   - Improved button interactions

### Context Providers

1. **ThemeContext.tsx**
   - Manages global theme state
   - Persists to localStorage
   - Syncs with backend API
   - Provides theme utilities

### Configuration

1. **theme.ts**
   - Defines Theme interface
   - Light and dark color schemes
   - Exportable theme objects

## Testing

### Backend Tests
- 9 comprehensive tests for UserPreferences model and API
- Tests cover CRUD operations, user isolation, authentication
- All tests passing ✅

### Frontend Build
- TypeScript compilation successful ✅
- No linting errors ✅
- Production build size: ~251 KB (gzipped)

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS transitions supported
- localStorage API required
- Keyboard shortcuts work with Cmd/Ctrl modifiers

## Accessibility

- Semantic HTML elements
- Keyboard navigation support
- ARIA labels on interactive elements
- Color contrast meets WCAG 2.1 guidelines
- Theme toggle has descriptive title attribute

## Performance

- Lazy theme loading
- Memoized theme context
- CSS transitions hardware-accelerated
- Minimal re-renders with React context

## Future Enhancements

### Planned Features
1. **User Layouts & Widgets**
   - Drag-and-drop dashboard customization
   - Widget library
   - Layout templates
   - Per-role default layouts

2. **Advanced Theme Options**
   - Auto theme based on system preference
   - Custom color scheme builder
   - Theme scheduler (auto-switch at specific times)

3. **Quick Menu Customization**
   - User-configurable quick menu items
   - Favorite routes pinning
   - Recent items history

4. **Layout Persistence**
   - Save sidebar state per user
   - Restore on login
   - Sync across devices

## Troubleshooting

### Theme Not Persisting
- Check localStorage permissions
- Verify backend API connectivity
- Check authentication token validity

### Sidebar Not Auto-Closing
- Verify window width detection
- Check route change detection
- Inspect useEffect dependencies

### Build Errors
- Run `npm install` to ensure dependencies
- Check TypeScript types
- Verify import paths

## Migration Guide

### Updating Existing Components to Use Theme

```typescript
// Before
const MyComponent = styled.div`
  background: #ffffff;
  color: #2c3e50;
`;

// After
import { Theme } from '../config/theme';

const MyComponent = styled.div<{ $theme: Theme }>`
  background: ${props => props.$theme.colors.surface};
  color: ${props => props.$theme.colors.textPrimary};
`;

// In component
const { theme } = useTheme();
<MyComponent $theme={theme} />
```

## Version History

- **v1.0** (2025-11-03): Initial implementation
  - Theme system with dark/light modes
  - Enhanced navigation with auto-close and hover
  - Quick menu in header
  - Backend UserPreferences model and API
  - Documentation

## Support

For questions or issues related to UI enhancements:
1. Check this documentation
2. Review component source code
3. Check backend API tests
4. Consult development team
