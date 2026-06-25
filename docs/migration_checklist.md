# Microsoft → Data Privacy Stack migration checklist

Tracking the de-Microsoft-ing of Presidio as it moves to
`github.com/data-privacy-stack`. Brand assets already use **Data Privacy Stack /
"Inky"** (`docs/assets/dps-icon.svg`, `docs/assets/inkey.svg`).

**Decisions made:**
- Copyright / author identity → **Data Privacy Stack**.
- Canonical endpoints (docs site URL, Docker Hub namespace, contact email) → **to be
  provided by the maintainer** before edits; replacements below are marked accordingly.

---

## ✅ Docs pass completed (2026-06-25) — `docs/` only

Done across `docs/`:
- `github.com/[Mm]icrosoft/presidio` → `github.com/data-privacy-stack/presidio` (incl.
  `raw.githubusercontent.com`).
- `microsoft.github.io/presidio` → `data-privacy-stack.github.io/presidio`
  *(GitHub Pages convention — confirm the final docs URL/custom domain)*.
- `faq.md` — rewrote the "Microsoft product / who created it" sections for community
  governance under Data Privacy Stack.
- Product-name prose "Microsoft Presidio" → "Presidio" (`getting_started.md`,
  `learn_presidio/concepts.md`, `recipes/index.md`, `redacting-telemetry/index.md`,
  `community.md`).
- `presidio@microsoft.com` → `presidio@dataprivacystack.org` (5 files).
- URL-encoded repo paths in the Azure "Deploy to Azure" buttons
  (`microsoft%2Fpresidio` → `data-privacy-stack%2Fpresidio`, 3 files); the Azure button
  asset itself kept.
- `aka.ms` Microsoft short-links resolved and replaced: `aka.ms/presidio` →
  `github.com/data-privacy-stack/presidio` (streamlit sample); `aka.ms/presidio-demo` →
  `huggingface.co/spaces/presidio/presidio_demo` (`faq.md`, `index.md`).
  *(kept `aka.ms/deploytoazurebutton` — standard Azure deploy-button asset)*
- Docker images `mcr.microsoft.com/presidio-*` → `ghcr.io/data-privacy-stack/presidio-*`
  (GitHub Container Registry) across all docs, incl. the k8s chart `registry:` value and
  `deploy-presidio.sh` default. *(kept `mcr.microsoft.com/devcontainers/python` base image)*
- `github.com/microsoft/presidio-research` → `github.com/data-privacy-stack/presidio-research`
  (all docs links + raw data URLs).
- Remaining "Microsoft Presidio" prose → "Presidio" (streamlit sample, notebooks,
  `tutorial/index.md`).
- k8s `index.md` default-images note repointed from "Microsoft syndicates container
  catalog" to the GHCR packages page.

**Held in `docs/` — need your input / a decision (NOT yet changed):**
- `docs/NOTICE` — third-party license attribution naming Microsoft (legal; treat with LICENSE).
- `docs/build_release.md` — "Microsoft container registry (and docker hub)" wording is now
  stale (images moved to GHCR); update together with the `.github/workflows/release.yml` pass.
- `Tools-for-Health-Data-Anonymization` link (`example_dicom_image_redactor.ipynb`) — an
  unrelated Microsoft tool, not part of this migration; left as-is.

**Intentionally kept** (not branding): Azure ARM resource types (`Microsoft.Web/*`,
`Microsoft.Storage/*`, etc.), Microsoft Fabric notebook metadata (`"microsoft": {…}`),
`learn.microsoft.com` Windows long-paths link, Azure service names in feature comparisons,
and the "originally created at Microsoft" history note in `faq.md`/`project_transition.md`.

---

Scope decision used below:
- **REMOVE/REPLACE** — Microsoft *ownership, brand, legal, or infra* that does not
  carry over to the new org.
