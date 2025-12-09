# Next Steps - Post-Pipeline Stabilization

**Created:** 2025-12-09  
**Status:** Tracking immediate follow-up tasks

---

## ✅ Recently Completed

- [x] Stabilized deployment pipeline (all stages passing)
- [x] Implemented "Build Once, Deploy Many" pattern
- [x] Fixed frontend runtime environment variable injection
- [x] Migrated to SSH-based database migrations
- [x] Archived obsolete documentation
- [x] Created single source of truth (`DEVELOPMENT_PIPELINE.md`)

---

## 🎯 Immediate Next Steps

### 1. Frontend Test Migration (High Priority)

**Status:** ⚠️ Tests currently SKIPPED

**Background:**
Frontend tests are currently skipped in the pipeline due to incomplete migration from Jest to Vitest.

**Tasks:**
- [ ] **Replace test framework dependencies**
  ```bash
  cd frontend
  npm uninstall jest @types/jest ts-jest
  npm install --save-dev vitest @vitest/ui @testing-library/dom
  ```

- [ ] **Update import statements**
  ```typescript
  // ❌ Old (Jest)
  const mockFn = require('./module');
  
  // ✅ New (ES6)
  import { mockFn } from './module';
  ```

- [ ] **Replace Jest mocks with Vitest**
  ```typescript
  // ❌ Old
  jest.fn()
  jest.mock()
  
  // ✅ New
  vi.fn()
  vi.mock()
  ```

- [ ] **Update test configuration**
  ```typescript
  // vitest.config.ts
  import { defineConfig } from 'vitest/config';
  
  export default defineConfig({
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
    },
  });
  ```

- [ ] **Re-enable tests in workflow**
  ```yaml
  # .github/workflows/reusable-deploy.yml
  - name: Run frontend tests
    run: npm run test:ci
    # Remove: if: false
  ```

