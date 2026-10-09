targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

param createResourceGroup bool = true
param resourceGroupName string = '' // Set in main.parameters.json

param backendServicePlanAseId string = '' // Set in main.parameters.json
param backendServicePlanName string = '' // Set in main.parameters.json
param backendServiceName string = '' // Set in main.parameters.json
param backendServiceSkuName string // Set in main.parameters.json
param backendServiceSkuTier string // Set in main.parameters.json

param logicAppServiceAseId string = '' // Set in main.parameters.json
param logicAppServicePlanName string = '' // Set in main.parameters.json
param logicAppServiceSkuName string // Set in main.parameters.json
param logicAppServiceSkuTier string // Set in main.parameters.json
param logicAppServiceName string = '' // Set in main.parameters.json

param applicationInsightsDashboardName string = '' // Set in main.parameters.json
param applicationInsightsName string = '' // Set in main.parameters.json
param logAnalyticsName string = '' // Set in main.parameters.json

param storageAccountName string = '' // Set in main.parameters.json
param storageResourceGroupName string = '' // Set in main.parameters.json
param storageResourceGroupLocation string = location
param storageContainerName string = 'content'
param storageSkuName string // Set in main.parameters.json
param storageTokenContainerName string = 'tokens'
param storageInstructionsContainerName string = 'instructions'
param storageInputContainerName string = 'inputs'
param storageSystemInstructionsFile string
param storageProcessingInstructionsFile string
param storageEvaluationInstructionsFile string

@allowed(['azure', 'openai', 'azure_custom'])
param openAiHost string // Set in main.parameters.json
param isAzureOpenAiHost bool = startsWith(openAiHost, 'azure')
param deployAzureOpenAi bool = true
param deployAzureOpenModels bool = true
param azureOpenAiCustomUrl string = ''
param azureOpenAiApiVersion string = ''
@secure()
param azureOpenAiApiKey string = ''
param azureOpenAiDisableKeys bool = false
param openAiServiceName string = ''
param openAiResourceGroupName string = ''

param useGPT4V bool = true
param useEval bool = false

@allowed(['free', 'provisioned', 'serverless'])
param cosmosDbSkuName string // Set in main.parameters.json
param cosmodDbResourceGroupName string = ''
param cosmosDbLocation string = ''
param cosmosDbAccountName string = ''
param cosmosDbThroughput int = 400
param cosmosDbWorkItemDatabaseName string = 'starter'
param cosmosDbWorkItemContainerName string = 'inputs'
param cosmosDbWorkItemApiVersion string = '2023-10-15' // Version of the Cosmos DB API to use, e.g. 2023-10-15

// https://learn.microsoft.com/azure/ai-services/openai/concepts/models?tabs=python-secure%2Cstandard%2Cstandard-chat-completions#standard-deployment-model-availability
@description('Location for the OpenAI resource group')
@allowed([
  'canadaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'switzerlandnorth'
  'uksouth'
  'japaneast'
  'northcentralus'
  'australiaeast'
  'swedencentral'
])
@metadata({
  azd: {
    type: 'location'
  }
})
param openAiLocation string

param openAiSkuName string = 'S0'

@secure()
param openAiApiKey string = ''
param openAiApiOrganization string = ''

@allowed([
  'new'
  'existing'
  'none'
])
param useFoundry string = 'none'
param foundryAccountName string = ''
param foundryAccountResourceId string = ''
param foundryProjectName string = 'starter'
param foundryProjectResourceId string = ''
param foundryResourceGroupName string = ''
param foundryLocation string = location
param foundrySkuName string = 'S0'
param foundryConnectBaseOpenAi bool = false

@allowed([
  'new'
  'existing'
  'none'
])
param useDocumentIntelligence string = 'none'
param documentIntelligenceName string = ''
param documentIntelligenceResourceId string = ''
param documentIntelligenceResourceGroupName string = ''
param documentIntelligenceLocation string = location
param documentIntelligenceSkuName string = 'S0'

param configureExistingAiServices bool = false

param chatGptModelName string = ''
param chatGptDeploymentName string = ''
param chatGptDeploymentVersion string = ''
param chatGptDeploymentSkuName string = ''
param chatGptDeploymentCapacity int = 0

var chatGpt = {
  modelName: !empty(chatGptModelName)
    ? chatGptModelName
    : startsWith(openAiHost, 'azure') ? 'gpt-4o' : 'gpt-4o'
  deploymentName: !empty(chatGptDeploymentName) ? chatGptDeploymentName : 'chat'
  deploymentVersion: !empty(chatGptDeploymentVersion) ? chatGptDeploymentVersion : '2024-11-20'
  deploymentSkuName: !empty(chatGptDeploymentSkuName) ? chatGptDeploymentSkuName : 'Standard'
  deploymentCapacity: chatGptDeploymentCapacity != 0 ? chatGptDeploymentCapacity : 30
}

param embeddingModelName string = ''
param embeddingDeploymentName string = ''
param embeddingDeploymentVersion string = ''
param embeddingDeploymentSkuName string = ''
param embeddingDeploymentCapacity int = 0
param embeddingDimensions int = 0
var embedding = {
  modelName: !empty(embeddingModelName) ? embeddingModelName : 'text-embedding-ada-002'
  deploymentName: !empty(embeddingDeploymentName) ? embeddingDeploymentName : 'embedding'
  deploymentVersion: !empty(embeddingDeploymentVersion) ? embeddingDeploymentVersion : '2'
  deploymentSkuName: !empty(embeddingDeploymentSkuName) ? embeddingDeploymentSkuName : 'Standard'
  deploymentCapacity: embeddingDeploymentCapacity != 0 ? embeddingDeploymentCapacity : 30
  dimensions: embeddingDimensions != 0 ? embeddingDimensions : 1536
}

param gpt4vModelName string = ''
param gpt4vDeploymentName string = ''
param gpt4vModelVersion string = ''
param gpt4vDeploymentSkuName string = ''
param gpt4vDeploymentCapacity int = 0
var gpt4v = {
  modelName: !empty(gpt4vModelName) ? gpt4vModelName : 'gpt-4o'
  deploymentName: !empty(gpt4vDeploymentName) ? gpt4vDeploymentName : 'gpt-4o'
  deploymentVersion: !empty(gpt4vModelVersion) ? gpt4vModelVersion : '2024-11-20'
  deploymentSkuName: !empty(gpt4vDeploymentSkuName) ? gpt4vDeploymentSkuName : 'Standard'
  deploymentCapacity: gpt4vDeploymentCapacity != 0 ? gpt4vDeploymentCapacity : 100
}

param evalModelName string = ''
param evalDeploymentName string = ''
param evalModelVersion string = ''
param evalDeploymentSkuName string = ''
param evalDeploymentCapacity int = 0
var eval = {
  modelName: !empty(evalModelName) ? evalModelName : 'gpt-4o'
  deploymentName: !empty(evalDeploymentName) ? evalDeploymentName : 'eval-gpt-4o'
  deploymentVersion: !empty(evalModelVersion) ? evalModelVersion : '2024-08-06'
  deploymentSkuName: !empty(evalDeploymentSkuName) ? evalDeploymentSkuName : 'Standard'
  deploymentCapacity: evalDeploymentCapacity != 0 ? evalDeploymentCapacity : 30
}

