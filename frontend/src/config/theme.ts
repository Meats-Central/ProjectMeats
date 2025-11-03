/**
 * Theme configuration for ProjectMeats
 * 
 * Defines light and dark color schemes for the application
 */

export interface Theme {
  name: 'light' | 'dark';
  colors: {
    // Primary colors
    primary: string;
    primaryHover: string;
    primaryActive: string;
    
    // Background colors
    background: string;
    surface: string;
    surfaceHover: string;
    
    // Text colors
    textPrimary: string;
    textSecondary: string;
    textDisabled: string;
    
    // Sidebar colors
    sidebarBackground: string;
    sidebarText: string;
    sidebarTextHover: string;
    sidebarActive: string;
    sidebarBorder: string;
    
    // Header colors
    headerBackground: string;
    headerText: string;
    headerBorder: string;
    
    // Border colors
    border: string;
    borderLight: string;
    
    // Status colors
    success: string;
    warning: string;
    error: string;
    info: string;
    
    // Shadow
    shadow: string;
    shadowMedium: string;
    shadowLarge: string;
  };
}

export const lightTheme: Theme = {
  name: 'light',
  colors: {
    primary: '#3498db',
    primaryHover: '#2980b9',
    primaryActive: '#2472a4',
    
    background: '#f8f9fa',
    surface: '#ffffff',
    surfaceHover: '#f0f0f0',
    
    textPrimary: '#2c3e50',
    textSecondary: '#6c757d',
    textDisabled: '#adb5bd',
    
    sidebarBackground: '#2c3e50',
    sidebarText: '#bdc3c7',
    sidebarTextHover: '#ffffff',
    sidebarActive: '#3498db',
    sidebarBorder: '#34495e',
    
    headerBackground: '#ffffff',
    headerText: '#2c3e50',
    headerBorder: '#e9ecef',
    
    border: '#dee2e6',
    borderLight: '#e9ecef',
    
    success: '#27ae60',
    warning: '#f39c12',
    error: '#e74c3c',
    info: '#3498db',
    
    shadow: 'rgba(0, 0, 0, 0.05)',
    shadowMedium: 'rgba(0, 0, 0, 0.1)',
    shadowLarge: 'rgba(0, 0, 0, 0.15)',
  },
};

export const darkTheme: Theme = {
  name: 'dark',
  colors: {
    primary: '#3498db',
    primaryHover: '#5dade2',
    primaryActive: '#2980b9',
    
    background: '#1a1a1a',
    surface: '#2d2d2d',
    surfaceHover: '#3d3d3d',
    
    textPrimary: '#e0e0e0',
    textSecondary: '#a0a0a0',
    textDisabled: '#606060',
    
    sidebarBackground: '#1f1f1f',
    sidebarText: '#a0a0a0',
    sidebarTextHover: '#e0e0e0',
    sidebarActive: '#3498db',
    sidebarBorder: '#2d2d2d',
    
    headerBackground: '#2d2d2d',
    headerText: '#e0e0e0',
    headerBorder: '#3d3d3d',
    
    border: '#3d3d3d',
    borderLight: '#4d4d4d',
    
    success: '#27ae60',
    warning: '#f39c12',
    error: '#e74c3c',
    info: '#3498db',
    
    shadow: 'rgba(0, 0, 0, 0.3)',
    shadowMedium: 'rgba(0, 0, 0, 0.5)',
    shadowLarge: 'rgba(0, 0, 0, 0.7)',
  },
};

export const themes = {
  light: lightTheme,
  dark: darkTheme,
};
