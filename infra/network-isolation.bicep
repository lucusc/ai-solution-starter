metadata description = 'Sets up private networking for all resources, using VNet, private endpoints, and DNS zones.'

@description('The name of the VNet to create')
param vnetName string

@description('The location to create the VNet and private endpoints')
param location string = resourceGroup().location

@description('The tags to apply to all resources')
param tags object = {}

@description('The name of an existing App Service Plan to connect to the VNet')
param appServicePlanName string

@description('The name of the existing Function App Service Plan to connect to the VNet')
param funcServicePlanName string

param usePrivateEndpoint bool = false

param useExistingVnet bool = false
param existingVnetSubscriptionId string = ''
param existingVnetResourceGroupName string = ''

param vnetAddressPrefix string

param subnetBackendName string
param subnetBackendAddressPrefix string

param subnetAppIntName string
param subnetAppIntAddressPrefix string

param subnetFuncIntName string
param subnetFuncIntAddressPrefix string

@allowed(['appservice', 'containerapps'])
param deploymentTarget string

var existingVnetSubscription = !empty(existingVnetSubscriptionId)
  ? existingVnetSubscriptionId
  : subscription().subscriptionId

var existingVnetResourceGroup = !empty(existingVnetResourceGroupName)
  ? existingVnetResourceGroupName
  : resourceGroup().name

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' existing = if (deploymentTarget == 'appservice') {
  name: appServicePlanName
}

resource funcServicePlan 'Microsoft.Web/serverfarms@2022-03-01' existing = {
  name: funcServicePlanName
}

resource existingVnet 'Microsoft.Network/virtualNetworks@2021-02-01' existing = if (useExistingVnet) {
  name: vnetName
  scope: resourceGroup(existingVnetSubscription, existingVnetResourceGroup)
}

resource existingBackendSubnet 'Microsoft.Network/virtualNetworks/subnets@2021-02-01' existing = if (useExistingVnet) {
  parent: existingVnet
  name: subnetBackendName
}

resource existingAppIntSubnet 'Microsoft.Network/virtualNetworks/subnets@2021-02-01' existing = if (useExistingVnet) {
  parent: existingVnet
  name: subnetAppIntName
}

resource existingFuncIntSubnet 'Microsoft.Network/virtualNetworks/subnets@2021-02-01' existing = if (useExistingVnet) {
  parent: existingVnet
  name: subnetFuncIntName
}

module vnet './modules/networking/vnet.bicep' = if (usePrivateEndpoint && !useExistingVnet) {
  name: 'vnet'
  params: {
    name: vnetName
    location: location
    tags: tags
    addressPrefix: vnetAddressPrefix
    subnets: [
      {
        name: subnetBackendName
        properties: {
          addressPrefix: subnetBackendAddressPrefix
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
      {
        name: subnetAppIntName
        properties: {
          addressPrefix: subnetAppIntAddressPrefix
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
          delegations: [
            {
              id: appServicePlan.id
              name: appServicePlan.name
              properties: {
                serviceName: deploymentTarget == 'appservice'
                  ? 'Microsoft.Web/serverFarms'
                  : 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
      {
        name: subnetFuncIntName
        properties: {
          addressPrefix: subnetFuncIntAddressPrefix
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
          delegations: [
            {
              id: funcServicePlan.id
              name: funcServicePlan.name
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
          serviceEndpoints: [
            {
              service: 'Microsoft.AzureCosmosDB'
            }
          ]
        }
      }
    ]
  }
}

output backendSubnetId string = usePrivateEndpoint
  ? (useExistingVnet ? existingBackendSubnet.id : vnet.outputs.vnetSubnets[0].id)
  : ''
output appSubnetId string = usePrivateEndpoint
  ? (useExistingVnet ? existingAppIntSubnet.id : vnet.outputs.vnetSubnets[1].id)
  : ''
output funcIntSubnetId string = usePrivateEndpoint
  ? (useExistingVnet ? existingFuncIntSubnet.id : vnet.outputs.vnetSubnets[2].id)
  : ''
output vnetName string = usePrivateEndpoint ? (useExistingVnet ? existingVnet.name : vnet.outputs.name) : ''