param tenantId string = tenant().tenantId
param authTenantId string = ''

// Force using MSAL app authentication instead of built-in App Service authentication
// https://learn.microsoft.com/azure/app-service/overview-authentication-authorization
param disableAppServicesAuthentication bool = false
param enableUnauthenticatedAccess bool = false
param serverAppId string = ''
@secure()
param serverAppSecret string = ''
param clientAppId string = ''
@secure()
param clientAppSecret string = ''

// Used for optional CORS support for alternate frontends
param allowedOrigin string = '' // should start with https://, shouldn't end with a /

param allowedIps string = ''
var ipRules = reduce(
  filter(array(split(allowedIps, ',')), o => length(trim(o)) > 0),
  [],
  (cur, next) =>
    union(cur, [
      {
        value: next
      }
    ])
)

@allowed(['None', 'AzureServices'])
@description('If allowedIp is set, whether azure services are allowed to bypass the storage and AI services firewall.')
param bypass string = 'AzureServices'

@description('Public network access value for all deployed resources')
@allowed(['Enabled', 'Disabled'])
param publicNetworkAccess string = 'Disabled'

@description('Add a private endpoints for network connectivity')
param usePrivateEndpoint bool = false

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Use Application Insights for monitoring and performance tracing')
param useApplicationInsights bool = true

param assignRoles bool = false

var abbrs = loadJsonContent('abbreviations.json')
var roles = loadJsonContent('azure_roles.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

var tenantIdForAuth = !empty(authTenantId) ? authTenantId : tenantId
var authenticationIssuerUri = '${environment().authentication.loginEndpoint}${tenantIdForAuth}/v2.0'

@description('Whether the deployment is running on GitHub Actions')
param runningOnGh string = ''

@description('Whether the deployment is running on Azure DevOps Pipeline')
param runningOnAdo string = ''

param containerRegistryName string = '' // Set in main.parameters.json

// Configure CORS for allowing different web apps to use the backend
// For more information please see https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
var msftAllowedOrigins = ['https://portal.azure.com', 'https://ms.portal.azure.com']
var loginEndpoint = environment().authentication.loginEndpoint
var loginEndpointFixed = lastIndexOf(loginEndpoint, '/') == length(loginEndpoint) - 1
  ? substring(loginEndpoint, 0, length(loginEndpoint) - 1)
  : loginEndpoint
var allMsftAllowedOrigins = !(empty(clientAppId)) ? union(msftAllowedOrigins, [loginEndpointFixed]) : msftAllowedOrigins
// Combine custom origins with Microsoft origins, remove any empty origin strings and remove any duplicate origins
var allowedOrigins = reduce(
  filter(union(split(allowedOrigin, ';'), allMsftAllowedOrigins), o => length(trim(o)) > 0),
  [],
  (cur, next) => union(cur, [next])
)

// Network isolation
param useExistingPrivateDnsZones bool = false
param privateDnsZonesSubscriptionId string = ''
param privateDnsZonesResourceGroupName string = ''
param linkPrivateEndpointToPrivateDnsZone bool = false
param skipPrivateDnsZones bool = false

param useExistingVnet bool = false
param existingVnetSubscriptionId string = ''
param existingVnetResourceGroupName string = ''
param existingVnetName string = ''
param existingBackendSubnetName string = ''
param existingAppIntSubnetName string = ''
param existingLogicIntSubnetName string = ''

param subnetBackendName string = 'backend-subnet'
param subnetAppIntName string = 'app-int-subnet'
param subnetLogicIntName string = 'logic-int-subnet'

param vnetAddressPrefix string = '10.0.0.0/16'
param subnetBackendAddressPrefix string = '10.0.1.0/24'
param subnetAppIntAddressPrefix string = '10.0.2.0/24'
param subnetLogicIntAddressPrefix string = '10.0.3.0/24'

// Organize resources in a resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = if (createResourceGroup) {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

resource existingResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!createResourceGroup) {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
}

var selectedResourceGroupName = (createResourceGroup ? resourceGroup.name : existingResourceGroup.name)

resource mainResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: selectedResourceGroupName
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : mainResourceGroup.name
}

resource storageResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(storageResourceGroupName)) {
  name: !empty(storageResourceGroupName) ? storageResourceGroupName : mainResourceGroup.name
}

resource cosmosDbResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(cosmodDbResourceGroupName)) {
  name: !empty(cosmodDbResourceGroupName) ? cosmodDbResourceGroupName : mainResourceGroup.name
}

var foundryEnabled = useFoundry != 'none'
var foundryExistingSourceId = !empty(foundryProjectResourceId)
  ? foundryProjectResourceId
  : foundryAccountResourceId
var foundryExistingResourceParts = split(foundryExistingSourceId, '/')
var foundrySubscriptionId = useFoundry == 'existing'
  ? foundryExistingResourceParts[2]
  : subscription().subscriptionId
var selectedFoundryResourceGroupName = useFoundry == 'existing'
  ? foundryExistingResourceParts[4]
  : (!empty(foundryResourceGroupName) ? foundryResourceGroupName : mainResourceGroup.name)
var selectedFoundryAccountName = useFoundry == 'existing'
  ? foundryExistingResourceParts[8]
  : (!empty(foundryAccountName) ? foundryAccountName : '${abbrs.cognitiveServicesAccounts}foundry-${resourceToken}')
var selectedFoundryProjectName = useFoundry == 'existing' && !empty(foundryProjectResourceId)
  ? foundryExistingResourceParts[10]
  : foundryProjectName

var documentIntelligenceEnabled = useDocumentIntelligence != 'none'
var documentIntelligenceResourceParts = split(documentIntelligenceResourceId, '/')
var documentIntelligenceSubscriptionId = useDocumentIntelligence == 'existing'
  ? documentIntelligenceResourceParts[2]
  : subscription().subscriptionId
var selectedDocumentIntelligenceResourceGroupName = useDocumentIntelligence == 'existing'
  ? documentIntelligenceResourceParts[4]
  : (!empty(documentIntelligenceResourceGroupName) ? documentIntelligenceResourceGroupName : mainResourceGroup.name)
var selectedDocumentIntelligenceName = useDocumentIntelligence == 'existing'
  ? documentIntelligenceResourceParts[8]
  : (!empty(documentIntelligenceName)
      ? documentIntelligenceName
      : '${abbrs.cognitiveServicesDocumentIntelligence}${resourceToken}')

module storage 'modules/storage/storage-account.bicep' = {
  name: 'storage'
  scope: storageResourceGroup
  params: {
    name: !empty(storageAccountName) ? storageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'
    location: !empty(storageResourceGroupLocation) ? storageResourceGroupLocation : location
    tags: tags
    publicNetworkAccess: !empty(ipRules) ? 'Enabled' : publicNetworkAccess
    networkAcls: {
      bypass: bypass
      defaultAction: 'Deny'
      ipRules: map(ipRules, ipRule => {
        value: ipRule.?value
        action: 'Allow'
      })
      resourceAccessRules: [
        {
          tenantId: subscription().tenantId
          resourceId: '/subscriptions/${subscription().subscriptionId}/resourceGroups/${mainResourceGroup.name}/providers/Microsoft.Logic/workflows/*'
        }
      ]
    }
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    sku: {
      name: storageSkuName
    }
    deleteRetentionPolicy: {
      enabled: true
      days: 2
    }
    containers: [
      {
        name: storageContainerName
        publicAccess: 'None'
      }
      {
        name: storageTokenContainerName
        publicAccess: 'None'
      }
      {
        name: storageInstructionsContainerName
        publicAccess: 'None'
      }
      {
        name: storageInputContainerName
        publicAccess: 'None'
      }
    ]
  }
}

