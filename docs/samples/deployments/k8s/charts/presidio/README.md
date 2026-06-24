# Presidio Helm chart

Deploys the [Presidio](https://github.com/microsoft/presidio) stack to Kubernetes — the
`presidio-analyzer` (PII detection) and `presidio-anonymizer` (PII anonymization) text
services, plus an optional `presidio-image-redactor` (PII redaction in images). It mirrors the
`docker-compose-text.yml` / `docker-compose-image.yml` topology and is scaffolded from
`helm create` following community best practices.

> Scope: the analyzer and anonymizer are enabled by default. The image-redactor is **disabled
> by default** (`imageRedactor.enabled=true` to opt in) — it bundles spaCy NLP models and
> Tesseract OCR, so it is heavy and slow to start. The transformers NLP engine and Ollama
> remain out of scope for this chart.

## Prerequisites

- Kubernetes 1.23+
- Helm 3.8+
- An Ingress controller (only if `ingress.enabled=true`); the default path rules assume
  [ingress-nginx](https://kubernetes.github.io/ingress-nginx/)

## Install

```bash
# From this chart directory: docs/samples/deployments/k8s/charts/presidio
helm install presidio . --namespace presidio --create-namespace

# Override the image tag (defaults to the chart appVersion)
helm install presidio . --namespace presidio --create-namespace --set image.tag=latest

# Custom values
helm install presidio . --namespace presidio --create-namespace -f my-values.yaml
```

Check rollout (the analyzer loads NLP models on first start and can take a few minutes):

```bash
kubectl rollout status deployment/presidio-presidio-analyzer -n presidio
helm test presidio -n presidio
```

## Uninstall

```bash
helm uninstall presidio
```

## What gets deployed

| Resource | analyzer | anonymizer | image-redactor |
| --- | --- | --- | --- |
| Enabled by default | ✅ | ✅ | ❌ (`imageRedactor.enabled`) |
| Deployment | ✅ | ✅ | ✅ |
| Service (ClusterIP) | ✅ | ✅ | ✅ |
| HorizontalPodAutoscaler | optional (`analyzer.autoscaling.enabled`) | optional (`anonymizer.autoscaling.enabled`) | optional (`imageRedactor.autoscaling.enabled`) |
| ServiceAccount (shared) | ✅ (`serviceAccount.create`) | | |
| Ingress (shared, routes all enabled) | optional (`ingress.enabled`) | | |

Pods run as the non-root UID `1001` baked into the Presidio images, with `ALL` capabilities
dropped, `allowPrivilegeEscalation: false`, and the `RuntimeDefault` seccomp profile.

Enable the image-redactor with:

```bash
helm install presidio . --namespace presidio --create-namespace --set imageRedactor.enabled=true
```

## Configuration

### Global

| Key | Default | Description |
| --- | --- | --- |
| `image.registry` | `mcr.microsoft.com` | Registry for both images. Set `""` for bare repos. |
| `image.pullPolicy` | `IfNotPresent` | Default pull policy. |
| `image.tag` | `""` | Default tag; empty falls back to chart `appVersion`. |
| `imagePullSecrets` | `[]` | Private registry pull secrets. |
| `serviceAccount.create` | `true` | Create a shared ServiceAccount. |
| `serviceAccount.automount` | `false` | Mount the SA token (Presidio does not call the K8s API). |
| `podSecurityContext` | non-root 1001 | Pod-level security context for all components. |
| `securityContext` | drop ALL caps | Container-level security context for all components. |
| `nodeSelector` / `tolerations` / `affinity` | empty | Default scheduling; per-component overrides supported. |
| `ingress.enabled` | `false` | Enable the shared Ingress. |
| `ingress.className` | `nginx` | IngressClass. |
| `ingress.hosts` | `presidio.local` | Host/path rules; each path maps to a `service` alias (`analyzer`, `anonymizer`, `image-redactor`). |

### Per component (`analyzer.*`, `anonymizer.*`, `imageRedactor.*`)

| Key | analyzer default | anonymizer default | imageRedactor default | Description |
| --- | --- | --- | --- | --- |
| `enabled` | `true` | `true` | `false` | Toggle the component. |
| `image.repository` | `presidio-analyzer` | `presidio-anonymizer` | `presidio-image-redactor` | Image repo (joined with `image.registry`). |
| `replicaCount` | `1` | `1` | `1` | Replicas (ignored when autoscaling is on). |
| `containerPort` | `3000` | `3000` | `3000` | Listen port; exported as the `PORT` env var. |
| `workers` | `1` | `1` | `1` | gunicorn workers; exported as the `WORKERS` env var. |
| `extraEnv` | `[]` | `[]` | `[]` | Extra environment variables. |
| `service.type` / `service.port` | `ClusterIP` / `8080` | `ClusterIP` / `8080` | `ClusterIP` / `8080` | Service exposure. |
| `resources` | 1.5–3Gi / 1.5–2 CPU | 128–512Mi / 0.125–0.5 CPU | 1.5–3Gi / 1.5–2 CPU | Requests/limits. |
| `startupProbe` / `livenessProbe` / `readinessProbe` | `/health` | `/health` | `/health` | HTTP probes. |
| `autoscaling.enabled` | `false` | `false` | `false` | Enable the HPA. |

> The image-redactor exposes `POST /redact` (multipart image upload) in addition to `/health`.
> Note the [`docker-compose-image.yml`](../../../../../../docker-compose-image.yml) reference sets
> `PORT=5001`, but this chart standardizes every component on container port `3000` (the image's
> Dockerfile default).

## Scaling caveat

Balancing traffic across **more than one replica** of a service requires a service mesh
(e.g. Linkerd or Istio) because the clients hold persistent connections — see
[microsoft/presidio#304](https://github.com/microsoft/presidio/issues/304). Plain
`replicaCount > 1` or HPA without a mesh may not distribute load evenly.

## Example: enable Ingress

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
  hosts:
    - host: presidio.example.com
      paths:
        - path: /analyzer(/|$)(.*)
          pathType: ImplementationSpecific
          service: analyzer
        - path: /anonymizer(/|$)(.*)
          pathType: ImplementationSpecific
          service: anonymizer
        # Only routed when imageRedactor.enabled is true.
        - path: /image-redactor(/|$)(.*)
          pathType: ImplementationSpecific
          service: image-redactor
```
