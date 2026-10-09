metadata description = 'Updates app settings for an Azure App Service.'
@description('The name of the app service resource within the current resource group scope')
param appServiceId string

output appSettings object = empty(appServiceId) ? {} : list('${appServiceId}/config/appsettings', '2024-11-01').properties
