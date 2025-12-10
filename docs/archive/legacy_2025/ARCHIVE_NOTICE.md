# ARCHIVED: Legacy Secret Documentation

**⚠️ THIS DOCUMENT IS OBSOLETE**

**Date Archived**: December 10, 2025  
**Reason**: Superseded by Environment Manifest System (v3.3)  
**Authority**: `config/env.manifest.json` + `docs/CONFIGURATION_AND_SECRETS.md`

---

## Why This Was Archived

This document was created before the implementation of the **unified environment manifest system**. It contains:
- Hardcoded secret names
- Manual configuration instructions  
- Environment-specific details now defined in the manifest
- Potential for secret drift due to multiple sources of truth

## What Replaced It

**Single Source of Truth**: [`config/env.manifest.json`](../../config/env.manifest.json)

**Documentation**: [`docs/CONFIGURATION_AND_SECRETS.md`](../CONFIGURATION_AND_SECRETS.md)

**Tooling**: `python config/manage_env.py audit`

## If You Found This While Searching

**DO NOT USE THIS DOCUMENT**

Instead:
1. Read the manifest: `cat config/env.manifest.json`
2. Run the audit: `python config/manage_env.py audit`
3. Consult official docs: `docs/CONFIGURATION_AND_SECRETS.md`

---

## Original Document Preserved Below for Historical Reference

*(The archived content follows this notice)*
