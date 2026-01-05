/**
 * Theme Utilities - Dynamic brand color extraction and manipulation
 * 
 * Features:
 * - Extract dominant color from tenant logo
 * - Convert colors between formats (hex, rgb, hsl)
 * - Calculate contrast ratios for accessibility
 * - Generate color variations (lighter, darker)
 */

import ColorThief from 'colorthief';

/**
 * Extract the dominant color from an image URL
 * Returns RGB array [r, g, b] or null if extraction fails
 */
export const extractBrandColors = async (logoUrl: string): Promise<number[] | null> => {
  try {
    const colorThief = new ColorThief();
    const img = new Image();
    
    // Enable CORS for cross-origin images
    img.crossOrigin = 'Anonymous';
    
    return new Promise((resolve, reject) => {
      img.onload = () => {
        try {
          const color = colorThief.getColor(img);
          resolve(color);
        } catch (error) {
          console.error('Error extracting color:', error);
          reject(error);
        }
      };
      
      img.onerror = () => {
        console.error('Error loading image for color extraction');
        reject(new Error('Failed to load image'));
      };
      
      img.src = logoUrl;
    });
  } catch (error) {
    console.error('Error in extractBrandColors:', error);
    return null;
  }
};

/**
 * Convert RGB array to hex string
 */
export const rgbToHex = (r: number, g: number, b: number): string => {
  return '#' + [r, g, b].map(x => {
    const hex = x.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
};

/**
 * Convert hex to RGB array
 */
export const hexToRgb = (hex: string): [number, number, number] | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16),
  ] : null;
};

/**
 * Calculate relative luminance for contrast ratio
 */
const getLuminance = (r: number, g: number, b: number): number => {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

/**
 * Calculate contrast ratio between two colors
 * Returns ratio (1 to 21)
 */
export const getContrastRatio = (
  rgb1: [number, number, number],
  rgb2: [number, number, number]
): number => {
  const lum1 = getLuminance(...rgb1);
  const lum2 = getLuminance(...rgb2);
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
};

/**
 * Determine if color is light or dark
 * Returns true if light (use dark text), false if dark (use light text)
 */
export const isLightColor = (r: number, g: number, b: number): boolean => {
  const luminance = getLuminance(r, g, b);
  return luminance > 0.5;
};

/**
 * Generate a lighter variation of a color
 */
export const lightenColor = (r: number, g: number, b: number, amount: number = 0.2): [number, number, number] => {
  return [
    Math.min(255, Math.round(r + (255 - r) * amount)),
    Math.min(255, Math.round(g + (255 - g) * amount)),
    Math.min(255, Math.round(b + (255 - b) * amount)),
  ];
};

/**
 * Generate a darker variation of a color
 */
export const darkenColor = (r: number, g: number, b: number, amount: number = 0.2): [number, number, number] => {
  return [
    Math.max(0, Math.round(r * (1 - amount))),
    Math.max(0, Math.round(g * (1 - amount))),
    Math.max(0, Math.round(b * (1 - amount))),
  ];
};

/**
 * Apply extracted brand color to CSS variables
 */
export const applyBrandColorToTheme = (rgb: number[]): void => {
  if (rgb && rgb.length === 3) {
    document.documentElement.style.setProperty('--color-primary', rgb.join(', '));
    
    // Generate lighter version for hover states
    const lighterRgb = lightenColor(rgb[0], rgb[1], rgb[2], 0.1);
    document.documentElement.style.setProperty('--color-primary-hover', lighterRgb.join(', '));
    
    // Generate darker version for active states
    const darkerRgb = darkenColor(rgb[0], rgb[1], rgb[2], 0.1);
    document.documentElement.style.setProperty('--color-primary-active', darkerRgb.join(', '));
  }
};

/**
 * Load and apply tenant brand colors from logo
 */
export const loadTenantBrandingColors = async (logoUrl: string): Promise<void> => {
  try {
    const brandColor = await extractBrandColors(logoUrl);
    if (brandColor) {
      applyBrandColorToTheme(brandColor);
      console.log('Applied brand colors:', rgbToHex(brandColor[0], brandColor[1], brandColor[2]));
    }
  } catch (error) {
    console.error('Failed to load tenant branding colors:', error);
    // Fallback to default theme colors (already set in CSS)
  }
};
