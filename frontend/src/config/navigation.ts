/**
 * Navigation configuration for ProjectMeats frontend
 * 
 * Defines the main navigation structure for the application.
 * This is the central location for managing navigation items.
 */

export interface NavigationItem {
  label: string;
  path: string;
  icon?: string;
  children?: NavigationItem[];
  requiresAuth?: boolean;
  roles?: string[];
}

export const navigation: NavigationItem[] = [];
