# UI Enhancements Documentation

This document describes the core UI enhancements implemented for ProjectMeats, including menu auto-close, on-hover functionality, dark/light mode toggle, quick menu, and user-specific layouts.

## Features Implemented

### 1. Dark/Light Theme Toggle

**Implementation:**
- Created `ThemeContext` in `frontend/src/contexts/ThemeContext.tsx`
- Theme preference persists in `localStorage`
- Applied CSS variables for easy theme switching
- Toggle button in header switches between light and dark modes

**Usage:**
```tsx
import { useTheme } from '../contexts/ThemeContext';

const MyComponent = () => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}
    </button>
  );
};
```

**CSS Variables:**
- Light theme: Clean, professional interface
- Dark theme: Reduced eye strain for low-light environments
- All components automatically adapt via CSS variables

### 2. Enhanced Sidebar Navigation

**Auto-Close Functionality:**
- Sidebar automatically closes on mobile devices (< 768px) when navigating
- Responsive design adapts to screen size changes
- Manual toggle button always available

**On-Hover Auto-Open:**
- When sidebar is collapsed, hovering triggers auto-open after 300ms delay
- Prevents accidental opens while maintaining quick access
- Smooth transitions for better UX

**Features:**
- Uniform icons for all navigation items
- Clear visual feedback on hover and active states
- Tooltips show full labels when sidebar is collapsed

### 3. Top Bar Quick Menu

**Implementation:**
- Quick action button (➕) in header
- Dropdown menu with common actions:
  - New Supplier
  - New Customer
  - New Purchase Order
  - New Contact
- Click-to-close behavior for better UX

**Customization:**
Add more quick actions by editing `Header.tsx`:
```tsx
const quickMenuItems = [
  { label: 'New Action', path: '/path', icon: '🎯' },
  // ... more items
];
```

### 4. User Preferences System

**Backend Model:**
- `UserPreferences` model stores user-specific settings
- Fields:
  - `theme`: 'light' or 'dark'
  - `sidebar_open`: Boolean for default sidebar state
  - `dashboard_layout`: JSON field for widget configuration
  - Auto-tracked `created_at` and `updated_at`

**API Endpoints:**
```
GET    /api/core/preferences/me/                  # Get current user's preferences
PATCH  /api/core/preferences/update_theme/        # Update theme only
PATCH  /api/core/preferences/update_sidebar/      # Update sidebar state only
PATCH  /api/core/preferences/update_dashboard_layout/  # Update dashboard layout
```

**Example API Usage:**
```bash
# Get preferences
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/core/preferences/me/

# Update theme
curl -X PATCH -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme": "dark"}' \
  http://localhost:8000/api/core/preferences/update_theme/

# Update dashboard layout
curl -X PATCH -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dashboard_layout": {"widgets": ["chart1", "chart2"]}}' \
  http://localhost:8000/api/core/preferences/update_dashboard_layout/
```

### 5. Dashboard Customization (Foundation)

**Current Implementation:**
- Backend model supports storing dashboard widget configurations
- JSON field allows flexible widget arrangement
- Foundation for drag-and-drop dashboard customization

**Future Enhancements:**
- Widget library component
- Drag-and-drop interface for arranging widgets
- Widget size and position persistence
- Predefined layout templates

## Technical Details

### Frontend Architecture

**Context Providers:**
- `ThemeProvider`: Manages theme state and persistence
- `AuthProvider`: User authentication
- `NavigationProvider`: Sidebar and breadcrumb state

**Component Structure:**
```
src/
├── contexts/
│   ├── ThemeContext.tsx         # Theme management
│   ├── AuthContext.tsx          # Authentication
│   └── NavigationContext.tsx    # Navigation state
├── components/
│   └── Layout/
│       ├── Layout.tsx           # Main layout with auto-close
│       ├── Sidebar.tsx          # Enhanced sidebar with hover
│       └── Header.tsx           # Header with quick menu & theme toggle
└── index.css                    # CSS variables for theming
```

### Backend Architecture

**Models:**
- `UserPreferences`: Stores user-specific UI settings
  - One-to-One relationship with User
  - JSONField for flexible configuration storage

**Views:**
- `UserPreferencesViewSet`: RESTful API for preferences
  - Custom actions for targeted updates
  - Automatic user filtering
  - Get-or-create pattern for seamless UX

**Admin:**
- UserPreferences admin interface for debugging
- Read-only timestamps
- Organized fieldsets

## Testing

### Frontend Testing
```bash
cd frontend
npm run lint        # Lint check
npm run type-check  # TypeScript validation
npm test           # Run tests
```

### Backend Testing
```bash
cd backend
python manage.py makemigrations --check  # Check for pending migrations
python manage.py check                    # System checks
python manage.py test apps.core          # Run core app tests
```

## Deployment

### Frontend
1. Build production assets:
   ```bash
   cd frontend
   npm run build
   ```

2. CSS variables are automatically applied via `index.css`

### Backend
1. Apply migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

2. User preferences are created on-demand (no setup required)

## Configuration

### Theme Colors

Edit `frontend/src/index.css` to customize theme colors:

```css
:root[data-theme='light'] {
  --bg-primary: #ffffff;
  --text-primary: #2c3e50;
  /* ... more variables */
}

:root[data-theme='dark'] {
  --bg-primary: #1a1a1a;
  --text-primary: #e9ecef;
  /* ... more variables */
}
```

### Sidebar Auto-Open Delay

Adjust hover delay in `Sidebar.tsx`:
```tsx
hoverTimeoutRef.current = setTimeout(() => {
  setIsHovered(true);
}, 300); // Change delay here (milliseconds)
```

### Mobile Breakpoint

Modify auto-close breakpoint in `Layout.tsx`:
```tsx
if (window.innerWidth < 768 && sidebarOpen) {
  // Change 768 to desired breakpoint
  setSidebarOpen(false);
}
```

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox support required
- localStorage required for theme persistence
- CSS variables (custom properties) required

## Accessibility

- Keyboard navigation supported
- ARIA labels on toggle buttons
- Sufficient color contrast in both themes
- Focus indicators visible
- Screen reader friendly

## Performance

- Theme switching: Instant (CSS variables)
- Sidebar animations: Hardware-accelerated (transform)
- Local storage: Synchronous (minimal impact)
- API calls: Debounced when preferences change

## Future Enhancements

1. **Widget System:**
   - Drag-and-drop dashboard builder
   - Pre-built widget library
   - Widget marketplace

2. **Advanced Theming:**
   - Custom color picker
   - Multiple theme presets
   - Per-module theming

3. **Sync Across Devices:**
   - Save theme to user profile
   - Sync sidebar state across sessions
   - Cloud-based layout storage

4. **Enhanced Quick Menu:**
   - Customizable quick actions
   - Recent actions history
   - Keyboard shortcuts

5. **Responsive Enhancements:**
   - Mobile-optimized navigation
   - Touch gestures for sidebar
   - Adaptive layouts

## Troubleshooting

### Theme not persisting
- Check localStorage is enabled in browser
- Clear browser cache and reload
- Check browser console for errors

### Sidebar not auto-opening
- Ensure you're hovering over sidebar area
- Check if JavaScript is enabled
- Verify no console errors

### Quick menu not appearing
- Check if user is authenticated
- Verify Header component is rendering
- Check z-index conflicts with other elements

### Preferences not saving
- Verify user is authenticated
- Check API endpoint is accessible
- Review browser network tab for failed requests
- Check backend logs for errors

## Support

For issues or questions:
1. Check this documentation
2. Review component source code
3. Check copilot-log.md for implementation details
4. Contact development team