- **REVIEW/KEEP** — Microsoft/**Azure** *product integrations* that remain valid for
  users (the transition doc explicitly says Azure usage continues). Keep the feature,
  just fix ownership URLs/branding inside it.

---

## 1. Legal & governance  (highest priority)

- [ ] **`LICENSE`** — `Copyright (c) Microsoft Corporation. All rights reserved.` →
      `Copyright (c) Data Privacy Stack`.
- [ ] **`CODE_OF_CONDUCT`** — currently just points to the *Microsoft Open Source Code of
      Conduct* + `opencode@microsoft.com`. Replace with a community CoC (e.g. Contributor
      Covenant) and a non-Microsoft contact.
- [ ] **`SECURITY.md`** — entire MSRC block (`secure@microsoft.com`,
      `msrc.microsoft.com`, `aka.ms/...`, bug bounty). Replace with the new project's
      vulnerability-disclosure process.
- [ ] **`SUPPORT.md`** — repo-search link `repo:microsoft/presidio` and
      `microsoft.github.io/presidio` docs link.
- [ ] **`CONTRIBUTING.md`** — Microsoft CLA section, `opencode@microsoft.com`,
      `presidio@microsoft.com`, Microsoft Open Source CoC reference, `github.com/microsoft`
      links. Also **`docs/recipes/CONTRIBUTING.md`** (`presidio@microsoft.com`,
      microsoft links).

## 2. Package metadata (PyPI — affects published packages)

- [ ] **6 × `pyproject.toml`** (`presidio/`, `presidio-analyzer/`, `presidio-anonymizer/`,
      `presidio-image-redactor/`, `presidio-structured/`, `presidio-cli/`):
  - [ ] `authors = [{name = "Presidio", email = "presidio@microsoft.com"}]` → new email.
  - [ ] `urls = {Homepage = "https://github.com/Microsoft/presidio"}` → new org URL
        (note inconsistent casing `Microsoft`/`microsoft`).
  - [ ] Decide on PyPI ownership/maintainers for the `presidio-*` packages.

## 3. CI/CD & GitHub configuration

- [ ] **`.github/workflows/defender-for-devops.yml`** — Microsoft Security DevOps (MSDO).
      Microsoft-specific; **remove** (or replace with an org-neutral scanner).
- [ ] **`.github/workflows/release.yml`** — publishes to **Azure Container Registry**
      (`ACR_NAME`, `azure/login`, `AZURE_CLIENT_ID/TENANT_ID/SUBSCRIPTION_ID`, `az acr login`).
      Per transition doc, retarget to **Docker Hub** under the new org.
- [ ] **`.github/workflows/ci.yml`** — `REGISTRY_NAME: 'mcr.microsoft.com'` (×2). Update
      registry.
- [ ] **`.github/CODEOWNERS`** — `@microsoft/presidio-administrators` team → new org team.
- [ ] **`.github/copilot-instructions.md`** — `mcr.microsoft.com` + microsoft refs.
- [ ] **`.github/PULL_REQUEST_TEMPLATE.md`** — `github.com/microsoft/presidio` contributing link.
- [ ] **`.github/workflows/codeql-analysis.yml`**, `release-docs.yml`, `label-external.yml`
      — sweep for org/registry/secret references.
- [ ] Re-point GitHub repo **secrets/OIDC** and branch protections in the new org.

## 4. Brand assets & README

- [ ] **`docs/assets/ms_icon.png`** — Microsoft icon. Remove or replace with DPS icon
      (no code references found; confirm before deleting).
- [ ] **`README.MD`** — badges and links hard-coded to `microsoft`:
      Build Status, Release, Coverage endpoints (`coverage-data-presidio-*` branches),
      `microsoft.github.io/presidio` full-docs link. Update all to new org/site.
- [ ] Verify the **demo gif / diagrams** (`docs/assets/*.gif/png`) contain no Microsoft chrome.

## 5. Docs site config (`mkdocs.yml`)

- [ ] `site_url: https://microsoft.github.io/presidio` → new docs site.
- [ ] `repo_url: https://github.com/microsoft/presidio/`.
- [ ] Changelog, REST API, and per-sample `github.com/microsoft/...` links.
- [ ] Footer: repo link, Docker link `hub.docker.com/_/microsoft-presidio`,
      `mailto:presidio@microsoft.com`.

## 6. Bulk URL / brand sweep across docs & code

Mostly mechanical find-replace, but review per file (some are sample *data*, not links):

- [ ] `github.com/microsoft/presidio` → `github.com/data-privacy-stack/presidio`
      — **~75 files** (mixed case `Microsoft`/`microsoft`).
- [ ] `microsoft.github.io/presidio` → new docs URL — **~33 files**.
- [ ] `mcr.microsoft.com/presidio*` → Docker Hub image path — **~14 files**
      (docs, k8s charts, app-service JSON, devcontainer, docker-compose).
- [ ] `hub.docker.com/_/microsoft-presidio` → new Docker Hub repo — **2 files**.
- [ ] **`CHANGELOG.md`** (45 microsoft hits) — historical; decide whether to leave as-is
      or only fix forward-looking links.
- [ ] `presidio@microsoft.com` everywhere (`docs/index.md`, `docs/faq.md`, recipes, etc.).

## 7. Microsoft/Azure product integrations  (KEEP — do not remove or relocate)

**Decision:** any sample or component that *uses* a Microsoft/Azure product **stays** in
the repo, unchanged as a feature. The only edits inside these are ownership pointers
(repo/docs URLs for files that live in *this* moving repo). Do **not** strip Azure
resource types, service names, Fabric metadata, or base images.

- [ ] **`docs/samples/fabric/`** — Microsoft Fabric notebook + assets.
- [ ] **`docs/samples/python/ahds/`** + **`docs/ahds_integration.md`** — Azure Health Data Services.
- [ ] **`docs/samples/deployments/data-factory/`** — Azure Data Factory ARM templates.
- [ ] **`docs/samples/deployments/app-service/`** — Azure App Service ARM/JSON.
- [ ] **`docs/samples/python/streamlit/azure_ai_language_wrapper.py`** — Azure AI Language
      recognizer wrapper.
- [ ] **`docs/samples/deployments/k8s/`**, `docker/`, `spark/` — Azure/MCR references.

## 8. Low-priority / sample data (optional)

- [ ] Test fixtures & demo text using `microsoft.com` as example PII
      (e.g. `azure_ai_language_wrapper.py` sample sentence, `e2e-tests/resources/demo.txt`,
      analyzer tests). Harmless; swap to a neutral example only if desired.

---

### Suggested order
1. Section 1 (legal) + Section 2 (package metadata) — blocking for a clean first release.
2. Section 3 (CI/CD) — needed before publishing from the new org.
3. Sections 4–6 (brand + bulk URL sweep) — can be largely scripted.
4. Section 7 (integration review) — needs maintainer judgement.