// Monitor application with Azure Monitor
module monitoring 'modules/monitor/monitoring.bicep' = if (useApplicationInsights) {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    applicationInsightsName: !empty(applicationInsightsName)
      ? applicationInsightsName
      : '${abbrs.insightsComponents}${resourceToken}'
    logAnalyticsName: !empty(logAnalyticsName)
      ? logAnalyticsName
      : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    publicNetworkAccess: publicNetworkAccess
    linkedStorageAccountId: storage.outputs.id
  }
}

module applicationInsightsDashboard 'backend-dashboard.bicep' = if (useApplicationInsights) {
  name: 'application-insights-dashboard'
  scope: mainResourceGroup
  params: {
    name: !empty(applicationInsightsDashboardName)
      ? applicationInsightsDashboardName
      : '${abbrs.portalDashboards}${resourceToken}'
    location: location
    applicationInsightsName: useApplicationInsights ? monitoring.outputs.applicationInsightsName : ''
  }
}

// TODO: Add support for existing container registries
module containerRegistry 'br/public:avm/res/container-registry/registry:0.5.1' = {
  name: 'container-registry'
  scope: mainResourceGroup
  params: {
    name: !empty(containerRegistryName) ? containerRegistryName : '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    acrAdminUserEnabled: false
    tags: tags
    acrSku: 'Premium'
    networkRuleSetIpRules: !empty(ipRules) ? ipRules : null
    publicNetworkAccess: !empty(ipRules) ? 'Enabled' : publicNetworkAccess
    networkRuleSetDefaultAction: 'Deny'
    exportPolicyStatus: !empty(ipRules) ? 'enabled' : (publicNetworkAccess == 'Enabled' ? 'enabled' : 'disabled')
  }
}

// Create an App Service Plan to group applications under the same payment plan and SKU
module backendPlan 'modules/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: mainResourceGroup
  params: {
    name: !empty(backendServicePlanName) ? backendServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: location
    tags: tags
    aseId: backendServicePlanAseId
    sku: {
      name: backendServiceSkuName
      capacity: 1
      tier: backendServiceSkuTier
    }
    kind: 'linux'
  }
}

var appEnvVariables = {
  AZURE_STORAGE_ACCOUNT: storage.outputs.name
  AZURE_STORAGE_CONTAINER: storageInputContainerName
  APPLICATIONINSIGHTS_CONNECTION_STRING: useApplicationInsights
    ? monitoring.outputs.applicationInsightsConnectionString
    : ''
  AZURE_COSMOSDB_ACCOUNT: cosmosDb.outputs.name
  AZURE_COSMOSDB_DATABASE: cosmosDbWorkItemDatabaseName
  AZURE_COSMOSDB_CONTAINER: cosmosDbWorkItemContainerName
  // Shared by all OpenAI deployments
  OPENAI_HOST: openAiHost
  AZURE_OPENAI_EMB_MODEL_NAME: embedding.modelName
  AZURE_OPENAI_EMB_DIMENSIONS: embedding.dimensions
  AZURE_OPENAI_CHATGPT_MODEL: chatGpt.modelName
  AZURE_OPENAI_GPT4V_MODEL: gpt4v.modelName
  // Specific to Azure OpenAI
  AZURE_OPENAI_SERVICE: isAzureOpenAiHost ? (deployAzureOpenAi ? openAi.outputs.name : existingOpenAi.name) : ''
  AZURE_OPENAI_CHATGPT_DEPLOYMENT: chatGpt.deploymentName
  AZURE_OPENAI_EMB_DEPLOYMENT: embedding.deploymentName
  AZURE_OPENAI_GPT4V_DEPLOYMENT: useGPT4V ? gpt4v.deploymentName : ''
  AZURE_OPENAI_API_VERSION: azureOpenAiApiVersion
  AZURE_OPENAI_API_KEY_OVERRIDE: azureOpenAiApiKey
  AZURE_OPENAI_CUSTOM_URL: azureOpenAiCustomUrl
  // Used only with non-Azure OpenAI deployments
  OPENAI_API_KEY: openAiApiKey
  OPENAI_ORGANIZATION: openAiApiOrganization
  // Optional login and item-level access control system
  AZURE_SERVER_APP_ID: serverAppId
  AZURE_CLIENT_APP_ID: clientAppId
  AZURE_TENANT_ID: tenantId
  AZURE_AUTH_TENANT_ID: tenantIdForAuth
  AZURE_AUTHENTICATION_ISSUER_URI: authenticationIssuerUri
  // CORS support, for frontends on other hosts
  ALLOWED_ORIGIN: join(allowedOrigins, ';')
  RUNNING_IN_PRODUCTION: 'true'
  WEBSITES_PORT: '8000'
}

// App Service for the web application (Python Quart app with JS frontend)
module backend 'modules/host/appservice.bicep' = {
  name: 'web'
  scope: mainResourceGroup
  params: {
    name: !empty(backendServiceName) ? backendServiceName : '${abbrs.webSitesAppService}backend-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'backend' })
    // Need to check deploymentTarget again due to https://github.com/Azure/bicep/issues/3990
    appServicePlanId: backendPlan.outputs.id
    kind: 'app,linux,container'
    imageName: '${containerRegistry.outputs.loginServer}/backend:latest'
    scmDoBuildDuringDeployment: true
    managedIdentity: true
    ipRules: ipRules
    publicNetworkAccess: !empty(ipRules) || !empty(backendServicePlanAseId) ? 'Enabled' : publicNetworkAccess
    virtualNetworkSubnetId: isolation.outputs.appSubnetId
    isHostedInAse: !empty(backendServicePlanAseId)
    allowedOrigins: allowedOrigins
    clientAppId: clientAppId
    serverAppId: serverAppId
    enableUnauthenticatedAccess: enableUnauthenticatedAccess
    disableAppServicesAuthentication: disableAppServicesAuthentication
    clientSecretSettingName: !empty(clientAppSecret) ? 'AZURE_CLIENT_APP_SECRET' : ''
    authenticationIssuerUri: authenticationIssuerUri
    use32BitWorkerProcess: backendServiceSkuName == 'F1'
    alwaysOn: backendServiceSkuName != 'F1'
    appSettings: union(appEnvVariables, {
      AZURE_SERVER_APP_SECRET: serverAppSecret
      AZURE_CLIENT_APP_SECRET: clientAppSecret
    })
    applicationInsightsName: monitoring.outputs.applicationInsightsName
  }
}

module logicIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  scope: mainResourceGroup
  name: 'logic-identity'
  params: {
    // Required parameters
    name: '${abbrs.managedIdentityUserAssignedIdentities}logic-${resourceToken}'
    // Non-required parameters
    location: location
  }
}

