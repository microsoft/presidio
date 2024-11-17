param aksClusterName string
param location string
param aksNodeCount int

resource aksCluster 'Microsoft.ContainerService/managedClusters@2023-07-01' = {
  name: aksClusterName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: toLower(aksClusterName)
    agentPoolProfiles: [
      {
        name: 'nodepool1'
        count: aksNodeCount
        vmSize: 'Standard_DS2_v2'
        osType: 'Linux'
        type: 'VirtualMachineScaleSets'
        mode: 'System'
      }
    ]
  }
}

output principalId string = aksCluster.identity.principalId
