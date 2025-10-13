# Changelog

All notable changes to ProjectMeats will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced error handling for read-only database errors in exception handler
  - Added specific detection for readonly database OperationalError messages
  - Returns HTTP 503 with clear error message for readonly database issues
  - Includes error_type flag for client-side handling
- New comprehensive test suite for readonly database error scenarios
  - Tests for exception handler readonly error detection
  - Tests for TenantMiddleware database error handling
  - Tests for admin access and session handling
  - Tests for database write permissions

### Changed
- Enhanced exception handler in `apps/core/exceptions.py`
  - Improved DatabaseError handling with specific readonly detection
  - Better error messages for read-only database scenarios
  - Changed status code from 500 to 503 for readonly errors

### Fixed
- Fixed syntax errors in `apps/purchase_orders/models.py`
  - Removed duplicate field definition for total_amount
- Fixed syntax errors in migration `0004_alter_purchaseorder_carrier_release_format_and_more.py`
  - Fixed missing parentheses in field definitions
  - Fixed duplicate name parameter in CreateModel operation

### Security
- Enhanced logging for readonly database errors to aid in security audits
- Better error messages that don't expose internal database details

## [4.2.7] - 2025-10-13

### Infrastructure
- PostgreSQL support already configured in development.py
- Database engine selection via DB_ENGINE environment variable
- Fallback to SQLite for backward compatibility

### Documentation
- Updated BACKEND_ARCHITECTURE.md with database configuration details
- Added guidance for PostgreSQL migration in DEPLOYMENT_GUIDE.md
