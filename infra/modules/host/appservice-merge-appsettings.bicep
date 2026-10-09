metadata description = 'Updates app settings for an Azure App Service.'
@description('The name of the app service resource within the current resource group scope')
param name string

@description('The app settings to be applied to the app service')
param appSettings object = {}

resource appService 'Microsoft.Web/sites@2024-11-01' existing = {
  name: name
}

module appServiceExistingAppSettings 'appservice-existing-appsettings.bicep' = {
  name: 'appservice-existing-app-settings'
  params: {
    appServiceId: appService.id
  }
}

resource mergeAppSettings 'Microsoft.Web/sites/config@2024-11-01' = {
  name: 'appsettings'
  parent: appService
  properties: union(appServiceExistingAppSettings.outputs.appSettings, appSettings)
}
