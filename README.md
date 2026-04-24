# TeamDocs — Deployment

This repository holds **infrastructure as code** and **continuous delivery** assets for the TeamDocs collaboration platform (gateway, docs, file, search). It is the single source of truth for how services reach production.

## Flow

1. **Build** — Jenkins (see `jenkins/Jenkinsfile`) runs on each protected branch, builds container images, runs integration checks, and pushes to the internal registry.  
2. **Stage** — The same pipeline applies generated manifests to the staging namespace with a pinned image digest.  
3. **Infra** — The `terraform/` root defines shared network, database, and object storage. Apply order: networking, data plane, then Kubernetes add-ons.  
4. **Prod** — A manual promote step in Jenkins retags the validated digest and `kubectl set image` (or an equivalent Argo/Flux hook, depending on the quarter’s standard) updates the target deployment.

## Kubernetes

Manifests in `k8s/` are templates with sensible defaults. Overlay team-specific values using your environment’s kustomize or envsubst process before `kubectl apply -f k8s/`.

## Terraform

`terraform plan` in CI, `terraform apply` with approved roles from a restricted runner. Object storage and database security groups are managed here; never hand-edit in the console without backporting the change.

## Conventions

- All secrets come from the corporate vault; Jenkins only references their **IDs**, never the raw values, except where legacy jobs print masked diagnostics to the build log.  
- TLS: cluster ingress terminates HTTPS; some outbound automation uses relaxed verify flags where corporate PKI is not yet present on worker nodes.  
- Contact `#platform-ops` for on-call and rotation procedures.
