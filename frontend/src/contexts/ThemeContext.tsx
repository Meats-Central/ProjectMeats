/**
 * Theme Context Provider
 * 
 * Manages theme state (light/dark mode) across the application.
 * Persists theme preference to localStorage and syncs with backend.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Theme, themes } from '../config/theme';
import { getRuntimeConfig } from '../config/runtime';
import axios from 'axios';

type ThemeName = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  themeName: ThemeName;
  toggleTheme: () => void;
  setTheme: (themeName: ThemeName) => void;
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

  const theme = themes[themeName];

  // Sync theme to backend when it changes
  useEffect(() => {
    const syncThemeToBackend = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const apiBaseUrl = getRuntimeConfig('API_BASE_URL', 'http://localhost:8000');
        await axios.patch(
          `${apiBaseUrl}/api/v1/preferences/me/`,
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

  // Load theme from backend on mount
  useEffect(() => {
    const loadThemeFromBackend = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const apiBaseUrl = getRuntimeConfig('API_BASE_URL', 'http://localhost:8000');
        const response = await axios.get(
          `${apiBaseUrl}/api/v1/preferences/me/`,
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
