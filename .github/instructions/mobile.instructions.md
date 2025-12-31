---
applyTo:
  - mobile/**/*.ts
  - mobile/**/*.tsx
  - mobile/**/*.jsx
  - mobile/src/**/*
---

# Mobile Development Instructions

## React Native + TypeScript Standards

### Component Structure
```typescript
// Use functional components with TypeScript
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';

type RootStackParamList = {
  MyScreen: { id: string };
};

interface MyScreenProps {
  navigation: StackNavigationProp<RootStackParamList, 'MyScreen'>;
  route: RouteProp<RootStackParamList, 'MyScreen'>;
}

export const MyScreen: React.FC<MyScreenProps> = ({ navigation, route }) => {
  // Component logic with type-safe navigation and route params
  return <View><Text>Content</Text></View>;
};
```

### State Management
- Use React hooks (`useState`, `useEffect`, `useContext`)
- Share business logic with frontend via `/shared` utilities
- Keep local state minimal
- Use React Navigation for screen navigation

### API Integration
```typescript
// Use axios with proper typing (shared with frontend)
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface ApiResponse {
  data: any[];
  message: string;
}

const fetchData = async (): Promise<ApiResponse> => {
  const response = await axios.get<ApiResponse>(`${API_BASE_URL}/endpoint`);
  return response.data;
};
```

## Testing

### Run Tests
```bash
# All tests
npm run test

# Watch mode
npm run test:watch

# iOS simulator
npm run ios

# Android emulator
npm run android
```

### Test Patterns
```typescript
import { render } from '@testing-library/react-native';
import { MyScreen } from './MyScreen';

describe('MyScreen', () => {
  it('renders correctly', () => {
    const { getByText } = render(<MyScreen />);
    expect(getByText('Content')).toBeTruthy();
  });
});
```

## Code Quality

### TypeScript
- Enable strict mode
- No `any` types (use `unknown` if needed)
- Define interfaces for all props
- Use type inference where possible
- Share types with frontend via `/shared/types`

### Style Guidelines
- Use functional components
- 2-space indentation
- Single quotes for strings
- Semicolons required
- Max line length: 100 characters

### Linting
```bash
npm run lint
npm run type-check
```

## Styling

### React Native StyleSheet
```typescript
import { StyleSheet, View, Text } from 'react-native';

const MyComponent = () => (
  <View style={styles.container}>
    <Text style={styles.title}>Hello</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
});
```

### Responsive Design
- Use Dimensions API for screen size
- Test on various device sizes (phones, tablets)
- Use flexbox for layouts
- Consider safe area insets (iOS notches)

## Performance

### Optimization Techniques
```typescript
// Use React.memo for expensive components
export const MyComponent = React.memo(({ data }) => {
  return <ExpensiveView data={data} />;
});

// Use useMemo for expensive calculations
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);

// Use useCallback for callbacks
const memoizedCallback = useCallback(() => {
  doSomething(a, b);
}, [a, b]);
```

### List Optimization
```typescript
// Use FlatList for long lists
<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={({ item }) => <ItemComponent item={item} />}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  windowSize={10}
/>
```

## Accessibility

### Required Practices
- Add `accessibilityLabel` to all interactive elements
- Use `accessibilityHint` for additional context
- Support VoiceOver (iOS) and TalkBack (Android)
- Ensure minimum touch target size: 44x44 points
- Test with screen readers enabled

### Example
```typescript
<TouchableOpacity
  accessibilityLabel="Close modal"
  accessibilityHint="Double tap to dismiss"
  onPress={onClose}
>
  <Icon name="close" />
</TouchableOpacity>
```

## Multi-Tenancy

### Tenant Context
```typescript
// Use shared tenant context
import { useTenant } from '@/shared/contexts/TenantContext';

const MyScreen = () => {
  const { tenant, switchTenant } = useTenant();
  
  return <Text>Current: {tenant.name}</Text>;
};
```

### API Calls with Tenant
```typescript
// Include tenant in API headers
import { getAuthHeaders } from '@/shared/utils/auth';

const fetchTenantData = async (tenantId: string) => {
  return axios.get(`/api/tenants/${tenantId}/data`, {
    headers: await getAuthHeaders(),
  });
};
```

## Platform-Specific Code

### Conditional Rendering
```typescript
import { Platform } from 'react-native';

const MyComponent = () => (
  <View>
    {Platform.OS === 'ios' && <IOSOnlyComponent />}
    {Platform.OS === 'android' && <AndroidOnlyComponent />}
  </View>
);
```

### Platform-Specific Files
```
MyComponent.ios.tsx  // iOS version
MyComponent.android.tsx  // Android version
```

## Navigation

### React Navigation Setup
```typescript
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

export const AppNavigator = () => (
  <NavigationContainer>
    <Stack.Navigator>
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Details" component={DetailsScreen} />
    </Stack.Navigator>
  </NavigationContainer>
);
```

## Common Patterns

### Form Handling
```typescript
import { useState } from 'react';
import { TextInput, Button } from 'react-native';

const MyForm = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = () => {
    if (!email) {
      setError('Email is required');
      return;
    }
    // Handle submission
  };
  
  return (
    <>
      <TextInput
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        accessibilityLabel="Email input"
      />
      {error && <Text style={styles.error}>{error}</Text>}
      <Button title="Submit" onPress={handleSubmit} />
    </>
  );
};
```

### Error Boundaries
```typescript
import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };
  
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  
  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorScreen />;
    }
    return this.props.children;
  }
}
```

## Environment Variables

### Access Variables
```typescript
// Using react-native-config or similar
import Config from 'react-native-config';

const API_URL = Config.API_BASE_URL;
const ENVIRONMENT = Config.ENVIRONMENT;
```

## Native Modules

### Linking Native Dependencies
```bash
# iOS
cd ios && pod install && cd ..

# Android
# Automatically linked via autolinking
```

### Test on Real Devices
- Always test camera, location, notifications on physical devices
- Test on both iOS and Android
- Test on various OS versions
- Test offline scenarios and poor connectivity

## Debugging

### React Native Debugger
- Use Flipper for debugging
- Enable Fast Refresh for instant updates
- Use console.log sparingly (affects performance)
- Profile with React DevTools

### Common Issues
```typescript
// Issue: Component not updating
// Solution: Ensure state updates are immutable

// ❌ Wrong
state.items.push(newItem);

// ✅ Correct
setState({ items: [...state.items, newItem] });
```

## Deployment

### Build Commands
```bash
# iOS
npm run ios:release

# Android
npm run android:release
```

### App Store Guidelines
- Follow Apple App Store and Google Play Store guidelines
- Ensure proper app icons and splash screens
- Test on TestFlight (iOS) and Internal Testing (Android) first
- Include privacy policy and terms of service
