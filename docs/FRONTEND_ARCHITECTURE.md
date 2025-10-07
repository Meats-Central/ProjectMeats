# ProjectMeats Frontend Architecture

## Overview

ProjectMeats frontend is a modern React 18 application with TypeScript, providing a comprehensive user interface for meat market operations. The application was migrated from Microsoft PowerApps to a custom React solution for better performance and customization.

## Technology Stack

- **Framework**: React 18.2.0
- **Language**: TypeScript 4.9.5
- **Build Tool**: Create React App (react-scripts 5.0.1)
- **UI Components**: Ant Design 5.27.3
- **Styling**: Styled Components 6.1.0
- **Routing**: React Router DOM 6.30.1
- **HTTP Client**: Axios 1.6.0
- **Charts**: Recharts 3.2.0
- **Workflows**: ReactFlow 11.11.4
- **Testing**: React Testing Library 16.3.0
- **Documentation**: Storybook 9.1.5

## Project Structure

```
frontend/
├── public/                        # Static assets
│   ├── index.html                # HTML template
│   └── favicon.ico               # App icon
├── src/
│   ├── components/               # Reusable UI components
│   │   ├── AIAssistant/         # AI chatbot components
│   │   ├── ChatInterface/       # Chat UI components
│   │   ├── Layout/              # Layout components (Header, Sidebar)
│   │   ├── Modal/               # Modal dialogs
│   │   ├── Navigation/          # Navigation components
│   │   ├── ProfileDropdown/     # User profile menu
│   │   ├── Visualization/       # Charts and data visualization
│   │   └── Workflow/            # Business workflow components
│   ├── pages/                    # Page-level components (routes)
│   │   ├── AIAssistant.tsx      # AI chat interface
│   │   ├── AccountsReceivables.tsx
│   │   ├── Carriers.tsx
│   │   ├── Contacts.tsx
│   │   ├── Customers.tsx
│   │   ├── Dashboard.tsx        # Main dashboard
│   │   ├── Login.tsx            # Authentication
│   │   ├── Plants.tsx
│   │   ├── Profile.tsx          # User profile
│   │   ├── PurchaseOrders.tsx
│   │   ├── Settings.tsx         # App settings
│   │   ├── SignUp.tsx           # User registration
│   │   └── Suppliers.tsx
│   ├── services/                 # API and business logic
│   │   ├── aiService.ts         # AI assistant API calls
│   │   ├── apiService.ts        # Generic API utilities
│   │   ├── authService.ts       # Authentication service
│   │   └── businessApi.ts       # Business entity APIs
│   ├── types/                    # TypeScript type definitions
│   │   └── index.ts             # Shared types and interfaces
│   ├── contexts/                 # React Context providers
│   │   └── ...                  # Auth, theme, etc.
│   ├── stories/                  # Storybook component stories
│   ├── App.tsx                  # Main application component
│   ├── index.tsx                # Application entry point
│   └── index.css                # Global styles
├── .storybook/                   # Storybook configuration
├── package.json                  # Dependencies and scripts
├── tsconfig.json                # TypeScript configuration
└── .env.example                 # Environment variables template
```

## Component Architecture

### Design Patterns

1. **Functional Components**: All components use React Hooks
2. **TypeScript**: Strong typing for props, state, and API responses
3. **Styled Components**: CSS-in-JS for component styling
4. **Ant Design**: Pre-built UI components for consistency
5. **Custom Hooks**: Reusable logic extraction

### Component Categories

#### Layout Components
- **Layout**: Main application layout wrapper
- **Header**: Top navigation bar with logo and user menu
- **Sidebar**: Left navigation menu with business entity links
- **ProfileDropdown**: User profile and settings menu
- **Breadcrumb**: Navigation breadcrumb trail

#### Business Components
- **Dashboard**: KPI cards, charts, and recent activity
- **PurchaseOrders**: Order management and tracking
- **Customers**: Customer relationship management
- **Suppliers**: Supplier management
- **Contacts**: Contact directory
- **AccountsReceivables**: Payment tracking
- **Plants**: Facility management
- **Carriers**: Transportation providers

