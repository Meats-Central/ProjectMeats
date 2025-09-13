import { StatusBar } from 'expo-status-bar';
import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import TenantsScreen from './src/screens/TenantsScreen';

// Services
import { ApiService } from './src/services/ApiService';

// Types
import { User, Tenant } from './src/types';

const Stack = createStackNavigator();

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [currentTenant, setCurrentTenant] = useState<Tenant | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      const userData = await AsyncStorage.getItem('userData');
      const tenantData = await AsyncStorage.getItem('currentTenant');
      
      if (token && userData) {
        setIsAuthenticated(true);
        setUser(JSON.parse(userData));
        ApiService.setAuthToken(token);
        
        if (tenantData) {
          setCurrentTenant(JSON.parse(tenantData));
        }
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async (token: string, userData: User) => {
    try {
      await AsyncStorage.setItem('authToken', token);
      await AsyncStorage.setItem('userData', JSON.stringify(userData));
      
      setIsAuthenticated(true);
      setUser(userData);
      ApiService.setAuthToken(token);
    } catch (error) {
      console.error('Error saving auth data:', error);
    }
  };

  const handleTenantSelect = async (tenant: Tenant) => {
    try {
      await AsyncStorage.setItem('currentTenant', JSON.stringify(tenant));
      setCurrentTenant(tenant);
    } catch (error) {
      console.error('Error saving tenant data:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.multiRemove(['authToken', 'userData', 'currentTenant']);
      setIsAuthenticated(false);
      setUser(null);
      setCurrentTenant(null);
      ApiService.removeAuthToken();
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  if (isLoading) {
    // You can replace this with a proper loading component
    return null;
  }

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isAuthenticated ? (
          <Stack.Screen name="Login">
            {(props) => (
              <LoginScreen
                {...props}
                onLogin={handleLogin}
              />
            )}
          </Stack.Screen>
        ) : !currentTenant ? (
          <Stack.Screen name="Tenants">
            {(props) => (
              <TenantsScreen
                {...props}
                user={user!}
                onTenantSelect={handleTenantSelect}
                onLogout={handleLogout}
              />
            )}
          </Stack.Screen>
        ) : (
          <Stack.Screen name="Home">
            {(props) => (
              <HomeScreen
                {...props}
                user={user!}
                tenant={currentTenant}
                onLogout={handleLogout}
                onSwitchTenant={() => setCurrentTenant(null)}
              />
            )}
          </Stack.Screen>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}