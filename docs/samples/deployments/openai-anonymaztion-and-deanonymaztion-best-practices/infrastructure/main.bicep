targetScope = 'resourceGroup'
param location string = resourceGroup().location

@description('Name of the AKS Cluster')
param aksClusterName string = 'preshack'

@description('Number of nodes in the AKS cluster')
param aksNodeCount int = 3

@description('Name of the Redis Cache instance')
param redisCacheName string = 'preshack'

@description('SKU capacity for Redis Cache (e.g., 1 for C1)')
param redisCapacity int = 1

@description('Name of the Azure Container Registry')
param acrName string = 'preshack'


// module acrModule 'modules/acr.bicep' = {
//     name: 'acrDeployment'
//     params: {
//       acrName: acrName
//       location: location
//     }
// }
  
// module aksModule 'modules/aks.bicep' = {
//     name: 'aksDeployment'
//     params: {
//       aksClusterName: aksClusterName
//       location: location
//       aksNodeCount: aksNodeCount
//     }
// }

// module roleAssignmentModule 'modules/roles.bicep' = {
//     name: 'roleAssignmentDeployment'
//     params: {
//       principalId: aksModule.outputs.principalId
//       acrId: acrModule.outputs.acrId
//     }
//     dependsOn: [
//       acrModule
//       aksModule
//     ]
// }

module redisModule 'modules/redis.bicep' = {
    name: 'redisDeployment'
    params: {
      redisCacheName: redisCacheName
      location: location
      redisCapacity: redisCapacity
    }
}
  