#### AI Components
- **AIAssistant/Omnibox**: AI-powered search and assistant
- **ChatInterface/ChatWindow**: Chat conversation display
- **ChatInterface/MessageList**: Message rendering
- **ChatInterface/MessageInput**: Message composition

#### Visualization Components
- **PurchaseOrderTrends**: Order volume and trends over time
- **SupplierPerformanceChart**: Supplier metrics and ratings

#### Workflow Components
- **PurchaseOrderWorkflow**: Visual order processing workflow

#### Common Components
- **Modal**: Reusable modal dialog
- **ApiTestComponent**: API testing utility (development)

## State Management

### Current Approach
- **React State**: Component-level state with useState
- **React Context**: Shared state for authentication and theme
- **Props Drilling**: Limited, mitigated by Context API

### Future Considerations
- Redux or Zustand for complex global state
- React Query for server state management
- Form state management (React Hook Form)

## Routing Structure

```
/                       → Dashboard (authenticated)
/login                  → Login page
/signup                 → Sign up page
/dashboard              → Main dashboard
/purchase-orders        → Purchase orders list
/customers              → Customers management
/suppliers              → Suppliers management
/contacts               → Contacts directory
/accounts-receivables   → Payment tracking
/plants                 → Facilities management
/carriers               → Transportation providers
/ai-assistant           → AI chat interface
/profile                → User profile
/settings               → Application settings
```

### Route Protection
- **Public Routes**: /login, /signup
- **Protected Routes**: All other routes (require authentication)
- **Role-Based**: Future implementation for different user roles

## API Integration

### Service Layer Architecture

#### apiService.ts
- **Purpose**: Generic HTTP client wrapper around Axios
- **Features**:
  - Base URL configuration from environment
  - Request/response interceptors
  - Error handling
  - Authentication token injection

#### authService.ts
- **Purpose**: Authentication operations
- **Functions**:
  - `login()`: User authentication
  - `logout()`: Session termination
  - `register()`: User registration
  - `getCurrentUser()`: Get authenticated user
  - `isAuthenticated()`: Check auth status

#### businessApi.ts
- **Purpose**: Business entity CRUD operations
- **Entities**:
  - Customers
  - Suppliers
  - Purchase Orders
  - Contacts
  - Plants
  - Carriers
- **Pattern**: RESTful API calls with typed responses

#### aiService.ts
- **Purpose**: AI assistant interactions
- **Functions**:
  - `sendMessage()`: Send chat message
  - `uploadDocument()`: Upload file for processing
  - `getConversationHistory()`: Retrieve chat history

### API Configuration

```typescript
// Environment variables
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
REACT_APP_AI_ASSISTANT_ENABLED=true
```

### Error Handling

- HTTP errors caught and displayed to users
- Network errors handled gracefully
- Loading states during API calls
- Optimistic UI updates where appropriate

## Styling Approach

### Styled Components

```typescript
import styled from 'styled-components';

const Button = styled.button`
  background: #1890ff;
  color: white;
  padding: 10px 20px;
  border-radius: 4px;
  
  &:hover {
    background: #40a9ff;
  }
`;
```

### Ant Design Integration

- Pre-built components for forms, tables, modals
- Consistent design language
- Responsive out of the box
- Customizable theme

### Global Styles

- Minimal global CSS in `index.css`
- CSS reset/normalize included
- Custom fonts and typography
- Color palette and design tokens

## Authentication Flow

### Login Process

1. User enters credentials on `/login`
2. `authService.login()` sends POST to `/api/auth/login/`
3. Backend returns JWT token (or session cookie)
4. Token stored in localStorage
5. User redirected to `/dashboard`
6. Protected routes check authentication via Context

### Protected Routes

```typescript
<Route 
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  } 
/>
```

### Session Persistence

- Token stored in localStorage
- Auto-login on page refresh
- Token refresh mechanism (planned)
- Logout clears stored credentials

## Data Visualization

### Charts (Recharts)

- **Line Charts**: Trends over time
- **Bar Charts**: Comparisons
- **Pie Charts**: Distributions
- **Area Charts**: Cumulative metrics

### Workflow Diagrams (ReactFlow)

- Visual purchase order workflows
- Drag-and-drop node editing (planned)
- Status tracking visualization

## AI Assistant Integration

