/**
 * Theme configuration for ProjectMeats
 * 
 * NEW: Semantic Design System using CSS Variables
 * This allows tenant-specific branding without component changes.
 * 
 * Components should use semantic names (primary, surface) not specific colors.
 * The ThemeContext injects tenant colors into CSS variables at runtime.
 */

export interface Theme {
  name: 'light' | 'dark';
  colors: {
    // Primary colors (semantic references to CSS variables)
    primary: string;
    primaryHover: string;
    primaryActive: string;
    primaryForeground: string;
    
    // Secondary colors
    secondary: string;
    secondaryHover: string;
    secondaryForeground: string;
    
    // Background colors
    background: string;
    surface: string;
    surfaceHover: string;
    surfaceForeground: string;
    
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
    danger: string;
    
    // Shadow
    shadow: string;
    shadowMedium: string;
    shadowLarge: string;
  };
}

/**
 * Helper function to create theme from CSS variables
 * This ensures all themes reference the CSS variables defined in index.css
 */
const createThemeFromCSSVars = (name: 'light' | 'dark'): Theme => ({
  name,
  colors: {
    // Brand colors - dynamically set by tenant
    primary: 'rgb(var(--color-primary))',
    primaryHover: 'rgb(var(--color-primary-hover))',
    primaryActive: 'rgb(var(--color-primary-active))',
    primaryForeground: 'rgb(var(--color-primary-foreground))',
    
    secondary: 'rgb(var(--color-secondary))',
    secondaryHover: 'rgb(var(--color-secondary-hover))',
    secondaryForeground: 'rgb(var(--color-secondary-foreground))',
    
    // UI colors
    background: 'rgb(var(--color-background))',
    surface: 'rgb(var(--color-surface))',
    surfaceHover: 'rgb(var(--color-surface-hover))',
    surfaceForeground: 'rgb(var(--color-surface-foreground))',
    
    // Text colors
    textPrimary: 'rgb(var(--color-text-primary))',
    textSecondary: 'rgb(var(--color-text-secondary))',
    textDisabled: 'rgb(var(--color-text-disabled))',
    
    // Sidebar colors
    sidebarBackground: 'rgb(var(--color-sidebar-background))',
    sidebarText: 'rgb(var(--color-sidebar-text))',
    sidebarTextHover: 'rgb(var(--color-sidebar-text-hover))',
    sidebarActive: 'rgb(var(--color-sidebar-active))',
    sidebarBorder: 'rgb(var(--color-sidebar-border))',
    
    // Header colors
    headerBackground: 'rgb(var(--color-header-background))',
    headerText: 'rgb(var(--color-header-text))',
    headerBorder: 'rgb(var(--color-header-border))',
    
    // Border colors
    border: 'rgb(var(--color-border))',
    borderLight: 'rgb(var(--color-border-light))',
    
    // Status colors (standardized across themes)
    success: 'rgb(var(--color-success))',
    warning: 'rgb(var(--color-warning))',
    error: 'rgb(var(--color-error))',
    info: 'rgb(var(--color-info))',
    danger: 'rgb(var(--color-danger))',
    
    // Shadows
    shadow: 'var(--shadow-sm)',
    shadowMedium: 'var(--shadow-md)',
    shadowLarge: 'var(--shadow-lg)',
  },
});

// Themes now reference CSS variables instead of hardcoded colors
export const lightTheme: Theme = createThemeFromCSSVars('light');
export const darkTheme: Theme = createThemeFromCSSVars('dark');

export const themes = {
  light: lightTheme,
  dark: darkTheme,
};

/**
 * Utility: Convert hex color to RGB format for CSS variables
 * @param hex - Hex color code (e.g., '#DC2626')
 * @returns RGB values as string (e.g., '220, 38, 38')
 */
export const hexToRgb = (hex: string): string => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : '0, 0, 0';
};

/**
 * Utility: Inject tenant colors into CSS variables
 * @param primaryColorLight - Primary color for light theme
 * @param primaryColorDark - Primary color for dark theme
 * @param themeName - Current theme ('light' or 'dark')
 */
export const injectTenantColors = (
  primaryColorLight: string,
  primaryColorDark: string,
  themeName: 'light' | 'dark'
) => {
  const root = document.documentElement;
  
  if (themeName === 'light') {
    root.style.setProperty('--color-primary', hexToRgb(primaryColorLight));
    root.style.setProperty('--color-primary-hover', hexToRgb(adjustColor(primaryColorLight, -10)));
    root.style.setProperty('--color-primary-active', hexToRgb(adjustColor(primaryColorLight, -20)));
    root.style.setProperty('--color-sidebar-active', hexToRgb(primaryColorLight));
  } else {
    root.style.setProperty('--color-primary', hexToRgb(primaryColorDark));
    root.style.setProperty('--color-primary-hover', hexToRgb(adjustColor(primaryColorDark, 10)));
    root.style.setProperty('--color-primary-active', hexToRgb(adjustColor(primaryColorDark, -10)));
    root.style.setProperty('--color-sidebar-active', hexToRgb(primaryColorDark));
  }
};

/**
 * Utility: Adjust color brightness
 * @param color - Hex color code
 * @param percent - Percentage to adjust (-100 to 100)
 * @returns Adjusted hex color
 */
export function adjustColor(color: string, percent: number): string {
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
