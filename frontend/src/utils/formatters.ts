/**
 * Date and Time Formatters with Timezone Support
 * 
 * All formatters automatically convert UTC timestamps to the user's local timezone.
 * This fixes the "wrong time" issue where backend sends UTC but displays show incorrect times.
 * 
 * Usage:
 *   formatToLocal('2026-01-08T14:00:00Z') // → "Jan 8, 2026 9:00 AM" (EST)
 *   formatDateLocal('2026-01-08T14:00:00Z') // → "Jan 8, 2026"
 *   formatTimeLocal('2026-01-08T14:00:00Z') // → "9:00 AM"
 */

/**
 * Format UTC datetime to local timezone with full date and time
 * Format: "MMM d, yyyy h:mm a" (e.g., "Jan 8, 2026 9:00 AM")
 */
export const formatToLocal = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return 'Invalid Date';
    }
    
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date);
  } catch (error) {
    console.error('Error formatting date:', error, dateString);
    return 'Error';
  }
};

/**
 * Format UTC date to local timezone (date only, no time)
 * Format: "MMM d, yyyy" (e.g., "Jan 8, 2026")
 */
export const formatDateLocal = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return 'Invalid Date';
    }
    
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(date);
  } catch (error) {
    console.error('Error formatting date:', error, dateString);
    return 'Error';
  }
};

/**
 * Format UTC time to local timezone (time only, no date)
 * Format: "h:mm a" (e.g., "9:00 AM")
 */
export const formatTimeLocal = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return 'Invalid Time';
    }
    
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date);
  } catch (error) {
    console.error('Error formatting time:', error, dateString);
    return 'Error';
  }
};

/**
 * Format UTC datetime with seconds precision
 * Format: "MMM d, yyyy h:mm:ss a" (e.g., "Jan 8, 2026 9:00:35 AM")
 */
export const formatToLocalWithSeconds = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return 'Invalid Date';
    }
    
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    }).format(date);
  } catch (error) {
    console.error('Error formatting datetime:', error, dateString);
    return 'Error';
  }
};

/**
 * Format relative time (e.g., "2 hours ago", "in 3 days")
 * Uses Intl.RelativeTimeFormat for internationalization
 */
export const formatRelativeTime = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    const now = new Date();
    
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return 'Invalid Date';
    }
    
    const diffMs = date.getTime() - now.getTime();
    const diffSec = Math.round(diffMs / 1000);
    const diffMin = Math.round(diffSec / 60);
    const diffHour = Math.round(diffMin / 60);
    const diffDay = Math.round(diffHour / 24);
    
    const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
    
    if (Math.abs(diffSec) < 60) {
      return rtf.format(diffSec, 'second');
    } else if (Math.abs(diffMin) < 60) {
      return rtf.format(diffMin, 'minute');
    } else if (Math.abs(diffHour) < 24) {
      return rtf.format(diffHour, 'hour');
    } else if (Math.abs(diffDay) < 30) {
      return rtf.format(diffDay, 'day');
    } else {
      // For dates beyond 30 days, show full date
      return formatDateLocal(dateString);
    }
  } catch (error) {
    console.error('Error formatting relative time:', error, dateString);
    return 'Error';
  }
};

/**
 * Get user's timezone name (e.g., "America/New_York", "Europe/London")
 */
export const getUserTimezone = (): string => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
};

/**
 * Get user's timezone offset (e.g., "-05:00", "+01:00")
 */
export const getTimezoneOffset = (): string => {
  const date = new Date();
  const offset = -date.getTimezoneOffset();
  const hours = Math.floor(Math.abs(offset) / 60);
  const minutes = Math.abs(offset) % 60;
  const sign = offset >= 0 ? '+' : '-';
  
  return `${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
};

/**
 * Check if a date is today
 */
export const isToday = (dateString: string): boolean => {
  const date = new Date(dateString);
  const today = new Date();
  
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
};

/**
 * Check if a date is in the past
 */
export const isPast = (dateString: string): boolean => {
  const date = new Date(dateString);
  const now = new Date();
  
  return date.getTime() < now.getTime();
};

/**
 * Check if a date is in the future
 */
export const isFuture = (dateString: string): boolean => {
  const date = new Date(dateString);
  const now = new Date();
  
  return date.getTime() > now.getTime();
};

/**
 * Legacy compatibility: Re-export shared utils with local timezone awareness
 */
export { formatCurrency } from '../../../shared/utils';

// Note: These maintain backward compatibility but DON'T convert timezones
// Use formatToLocal() instead for new code
export { 
  formatDate as formatDateUTC,
  formatDateTime as formatDateTimeUTC 
} from '../../../shared/utils';
