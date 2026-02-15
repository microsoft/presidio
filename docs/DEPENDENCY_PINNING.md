# Dependency Pinning Security Guide

This document explains the dependency pinning strategy used in the Presidio repository to enhance security and ensure reproducible builds.

## Overview

Dependency pinning is a security best practice that ensures:
- **Reproducible builds**: The same code always builds with the same dependencies
- **Security**: Protection against compromised dependencies or supply chain attacks
- **Stability**: Avoiding unexpected breaking changes from dependency updates

## Pinning Strategy

### 1. GitHub Actions (Workflows)

GitHub Actions in workflow files are pinned using either commit SHAs or semantic version tags:

```yaml
# Preferred: Pinned to commit SHA (immutable)
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v6.0.0

# Acceptable: Semantic version tag (when SHA cannot be verified)
uses: actions/setup-python@v6 # v6
uses: github/codeql-action/init@v3 # v3
uses: microsoft/security-devops-action@v1 # v1
uses: py-cov-action/python-coverage-comment-action@v3 # v3
```

**Rationale**: 
- Commit SHAs are immutable and ensure the exact same action code runs every time (preferred)
- Semantic version tags (e.g., `@v6`, `@v3`) are acceptable when commit SHAs cannot be verified, but provide less security
- Tags like `@latest` or major version tags can be moved to point to different commits

**Note**: Several actions use semantic version tags instead of commit SHAs due to verification limitations. This is a pragmatic tradeoff between security and functionality.

**Actions using version tags:**
- `actions/setup-python@v6` - SHA could not be verified
- `github/codeql-action/*@v3` - SHA could not be verified  
- `microsoft/security-devops-action@v1` - SHA could not be verified
- `py-cov-action/python-coverage-comment-action@v3` - SHA could not be verified


### 2. Docker Base Images

All Docker base images are pinned using SHA256 digests:

```dockerfile
# ❌ Before (mutable tag)
FROM python:3.12-slim

# ✅ After (immutable digest)
FROM python:3.12-slim@sha256:9e01bf1ae5db7649a236da7be1e94ffbbbdd7a93f867dd0d8d5720d9e1f89fab
```

**Rationale**: Docker tags like `3.12-slim` can be updated to newer builds. SHA256 digests guarantee the exact same base image is used.

### 3. Build Tools (pip, poetry, ruff, build)

Build tools are pinned to specific versions in workflows and Dockerfiles:

```yaml
# In GitHub Actions workflows
- name: Install Poetry
  run: |
    python -m pip install --upgrade pip==25.0.0
    python -m pip install poetry==2.3.2
```

```dockerfile
# In Dockerfiles
RUN pip install poetry==2.3.2 \
    && poetry install --no-root --only=main -E server
```

**Rationale**: Ensures consistent tooling across all build environments.

### 4. Application Dependencies (Poetry Lock Files)

Application dependencies are managed through Poetry's lock files (`poetry.lock`), which:
- Pin exact versions of all dependencies (including transitive ones)
- Include SHA256 hashes for verification
- Are automatically generated when running `poetry install`

**No additional action needed**: Poetry's lock files already provide hash-based verification for all application dependencies.

### 5. Requirements Files

For sample applications and E2E tests, `requirements.txt` files specify minimum versions:

```txt
requests>=2.32.4
pytest
```

**Rationale**: Sample code demonstrates typical usage patterns. In production deployments, these should be replaced with Poetry-managed dependencies or requirements files with pinned versions and hashes.

## Maintaining Pinned Dependencies

### Automated Updates

Use tools like Dependabot or Renovate to:
1. Monitor for new versions of pinned dependencies
2. Automatically create PRs to update pins
3. Run tests to verify compatibility

### Manual Updates

When updating GitHub Actions:
1. Check the action's repository for the latest version tag
2. Find the commit SHA for that tag
3. Update the workflow file with both SHA and version comment

When updating Docker images:
1. Pull the desired image: `docker pull python:3.12-slim`
2. Get the digest: `docker inspect python:3.12-slim | grep "sha256"`
3. Update the Dockerfile with the digest

When updating build tools:
1. Check PyPI for the latest stable version
2. Update version numbers in workflows and Dockerfiles
3. Test the build locally before committing

## Security Benefits

1. **Supply Chain Attack Prevention**: Pinned dependencies cannot be silently replaced with malicious versions
2. **Reproducible Builds**: The same source code always produces the same build artifacts
3. **Audit Trail**: Clear record of which exact versions are being used
4. **Controlled Updates**: Dependency updates happen deliberately through code review, not automatically

## References

- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Docker Image Pinning Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [OSSF Scorecard - Dependency Pinning](https://github.com/ossf/scorecard/blob/main/docs/checks.md#pinned-dependencies)