module logicAppServicePlan 'modules/host/appserviceplan.bicep' = {
  name: 'logicserviceplan'
  scope: mainResourceGroup
  params: {
    name: !empty(logicAppServicePlanName) ? logicAppServicePlanName : '${abbrs.webServerFarms}logic-${resourceToken}'
    location: location
    tags: tags
    aseId: logicAppServiceAseId
    sku: {
      name: logicAppServiceSkuName
      capacity: 1
      tier: logicAppServiceSkuTier
    }
    reserved: false
    kind: 'elastic'
  }
}

module logicAppStorage 'modules/storage/storage-account.bicep' = {
  name: 'logic-storage'
  scope: storageResourceGroup
  params: {
    name: '${abbrs.storageStorageAccounts}logic${resourceToken}'
    location: !empty(storageResourceGroupLocation) ? storageResourceGroupLocation : location
    tags: tags
    publicNetworkAccess: !empty(ipRules) ? 'Enabled' : publicNetworkAccess
    networkAcls: {
      bypass: bypass
      defaultAction: 'Deny'
      ipRules: map(ipRules, ipRule => {
        value: ipRule.?value
        action: 'Allow'
      })
    }
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    sku: {
      name: storageSkuName
    }
    deleteRetentionPolicy: {
      enabled: true
      days: 2
    }
  }
}

module logicApp 'br/public:avm/res/web/site:0.16.0' = {
  name: 'logic'
  scope: mainResourceGroup
  params: {
    // Required parameters
    kind: 'functionapp,workflowapp'
    tags: union(tags, { 'azd-service-name': 'logic' })
    name: !empty(logicAppServiceName) ? logicAppServiceName : '${abbrs.logicWorkflows}${resourceToken}'
    serverFarmResourceId: logicAppServicePlan.outputs.id
    managedIdentities: {
      systemAssigned: true
      userAssignedResourceIds: [
        logicIdentity.outputs.resourceId
      ]
    }
    configs: [
      {
        name: 'appsettings'
        retainCurrentAppSettings: true
        applicationInsightResourceId: useApplicationInsights ? monitoring.outputs.applicationInsightsId : ''
        storageAccountResourceId: logicAppStorage.outputs.id
        storageAccountUseIdentityAuthentication: true
        properties: {
          APP_KIND: 'workflowApp'
          FUNCTIONS_EXTENSION_VERSION: '~4'
          FUNCTIONS_WORKER_RUNTIME: 'dotnet'
          WEBSITE_NODE_DEFAULT_VERSION: '~20'
          WORKFLOWS_LOCATION_NAME: location
          WORKFLOWS_MANAGEMENT_BASE_URI: 'https://management.azure.com/'
          WORKFLOWS_RESOURCE_GROUP_NAME: mainResourceGroup.name
          WORKFLOWS_SUBSCRIPTION_ID: subscription().subscriptionId
          WORKFLOWS_TENANT_ID: tenantId
          AZURE_COSMOS_ACCOUNT_NAME: cosmosDb.outputs.name
          AZURE_COSMOS_ACCOUNT_URI: cosmosDb.outputs.endpoint
          AZURE_COSMOS_CONTAINER: cosmosDbWorkItemContainerName
          AZURE_COSMOS_DATABASE: cosmosDbWorkItemDatabaseName
          AZURE_OPENAI_DEPLOYMENT_NAME: gpt4v.deploymentName
          AZURE_OPENAI_ENDPOINT: isAzureOpenAiHost
            ? (deployAzureOpenAi ? openAi.outputs.endpoint : existingOpenAi.properties.endpoint)
            : ''
          AZURE_OPENAI_MODEL_NAME: gpt4v.modelName
          AZURE_OPENAI_MODEL_VERSION: gpt4v.deploymentVersion
          AZURE_OPENAI_RESOURCE_ID: isAzureOpenAiHost
            ? (deployAzureOpenAi ? openAi.outputs.resourceId : existingOpenAi.id)
            : ''
          AZURE_STORAGE_ENDPOINT: storage.outputs.primaryEndpoints.blob
          AZURE_STORAGE_INSTRUCTIONS_CONTAINER: storageInstructionsContainerName
          AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE: storageSystemInstructionsFile
          AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE: storageProcessingInstructionsFile
          AZURE_STORAGE_EVALUATION_INSTRUCTIONS_FILE: storageEvaluationInstructionsFile
          AZURE_STORAGE_INPUT_CONTAINER: storageInputContainerName
          AzureWebJobsStorage__credential: 'managedidentity'
          AzureWebJobsStorage__managedIdentityResourceId: logicIdentity.outputs.resourceId
          WORKFLOWS_IDENTITY_RESOURCE_ID: logicIdentity.outputs.resourceId
        }
      }
      {
        name: 'web'
        properties: {
          cors: {
            allowedOrigins: allowedOrigins
          }
          httpLoggingEnabled: true
        }
      }
    ]
    publicNetworkAccess: !empty(ipRules) ? 'Enabled' : publicNetworkAccess
    virtualNetworkSubnetId: empty(logicAppServiceAseId) ? isolation.outputs.funcIntSubnetId : null
    vnetImagePullEnabled: true
    vnetContentShareEnabled: true
    vnetRouteAllEnabled: true
    storageAccountRequired: true
    // Non-required parameters
    siteConfig: {
      ipSecurityRestrictions: map(ipRules, ipRule => {
        ipAddress: lastIndexOf(ipRule.?value, '/') == -1 ? '${ipRule.?value}/32' : ipRule.?value
        action: 'Allow'
      })
      ipSecurityRestrictionsDefaultAction: 'Deny'
      alwaysOn: true
      minTlsVersion: '1.2'
      functionsRuntimeScaleMonitoringEnabled: true
      use32BitWorkerProcess: false
    }
    diagnosticSettings: [
      {
        name: 'default'
        workspaceResourceId: useApplicationInsights ? monitoring.outputs.logAnalyticsWorkspaceId : ''
        logCategoriesAndGroups: [
          {
            category: 'WorkflowRuntime'
            enabled: true
          }
          {
            category: 'FunctionAppLogs'
            enabled: true
          }
          {
            category: 'AppServiceAuthenticationLogs'
            enabled: true
          }
        ]
        metricCategories: [
          {
            category: 'AllMetrics'
            enabled: true
          }
        ]
      }
    ]
  }
}

module logicCosmosConnection 'modules/host/connection.bicep' = {
  scope: cosmosDbResourceGroup
  name: 'cosmos-connection'
  params: {
    connectionName: 'documentdb'
    displayName: 'connection_documentdb'
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: logicApp.outputs.?systemAssignedMIPrincipalId
      }
      {
        tenantId: subscription().tenantId
        objectId: logicIdentity.outputs.principalId
      }
    ]
  }
}

module logicAppSettings 'modules/host/appservice-merge-appsettings.bicep' = {
  name: 'logic-merge-app-settings'
  scope: mainResourceGroup
  params: {
    name: logicApp.outputs.name
    appSettings: {
      AZURE_COSMOS_CONNECTIONRUNTIMEURL: logicCosmosConnection.outputs.connectionRuntimeUrl
    }
  }
}

var defaultOpenAiDeployments = [
  {
    name: chatGpt.deploymentName
    model: {
      format: 'OpenAI'
      name: chatGpt.modelName
      version: chatGpt.deploymentVersion
    }
    sku: {
      name: chatGpt.deploymentSkuName
      capacity: chatGpt.deploymentCapacity
    }
  }
  {
    name: embedding.deploymentName
    model: {
      format: 'OpenAI'
      name: embedding.modelName
      version: embedding.deploymentVersion
    }
    sku: {
      name: embedding.deploymentSkuName
      capacity: embedding.deploymentCapacity
    }
  }
]