### Features

1. **Chat Interface**
   - Natural language queries
   - Conversation history
   - Typing indicators

2. **Document Processing**
   - Drag-and-drop file upload
   - PDF, image, document support
   - Entity extraction from documents

3. **Omnibox Search**
   - Quick access to AI assistant
   - Keyboard shortcuts
   - Context-aware suggestions

### Implementation

```typescript
// AI Service usage
import { aiService } from './services/aiService';

const response = await aiService.sendMessage({
  conversationId: 'uuid',
  message: 'Show me this week\'s purchase orders',
  context: {}
});
```

## Testing Strategy

### Unit Tests
- Component rendering
- User interactions
- State changes
- API service mocking

### Integration Tests
- Multi-component flows
- Route navigation
- API integration

### E2E Tests (Planned)
- Complete user workflows
- Critical business paths
- Cross-browser testing

### Running Tests

```bash
# Run tests
npm test

# Run tests in CI mode
npm run test:ci

# Run with coverage
npm test -- --coverage
```

## Build and Deployment

### Development Build

```bash
npm start
# Runs on http://localhost:3000
# Hot reload enabled
# Source maps for debugging
```

### Production Build

```bash
npm run build
# Creates optimized build in /build
# Minification and tree-shaking
# Code splitting
# Asset optimization
```

### Environment-Specific Builds

```bash
# Production build with env variables
npm run build:production
```

### Serving Built App

```bash
npm run serve
# Serves production build on http://localhost:3000
```

## Performance Optimization

### Code Splitting

- Route-based code splitting with React.lazy()
- Dynamic imports for heavy components
- Reduced initial bundle size

### Lazy Loading

```typescript
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
```

### Memoization

- React.memo for expensive components
- useMemo for computed values
- useCallback for event handlers

### Bundle Analysis

```bash
npm run analyze
# Visualize bundle composition
# Identify optimization opportunities
```

## Development Workflow

### Local Development

1. Install dependencies: `npm install`
2. Set up environment: Copy `.env.example` to `.env.local`
3. Start dev server: `npm start`
4. Backend proxy configured in package.json

### Code Quality

```bash
# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Formatting
npm run format
```

### Storybook

```bash
# Start Storybook
npm run storybook
# View component documentation at http://localhost:6006

# Build Storybook
npm run build-storybook
```

## Browser Support

### Production
- Modern browsers (>0.2% usage)
- No IE11 support
- Progressive enhancement

### Development
- Latest Chrome, Firefox, Safari
- Developer tools integration

## Security Considerations

### XSS Prevention
- React's built-in escaping
- Sanitize user input
- Content Security Policy headers

### CSRF Protection
- CSRF tokens for state-changing requests
- SameSite cookie attributes

### Authentication
- Secure token storage
- HTTPS in production
- Token expiration handling

### Environment Variables
- Sensitive data not exposed
- `.env.local` in .gitignore
- Production secrets in deployment platform

## Future Enhancements

### Planned Features

1. **State Management**
   - Redux or Zustand for complex state
   - React Query for server state

2. **Forms**
   - React Hook Form integration
   - Advanced validation
   - Multi-step forms

3. **Real-time Updates**
   - WebSocket integration
   - Live notifications
   - Collaborative features

4. **PWA Support**
   - Service workers
   - Offline functionality
   - Install prompts

5. **Mobile Optimization**
   - Responsive design improvements
   - Touch gestures
   - Mobile-specific UI patterns

6. **Advanced Visualizations**
   - Interactive dashboards
   - Custom chart types
   - Data export capabilities

7. **Internationalization**
   - Multi-language support
   - Date/time localization
   - Currency formatting

8. **Accessibility**
   - WCAG 2.1 AA compliance
   - Keyboard navigation
   - Screen reader support

### Technical Debt

- Migrate from Create React App to Vite (faster builds)
- Improve component test coverage
- Refactor large components into smaller ones
- Standardize error handling patterns
- Add loading skeletons for better UX

## References

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Ant Design](https://ant.design/)
- [Styled Components](https://styled-components.com/)
- [React Router](https://reactrouter.com/)
- [Recharts](https://recharts.org/)
- [React Testing Library](https://testing-library.com/react)
