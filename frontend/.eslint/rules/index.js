/**
 * ESLint Custom Rules Plugin
 * 
 * Contains custom rules specific to ProjectMeats UI standards.
 * 
 * Rules:
 * - no-hardcoded-colors: Prevents hardcoded hex colors in favor of theme variables
 * 
 * @author ProjectMeats UI Standardization Team
 * @date 2026-01-10
 */

module.exports = {
  rules: {
    'no-hardcoded-colors': require('./no-hardcoded-colors')
  }
};
