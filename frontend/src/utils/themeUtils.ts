/**
 * Theme Utilities - Dynamic brand color extraction
 * Note: colorthief types are not available, using 'any' sparingly
 */

// @ts-ignore - colorthief doesn't have TypeScript definitions
import ColorThief from 'colorthief';

export const extractBrandColors = async (logoUrl: string): Promise<number[] | null> => {
  try {
    const colorThief: any = new ColorThief();
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    
    return new Promise((resolve, reject) => {
      img.onload = () => {
        try {
          const color = colorThief.getColor(img);
          resolve(color);
        } catch (error) {
          reject(error);
        }
      };
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = logoUrl;
    });
  } catch (error) {
    console.error('Error in extractBrandColors:', error);
    return null;
  }
};

export const rgbToHex = (r: number, g: number, b: number): string => {
  return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
};

export const hexToRgb = (hex: string): [number, number, number] | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)] : null;
};

const getLuminance = (r: number, g: number, b: number): number => {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

export const isLightColor = (r: number, g: number, b: number): boolean => {
  return getLuminance(r, g, b) > 0.5;
};

export const lightenColor = (r: number, g: number, b: number, amount = 0.2): [number, number, number] => {
  return [
    Math.min(255, Math.round(r + (255 - r) * amount)),
    Math.min(255, Math.round(g + (255 - g) * amount)),
    Math.min(255, Math.round(b + (255 - b) * amount)),
  ];
};

export const darkenColor = (r: number, g: number, b: number, amount = 0.2): [number, number, number] => {
  return [
    Math.max(0, Math.round(r * (1 - amount))),
    Math.max(0, Math.round(g * (1 - amount))),
    Math.max(0, Math.round(b * (1 - amount))),
  ];
};

export const applyBrandColorToTheme = (rgb: number[]): void => {
  if (rgb && rgb.length === 3) {
    document.documentElement.style.setProperty('--color-primary', rgb.join(', '));
    const lighterRgb = lightenColor(rgb[0], rgb[1], rgb[2], 0.1);
    document.documentElement.style.setProperty('--color-primary-hover', lighterRgb.join(', '));
  }
};

export const loadTenantBrandingColors = async (logoUrl: string): Promise<void> => {
  try {
    const brandColor = await extractBrandColors(logoUrl);
    if (brandColor) {
      applyBrandColorToTheme(brandColor);
    }
  } catch (error) {
    console.error('Failed to load tenant branding colors:', error);
  }
};
