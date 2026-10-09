metadata description = 'Creates a private DNS zone and links it to an existing virtual network'

@description('The name of the private DNS zone')
param dnsZoneName string

@description('The name of the existing virtual network to link to the private DNS zone')
param virtualNetworkName string

@description('The tags to associate with the private DNS zone and VNet link')
param tags object = {}

param virtualNetworkSubscriptionId string = subscription().subscriptionId
param virtualNetworkResourceGroupName string = resourceGroup().name
param useExistingPrivateDnsZones bool = false
param linkPrivateEndpointToPrivateDnsZone bool = false

resource vnet 'Microsoft.Network/virtualNetworks@2020-06-01' existing = {
  scope: resourceGroup(virtualNetworkSubscriptionId, virtualNetworkResourceGroupName)
  name: virtualNetworkName
}

resource existingDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' existing = if (useExistingPrivateDnsZones) {
  name: dnsZoneName
}

resource existingPrivateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = if (useExistingPrivateDnsZones && linkPrivateEndpointToPrivateDnsZone) {
  parent: existingDnsZone
  name: '${virtualNetworkName}-dnslink'
  location: 'global'
  tags: tags
  properties: {
    virtualNetwork: {
      id: vnet.id
    }
    registrationEnabled: false
  }
}

resource dnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (!useExistingPrivateDnsZones) {
  name: dnsZoneName
  location: 'global'
  tags: tags
  dependsOn: [
    vnet
  ]

  resource privateDnsZoneLink 'virtualNetworkLinks' = if (linkPrivateEndpointToPrivateDnsZone) {
    name: '${virtualNetworkName}-dnslink'
    location: 'global'
    tags: tags
    properties: {
      virtualNetwork: {
        id: vnet.id
      }
      registrationEnabled: false
    }
  }
}

output privateDnsZoneName string = dnsZone.name
output id string = useExistingPrivateDnsZones ? existingDnsZone.id : dnsZone.id
