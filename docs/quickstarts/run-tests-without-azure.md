# Run tests without Azure

Install the project and run its test suites with no Azure subscription. This
confirms your machine is set up for development. Nothing is deployed and no
model is called.

**You will need:** Git, Python 3.12 and Node.js 20.19+.

## 1. Clone and install

```bash
git clone https://github.com/lucusc/ai-solution-starter.git
cd ai-solution-starter
python3 -m venv .venv
.venv/bin/python -m pip install -r app/backend/requirements-dev.txt
npm --prefix app/frontend ci
```

## 2. Run the tests

```bash
.venv/bin/python -m pytest app/backend/tests app/agent/tests scripts/tests
.venv/bin/python scripts/verify_logic_app_package.py
npm --prefix app/frontend test -- --run
```

All three commands should finish without failures. Azure calls are mocked.

## 3. Build the web app

```bash
npm --prefix app/frontend run build
```

This writes the compiled site to `app/backend/static/` (ignored by Git). The
backend container serves it in production.

## What this proves

| Checked | Not checked |
| --- | --- |
| API behavior with mocked Storage and Cosmos | Real Azure sign-in, storage or networking |
| Workflow definition structure | Running the Logic App or calling the model |
| Frontend behavior and build | A real end-to-end upload |

## Next

- [Contributor setup and all checks](../contributing/development.md)
- [Deploy the demo](deploy-demo.md) to see it run for real
