@allowed([
  'new'
  'existing'
])
param mode string

param accountName string
param location string
param skuName string = 'S0'
param tags object = {}

@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Disabled'

@allowed([
  'None'
  'AzureServices'
])
param networkBypass string = 'AzureServices'

param ipRules array = []
param disableLocalAuth bool = true
param configureExistingResource bool = false
param enableDiagnostics bool = false
param logAnalyticsWorkspaceId string = ''
param assignRoles bool = false
param principalId string = ''

@allowed([
  'Device'
  'ForeignGroup'
  'Group'
  'ServicePrincipal'
  'User'
])
param principalType string = 'ServicePrincipal'

param cognitiveServicesUserRoleId string

var shouldConfigureAccount = mode == 'new' || configureExistingResource

resource newAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' = if (mode == 'new') {
  name: accountName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'FormRecognizer'
  sku: {
    name: skuName
  }
  properties: {
    customSubDomainName: accountName
    disableLocalAuth: disableLocalAuth
    dynamicThrottlingEnabled: false
    publicNetworkAccess: publicNetworkAccess
    networkAcls: {
      defaultAction: 'Deny'
      bypass: networkBypass
      ipRules: ipRules
      virtualNetworkRules: []
    }
  }
}

resource existingAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = if (mode == 'existing') {
  name: accountName
}

resource newAccountUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (mode == 'new' && assignRoles && !empty(principalId)) {
  name: guid(newAccount.id, principalId, cognitiveServicesUserRoleId)
  scope: newAccount
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
  }
}

resource existingAccountUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (mode == 'existing' && configureExistingResource && assignRoles && !empty(principalId)) {
  name: guid(existingAccount.id, principalId, cognitiveServicesUserRoleId)
  scope: existingAccount
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
  }
}

resource newAccountDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (mode == 'new' && enableDiagnostics) {
  name: 'default'
  scope: newAccount
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

resource existingAccountDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (mode == 'existing' && configureExistingResource && enableDiagnostics) {
  name: 'default'
  scope: existingAccount
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

output mode string = mode
output accountName string = accountName
output resourceId string = mode == 'new' ? newAccount.id : existingAccount.id
output endpoint string = mode == 'new' ? newAccount.properties.endpoint : existingAccount.properties.endpoint
output location string = mode == 'new' ? newAccount.location : existingAccount.location
output principalId string = mode == 'new'
  ? newAccount.identity.principalId
  : (existingAccount.identity.?principalId ?? '')
output configuredExistingResource bool = mode == 'existing' && shouldConfigureAccount
