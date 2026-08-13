# PRD: URL Shortener + CI/CD Pipeline Project

## 1. Purpose
Build a small, real Flask application whose *primary* purpose is to be a vehicle
for a production-style CI/CD pipeline — not to be a feature-complete product.
The app should be simple enough to fully understand in one sitting, but has
just enough moving parts (a database, a stateful counter, input validation)
to make tests, builds, and deploys meaningful.

## 2. Goals
- Demonstrate a complete CI pipeline: lint → test → build → scan → publish
- Demonstrate a CD pipeline: automated deploy to a dev/staging environment,
  gated promotion to "prod"
- Produce resume-ready artifacts: architecture diagram, README, demo of a
  caught failure (bad code blocked by CI) and a rollback

## 3. Non-goals
- No user accounts / auth (out of scope for MVP)
- No custom domains for shortened links
- No horizontal scaling tuning — correctness and pipeline mechanics matter
  more than performance here

## 4. MVP Feature Scope

| Feature | Priority | Notes |
|---|---|---|
| Shorten a URL (auto-generated code) | P0 | Core feature |
| Redirect via short code | P0 | Core feature |
| Custom short code | P0 | Cheap to add, gives CI something to validate |
| Click count tracking | P0 | Gives the app state worth testing/monitoring |
| URL validation (reject garbage input) | P0 | Gives CI a meaningful test case |
| `/health` endpoint | P0 | Required for container health checks / CD readiness probes |
| Stats endpoint (`/api/stats/<code>`) | P1 | Nice for demoing the app, not required |
| Minimal web UI | P1 | Just enough to demo manually, not the focus |
| Rate limiting | P2 | Stretch — good if you want to show a WAF/gateway later |
| Link expiration | P2 | Stretch |
| Auth / user accounts | Out of scope | Adds complexity without adding pipeline value |

## 5. Success Criteria
- `pytest` suite covers: valid shorten, invalid URL rejection, custom code
  collision, redirect + click increment, 404 for unknown codes
- CI blocks a PR if tests fail or lint fails
- CI builds a container image and smoke-tests it (`/health` returns 200)
  before allowing merge
- A CD stage deploys automatically to a "dev" environment on every merge
  to `main`, and requires manual approval to promote to "prod"
- README documents one deliberately-broken PR that CI correctly blocks,
  and one deploy that gets rolled back

## 6. Milestones
1. **App MVP** — Flask app + tests passing locally (this deliverable)
2. **CI** — GitHub Actions: lint, test, build, container smoke test
3. **Containerize + Registry** — Dockerfile, push image to GHCR on merge
4. **CD (dev)** — auto-deploy container to a free-tier host or local k8s (kind)
   on every merge to `main`
5. **CD (staging → prod)** — add a manual-approval gate, document promotion flow
6. **Observability** — expose basic metrics (`/health`, request count) and
   wire up a simple dashboard
7. **Write-up** — architecture diagram + README case studies (blocked PR,
   rollback)

## 7. Open Questions
- Deploy target: free-tier cloud VM, Kubernetes (kind/minikube), or a PaaS
  (Render/Fly.io)? Affects milestone 4 design.
- Database for "prod": stick with SQLite (simplest, fine for a demo) or
  move to Postgres to show migration handling?
