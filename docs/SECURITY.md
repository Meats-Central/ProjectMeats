# Security Guidelines

**Last Updated**: November 2025

This document outlines security policies, vulnerability reporting procedures, and multi-tenant security best practices for ProjectMeats.

---

## 📋 Table of Contents

- [Reporting Vulnerabilities](#-reporting-vulnerabilities)
- [Security Response Process](#-security-response-process)
- [Multi-Tenant Security](#-multi-tenant-security)
- [Authentication & Authorization](#-authentication--authorization)
- [Data Protection](#-data-protection)
- [Infrastructure Security](#-infrastructure-security)
- [Development Security](#-development-security)
- [Compliance](#-compliance)

---

## 🚨 Reporting Vulnerabilities

### Responsible Disclosure

If you discover a security vulnerability in ProjectMeats, please report it responsibly:

1. **DO NOT** create a public GitHub issue
2. **Email**: Contact repository maintainers directly via GitHub, or use a security-specific contact if configured
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if available)

### What to Report

- Authentication/authorization bypasses
- Data exposure or leakage between tenants
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Insecure direct object references
- Security misconfigurations
- Sensitive data exposure

### Response Timeline

| Phase | Timeline |
|-------|----------|
| Initial acknowledgment | Within 48 hours |
| Preliminary assessment | Within 7 days |
| Fix development | Within 30 days (critical), 90 days (others) |
| Public disclosure | After fix is deployed |

---

## 🔄 Security Response Process

### Severity Classification

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Critical** | Active exploitation, data breach risk | Immediate (< 24 hours) |
| **High** | Significant impact, no active exploitation | < 7 days |
| **Medium** | Limited impact, requires specific conditions | < 30 days |
| **Low** | Minimal impact, defense-in-depth issue | < 90 days |

### Incident Response

1. **Detection**: Identify and confirm the vulnerability
2. **Containment**: Isolate affected systems if necessary
3. **Assessment**: Determine scope and impact
4. **Remediation**: Develop and test fix
5. **Deployment**: Roll out fix to all environments
6. **Communication**: Notify affected parties
7. **Post-mortem**: Document lessons learned

---

## 🏢 Multi-Tenant Security

### Isolation Strategies

ProjectMeats implements multiple layers of tenant isolation:

#### 1. Schema-Based Isolation (Primary)

Using `django-tenants` for PostgreSQL schema isolation:

```python
# Each tenant has its own database schema
TENANT_APPS = [
    "apps.suppliers",
    "apps.customers",
    "apps.purchase_orders",
    # ... tenant-specific data
]

SHARED_APPS = [
    "django_tenants",
    "apps.core",
    "apps.tenants",
    # ... shared infrastructure
]
```

**Benefits**:
- Complete data separation at database level
- No risk of cross-tenant data leakage
- Easier compliance with data residency requirements

#### 2. Row-Level Security (Secondary)

For shared-schema models, enforce tenant filtering:

```python
# Always filter by tenant in queries
class TenantAwareManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            tenant=get_current_tenant()
        )
```

#### 3. Request-Level Tenant Context

Middleware ensures tenant context is set for every request:

```python
# apps/tenants/middleware.py
class TenantMiddleware:
    def __call__(self, request):
        # Set tenant from subdomain/header
        tenant = self.get_tenant(request)
        set_current_tenant(tenant)
        # ...
```

### Tenant Security Best Practices

1. **Minimal Privileges**: Database users have only necessary permissions
2. **No Cross-Tenant Queries**: Never allow queries across tenant schemas
3. **Audit Logging**: Log all tenant data access
4. **Encryption**: Tenant data encrypted at rest
5. **Backup Isolation**: Separate backups per tenant (for enterprise)

### Common Vulnerabilities to Avoid

| Vulnerability | Prevention |
|---------------|------------|
| Tenant ID manipulation | Validate tenant from session, not request params |
| Insecure direct object reference | Always filter by current tenant |
| Mass assignment | Use explicit serializer fields |
| SQL injection | Use ORM, parameterized queries |
| Privilege escalation | Verify tenant membership on every request |

---

## 🔐 Authentication & Authorization

### Authentication Standards

- **Token-based**: JWT tokens with tenant context
- **Session security**: HttpOnly, Secure, SameSite cookies
- **Password policy**: Minimum 12 characters, complexity requirements
- **MFA**: Recommended for admin accounts (future enhancement)

### Role-Based Access Control (RBAC)

```python
# Example permission structure
ROLES = {
    'owner': ['*'],  # Full access
    'admin': ['read', 'write', 'delete', 'manage_users'],
    'manager': ['read', 'write', 'delete'],
    'user': ['read', 'write'],
    'viewer': ['read'],
}
```

### Authorization Checks

1. **View-level**: DRF permission classes
2. **Object-level**: Custom permission logic
3. **Field-level**: Serializer field permissions

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

---

## 🛡️ Data Protection

### Data Classification

| Classification | Examples | Protection Level |
|----------------|----------|------------------|
| **Public** | Marketing content | Basic |
| **Internal** | Business metrics | Standard |
| **Confidential** | Customer data, PII | High |
| **Restricted** | Credentials, tokens | Maximum |

### Encryption

- **At Rest**: PostgreSQL encryption, encrypted backups
- **In Transit**: TLS 1.2+ for all connections
- **Application Level**: Sensitive fields encrypted before storage

### Data Retention

- Follow GDPR/regulatory requirements
- Implement data deletion on tenant offboarding
- Audit log retention: 2 years minimum

---

## 🏗️ Infrastructure Security

### Network Security

- **Firewall**: Restrict database access to application servers
- **VPC**: Private networking for production
- **Load Balancer**: DDoS protection, rate limiting

### Environment Security

- **Secrets Management**: Use GitHub Secrets or vault
- **Environment Separation**: Isolated dev/staging/production
- **Access Control**: Principle of least privilege

### Monitoring & Alerting

- **Log Aggregation**: Centralized security logs
- **Intrusion Detection**: Monitor for suspicious activity
- **Automated Alerts**: Critical security events

---

## 💻 Development Security

### Secure Coding Practices

1. **Input Validation**: Validate all user input
2. **Output Encoding**: Prevent XSS via proper encoding
3. **Parameterized Queries**: Always use ORM or prepared statements
4. **Error Handling**: Never expose stack traces in production
5. **Dependency Management**: Regular security updates

### Code Review Checklist

- [ ] No hardcoded credentials or secrets
- [ ] Input validation for all user inputs
- [ ] Proper authentication/authorization checks
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection enabled
- [ ] Sensitive data not logged
- [ ] Error messages don't leak information

### Pre-Commit Security Hooks

```yaml
# .pre-commit-config.yaml includes
- repo: https://github.com/PyCQA/bandit
  hooks:
  - id: bandit
    args: ["-ll"]  # Security linting for Python
```

### Dependency Security

```bash
# Check for known vulnerabilities
pip install safety
safety check -r requirements.txt

# npm audit for frontend
cd frontend && npm audit
```

---

## ✅ Compliance

### Standards & Frameworks

ProjectMeats follows these security standards:

- **OWASP Top 10**: Web application security risks
- **GDPR**: Data protection for EU users
- **SOC 2**: Security, availability, confidentiality (future)

### Security Checklist by Environment

#### Development
- [ ] Use `.env` files (never commit)
- [ ] Local-only database access
- [ ] Debug mode enabled
- [ ] Pre-commit hooks active

#### Staging (UAT)
- [ ] HTTPS enforced
- [ ] Staging secrets (not production)
- [ ] Database access restricted
- [ ] Basic monitoring enabled

#### Production
- [ ] HTTPS with HSTS
- [ ] Strong secrets, regularly rotated
- [ ] Full monitoring and alerting
- [ ] Backup encryption
- [ ] Access logging
- [ ] Regular security audits

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Best Practices](https://docs.djangoproject.com/en/4.2/topics/security/)
- [React Security Best Practices](https://reactjs.org/docs/security.html)
- [GDPR Compliance Guide](https://gdpr.eu/)
- [django-tenants Security](https://django-tenants.readthedocs.io/)

---

## 📞 Security Contacts

- **Security Reports**: Contact repository maintainers directly via GitHub
- **Repository Issues**: Via GitHub issues (non-sensitive only)
- **Emergency**: Contact repository admins directly

---

**Document Owner**: ProjectMeats Security Team  
**Review Frequency**: Quarterly
