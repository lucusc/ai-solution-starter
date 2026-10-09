param openAiServiceName string
param deployments array = []

resource openAiService 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: openAiServiceName
}

@batchSize(1)
resource openAiDeployments 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [
  for deployment in deployments: {
    name: deployment.name
    parent: openAiService
    sku: {
      name: deployment.sku.name
      capacity: deployment.sku.?capacity
      tier: deployment.sku.?tier
      size: deployment.sku.?size
      family: deployment.sku.?family
    }
    properties: {
      model: {
        name: deployment.model.name
        version: deployment.model.version
        format: deployment.model.format
      }
      raiPolicyName: deployment.?raiPolicyName
      versionUpgradeOption: deployment.?versionUpgradeOption
    }
  }
]
