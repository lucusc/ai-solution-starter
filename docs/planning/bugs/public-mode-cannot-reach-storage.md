# BUG-08: Public modes can't reach Storage

**Type:** Bug · **Area:** Infra · **Priority:** High · **Status:** Proposed

## Summary

With `AZURE_USE_PRIVATE_ENDPOINT=false`, the app deploys but uploads fail,
because the web app can't reach primary Storage.

## Current behavior

- [`infra/network-isolation.bicep`](../../../infra/network-isolation.bicep)
  line ~74 creates the VNet only when `usePrivateEndpoint` is true, so in
  public modes the web app has no VNet integration.
- [`infra/main.bicep`](../../../infra/main.bicep) line ~383 always sets
  primary Storage `networkAcls.defaultAction` to `Deny`. The only
  exceptions are `AZURE_ALLOWED_IPS`, trusted services and Logic App
  resource rules; the web app's outbound addresses aren't included.

## Impact

The **Restricted public** and **Public** modes in
[networking](../../concepts/networking.md#public-mode-limitation) don't work
end to end.

## Proposed change

**Infra.** Needs approval under
[infrastructure change control](../../contributing/infra-change-control.md).
Options:

1. In public modes, set Storage `defaultAction` to `Allow` when
   `AZURE_PUBLIC_NETWORK_ACCESS=Enabled` and `AZURE_ALLOWED_IPS` is empty.
2. Or add the web app's outbound IP addresses to the Storage IP rules.
3. Or drop the public modes and document private as the only supported
   option.

## Acceptance criteria

- [ ] An upload and result work in each mode that remains documented.
- [ ] The private-mode resource graph is unchanged.
- [ ] The baseline manifest is updated after approval.
