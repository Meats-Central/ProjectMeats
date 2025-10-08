# ProjectMeats Mobile App

React Native mobile application for the ProjectMeats multi-tenant SaaS platform.

## Overview

This mobile app provides core functionality for managing meat sales operations on mobile devices. It shares API endpoints and business logic with the web application while providing a mobile-optimized interface.

## Features

### Phase 1 (Current)
- ✅ User authentication
- ✅ Multi-tenant organization selection
- ✅ Basic dashboard with entity counts
- ✅ Shared utilities with web app
- ✅ TypeScript support
- ✅ Expo configuration

### Phase 2 (Planned)
- [ ] Customer management (CRUD operations)
- [ ] Supplier management (CRUD operations) 
- [ ] Contact management
- [ ] Plant management
- [ ] Carrier management
- [ ] Purchase order creation and management
- [ ] AI assistant integration
- [ ] Offline mode with sync
- [ ] Push notifications

## Tech Stack

- **React Native**: 0.74.5
- **Expo**: ~51.0.0
- **React Navigation**: ^6.1.0
- **TypeScript**: ~5.3.3
- **Axios**: ^1.6.0 (API communication)
- **Styled Components**: ^6.1.0
- **AsyncStorage**: For local data persistence

## Project Structure

```
mobile/
├── App.tsx                 # Main app component with navigation
├── app.json               # Expo configuration
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── babel.config.js        # Babel configuration
├── .eslintrc.js          # ESLint configuration
├── assets/               # Images, fonts, and other assets
└── src/
    ├── components/       # Reusable UI components
    ├── screens/         # Screen components
    │   ├── LoginScreen.tsx
    │   ├── TenantsScreen.tsx
    │   └── HomeScreen.tsx
    ├── services/        # API services
    │   └── ApiService.ts
    ├── types/           # TypeScript type definitions
    │   └── index.ts
    ├── utils/           # Utility functions
    ├── shared/          # Re-exports from /shared (cross-platform utilities)
    │   └── utils.ts     # Re-exports from ../../../shared/utils.ts
    └── styles/          # Global styles and themes
```

**Note**: The `src/shared/utils.ts` file re-exports utilities from the repository root's `/shared/utils.ts` to maintain a consistent import path across the mobile app while keeping the actual utilities in a centralized location shared between frontend and mobile.

## Getting Started

### Prerequisites

- Node.js (v18 or later)
- npm or yarn
- Expo CLI: `npm install -g expo-cli`
- For iOS: Xcode and iOS Simulator
- For Android: Android Studio and Android Emulator
- Expo Go app on your physical device (for testing)

### Installation

1. Install dependencies:
```bash
cd mobile
npm install
```

2. Start the development server:
```bash
npm start
# or
expo start
```

3. Run on specific platform:
```bash
# iOS Simulator
npm run ios

# Android Emulator  
npm run android

# Web browser (for testing)
npm run web
```

### Testing on Device

1. Install the Expo Go app on your iOS or Android device
2. Scan the QR code from the terminal or Expo DevTools
3. The app will load on your device

## Development

### Environment Configuration

The app automatically detects development vs production based on the `__DEV__` flag:

- **Development**: Uses `http://localhost:8000/api/v1` (assumes backend running locally)
- **Production**: Uses your production API URL (configure in `src/services/ApiService.ts`)

### Adding New Features

1. Create new screen components in `src/screens/`
2. Add navigation routes in `App.tsx`
3. Create API service methods in `src/services/ApiService.ts`
4. Add type definitions in `src/types/index.ts`
5. Use shared utilities from `/shared/utils.ts` (re-exported via `src/shared/utils.ts`)

### Code Sharing with Web App

The mobile app is designed to share as much code as possible with the web application:

- **Types**: Located in `src/types/index.ts`
- **Utilities**: Shared functions from `/shared/utils.ts` (re-exported in `src/shared/utils.ts`)
- **API Interfaces**: Same endpoints and data structures
- **Business Logic**: Consistent validation and processing

All shared utilities are centralized in the `/shared` directory at the repository root and re-exported in both `frontend/src/shared/utils.ts` and `mobile/src/shared/utils.ts` for easy access.

## Building for Production

### Android

1. Configure `app.json` with your app details
2. Build APK:
```bash
expo build:android
```

3. Build AAB (for Google Play):
```bash
expo build:android -t app-bundle
```

### iOS

1. Configure `app.json` with your app details
2. Build IPA:
```bash
expo build:ios
```

## Deployment

### Expo Publish

For OTA (Over-the-Air) updates:
```bash
expo publish
```

### App Stores

1. Build production binaries (see Building for Production)
2. Submit to Google Play Store and Apple App Store
3. Use Expo's build service or build locally with EAS Build

## API Integration

The mobile app uses the same REST API as the web application:

- **Base URL**: Configured in `ApiService.ts`
- **Authentication**: Token-based authentication
- **Endpoints**: Full CRUD operations for all entities
- **Multi-tenancy**: Tenant context maintained in API calls

### Key API Endpoints Used

- `POST /auth/login/` - User authentication
- `GET /api/tenants/my_tenants/` - Get user's tenants
- `GET /api/tenants/{id}/` - Get tenant details
- `GET /customers/` - List customers
- `GET /suppliers/` - List suppliers
- And more... (see `ApiService.ts`)

## Testing

```bash
# Run Jest tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- LoginScreen.test.tsx
```

## Troubleshooting

### Common Issues

1. **Metro bundler issues**: Clear cache with `expo start -c`
2. **iOS simulator not starting**: Reset simulator or restart Xcode
3. **Android emulator issues**: Ensure Android Studio is properly configured
4. **Network requests failing**: Check that backend server is running

### Debug Mode

- Shake your device or press `Cmd+D` (iOS) / `Cmd+M` (Android) to open developer menu
- Enable "Debug" mode to see network requests and Redux actions
- Use React Developer Tools for component inspection

## Contributing

1. Follow the existing code structure and naming conventions
2. Add TypeScript types for all new interfaces
3. Write tests for new components and utilities
4. Update this README when adding new features
5. Ensure code works on both iOS and Android

## License

This project is part of the ProjectMeats platform and follows the same licensing terms.

## Changelog

### Version 1.0.0 (Current)
- Initial mobile app setup
- User authentication flow
- Multi-tenant organization selection
- Basic dashboard with entity counts
- Shared utilities with web application
- TypeScript integration
- Expo configuration and build setup