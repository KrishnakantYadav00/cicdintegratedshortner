
# URL Shortener

A small Flask app built as the foundation for a CI/CD pipeline project.
See [PRD.md](./PRD.md) for scope and roadmap.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt

# Confirm your environment has everything needed
python check_deps.py

# Run tests
pytest tests/ -v --cov=app

# Run the app
python app.py
# → visit http://localhost:5000
```

## API

| Method | Path | Description |
|---|---|---|
| POST | `/api/shorten` | Body: `{"url": "...", "custom_code": "optional"}` |
| GET | `/<code>` | Redirects to the target URL |
| GET | `/api/stats/<code>` | Returns click count + metadata |
| GET | `/health` | Liveness/readiness probe |

## Docker

```bash
docker build -t url-shortener .
docker run -p 5000:5000 url-shortener
curl http://localhost:5000/health
```

## Pushing to a remote repo

```bash
cd url-shortener
git init
git add .
git commit -m "Initial commit: URL shortener MVP"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

Then in GitHub: Settings → Branches → add a protection rule on `main`
requiring the `CI / test` and `CI / build` checks to pass before merging.
That's what makes the pipeline actually enforce something, rather than
just running for show.

## Roadmap
See [PRD.md](./PRD.md) — next steps are containerizing the deploy step
and wiring up GitOps-based CD.