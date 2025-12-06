# Scoped Copilot Instructions

This directory contains scoped instruction files that guide GitHub Copilot's behavior for specific parts of the repository.

## Available Instruction Files

### backend.instructions.md
**Scope:** Backend Python/Django code
- Applies to: `backend/**/*.py`
- Covers: Django models, views, serializers, migrations, testing
- Key focus: Shared-schema multi-tenancy patterns, DRF best practices

### frontend.instructions.md
**Scope:** Frontend React/TypeScript code
- Applies to: `frontend/**/*.ts`, `frontend/**/*.tsx`, `frontend/**/*.jsx`
- Covers: React components, state management, TypeScript patterns, testing
- Key focus: Functional components, accessibility, performance optimization

### workflows.instructions.md
**Scope:** GitHub Actions workflows
- Applies to: `.github/workflows/**/*.yml`
- Covers: CI/CD patterns, deployment strategies, migration jobs
- Key focus: Immutable tagging, security best practices, idempotent migrations

## How Scoped Instructions Work

These instruction files use YAML frontmatter with `applyTo` patterns to automatically apply when Copilot is working on files matching those patterns. This ensures context-appropriate guidance without cluttering the main instructions file.

Example frontmatter:
```yaml
---
applyTo:
  - backend/**/*.py
---
```

## Best Practices

1. **Keep instructions focused**: Each file should cover only its domain
2. **Provide examples**: Show correct patterns with code examples
3. **Highlight critical rules**: Use clear warnings for common mistakes
4. **Include commands**: Show how to build, test, and run the code
5. **Stay consistent**: Align with the main `.github/copilot-instructions.md`

## Maintenance

- Review and update instructions when architectural patterns change
- Remove outdated references (e.g., deprecated libraries or patterns)
- Add new files for emerging areas (e.g., mobile, infrastructure)
- Test instructions by assigning tasks to Copilot and reviewing results

## References

- [Main Copilot Instructions](../copilot-instructions.md)
- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)
- [Custom Instructions Documentation](https://github.blog/changelog/2025-07-23-github-copilot-coding-agent-now-supports-instructions-md-custom-instructions/)
