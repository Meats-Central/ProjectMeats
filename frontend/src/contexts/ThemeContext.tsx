/**
 * Theme Context Provider
 * 
 * NEW: Semantic Design System Implementation
 * - Injects tenant colors into CSS variables at runtime
 * - Manages theme state (light/dark mode) across the application
 * - Persists theme preference to localStorage and syncs with backend
 * - Fetches tenant-specific branding (logo, colors) from backend
 * 
 * Components now reference CSS variables (--color-primary) instead of hardcoded colors.
 * This allows the same component to look completely different for each tenant.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Theme, themes, lightTheme, darkTheme, injectTenantColors } from '../config/theme';
import { getRuntimeConfig } from '../config/runtime';
import axios from 'axios';

type ThemeName = 'light' | 'dark';

interface TenantBranding {
  logoUrl: string | null;
  primaryColorLight: string;
  primaryColorDark: string;
  tenantName: string;
}

interface ThemeContextType {
  theme: Theme;
  themeName: ThemeName;
  toggleTheme: () => void;
  setTheme: (themeName: ThemeName) => void;
  tenantBranding: TenantBranding | null;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Initialize theme from localStorage or default to 'dark'
  const [themeName, setThemeName] = useState<ThemeName>(() => {
    const stored = localStorage.getItem('theme');
    return (stored === 'light' || stored === 'dark') ? stored : 'dark';
  });
  
  const [tenantBranding, setTenantBranding] = useState<TenantBranding | null>(null);

  // NEW: Always use CSS variable-based themes (no custom theme object needed)
  const theme = themes[themeName];

  // Apply theme to document body (now sets data-theme attribute for CSS variable switching)
  useEffect(() => {
    document.body.setAttribute('data-theme', themeName);
    // Background and text color are now controlled by CSS variables
    // No need to manually set body styles here
  }, [themeName]);

  // Sync theme to backend when it changes
  useEffect(() => {
    const syncThemeToBackend = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const apiBaseUrl = getRuntimeConfig('API_BASE_URL', 'http://localhost:8000/api/v1');
        await axios.patch(
          `${apiBaseUrl}/preferences/me/`,
          { theme: themeName },
          {
            headers: {
              Authorization: `Token ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );
      } catch (error) {
        console.error('Failed to sync theme to backend:', error);
      }
    };

    syncThemeToBackend();
  }, [themeName]);

  // Load tenant branding from backend on mount (only once)
  useEffect(() => {
    const loadTenantBranding = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const apiBaseUrl = getRuntimeConfig('API_BASE_URL', 'http://localhost:8000/api/v1');
        const response = await axios.get(
          `${apiBaseUrl}/tenants/current_theme/`,
          {
            headers: {
              Authorization: `Token ${token}`,
            },
          }
        );

        const branding = {
          logoUrl: response.data.logo_url,
          primaryColorLight: response.data.primary_color_light,
          primaryColorDark: response.data.primary_color_dark,
          tenantName: response.data.name,
        };
        
        setTenantBranding(branding);
      } catch (error) {
        console.error('Failed to load tenant branding:', error);
      }
    };

    loadTenantBranding();
  }, []); // Only run once on mount

  // NEW: Inject tenant colors into CSS variables when branding or theme changes
  useEffect(() => {
    if (tenantBranding) {
      console.log('🎨 Injecting tenant branding into CSS variables:', {
        tenant: tenantBranding.tenantName,
        theme: themeName,
        primaryLight: tenantBranding.primaryColorLight,
        primaryDark: tenantBranding.primaryColorDark,
      });

      // Inject colors into CSS variables (defined in config/theme.ts)
      injectTenantColors(
        tenantBranding.primaryColorLight,
        tenantBranding.primaryColorDark,
        themeName
      );
    }
  }, [themeName, tenantBranding]);

  // Load theme from backend on mount
  useEffect(() => {
    const loadThemeFromBackend = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const apiBaseUrl = getRuntimeConfig('API_BASE_URL', 'http://localhost:8000/api/v1');
        const response = await axios.get(
          `${apiBaseUrl}/preferences/me/`,
          {
            headers: {
              Authorization: `Token ${token}`,
            },
          }
        );

        const backendTheme = response.data.theme;
        if (backendTheme === 'light' || backendTheme === 'dark') {
          setThemeName(backendTheme);
          localStorage.setItem('theme', backendTheme);
        }
      } catch (error) {
        console.error('Failed to load theme from backend:', error);
      }
    };

    loadThemeFromBackend();
  }, []);

  const toggleTheme = () => {
    const newTheme = themeName === 'light' ? 'dark' : 'light';
    setThemeName(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const setTheme = (newTheme: ThemeName) => {
    setThemeName(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const value: ThemeContextType = {
    theme,
    themeName,
    toggleTheme,
    setTheme,
    tenantBranding,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
