# Example: Generated Issue for Deployment Failure

This is an example of what the automatically generated issue would look like when a staging deployment fails.

---

**Title:** Fix Frontend UAT2 Staging Deployment Failure - 2024-09-13

**Labels:** `bug`, `deployment`, `staging`, `urgent`  
**Assignee:** @copilot

## 🚨 Frontend UAT2 Staging Deployment Failed

**Workflow:** Deploy Frontend to UAT2 Staging  
**Branch:** development  
**Commit:** abc1234567890abcdef1234567890abcdef123456  
**Triggered by:** @developer-username  
**Failed on:** 9/13/2024, 2:30:45 PM  

### 🔗 Workflow Run Details
- **Direct Link:** [View Failed Workflow Run](https://github.com/Meats-Central/ProjectMeats/actions/runs/123456789)
- **Run ID:** 123456789

### ❌ Failed Jobs
```
deploy: https://github.com/Meats-Central/ProjectMeats/actions/runs/123456789/job/987654321
```

### 📋 Error Details
<details>
<summary>Click to view error logs (last 50 lines)</summary>

```
npm ERR! code ENOTFOUND
npm ERR! syscall getaddrinfo  
npm ERR! errno ENOTFOUND
npm ERR! network request to https://registry.npmjs.org/some-package failed
npm ERR! network This is a problem related to network connectivity.
npm ERR! network In most cases you are behind a proxy or have bad network settings.

> frontend@1.0.0 build
> react-scripts build

Creating an optimized production build...
Failed to compile.

Module not found: Error: Can't resolve 'some-missing-module' in '/github/workspace/frontend/src'
ERROR in ./src/components/Dashboard.tsx
Module not found: Error: Can't resolve 'some-missing-module'
npm ERR! code 1
npm ERR! path /github/workspace/frontend  
npm ERR! command failed
npm ERR! command sh -c react-scripts build
```
</details>

### 🔧 Resolution Instructions

**Important:** Any pull requests created to fix this issue should be made against the **`development`** branch, not `main`.

### 📝 Next Steps
1. Review the error logs above and the [workflow run](https://github.com/Meats-Central/ProjectMeats/actions/runs/123456789)
2. Investigate the root cause of the deployment failure
3. Create a pull request with the fix targeting the **`development`** branch
4. Test the fix in the development environment before merging
5. Monitor the next deployment to ensure the issue is resolved

### 📚 Related Documentation
- [Deployment Documentation](./DEPLOYMENT_DOCUMENTATION.md)
- [Troubleshooting Guide](./docs/legacy/DEPLOYMENT_GUIDE.md#-troubleshooting)

---
*This issue was automatically created by the deployment failure monitoring workflow.*

---

**Comment (automatically added):**

🔍 **Additional Context:**

This deployment failure was automatically detected. Please:

1. Check if this is a recurring issue by searching for similar deployment failures
2. Review recent changes to the frontend that might have caused this failure
3. Verify that all environment variables and secrets are properly configured
4. Consider if this requires an immediate hotfix or can be addressed in the normal development cycle

If this is a critical issue affecting production readiness, please escalate accordingly.