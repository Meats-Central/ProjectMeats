/**
 * Semantic UI Components
 * 
 * These components use CSS variables defined in index.css,
 * allowing tenant-specific branding without component changes.
 * 
 * All components reference semantic color names (primary, surface)
 * instead of hardcoded colors, making them truly themeable.
 */

export { Button } from './Button';
export { Card, CardHeader, CardContent, CardFooter } from './Card';
export { PageContainer } from './PageContainer';

// Re-export types if needed
export type { default as ButtonProps } from './Button';