var openAiDeployments = concat(
  defaultOpenAiDeployments,
  useEval
    ? [
        {
          name: eval.deploymentName
          model: {
            format: 'OpenAI'
            name: eval.modelName
            version: eval.deploymentVersion
          }
          sku: {
            name: eval.deploymentSkuName
            capacity: eval.deploymentCapacity
          }
        }
      ]
    : [],
  useGPT4V
    ? [
        {
          name: gpt4v.deploymentName
          model: {
            format: 'OpenAI'
            name: gpt4v.modelName
            version: gpt4v.deploymentVersion
          }
          sku: {
            name: gpt4v.deploymentSkuName
            capacity: gpt4v.deploymentCapacity
          }
        }
      ]
    : []
)

module openAi 'br/public:avm/res/cognitive-services/account:0.7.2' = if (isAzureOpenAiHost && deployAzureOpenAi) {
  name: 'openai'
  scope: openAiResourceGroup
  params: {
    name: !empty(openAiServiceName) ? openAiServiceName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: openAiLocation
    tags: tags
    kind: 'OpenAI'
    managedIdentities: {
      systemAssigned: true
    }
    customSubDomainName: !empty(openAiServiceName)
      ? openAiServiceName
      : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    publicNetworkAccess: !empty(ipRules) ? 'Enabled' : publicNetworkAccess
    networkAcls: {
      defaultAction: 'Deny'
      bypass: bypass
      ipRules: ipRules
    }
    sku: openAiSkuName
    deployments: openAiDeployments
    disableLocalAuth: azureOpenAiDisableKeys
  }
}

resource existingOpenAi 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = if (isAzureOpenAiHost && !deployAzureOpenAi) {
  name: openAiServiceName
  scope: openAiResourceGroup
}

module openAiDeploymentsInExistingOpenAi 'modules/ai/openai-deployments.bicep' = if (isAzureOpenAiHost && !deployAzureOpenAi && deployAzureOpenModels) {
  name: 'openai-deployments'
  scope: openAiResourceGroup
  params: {
    deployments: openAiDeployments
    openAiServiceName: existingOpenAi.name
  }
}

module foundry 'modules/ai/foundry.bicep' = if (foundryEnabled) {
  name: 'foundry'
  scope: az.resourceGroup(foundrySubscriptionId, selectedFoundryResourceGroupName)
  params: {
    mode: useFoundry == 'new' ? 'new' : 'existing'
    accountName: selectedFoundryAccountName
    projectName: selectedFoundryProjectName
    existingProjectName: useFoundry == 'existing' && !empty(foundryProjectResourceId)
      ? selectedFoundryProjectName
      : ''
    location: foundryLocation
    skuName: foundrySkuName
    tags: tags
    publicNetworkAccess: !empty(ipRules) ? 'Enabled' : publicNetworkAccess
    networkBypass: bypass
    ipRules: ipRules
    disableLocalAuth: true
    configureExistingResource: configureExistingAiServices
    enableDiagnostics: useApplicationInsights && (useFoundry == 'new' || configureExistingAiServices)
    logAnalyticsWorkspaceId: useApplicationInsights ? monitoring.outputs.logAnalyticsWorkspaceId : ''
    assignRoles: assignRoles
    principalId: principalId
    principalType: principalType
    cognitiveServicesUserRoleId: roles.CognitiveServicesUser
    connectAzureOpenAi: foundryConnectBaseOpenAi
    azureOpenAiEndpoint: openAiHost == 'azure'
      ? (deployAzureOpenAi ? openAi.outputs.endpoint : existingOpenAi.properties.endpoint)
      : ''
  }
}

module documentIntelligence 'modules/ai/document-intelligence.bicep' = if (documentIntelligenceEnabled) {
  name: 'document-intelligence'
  scope: az.resourceGroup(documentIntelligenceSubscriptionId, selectedDocumentIntelligenceResourceGroupName)
  params: {
    mode: useDocumentIntelligence == 'new' ? 'new' : 'existing'
    accountName: selectedDocumentIntelligenceName
    location: documentIntelligenceLocation
    skuName: documentIntelligenceSkuName
    tags: tags
    publicNetworkAccess: !empty(ipRules) ? 'Enabled' : publicNetworkAccess
    networkBypass: bypass
    ipRules: ipRules
    disableLocalAuth: true
    configureExistingResource: configureExistingAiServices
    enableDiagnostics: useApplicationInsights && (useDocumentIntelligence == 'new' || configureExistingAiServices)
    logAnalyticsWorkspaceId: useApplicationInsights ? monitoring.outputs.logAnalyticsWorkspaceId : ''
    assignRoles: assignRoles
    principalId: principalId
    principalType: principalType
    cognitiveServicesUserRoleId: roles.CognitiveServicesUser
  }
}

