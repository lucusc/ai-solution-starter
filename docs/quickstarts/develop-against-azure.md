# Develop against Azure

Run the web app and API on your machine while using the Storage, Cosmos DB
and workflow you already deployed. Your code changes reload instantly, and
uploads are still processed by the real Logic App and model.

**You will need:** a working deployment from [deploy the demo](deploy-demo.md)
(or another quick start), Python 3.12 and Node.js 20.19+.

## 1. Make sure your machine can reach the data

The demo quick start already allowed your IP and gave your account data
access. If your IP has changed, update it:

```bash
azd env set AZURE_ALLOWED_IPS "$(curl -fsS https://api.ipify.org)"
azd provision
```

## 2. Install dependencies

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r app/backend/requirements-dev.txt
npm --prefix app/frontend ci
```

## 3. Configure the backend

Write `app/backend/.env` from your azd environment. This file is ignored by
Git.

```bash
cat > app/backend/.env <<EOF
LOCAL_AUTH_SUBJECT=local-developer
AZURE_STORAGE_ACCOUNT=$(azd env get-value AZURE_STORAGE_ACCOUNT)
AZURE_STORAGE_CONTAINER=$(azd env get-value AZURE_STORAGE_CONTAINER)
AZURE_COSMOSDB_ACCOUNT=$(azd env get-value AZURE_COSMOSDB_ACCOUNT)
AZURE_COSMOSDB_DATABASE=$(azd env get-value AZURE_COSMOSDB_DATABASE)
AZURE_COSMOSDB_CONTAINER=$(azd env get-value AZURE_COSMOSDB_CONTAINER)
EOF
```

`LOCAL_AUTH_SUBJECT` stands in for the signed-in user, because there is no
App Service sign-in locally. The backend signs in to Azure with your
`az login` account.

## 4. Start the API and the web app

In one terminal:

```bash
PYTHONPATH=app/backend .venv/bin/hypercorn \
  --config app/backend/hypercorn.toml backend.main:app
```

Check `http://localhost:8000/readyz`. It should return `{"status":"ready"}`.

In a second terminal:

```bash
cp app/frontend/.env.example app/frontend/.env.local
npm --prefix app/frontend run dev
```

Open `http://localhost:5173` and upload a PDF. Vite sends `/api` calls to the
local API.

## If something goes wrong

| Problem | Fix |
| --- | --- |
| `/readyz` returns `not_ready` or you see `403` | Your IP or role is missing. See step 1. Role changes can take 5 minutes. |
| Startup says a setting is missing | Re-run step 3 and check `app/backend/.env` |
| Item stays **queued** | Deploy the workflow: `./scripts/deploy_app.sh agent` |

For persistent access across changing IPs, `./scripts/allow_my_ip_address.sh`
also opens the Storage and Cosmos firewalls. Note that it adds broad Cosmos
access (all Azure datacenters) and does not undo itself. See
[access a private deployment](../how-to/access-a-private-deployment.md).

## Next

- [App settings reference](../reference/app-settings.md)
- [Contributor setup and checks](../contributing/development.md)
