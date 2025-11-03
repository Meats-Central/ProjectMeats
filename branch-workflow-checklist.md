# Branch Workflow Checklist

This checklist ensures safe and correct progress from development to production.  
Applicable to repos with three main branches/environments: **development**, **UAT**, and **main**.

## Workflow Steps

1. **Start All Work from `development`**
   - Create new feature/bugfix branches _from_ `development`.
     - Example: `git checkout development && git checkout -b feature/new-api-endpoint`

2. **Feature Branch PRs**
   - Merge feature branches _into_ `development` via Pull Request.
   - Ensure automated tests and code review are completed.

3. **Promote Changes to UAT**
   - Once ready for UAT, create a PR to merge `development` into `UAT`.
   - UAT is for staging, final testing, and user acceptance.
   - Automated UAT tests must pass.

4. **Production Release**
   - Once UAT is fully validated, create a PR to merge `UAT` into `main`.
   - This triggers the release to production.

## Tips

- _Never create feature branches from `main` or `UAT`._
- PR base branch should always be `development` unless promoting to UAT or main.
- Keep branches up to date with upstream merges if multiple features are developed in parallel.
- Tag production releases in `main` for traceability.

## Diagram

```mermaid
graph LR
    A[development] -- Feature/Fix PRs --> A
    A -- Promote to UAT --> B[UAT]
    B -- On UAT approval --> C[main (production)]
```

## Reference

- [Meats-Central/ProjectMeats](https://github.com/Meats-Central/ProjectMeats)
- See `.github/copilot-instructions.md` for Copilot and PR automation guidelines.