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
export { Select } from './Select';
export { PhoneInput } from './PhoneInput';

// Re-export types
export type { ButtonProps } from './Button';
export type { CardProps, CardHeaderProps, CardContentProps, CardFooterProps } from './Card';
export type { PageContainerProps } from './PageContainer';
export type { SelectProps, SelectOption } from './Select';
export type { PhoneInputProps } from './PhoneInput';
