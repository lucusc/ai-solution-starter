@allowed([
  'new'
  'existing'
])
param mode string

param accountName string
param projectName string
param existingProjectName string = ''
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
param connectAzureOpenAi bool = false
param azureOpenAiEndpoint string = ''

var shouldConfigureAccount = mode == 'new' || configureExistingResource

resource newAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' = if (mode == 'new') {
  name: accountName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'AIServices'
  sku: {
    name: skuName
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: accountName
    disableLocalAuth: disableLocalAuth
    dynamicThrottlingEnabled: false
    publicNetworkAccess: publicNetworkAccess
    restrictOutboundNetworkAccess: false
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

resource newProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = if (mode == 'new') {
  parent: newAccount
  name: projectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    description: 'AI Solution Starter project'
    displayName: projectName
  }
}

resource projectInExistingAccount 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = if (mode == 'existing' && empty(existingProjectName)) {
  parent: existingAccount
  name: projectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    description: 'AI Solution Starter project'
    displayName: projectName
  }
}

resource existingProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' existing = if (mode == 'existing' && !empty(existingProjectName)) {
  parent: existingAccount
  name: existingProjectName
}

resource newProjectOpenAiConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-06-01' = if (mode == 'new' && connectAzureOpenAi) {
  parent: newProject
  name: 'azure-openai'
  properties: {
    authType: 'AAD'
    category: 'AzureOpenAI'
    isSharedToAll: true
    target: azureOpenAiEndpoint
    useWorkspaceManagedIdentity: true
  }
}

resource existingAccountProjectOpenAiConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-06-01' = if (mode == 'existing' && empty(existingProjectName) && connectAzureOpenAi) {
  parent: projectInExistingAccount
  name: 'azure-openai'
  properties: {
    authType: 'AAD'
    category: 'AzureOpenAI'
    isSharedToAll: true
    target: azureOpenAiEndpoint
    useWorkspaceManagedIdentity: true
  }
}

resource existingProjectOpenAiConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-06-01' = if (mode == 'existing' && !empty(existingProjectName) && connectAzureOpenAi) {
  parent: existingProject
  name: 'azure-openai'
  properties: {
    authType: 'AAD'
    category: 'AzureOpenAI'
    isSharedToAll: true
    target: azureOpenAiEndpoint
    useWorkspaceManagedIdentity: true
  }
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

var selectedProjectName = mode == 'new'
  ? projectName
  : (!empty(existingProjectName) ? existingProjectName : projectName)

output mode string = mode
output accountName string = accountName
output accountId string = mode == 'new' ? newAccount.id : existingAccount.id
output accountEndpoint string = mode == 'new' ? newAccount.properties.endpoint : existingAccount.properties.endpoint
output location string = mode == 'new' ? newAccount.location : existingAccount.location
output projectName string = selectedProjectName
output projectId string = mode == 'new'
  ? newProject.id
  : (!empty(existingProjectName) ? existingProject.id : projectInExistingAccount.id)
output projectEndpoint string = 'https://${accountName}.services.ai.azure.com/api/projects/${selectedProjectName}'
output projectPrincipalId string = mode == 'new'
  ? newProject.identity.principalId
  : (!empty(existingProjectName)
      ? (existingProject.identity.?principalId ?? '')
      : projectInExistingAccount.identity.principalId)
output accountPrincipalId string = mode == 'new'
  ? newAccount.identity.principalId
  : (existingAccount.identity.?principalId ?? '')
output configuredExistingResource bool = mode == 'existing' && shouldConfigureAccount