module cosmosDb 'br/public:avm/res/document-db/database-account:0.6.1' = {
  name: 'cosmosdb'
  scope: cosmosDbResourceGroup
  params: {
    name: !empty(cosmosDbAccountName) ? cosmosDbAccountName : '${abbrs.documentDBDatabaseAccounts}${resourceToken}'
    location: !empty(cosmosDbLocation) ? cosmosDbLocation : location
    locations: [
      {
        locationName: !empty(cosmosDbLocation) ? cosmosDbLocation : location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    enableFreeTier: cosmosDbSkuName == 'free'
    capabilitiesToAdd: cosmosDbSkuName == 'serverless' ? ['EnableServerless'] : []
    networkRestrictions: {
      ipRules: map(ipRules, ipRule => lastIndexOf(ipRule.?value, '/') == -1 ? '${ipRule.?value}/32' : ipRule.?value)
      networkAclBypass: bypass
      publicNetworkAccess: !empty(ipRules) ? 'Enabled' : publicNetworkAccess
      virtualNetworkRules: []
    }
    sqlDatabases: [
      {
        name: cosmosDbWorkItemDatabaseName
        throughput: (cosmosDbSkuName == 'serverless') ? null : cosmosDbThroughput
        containers: [
          {
            name: cosmosDbWorkItemContainerName
            kind: 'Hash'
            paths: [
              '/created_at'
            ]
            indexingPolicy: {
              indexingMode: 'consistent'
              automatic: true
              includedPaths: [
                {
                  path: '/created_at/?'
                }
                {
                  path: '/source_name/?'
                }
              ]
              excludedPaths: [
                {
                  path: '/*'
                }
                {
                  path: '/"_etag"/?'
                }
              ]
              fullTextIndexes: []
            }
          }
        ]
      }
    ]
  }
}

module isolation 'network-isolation.bicep' = {
  name: 'networks'
  scope: mainResourceGroup
  params: {
    deploymentTarget: 'appservice'
    location: location
    tags: tags
    vnetName: useExistingVnet
      ? (!empty(existingVnetName) ? existingVnetName : '${abbrs.networkVirtualNetworks}${resourceToken}')
      : '${abbrs.networkVirtualNetworks}${resourceToken}'
    // Need to check deploymentTarget due to https://github.com/Azure/bicep/issues/3990
    appServicePlanName: backendPlan.outputs.name
    funcServicePlanName: logicAppServicePlan.outputs.name
    usePrivateEndpoint: usePrivateEndpoint
    vnetAddressPrefix: vnetAddressPrefix
    subnetAppIntAddressPrefix: subnetAppIntAddressPrefix
    subnetBackendAddressPrefix: subnetBackendAddressPrefix
    subnetFuncIntAddressPrefix: subnetLogicIntAddressPrefix
    useExistingVnet: useExistingVnet
    existingVnetSubscriptionId: existingVnetSubscriptionId
    existingVnetResourceGroupName: existingVnetResourceGroupName
    subnetAppIntName: useExistingVnet
      ? (!empty(existingAppIntSubnetName) ? existingAppIntSubnetName : subnetAppIntName)
      : subnetAppIntName
    subnetBackendName: useExistingVnet
      ? (!empty(existingBackendSubnetName) ? existingBackendSubnetName : subnetBackendName)
      : subnetBackendName
    subnetFuncIntName: useExistingVnet
      ? (!empty(existingLogicIntSubnetName) ? existingLogicIntSubnetName : subnetLogicIntName)
      : subnetLogicIntName
  }
}

var environmentData = environment()

var openAiPrivateEndpointConnection = (isAzureOpenAiHost && deployAzureOpenAi)
  ? [
      {
        groupId: 'account'
        dnsZoneName: 'privatelink.openai.azure.com'
        resourceIds: [openAi.outputs.resourceId]
      }
    ]
  : []

var foundryPrivateEndpointConnection = (foundryEnabled && usePrivateEndpoint && (useFoundry == 'new' || configureExistingAiServices))
  ? [
      {
        groupId: 'account'
        dnsZoneName: 'privatelink.services.ai.azure.com'
        resourceIds: [foundry.outputs.accountId]
      }
    ]
  : []

var documentIntelligencePrivateEndpointConnection = (documentIntelligenceEnabled && usePrivateEndpoint && (useDocumentIntelligence == 'new' || configureExistingAiServices))
  ? [
      {
        groupId: 'account'
        dnsZoneName: 'privatelink.cognitiveservices.azure.com'
        resourceIds: [documentIntelligence.outputs.resourceId]
      }
    ]
  : []

var websiteResourceIds = union(
  [],
  empty(backendServicePlanAseId) ? [backend.outputs.id] : [],
  empty(logicAppServiceAseId) ? [logicApp.outputs.resourceId] : []
)

var otherPrivateEndpointConnections = (usePrivateEndpoint)
  ? union(
      [
        {
          groupId: 'blob'
          dnsZoneName: 'privatelink.blob.${environmentData.suffixes.storage}'
          resourceIds: [storage.outputs.id, logicAppStorage.outputs.id]
        }
        {
          groupId: 'table'
          dnsZoneName: 'privatelink.table.${environmentData.suffixes.storage}'
          resourceIds: [storage.outputs.id, logicAppStorage.outputs.id]
        }
        {
          groupId: 'queue'
          dnsZoneName: 'privatelink.queue.${environmentData.suffixes.storage}'
          resourceIds: [storage.outputs.id, logicAppStorage.outputs.id]
        }
        {
          groupId: 'file'
          dnsZoneName: 'privatelink.file.${environmentData.suffixes.storage}'
          resourceIds: [storage.outputs.id, logicAppStorage.outputs.id]
        }
        {
          groupId: 'dfs'
          dnsZoneName: 'privatelink.dfs.${environmentData.suffixes.storage}'
          resourceIds: [storage.outputs.id, logicAppStorage.outputs.id]
        }
        {
          groupId: 'sql'
          dnsZoneName: 'privatelink.documents.azure.com'
          resourceIds: [cosmosDb.outputs.resourceId]
        }
        {
          groupId: 'registry'
          dnsZoneName: 'privatelink.azurecr.io'
          resourceIds: [containerRegistry.outputs.resourceId]
        }
      ],
      !empty(websiteResourceIds)
        ? [
            {
              groupId: 'sites'
              dnsZoneName: 'privatelink.azurewebsites.net'
              resourceIds: websiteResourceIds
            }
          ]
        : []
    )
  : []

var privateEndpointConnections = concat(
  otherPrivateEndpointConnections,
  openAiPrivateEndpointConnection,
  foundryPrivateEndpointConnection,
  documentIntelligencePrivateEndpointConnection
)

module privateEndpoints 'private-endpoints.bicep' = if (usePrivateEndpoint) {
  name: 'privateEndpoints'
  scope: mainResourceGroup
  params: {
    location: location
    tags: tags
    resourceToken: resourceToken
    privateEndpointConnections: privateEndpointConnections
    applicationInsightsId: useApplicationInsights ? monitoring.outputs.applicationInsightsId : ''
    logAnalyticsWorkspaceId: useApplicationInsights ? monitoring.outputs.logAnalyticsWorkspaceId : ''
    vnetName: isolation.outputs.vnetName
    vnetPeSubnetName: isolation.outputs.backendSubnetId
    privateDnsZonesSubscriptionId: privateDnsZonesSubscriptionId
    privateDnsZonesResourceGroupName: privateDnsZonesResourceGroupName
    useExistingPrivateDnsZones: useExistingPrivateDnsZones
    linkPrivateEndpointToPrivateDnsZone: linkPrivateEndpointToPrivateDnsZone
    skipPrivateDnsZones: skipPrivateDnsZones
  }
}

// USER ROLES
var principalType = empty(runningOnGh) && empty(runningOnAdo) ? 'User' : 'ServicePrincipal'

module foundryProjectOpenAiRole 'modules/security/role.bicep' = if (foundryEnabled && foundryConnectBaseOpenAi && openAiHost == 'azure' && assignRoles) {
  scope: openAiResourceGroup
  name: 'foundry-project-openai-role'
  params: {
    principalId: foundry.outputs.projectPrincipalId
    roleDefinitionId: roles.CognitiveServicesOpenAIUser
    principalType: 'ServicePrincipal'
  }
}

var firstId = !deployAzureOpenAi && !empty(existingOpenAi.identity.?userAssignedIdentities)
  ? first(objectKeys(existingOpenAi.identity.userAssignedIdentities))
  : ''
var existingOpenAiUserIdentityPrincipalId = !deployAzureOpenAi && !empty(firstId)
  ? existingOpenAi.identity.userAssignedIdentities[firstId!].principalId
  : ''
var existingOpenAiManagedIdentityPrincipalId = (!deployAzureOpenAi && !empty(existingOpenAi.identity.?principalId)
  ? existingOpenAi.identity.principalId
  : existingOpenAiUserIdentityPrincipalId)

module openAiRoleUser 'modules/security/role.bicep' = if (isAzureOpenAiHost && assignRoles && !empty(principalId)) {
  scope: openAiResourceGroup
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.CognitiveServicesOpenAIUser
    principalType: principalType
  }
}

// For both document intelligence and computer vision
module cognitiveServicesRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: mainResourceGroup
  name: 'cognitiveservices-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.CognitiveServicesUser
    principalType: principalType
  }
}

module storageRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: storageResourceGroup
  name: 'storage-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.StorageBlobDataReader
    principalType: principalType
  }
}

module storageContribRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: storageResourceGroup
  name: 'storage-contrib-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalType: principalType
  }
}

module storageOwnerRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: storageResourceGroup
  name: 'storage-owner-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.StorageBlobDataOwner
    principalType: principalType
  }
}

module cosmosDbAccountContribRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: cosmosDbResourceGroup
  name: 'cosmosdb-account-contrib-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.DocumentDBAccountContributor
    principalType: principalType
  }
}

// RBAC for Cosmos DB
// https://learn.microsoft.com/azure/cosmos-db/nosql/security/how-to-grant-data-plane-role-based-access
module cosmosDbDataContribRoleUser 'modules/security/documentdb-sql-role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: cosmosDbResourceGroup
  name: 'cosmosdb-data-contrib-role-user'
  params: {
    databaseAccountName: cosmosDb.outputs.name
    principalId: principalId
    // Cosmos DB Built-in Data Contributor role
    roleDefinitionId: '/${subscription().id}/resourceGroups/${cosmosDb.outputs.resourceGroupName}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDb.outputs.name}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002'
  }
}

module queueDataReaderRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: cosmosDbResourceGroup
  name: 'queue-data-reader-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.StorageQueueDataReader
    principalType: principalType
  }
}

module queueDataContribRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: cosmosDbResourceGroup
  name: 'queue-data-contrib-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.StorageQueueDataContributor
    principalType: principalType
  }
}

module queueDataMessageProcRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: cosmosDbResourceGroup
  name: 'queue-data-message-proc-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.StorageQueueDataMessageProcessor
    principalType: principalType
  }
}

module queueDataMessageSenderRoleUser 'modules/security/role.bicep' = if (assignRoles && !empty(principalId)) {
  scope: cosmosDbResourceGroup
  name: 'queue-data-message-sender-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: roles.StorageQueueDataMessageSender
    principalType: principalType
  }
}

// SYSTEM IDENTITIES
module openAiRoleBackend 'modules/security/role.bicep' = if (isAzureOpenAiHost && assignRoles) {
  scope: openAiResourceGroup
  name: 'openai-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: roles.CognitiveServicesOpenAIUser
    principalType: 'ServicePrincipal'
  }
}

module storageRoleBackend 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: roles.StorageBlobDataReader
    principalType: 'ServicePrincipal'
  }
}

module storageContribRoleBackend 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-contrib-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: roles.StorageBlobDataContributor
    principalType: 'ServicePrincipal'
  }
}

module storageQueueMessageSenderRoleBackend 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-message-sender-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: roles.StorageQueueDataMessageSender
    principalType: 'ServicePrincipal'
  }
}

module containerRegistryRoleBackend 'modules/security/role.bicep' = if (assignRoles) {
  scope: mainResourceGroup
  name: 'container-registry-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: roles.AcrPull
    principalType: 'ServicePrincipal'
  }
}

module storageOwnerRoleBackend 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-owner-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: roles.StorageBlobDataOwner
    principalType: 'ServicePrincipal'
  }
}

// RBAC for Cosmos DB
// https://learn.microsoft.com/azure/cosmos-db/nosql/security/how-to-grant-data-plane-role-based-access
module cosmosDbRoleBackend 'modules/security/documentdb-sql-role.bicep' = if (assignRoles) {
  scope: cosmosDbResourceGroup
  name: 'cosmosdb-role-backend'
  params: {
    databaseAccountName: cosmosDb.outputs.name
    principalId: backend.outputs.identityPrincipalId
    // Cosmos DB Built-in Data Contributor role
    roleDefinitionId: '/${subscription().id}/resourceGroups/${cosmosDb.outputs.resourceGroupName}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDb.outputs.name}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002'
  }
}

module storageContribRoleDiag 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-contrib-role-diag'
  params: {
    principalId: '47a8880e-8e60-4153-9e25-fa98482bae5d'
    roleDefinitionId: roles.StorageBlobDataContributor
    principalType: 'ServicePrincipal'
  }
}

module openAiRoleLogicUserAssigned 'modules/security/role.bicep' = if (isAzureOpenAiHost && assignRoles) {
  scope: openAiResourceGroup
  name: 'openai-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.CognitiveServicesOpenAIUser
    principalType: 'ServicePrincipal'
  }
}

module openAiRoleLogic 'modules/security/role.bicep' = if (isAzureOpenAiHost && assignRoles) {
  scope: openAiResourceGroup
  name: 'openai-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.CognitiveServicesOpenAIUser
    principalType: 'ServicePrincipal'
  }
}

module storageRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-blob-reader-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageBlobDataReader
    principalType: 'ServicePrincipal'
  }
}

module storageRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-blob-reader-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageBlobDataReader
    principalType: 'ServicePrincipal'
  }
}

module storageContribRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-blob-contrib-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageBlobDataContributor
    principalType: 'ServicePrincipal'
  }
}

module storageContribRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-blob-contrib-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageBlobDataContributor
    principalType: 'ServicePrincipal'
  }
}

module storageAccountContributorRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-acc-contrib-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageAccountContributor
    principalType: 'ServicePrincipal'
  }
}

module storageTableDataContributorRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-table-data-contrib-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageTableDataContributor
    principalType: 'ServicePrincipal'
  }
}

module storageQueueContributorRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-contrib-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageQueueDataContributor
    principalType: 'ServicePrincipal'
  }
}

module storageFileContributorRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-file-contrib-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageFileDataPrivilegedContributor
    principalType: 'ServicePrincipal'
  }
}

module storageQueueDataReaderRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-data-reader-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageQueueDataReader
    principalType: 'ServicePrincipal'
  }
}

module storageQueueMessageProcRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-message-proc-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageQueueDataMessageProcessor
    principalType: 'ServicePrincipal'
  }
}

module storageQueueMessageSenderRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-message-sender-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageQueueDataMessageSender
    principalType: 'ServicePrincipal'
  }
}

module containerRegistryRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: mainResourceGroup
  name: 'container-registry-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.AcrPull
    principalType: 'ServicePrincipal'
  }
}

module storageOwnerRoleLogicUserAssigned 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-owner-role-logic-user-assigned'
  params: {
    principalId: logicIdentity.outputs.principalId
    roleDefinitionId: roles.StorageBlobDataOwner
    principalType: 'ServicePrincipal'
  }
}

module cosmosDbRoleLogicUserAssigned 'modules/security/documentdb-sql-role.bicep' = if (assignRoles) {
  scope: cosmosDbResourceGroup
  name: 'cosmosdb-role-logic-user-assigned'
  params: {
    databaseAccountName: cosmosDb.outputs.name
    principalId: logicIdentity.outputs.principalId
    // Cosmos DB Built-in Data Contributor role
    roleDefinitionId: '/${subscription().id}/resourceGroups/${cosmosDb.outputs.resourceGroupName}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDb.outputs.name}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002'
  }
}

module storageAccountContributorRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-acc-contrib-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageAccountContributor
    principalType: 'ServicePrincipal'
  }
}

module storageTableDataContributorRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-table-data-contrib-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageTableDataContributor
    principalType: 'ServicePrincipal'
  }
}

module storageQueueContributorRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-contrib-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageQueueDataContributor
    principalType: 'ServicePrincipal'
  }
}

module storageFileContributorRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-file-contrib-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageFileDataPrivilegedContributor
    principalType: 'ServicePrincipal'
  }
}

module storageQueueDataReaderRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-data-reader-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageQueueDataReader
    principalType: 'ServicePrincipal'
  }
}

module storageQueueMessageProcRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-message-proc-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageQueueDataMessageProcessor
    principalType: 'ServicePrincipal'
  }
}

module storageQueueMessageSenderRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-queue-message-sender-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageQueueDataMessageSender
    principalType: 'ServicePrincipal'
  }
}

module containerRegistryRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: mainResourceGroup
  name: 'container-registry-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.AcrPull
    principalType: 'ServicePrincipal'
  }
}

module storageOwnerRoleLogic 'modules/security/role.bicep' = if (assignRoles) {
  scope: storageResourceGroup
  name: 'storage-owner-role-logic'
  params: {
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    roleDefinitionId: roles.StorageBlobDataOwner
    principalType: 'ServicePrincipal'
  }
}

module cosmosDbRoleLogic 'modules/security/documentdb-sql-role.bicep' = if (assignRoles) {
  scope: cosmosDbResourceGroup
  name: 'cosmosdb-role-logic'
  params: {
    databaseAccountName: cosmosDb.outputs.name
    principalId: logicApp.outputs.?systemAssignedMIPrincipalId
    // Cosmos DB Built-in Data Contributor role
    roleDefinitionId: '/${subscription().id}/resourceGroups/${cosmosDb.outputs.resourceGroupName}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDb.outputs.name}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002'
  }
}

module cosmosDbRoleOpenAi 'modules/security/documentdb-sql-role.bicep' = if (isAzureOpenAiHost && assignRoles) {
  scope: cosmosDbResourceGroup
  name: 'cosmosdb-role-openai'
  params: {
    databaseAccountName: cosmosDb.outputs.name
    principalId: deployAzureOpenAi
      ? openAi.outputs.systemAssignedMIPrincipalId
      : existingOpenAiManagedIdentityPrincipalId
    // Cosmos DB Built-in Data Contributor role
    roleDefinitionId: '/${subscription().id}/resourceGroups/${cosmosDb.outputs.resourceGroupName}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDb.outputs.name}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002'
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenantId
output AZURE_AUTH_TENANT_ID string = tenantIdForAuth
output AZURE_RESOURCE_GROUP string = mainResourceGroup.name

// Shared by all OpenAI deployments
output OPENAI_HOST string = openAiHost
output AZURE_OPENAI_EMB_MODEL_NAME string = embedding.modelName
output AZURE_OPENAI_CHATGPT_MODEL string = chatGpt.modelName
output AZURE_OPENAI_GPT4V_MODEL string = gpt4v.modelName

// Specific to Azure OpenAI
output AZURE_OPENAI_SERVICE string = isAzureOpenAiHost
  ? (deployAzureOpenAi ? openAi.outputs.name : existingOpenAi.name)
  : ''
output AZURE_OPENAI_API_VERSION string = isAzureOpenAiHost ? azureOpenAiApiVersion : ''
output AZURE_OPENAI_RESOURCE_GROUP string = isAzureOpenAiHost ? openAiResourceGroup.name : ''
output AZURE_OPENAI_CHATGPT_DEPLOYMENT string = isAzureOpenAiHost ? chatGpt.deploymentName : ''
output AZURE_OPENAI_EMB_DEPLOYMENT string = isAzureOpenAiHost ? embedding.deploymentName : ''
output AZURE_OPENAI_GPT4V_DEPLOYMENT string = isAzureOpenAiHost && useGPT4V ? gpt4v.deploymentName : ''
output AZURE_OPENAI_EVAL_DEPLOYMENT string = isAzureOpenAiHost && useEval ? eval.deploymentName : ''
output AZURE_OPENAI_EVAL_MODEL string = isAzureOpenAiHost && useEval ? eval.modelName : ''

output USE_FOUNDRY string = useFoundry
output AZURE_FOUNDRY_ACCOUNT string = foundryEnabled ? foundry.outputs.accountName : ''
output AZURE_FOUNDRY_ACCOUNT_ID string = foundryEnabled ? foundry.outputs.accountId : ''
output AZURE_FOUNDRY_ACCOUNT_ENDPOINT string = foundryEnabled ? foundry.outputs.accountEndpoint : ''
output AZURE_FOUNDRY_RESOURCE_GROUP string = foundryEnabled ? selectedFoundryResourceGroupName : ''
output AZURE_FOUNDRY_LOCATION string = foundryEnabled ? foundry.outputs.location : ''
output AZURE_FOUNDRY_ACCOUNT_PRINCIPAL_ID string = foundryEnabled ? foundry.outputs.accountPrincipalId : ''
output AZURE_FOUNDRY_PROJECT string = foundryEnabled ? foundry.outputs.projectName : ''
output AZURE_FOUNDRY_PROJECT_ID string = foundryEnabled ? foundry.outputs.projectId : ''
output AZURE_FOUNDRY_PROJECT_ENDPOINT string = foundryEnabled ? foundry.outputs.projectEndpoint : ''
output AZURE_FOUNDRY_PROJECT_PRINCIPAL_ID string = foundryEnabled ? foundry.outputs.projectPrincipalId : ''

output USE_DOCUMENT_INTELLIGENCE string = useDocumentIntelligence
output AZURE_DOCUMENT_INTELLIGENCE_ACCOUNT string = documentIntelligenceEnabled
  ? documentIntelligence.outputs.accountName
  : ''
output AZURE_DOCUMENT_INTELLIGENCE_RESOURCE_GROUP string = documentIntelligenceEnabled
  ? selectedDocumentIntelligenceResourceGroupName
  : ''
output AZURE_DOCUMENT_INTELLIGENCE_LOCATION string = documentIntelligenceEnabled
  ? documentIntelligence.outputs.location
  : ''
output AZURE_DOCUMENT_INTELLIGENCE_RESOURCE_ID string = documentIntelligenceEnabled
  ? documentIntelligence.outputs.resourceId
  : ''
output AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT string = documentIntelligenceEnabled
  ? documentIntelligence.outputs.endpoint
  : ''
output AZURE_DOCUMENT_INTELLIGENCE_PRINCIPAL_ID string = documentIntelligenceEnabled
  ? documentIntelligence.outputs.principalId
  : ''

output AZURE_COSMOSDB_ACCOUNT string = cosmosDb.outputs.name
output AZURE_COSMOSDB_RESOURCE_GROUP string = cosmosDbResourceGroup.name
output AZURE_COSMOSDB_DATABASE string = cosmosDbWorkItemDatabaseName
output AZURE_COSMOSDB_CONTAINER string = cosmosDbWorkItemContainerName
output AZURE_COSMOSDB_API_VERSION string = cosmosDbWorkItemApiVersion

output AZURE_STORAGE_ACCOUNT string = storage.outputs.name
output AZURE_STORAGE_CONTAINER string = storageInputContainerName
output AZURE_STORAGE_INSTRUCTIONS_CONTAINER string = storageInstructionsContainerName
output AZURE_STORAGE_RESOURCE_GROUP string = storageResourceGroup.name

output AZURE_USE_AUTHENTICATION bool = true

output BACKEND_URI string = backend.outputs.uri
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name

output AZURE_BACKEND_SERVICE_NAME string = backend.outputs.name
output AZURE_LOGICAPP_SERVICE_NAME string = logicApp.outputs.name
