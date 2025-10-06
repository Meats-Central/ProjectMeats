# Enhanced Copilot Instructions for ProjectMeats

## General Guidelines

1. Always create a new feature branch from main for each task, named descriptively (e.g., "feature/enhance-db-models").
2. Review the entire task context carefully, including any referenced previous responses or PRs.
3. If the task involves code changes, especially database models:
   - Update models.py files with new fields/relationships using Django best practices (e.g., appropriate field types, choices, null/blank, migrations).
   - Generate and apply migrations (makemigrations and migrate) locally to test.
   - Update related components: admin.py for admin interface visibility, serializers.py for API, views.py if needed, forms.py for frontend forms, and templates if displaying data.
   - Ensure no data loss or conflicts with existing data.
   - Test changes locally, then push to UAT for verification.

4. Assume repo structure: backend/apps/[app_name]/models.py, etc. Adjust if incorrect.
5. If changes affect production, ensure CI/CD workflow approvals are followed.
6. Minimize changes to only what's necessary; merge without duplication if fields exist.
7. After implementation, verify on UAT (uat.meatscentral.com) and note if fields are visible in admin or relevant pages. If not, fix deployment or configuration issues.
8. Commit with clear messages, e.g., "Enhance models and apply migrations for visibility".

## Continuous Learning and Logging

For every task, after completion and before creating the PR, append an entry to "copilot-log.md" in the root:

### Format:
```
## Task: [Brief task description] - [Date: YYYY-MM-DD]
- **Actions Taken**: [List key steps]
- **Misses/Failures**: [What was overlooked or didn't work, e.g., forgot to update admin.py leading to invisible fields]
- **Lessons Learned**: [Insights, e.g., Always check admin interface after model changes]
- **Efficiency Suggestions**: [Ways to improve next time, e.g., Add automated tests for model fields]
```

Keep entries concise (under 200 words). Review previous logs before starting a task to apply past learnings.
If a task repeats a past mistake, note it and propose preventive measures.

## Specific to DB Enhancements

1. For customer/supplier models: Ensure ManyToMany for proteins, ForeignKeys to Plant/Contact, etc., as per spreadsheets.
2. If fields aren't visible post-merge: Check if migrations were run on UAT/PROD, update admin registrations, or debug deployment.

## Migration Verification Checklist

Before considering any database-related task complete:

- [ ] Run `python manage.py makemigrations` locally
- [ ] Run `python manage.py migrate` locally  
- [ ] Test model changes in Django admin interface
- [ ] Update admin.py registrations for new fields
- [ ] Update serializers.py for API endpoints
- [ ] Update forms.py if frontend forms are affected
- [ ] Test API endpoints with new fields
- [ ] Verify field visibility in admin interface
- [ ] Document migration dependencies and potential rollback procedures

## Component Update Checklist

When adding new model fields or relationships:

- [ ] **Models**: Add fields with appropriate types, constraints, and defaults
- [ ] **Admin**: Update admin.py to display new fields in list_display, fieldsets, etc.
- [ ] **Serializers**: Update API serializers to include new fields
- [ ] **Views**: Update views if they need to handle new fields
- [ ] **Forms**: Update frontend forms if they interact with new fields
- [ ] **Templates**: Update templates if they display new data
- [ ] **Tests**: Add or update tests for new functionality
- [ ] **Documentation**: Update API documentation and field descriptions

## UAT and Production Verification

After deploying changes:

1. **UAT Environment** (uat.meatscentral.com):
   - [ ] Verify migrations were applied successfully
   - [ ] Check admin interface for field visibility
   - [ ] Test API endpoints return new fields
   - [ ] Verify frontend displays new data correctly
   - [ ] Check for any console errors or warnings

2. **Production Environment**:
   - [ ] Confirm CI/CD workflow approvals completed
   - [ ] Monitor deployment logs for migration success
   - [ ] Verify field visibility and functionality
   - [ ] Check performance impact of new fields
   - [ ] Monitor error logs for any issues

## Error Prevention Strategies

1. **Before Starting**: Always review copilot-log.md for similar past tasks and lessons learned
2. **During Development**: Use the checklists above systematically
3. **Testing**: Test locally before pushing, test on UAT before production
4. **Documentation**: Document any non-standard approaches or workarounds
5. **Review**: Have changes reviewed by team members for complex modifications

## Common Pitfalls to Avoid

1. **Missing Admin Updates**: Always update admin.py when adding model fields
2. **Incomplete Migrations**: Ensure migrations handle data preservation and constraints
3. **API Inconsistencies**: Update serializers to maintain API contract consistency
4. **Frontend Disconnection**: Ensure frontend components can handle new data structures
5. **Testing Gaps**: Don't skip local testing before UAT deployment
6. **Documentation Lag**: Update documentation as changes are made, not afterwards

## Best Practices for Django Development

1. **Model Fields**: Use appropriate field types, set null/blank correctly, add help_text
2. **Migrations**: Review generated migrations before applying, add custom migrations when needed
3. **Admin Interface**: Use fieldsets, list_display, search_fields for better UX
4. **API Design**: Follow RESTful principles, maintain backward compatibility
5. **Error Handling**: Implement proper error handling and user feedback
6. **Performance**: Consider database indexing for frequently queried fields