**References:**
- [Vitest Migration Guide](https://vitest.dev/guide/migration.html)
- [Testing Library with Vitest](https://testing-library.com/docs/react-testing-library/setup#vitest)

**Estimated Effort:** 2-3 days

---

### 2. Database Access Investigation (Medium Priority)

**Status:** 📋 Research Phase

**Background:**
Currently, migrations run via SSH on deployment servers because GitHub Actions runners cannot reach the private database. This adds SSH dependency and complexity.

**Options to Investigate:**

#### Option A: Whitelist GitHub Actions IP Ranges
**Pros:**
- Simple configuration change
- No infrastructure changes

**Cons:**
- 5,462 IP ranges to whitelist
- Ranges change frequently (maintenance burden)
- Security concern (broad access)

**Not Recommended** - Too many IPs, high maintenance

---

#### Option B: VPN/Bastion for GitHub Runners
**Pros:**
- Secure tunnel to private network
- Single IP to whitelist (VPN endpoint)
- Works with GitHub-hosted runners

**Cons:**
- Additional infrastructure (VPN server)
- Increased complexity
- Potential latency

**Services to Evaluate:**
- [Tailscale GitHub Action](https://github.com/tailscale/github-action)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [WireGuard + self-hosted gateway](https://www.wireguard.com/)

**Estimated Setup:** 1-2 weeks

---

#### Option C: Self-Hosted GitHub Runner in VPC
**Pros:**
- Runner lives in same VPC as database
- No firewall changes needed
- Fast, secure access
- Full control

**Cons:**
- Runner maintenance (updates, monitoring)
- Additional infrastructure cost
- Need to secure runner environment

**Requirements:**
- DigitalOcean Droplet (2GB RAM minimum)
- Register as self-hosted runner
- Configure auto-updates

**Estimated Setup:** 3-5 days

---

#### Recommendation
**Start with:** Current SSH approach (works reliably)  
**Evaluate:** Option C (self-hosted runner) if migration volume increases  
**Avoid:** Option A (too many IPs)

**Decision Deadline:** Q1 2026 (unless migration reliability issues arise)

---

### 3. Documentation Updates (Low Priority)

**Status:** 🔄 Ongoing

**Tasks:**
- [ ] Update `README.md` to reference new `DEVELOPMENT_PIPELINE.md`
- [ ] Update `CONTRIBUTING.md` with new workflow instructions
- [ ] Update `ROADMAP.md` to reflect completed pipeline work
- [ ] Archive remaining root-level docs to `docs/` subdirectories
- [ ] Create `docs/TROUBLESHOOTING.md` with common deployment issues

**Estimated Effort:** 1 day

---

### 4. Security Hardening (Medium Priority)

**Status:** 📋 Planned

**Tasks:**
- [ ] **Rotate SSH credentials**
  - Generate new SSH key pairs
  - Update GitHub secrets
  - Remove old keys from servers

- [ ] **Audit GitHub Actions permissions**
  - Review `permissions:` blocks in workflows
  - Apply principle of least privilege
  - Remove unused secrets

- [ ] **Container image scanning**
  ```yaml
  - name: Scan for vulnerabilities
    uses: aquasecurity/trivy-action@master
    with:
      image-ref: 'registry.digitalocean.com/meatscentral/projectmeats-backend:dev-${{ github.sha }}'
      severity: 'CRITICAL,HIGH'
  ```

- [ ] **Secrets rotation schedule**
  - Document rotation procedures
  - Set calendar reminders (quarterly)
  - Implement automated rotation where possible

**Estimated Effort:** 2-3 days

---

## 🚀 Long-Term Improvements

### 5. Zero-Downtime Deployments (Q2-Q3 2026)

**Current Downtime:** ~5-10 seconds during container swap

**Options:**
1. **Docker Compose with rolling updates** (simplest)
2. **Dokku** (lightweight PaaS)
3. **Kubernetes** (full orchestration, highest complexity)

**Recommendation:** Start with Dokku, migrate to K8s only if scale demands it.

---

### 6. Automated Rollback (Q2 2026)

**Concept:**
```bash
if ! health_check_passes; then
  echo "New deployment failed, rolling back..."
  docker run -d ... <PREVIOUS_WORKING_IMAGE>
  send_alert "Deployment failed, auto-rolled back to $PREVIOUS_SHA"
fi
```

**Requirements:**
- Track last successful SHA per environment
- Store in GitHub environment variables
- Implement automatic rollback logic in workflow

---

### 7. Canary Deployments (Q3 2026)

**Concept:**
- Deploy new version to 10% of traffic
- Monitor error rates for 10 minutes
- If stable → route 100% traffic
- If unstable → automatic rollback

**Requirements:**
- Load balancer with traffic splitting
- Monitoring/alerting system
- Multiple backend replicas

---

## 📊 Success Metrics

Track these to measure pipeline health:

| Metric | Target | Current |
|--------|--------|---------|
| **Deployment Success Rate** | >95% | ✅ 100% (recent) |
| **Deployment Duration** | <10 min | ✅ ~8 min |
| **Downtime per Deployment** | <30s | ⚠️ ~10s |
| **Rollback Time** | <5 min | 📋 Not measured |
| **Test Coverage (Backend)** | >80% | 📊 TBD |
| **Test Coverage (Frontend)** | >70% | ❌ 0% (tests skipped) |

---

## 🎯 Priority Matrix

```
High Priority, High Impact
├─ Frontend Test Migration
└─ Security Hardening

Medium Priority, Medium Impact
├─ Database Access Investigation
└─ Documentation Updates

Low Priority, High Impact (Future)
├─ Zero-Downtime Deployments
├─ Automated Rollback
└─ Canary Deployments
```

---

## 📝 Notes

- **Do NOT** start new initiatives until frontend tests are re-enabled
- **Do NOT** change migration approach without thorough testing in dev/UAT
- **Do** keep this document updated as tasks are completed
- **Do** reference this in sprint planning and standups

---

**Last Updated:** 2025-12-09  
**Next Review:** 2026-01-09 (monthly)
