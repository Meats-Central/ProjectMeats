/**
 * Theme Context Provider
 * 
 * Manages theme state (light/dark mode) across the application.
 * Persists theme preference to localStorage and syncs with backend.
 * Fetches tenant-specific branding (logo, colors) from backend.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Theme, themes, lightTheme, darkTheme } from '../config/theme';
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
  // Initialize theme from localStorage or default to 'light'
  const [themeName, setThemeName] = useState<ThemeName>(() => {
    const stored = localStorage.getItem('theme');
    return (stored === 'light' || stored === 'dark') ? stored : 'light';
  });
  
  const [tenantBranding, setTenantBranding] = useState<TenantBranding | null>(null);
  const [customTheme, setCustomTheme] = useState<Theme | null>(null);

  // Use custom theme if tenant branding is loaded, otherwise use default theme
  const theme = customTheme || themes[themeName];

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

  // Update custom theme when themeName changes (switch between light/dark)
  useEffect(() => {
    if (tenantBranding) {
      // Deep copy to avoid mutations
      const baseLight = { 
        ...lightTheme, 
        colors: { ...lightTheme.colors }
      };
      const baseDark = { 
        ...darkTheme, 
        colors: { ...darkTheme.colors }
      };
      
      // Apply tenant primary colors to both themes
      baseLight.colors.primary = tenantBranding.primaryColorLight;
      baseLight.colors.primaryHover = adjustColor(tenantBranding.primaryColorLight, -10);
      baseLight.colors.primaryActive = adjustColor(tenantBranding.primaryColorLight, -20);
      baseLight.colors.sidebarActive = tenantBranding.primaryColorLight;
      
      baseDark.colors.primary = tenantBranding.primaryColorDark;
      baseDark.colors.primaryHover = adjustColor(tenantBranding.primaryColorDark, 10);
      baseDark.colors.primaryActive = adjustColor(tenantBranding.primaryColorDark, -10);
      baseDark.colors.sidebarActive = tenantBranding.primaryColorDark;
      
      // Set the custom theme based on current theme name
      setCustomTheme(themeName === 'light' ? baseLight : baseDark);
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

// Helper function to adjust color brightness
function adjustColor(color: string, percent: number): string {
  const num = parseInt(color.replace('#', ''), 16);
  const amt = Math.round(2.55 * percent);
  const R = ((num >> 16)) + amt;
  const G = ((num >> 8) & 0x00FF) + amt;
  const B = (num & 0x0000FF) + amt;
  return '#' + (
    0x1000000 +
    (R < 255 ? (R <= 0 ? 0 : R) : 255) * 0x10000 +
    (G < 255 ? (G <= 0 ? 0 : G) : 255) * 0x100 +
    (B < 255 ? (B <= 0 ? 0 : B) : 255)
  ).toString(16).slice(1).toUpperCase();
}

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
