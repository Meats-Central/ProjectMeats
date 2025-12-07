# 502 Error Fix - Quick Summary

**Status:** ✅ FIXED  
**Site:** https://dev.meatscentral.com working perfectly

---

## What Was Wrong
Backend and frontend are on **separate servers**. Nginx tried to proxy to `localhost` (wrong server).

## The Fix
Use backend's **public IP** in nginx config and docker container.

---

## 🚀 To Deploy (3 Steps)

### 1. Add GitHub Secret
https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions
- Name: `DEV_BACKEND_IP`
- Value: `157.245.114.182`

### 2. Merge PR #1224
https://github.com/Meats-Central/ProjectMeats/pull/1224

### 3. Deploy
Push to development → Deployment works automatically

---

## 📋 For UAT/Production

**Get IPs:**
```bash
ssh server && ip addr show eth0 | grep "inet "
```

**Add Secrets:**
- `UAT_BACKEND_IP` = UAT backend public IP
- `PROD_BACKEND_IP` = Prod backend public IP

**Done!** Workflows already updated.

---

## 📖 Full Docs
- `DEPLOYMENT_SETUP_COMPLETE.md` - Complete guide
- `FINAL_DEPLOYMENT_STATUS.md` - Status report

**That's it! 🎉**
