# Developer & Copilot Coding Agent Instructions  
## ProjectMeats – Repository Maintenance, PR Automation, and Coding Standards

---

## 🚩 Branch Organization, Naming, Tagging, and Promotion

- **Branch Structure:**  
  Use three main branches:
  - `development` (all features/fixes/experiments start + merge here)
  - `UAT` (staging; only code tested/reviewed in dev gets promoted here)
  - `main` (production; only code signed off in UAT is promoted here)

  See [Branch Workflow Checklist](../branch-workflow-checklist.md) for diagrams and step-by-step workflow.

- **Branch Naming Conventions:**  
  ```
  feature/<concise-topic>          # New features
  fix/<bug-topic>                  # Bugfixes
  chore/<infra-maintenance>        # Tooling, infra or CI
  refactor/<module>                # Refactoring
  hotfix/<emergency-topic>         # Emergency quick fixes
  ```
  - Use lowercase/hyphens; prefix by type for scanning.
  - Never work or merge directly in `main` or `UAT`.

- **Tagging & Releases:**  
  - Tag major/minor releases in `main` as `vX.Y.Z` after stable PR merges.
  - Use annotated tags for official releases.
  - Remove obsolete tags/branches as part of monthly repo maintenance.

- **Branch Protection:**  
  - Enable branch protection in GitHub settings: require status checks, reviews, restrict force-pushes/deletes on `main`, `UAT`, `development`.

---

## 💡 Auto-PR Creation for Environment Promotion (via GitHub Actions)

Auto-promotion between environments is implemented in `.github/workflows/` with workflows like below:

**Example**: Promote changes from `development` → `UAT` automatically after merge:

```yaml name=.github/workflows/promote-dev-to-uat.yml
name: Promote Dev to UAT

on:
  push:
    branches:
      - development
  workflow_dispatch:

jobs:
  create-uat-pr:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Create Pull Request to UAT
        uses: peter-evans/create-pull-request@v5
        with:
          source-branch: development
          destination-branch: uat
          title: 'Promote development to UAT'
          body: |
            Auto-created PR to promote tested changes from development to UAT environment.
          labels: uat-promotion, automation
          reviewers: Vacilator
```

Repeat similarly for `UAT` → `main`:

- Ensure only fast-forward, conflict-free merges
- PR is auto-created, not auto-merged (review/approval required, CI must pass)
- Template body should clearly state promotion reason/scope
- Configure branch protection to prevent unintended merges

---

## 📄 Documentation, File Placement, Standards & Logging

- **Docs Location:**  
  - Main guides: `/docs/`, root `README.md`
  - API/component: with module code (see `backend/apps/<app>/docs/`, `frontend/docs/`)
  - Workflow/process: `/docs/WORKFLOW.md` (gives branch flow, environments, CI)
  - Use usage/code examples + diagrams (`mermaid`/PlantUML)

- **Copilot Logging:**  
  - After each PR/task, add to `copilot-log.md`:
    ```
    ## Task: [Brief task] - [Date: YYYY-MM-DD]
    - **Actions Taken**:
    - **Misses/Failures**:
    - **Lessons Learned**:
    ```
- **Docs Updates:**  
  - Keep all env/config/infra docs up to date with code/workflow changes

---

## 🧹 Clean-Ups, Refactoring, & Repository Health

- **Regular Clean-Up:**  
  - Remove unused deps, dead code, deprecated configs/scripts
  - Archive inactive branches/tags (> 3 months old unless needed)
  - Format/lint all code before merge (Black for Python, Prettier for JS/TS)

- **Refactoring:**  
  - Modularize/reduce tech debt, maintain/test coverage
  - No breaking API/model changes without migration plan/docs/review
  - Remove feature flags once stable

- **Maintenance:**  
  - Audit permissions, branches, tags, dependencies monthly
  - Remove/Archive obsolete Terraform/HCL/infra unless strictly needed
  - Sync CI/CD pipeline configs to current branch/env structure

---

## ⚡ Requirements & Dependency Management

**Python/Django**
- Pin dependencies in `requirements*.txt`
- Lock with pip-compile/poetry (keep sync!)
- Run `pip-audit` for vulnerabilities regularly

**TypeScript/Node**
- Pin in `package.json`/`lock`
- Audit/cleanup regularly (`npm audit`, `yarn audit`)
- Remove unused packages monthly
- Enable Dependabot for automated update PRs

**Makefile/Shell**
- Document all scripts (`docs/dev-scripts.md`)
- Remove those not used in CI/docs

---

## 🔄 PR Automation & Review Requirements

- All code changes merged by PR, with required reviewers and checklist
- CI must pass on `development`, `UAT`, `main`
- Promotion/merges require environment-specific checks
- PR template must include migration notes, review checklist, clear scope/reasoning

---

## ⚙️ Coding Guidelines & Component Update Checklists

- Always update relevant files for component changes (models, admin, serializers, forms, templates, docs, tests)
- Test locally and in UAT before production
- Use descriptive commits referencing issues/PRs

**Django/Backend**
- Use Django model best practices
- Always commit/run migrations with model changes
- Update admin.py/serializers/tests/docs for new fields

**Frontend/TypeScript**
- Use best practices in components/state/UI/auth
- API contract compatibility with backend—document in frontend docs
- Add/maintain tests for all new UI/endpoint logic

**Continuous Improvement**
- Use copilot-log.md for postmortems and to prevent repeated errors
- Log and solve recurring issues through workflow updates

---

## 🛡️ Repository Maintenance for Ideal State

- Monthly audit: stale branches, tags, permissions, dependencies/CI
- Remove legacy infra (e.g., Terraform) unless referenced by docs/workflows
- README must cover all of: project goals, stack overview, branch/workflow, getting started
- Archive deprecated docs/code/scripts

---

## ⚡ Checklist Summaries

### Migration Verification Checklist

- [ ] Run `python manage.py makemigrations` locally
- [ ] Run `python manage.py migrate` locally
- [ ] Test model changes in Django admin interface
- [ ] Update admin.py for new fields
- [ ] Update serializers/forms/templates/tests/docs
- [ ] Test API endpoints with new fields
- [ ] Document migration dependencies and rollback steps

### Component Update Checklist

- [ ] **Models**: Field changes, types/constraints
- [ ] **Admin**: Register new fields
- [ ] **Serializers**: API coverage
- [ ] **Views**: Handle new fields
- [ ] **Forms**: Support in UI
- [ ] **Templates**: Show new fields
- [ ] **Tests**: Add/update tests
- [ ] **Docs**: Update documentation

### UAT and Production Verification
- **UAT**:  migrations/tests/UI/API/permissions
- **Production**: CI approvals/logs/db/api monitoring

---

## 🏷️ Common Pitfalls to Avoid

- Missing admin/serializer updates for model changes
- Incomplete migrations/tests
- API inconsistencies across stack
- Outdated documentation and stale branches/tags
- Unused/test/deprecated dependencies/scripts
- Direct merges to production branches
- Skipping code reviews or required CI status

---

## 🔗 References

- [Branch Workflow Checklist](../branch-workflow-checklist.md)
- [Django Best Practices](https://docs.djangoproject.com/en/5.0/topics/db/models/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [GitHub Flow & DX Best Practices](https://docs.github.com/en/get-started/quickstart/github-flow)
- Questions/improvements → open an issue or start a repo discussion.
