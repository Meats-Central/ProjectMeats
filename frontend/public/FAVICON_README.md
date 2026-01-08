# Environment-Specific Favicons

## Overview
ProjectMeats uses different favicon colors to visually distinguish between environments in browser tabs.

## Favicon Files

### Production (Default)
- **File**: `favicon.ico`
- **Color**: Red
- **Label**: "MC" (Meats Central)
- **Description**: Default production favicon (already exists)

### Development
- **File**: `favicon-dev.ico`
- **Color**: Green
- **Label**: "DEV"
- **Description**: Used in development environment
- **Status**: ⚠️ **NEEDS TO BE CREATED**

### UAT/Staging
- **File**: `favicon-uat.ico`
- **Color**: Yellow/Orange
- **Label**: "UAT"
- **Description**: Used in UAT/staging environment
- **Status**: ⚠️ **NEEDS TO BE CREATED**

## Icon Specifications

### Size
- **Recommended**: 32x32 pixels or 64x64 pixels
- **Format**: .ico (supports multiple sizes in one file)
- **Alternative**: .png files can also work

### Design Guidelines
1. **Simple and Bold**: Text should be legible at small sizes
2. **High Contrast**: Use solid backgrounds with contrasting text
3. **Consistent Style**: All three should follow the same design pattern

### Color Palette
- **Production (Red)**: `#DC2626` (red-600)
- **Development (Green)**: `#16A34A` (green-600)
- **UAT (Yellow)**: `#EAB308` (yellow-500) or `#F59E0B` (amber-500)

## How It Works

The dynamic favicon switching is implemented in `src/App.tsx`:

```typescript
// Reads environment from window.ENV (set by deployment pipeline)
const environment = window.ENV?.ENVIRONMENT || 'development';

// Selects appropriate favicon
if (environment === 'development') {
  faviconPath = '/favicon-dev.ico'; // Green
  titlePrefix = '[DEV] ';
} else if (environment === 'uat') {
  faviconPath = '/favicon-uat.ico'; // Yellow
  titlePrefix = '[UAT] ';
} else {
  faviconPath = '/favicon.ico'; // Red (production)
}
```

## Creating the Icons

### Option 1: Using Figma/Sketch
1. Create 64x64px artboard with colored background
2. Add white text ("DEV" or "UAT")
3. Export as .ico or .png
4. If .png, convert to .ico using online tool

### Option 2: Using Online Generator
1. Visit: https://favicon.io/
2. Use "Text" option
3. Enter "DEV" or "UAT"
4. Choose background color
5. Download and rename to `favicon-dev.ico` or `favicon-uat.ico`

### Option 3: Using Photoshop
1. Create 64x64px canvas
2. Fill with background color
3. Add text layer with "DEV" or "UAT" in white
4. Save for Web as .ico format

## Installation

Once created, place the icon files in:
```
frontend/public/
├── favicon.ico (already exists - red)
├── favicon-dev.ico (needs creation - green)
└── favicon-uat.ico (needs creation - yellow)
```

## Testing

After adding the icons:

1. **Local Development**:
   - Run `npm start`
   - Check browser tab shows green "DEV" icon
   - Check title shows "[DEV] ProjectMeats"

2. **UAT Environment**:
   - Deploy to UAT
   - Visit https://uat.meatscentral.com
   - Check browser tab shows yellow "UAT" icon
   - Check title shows "[UAT] ProjectMeats"

3. **Production**:
   - Visit https://meatscentral.com
   - Check browser tab shows red "MC" icon
   - Check title shows "ProjectMeats" (no prefix)

## Benefits

✅ **Instant Visual Feedback**: Know which environment you're in at a glance
✅ **Prevent Mistakes**: Reduces risk of making changes in wrong environment
✅ **Professional**: Shows attention to detail and developer experience
✅ **Multi-Tab Clarity**: Easy to identify tabs when multiple environments open

## Implementation Status

- ✅ **Logic**: Dynamic switching implemented in App.tsx
- ✅ **Production Icon**: Already exists (red MC)
- ⚠️ **Dev Icon**: Needs to be created (green DEV)
- ⚠️ **UAT Icon**: Needs to be created (yellow UAT)

## Quick Action Items

1. Create `favicon-dev.ico` (green with "DEV" text)
2. Create `favicon-uat.ico` (yellow with "UAT" text)
3. Place both files in `frontend/public/`
4. Test in each environment
5. Update this README status to ✅ when complete
