# Configure authentication

The site uses **App Service authentication** (also called Easy Auth) with
Microsoft Entra ID. App Service signs the user in, then passes their
identity to the API in the `X-MS-CLIENT-PRINCIPAL` header. The API uses
that identity to show each user only their own items.

## Default setup (recommended)

```bash
azd env set AZURE_USE_AUTHENTICATION true
azd provision
```

During `azd provision`:

1. **Before** provisioning, the `preprovision` hook creates two app
   registrations: an API (server) app and a browser (client) app. It saves
   their IDs and secrets in your azd environment as `AZURE_SERVER_APP_ID`,
   `AZURE_SERVER_APP_SECRET`, `AZURE_CLIENT_APP_ID` and
   `AZURE_CLIENT_APP_SECRET`.
2. The template turns on App Service authentication with those apps.
3. **After** provisioning, the `postprovision` hook adds the site's redirect
   URLs (`<BACKEND_URI>/.auth/login/aad/callback` and `/redirect`) plus
   `localhost` URLs for local development.

Re-running `azd provision` reuses the same apps and secrets.

If `AZURE_USE_AUTHENTICATION` is not `true`, the hooks skip this. The site
then returns **401** to everyone, because the API requires a signed-in user.

## Use a different tenant

To sign users in from a tenant other than the subscription's tenant:

```bash
azd env set AZURE_AUTH_TENANT_ID "<tenant-id>"
```

## Use app registrations you already have

Use this when you cannot create app registrations, or your identity team
provides them:

```bash
azd env set AZURE_BYPASS_AUTHENTICATION_SETUP true
azd env set AZURE_SERVER_APP_ID "<api-app-id>"
azd env set AZURE_SERVER_APP_SECRET "<api-app-secret>"
azd env set AZURE_CLIENT_APP_ID "<client-app-id>"
azd env set AZURE_CLIENT_APP_SECRET "<client-app-secret>"
azd env set AZURE_AUTH_TENANT_ID "<tenant-id>"
```

The hooks will not touch the registrations, so add the redirect URLs above
yourself after the first `azd provision`.

## GitHub Actions

The workflow does not run the registration hooks. Create the apps once from
your machine and copy the values into GitHub, as described in
[deploy with GitHub Actions](../quickstarts/deploy-github-actions.md#2-create-the-sign-in-apps).

## Other settings

| Setting | Effect |
| --- | --- |
| `AZURE_ENABLE_UNAUTHENTICATED_ACCESS=true` | App Service lets anonymous users load pages. API calls still return 401 without sign-in. |
| `AZURE_DISABLE_APP_SERVICES_AUTHENTICATION=true` | Turns App Service authentication off. **Do not use with this backend.** Without it, a caller could forge the identity header. |
| `AZURE_ENFORCE_ACCESS_CONTROL=true` | Legacy check. If authentication is off, the hooks print a warning and skip setup. It does not change the deployment. |

## Local development

There is no App Service in front of a local API. Set
`LOCAL_AUTH_SUBJECT=<any-id>` in `app/backend/.env` to act as one fixed user.
The API refuses this setting when `RUNNING_IN_PRODUCTION=true`.

## Remove the app registrations

`azd down` does not delete them. List and delete:

```bash
az ad app show --id "$(azd env get-value AZURE_CLIENT_APP_ID)" --query displayName
az ad app delete --id "$(azd env get-value AZURE_CLIENT_APP_ID)"
az ad app delete --id "$(azd env get-value AZURE_SERVER_APP_ID)"
```

See also [identity and access](../concepts/identity-and-access.md).
