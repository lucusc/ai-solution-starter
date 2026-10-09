param location string = resourceGroup().location
param subscriptionId string = subscription().subscriptionId
param connectionName string
param accessPolicies array = []
param displayName string = 'Office 365 Outlook Connection'
param authenticatedUser object = {}

resource office365Connection 'Microsoft.Web/connections@2016-06-01' = {
  name: connectionName
  location: location
  #disable-next-line BCP187
  kind: 'V2'
  properties: {
    displayName: displayName
    #disable-next-line BCP037
    authenticatedUser: authenticatedUser
    #disable-next-line BCP089
    parameterValueSet: {
      name: 'managedIdentityAuth'
      values: {}
    }
    api: {
      name: connectionName
      type: 'Microsoft.Web/locations/managedApis'
      #disable-next-line use-resource-id-functions
      id: '/subscriptions/${subscriptionId}/providers/Microsoft.Web/locations/${location}/managedApis/${connectionName}'
    }
  }

  #disable-next-line BCP081
  resource accessPolicy 'accessPolicies' = [
    for (policy, i) in accessPolicies: {
      name: 'policy-${i}'
      properties: {
        principal: {
          type: 'ActiveDirectory'
          identity: {
            tenantId: policy.tenantId
            objectId: policy.objectId
          }
        }
      }
    }
  ]
}

#disable-next-line use-resource-symbol-reference
output connectionRuntimeUrl string = reference(
  resourceId('Microsoft.Web/connections', connectionName),
  '2016-06-01',
  'full'
).properties.connectionRuntimeUrl
