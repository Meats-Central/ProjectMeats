# Network Error Troubleshooting Guide

## Issue: Supplier Creation Network Error

### Background
Users were encountering generic "Network Error" messages when attempting to create suppliers. This error occurred when the frontend couldn't successfully communicate with the backend API.

### Root Cause
The original error handling in the frontend application didn't provide sufficient diagnostic information. When Axios encountered network-level failures (CORS issues, DNS failures, connection timeouts, etc.), it would only show "Network Error" without any context about:
- Which endpoint failed
- What type of network error occurred
- Authentication/tenant status
- The full URL being accessed

### Solution Implemented
Enhanced error handling with the following improvements:

#### 1. Better Error Message Detection
The `getErrorMessage` function now:
- Extracts detailed error messages from server responses (checking multiple fields: `message`, `error`, `detail`, `details`)
- Identifies specific network error codes:
  - `ERR_NETWORK`: Cannot connect to server (network/CORS/firewall issues)
  - `ECONNABORTED`: Connection timeout
  - `ERR_BAD_REQUEST`: Invalid request format
- Provides HTTP status code-specific messages (401, 403, 404, 500, etc.)
- Includes the full URL in error messages to help identify endpoint issues

#### 2. Enhanced Logging
Added comprehensive debug and error logging that includes:
- Request details: endpoint, authentication status, tenant status, base URL
- Error details: status code, error code, URL, response/request presence
- Action context (create vs update)

#### 3. User-Friendly Messages
Error messages now provide:
- Clear description of what went wrong
- Actionable guidance (e.g., "Please check your internet connection")
- Full endpoint URL for support/debugging purposes

### Common Network Error Scenarios

#### Scenario 1: CORS Configuration Issue
**Symptom:** Error code `ERR_NETWORK` when accessing API from browser
**Error Message:** "Unable to connect to the server at [URL]. Please check your internet connection or contact support."
**Diagnosis:** Check browser console for CORS-related errors
**Solution:** Ensure CORS_ALLOWED_ORIGINS in backend settings includes the frontend domain

#### Scenario 2: Backend Not Running
**Symptom:** Connection refused
**Error Message:** "Network error while connecting to [URL]..."
**Diagnosis:** Backend server is not accessible
**Solution:** Verify backend is running and accessible at the configured API_BASE_URL

#### Scenario 3: Wrong API Endpoint
**Symptom:** 404 Not Found
**Error Message:** "The requested resource was not found."
**Diagnosis:** API endpoint doesn't exist or URL is misconfigured
**Solution:** Verify API_BASE_URL configuration and endpoint paths

#### Scenario 4: Authentication Issues
**Symptom:** 401 Unauthorized
**Error Message:** "Authentication required. Please log in again."
**Diagnosis:** No auth token or expired token
**Solution:** User needs to log in again

#### Scenario 5: Missing Tenant Context
**Symptom:** 400 Bad Request with validation error
**Error Message:** Server response indicating tenant context is required
**Diagnosis:** User not associated with a tenant or X-Tenant-ID header missing
**Solution:** Ensure user is properly associated with a tenant

#### Scenario 6: Request Timeout
**Symptom:** Error code `ECONNABORTED` or timeout message
**Error Message:** "Request to [URL] timed out. The server may be experiencing high load. Please try again."
**Diagnosis:** Server taking too long to respond (>30s)
**Solution:** Check server performance, consider increasing timeout

### Debugging Steps

1. **Check Browser Console**
   - Look for detailed error logs with `[API]` or `[Suppliers]` prefix
   - Review the logged error details (status, code, URL, etc.)

2. **Verify Configuration**
   - Check `window.ENV.API_BASE_URL` in browser console
   - Ensure it matches the backend server address

3. **Check Network Tab**
   - Open browser DevTools Network tab
   - Look for failed requests to `/api/v1/suppliers/`
   - Check request headers (Authorization, X-Tenant-ID)
   - Review response details

4. **Verify Backend**
   - Ensure backend server is running
   - Check backend logs for errors
   - Verify CORS configuration includes frontend domain

5. **Test Authentication**
   - Check `localStorage.getItem('authToken')` in browser console
   - Verify token is present and valid
   - Check `localStorage.getItem('tenantId')` for tenant context

### Files Modified
- `frontend/src/services/apiService.ts`: Enhanced error handling and logging
- `frontend/src/pages/Suppliers.tsx`: Improved error display
- This documentation file

### Additional Resources
- Axios Error Handling: https://axios-http.com/docs/handling_errors
- Django CORS Headers: https://github.com/adamchainz/django-cors-headers
- Browser DevTools Network Panel: https://developer.chrome.com/docs/devtools/network/
