# GitHub Actions CI for External Contributors

This document explains how the GitHub Actions CI workflow handles pull requests from external contributors.

## Problem

When external contributors open pull requests, the GitHub Actions CI workflow fails because it requires Azure secrets that are not available to external contributors for security reasons:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID` 
- `AZURE_SUBSCRIPTION_ID`
- `ACR_NAME`

## Solution

The CI workflow now automatically detects whether Azure secrets are available and runs different job paths accordingly.

### For External Contributors (No Secrets)

**Detection**: `secrets.ACR_NAME == ''`

**Jobs executed**:
1. `lint` - Runs `ruff check` for code style validation
2. `test` - Unit tests for all components across Python 3.9-3.12
3. `local-build-and-test` - Builds Docker images locally and runs E2E tests

**Process**:
- Docker images are built locally using `docker compose build`
- No image pushing to Azure Container Registry
- E2E tests run against locally built images
- Same test coverage as the full pipeline

### For Maintainers (With Secrets)

**Detection**: `secrets.ACR_NAME != ''`

**Jobs executed**:
1. `lint` - Code style validation
2. `test` - Unit tests for all components
3. `build-platform-images` - Multi-platform Docker builds (amd64, arm64)
4. `create-manifests` - Multi-platform manifest creation in ACR
5. `e2e-tests` - E2E tests using images from ACR

**Process**:
- Images built for multiple platforms and pushed to ACR
- Full deployment pipeline with registry operations
- E2E tests run against ACR images

## Benefits

- **Security**: External contributors cannot access Azure secrets
- **Functionality**: Full validation including E2E tests for external contributors
- **Performance**: Local builds are faster than registry operations
- **Compatibility**: Existing workflow unchanged for maintainers
- **Coverage**: Same E2E test suite runs in both paths

## Environment Variables

The workflow automatically sets appropriate environment variables:

**External contributors**:
```bash
REGISTRY_NAME=''
IMAGE_PREFIX=''
TAG=''
```

**Maintainers**:
```bash
REGISTRY_NAME=${{ secrets.ACR_NAME }}.azurecr.io
TAG=gha${{ github.run_number }}
```

## Testing

Both paths run the same E2E test suite located in `e2e-tests/`, ensuring consistent validation regardless of the execution path.