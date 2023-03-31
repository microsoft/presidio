// This template is used to create a Synapse workspace.
targetScope = 'resourceGroup'

// Parameters
@description('Specifies the location for all resources.')
param location string
@description('(Optional) Specifies the resource tags to apply to all resources.')
param tags object = {}
@description('Specifies the name of the synapse workspace.')
param synapseName string
@description('(Optional) Specifies the administrator username of the synapse workspace.')
param administratorUsername string = 'SqlServerMainUser'
@secure()
@description('(Optional) Specifies the administrator password of the synapse workspace.')
param administratorPassword string = ''
@description('(Optional) Specifies the AAD admin group name for the synapse workspace.')
param synapseSqlAdminGroupName string = ''
@description('(Optional) Specifies the AAD admin group object ID for the synapse workspace.')
param synapseSqlAdminGroupObjectID string = ''
@description('Specifies the name of the storage account.')
param storageName string
@allowed([
  'Standard_LRS'
  'Standard_ZRS'
  'Standard_GRS'
  'Standard_GZRS'
  'Standard_RAGRS'
  'Standard_RAGZRS'
  'Premium_LRS'
  'Premium_ZRS'
])
@description('(Optional) Specifies the sku name of the storage account.')
param storageSkuName string = 'Standard_LRS'
@description('(Optional) Specifies the resource id of the subnet to use for private endpoints.')
param subnetId string = ''
@description('(Optional) Specifies the private DNS zone for synapse sql.')
param privateDnsZoneIdSynapseSql string = ''
@description('(Optional) Specifies the private DNS zone for synapse dev.')
param privateDnsZoneIdSynapseDev string = ''
@description('(Optional) Specifies the private DNS zone for storage blob.')
param privateDnsZoneIdBlob string = ''
@description('(Optional) Specifies the private DNS zone for storage dfs.')
param privateDnsZoneIdDfs string = ''
@description('(Optional) Specifies the resource ID of the Purview account.')
param purviewId string = ''
@description('(Optional) Specifies whether a synapse dedicated sql pool should be deployed.')
param enableSqlPool bool = false

// Variables
var storageNameCleaned = replace(storageName, '-', '')
var storagePrivateEndpointNameBlob = '${storage.name}-blob-pe'
var storagePrivateEndpointNameDfs = '${storage.name}-dfs-pe'
var synapsePrivateEndpointNameSql = '${synapse.name}-sql-pe'
var synapsePrivateEndpointNameSqlOnDemand = '${synapse.name}-sqlondemand-pe'
var synapsePrivateEndpointNameDev = '${synapse.name}-dev-pe'
var storageContainerNames = [
  'default'
]

// Resources
resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageNameCleaned
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: storageSkuName
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowedCopyScope: 'AAD'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    allowSharedKeyAccess: true
    defaultToOAuthAuthentication: true
    encryption: {
      keySource: 'Microsoft.Storage'
      requireInfrastructureEncryption: false
      services: {
        blob: {
          enabled: true
          keyType: 'Account'
        }
        file: {
          enabled: true
          keyType: 'Account'
        }
        queue: {
          enabled: true
          keyType: 'Service'
        }
        table: {
          enabled: true
          keyType: 'Service'
        }
      }
    }
    isLocalUserEnabled: false
    isSftpEnabled: false
    isHnsEnabled: true
    isNfsV3Enabled: false
    keyPolicy: {
      keyExpirationPeriodInDays: 7
    }
    largeFileSharesState: 'Disabled'
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      bypass: 'Metrics'
      defaultAction: 'Deny'
      ipRules: []
      virtualNetworkRules: []
    }
    publicNetworkAccess: 'Enabled'
    routingPreference: {
      routingChoice: 'MicrosoftRouting'
      publishInternetEndpoints: false
      publishMicrosoftEndpoints: false
    }
    supportsHttpsTrafficOnly: true
  }
}

resource storageBlobServices 'Microsoft.Storage/storageAccounts/blobServices@2021-02-01' = {
  parent: storage
  name: 'default'
  properties: {
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    cors: {
      corsRules: []
    }
    // automaticSnapshotPolicyEnabled: true  // Uncomment, if you want to enable addition features on the storage account
    // changeFeed: {
    //   enabled: true
    //   retentionInDays: 7
    // }
    // defaultServiceVersion: ''
    // deleteRetentionPolicy: {
    //   enabled: true
    //   days: 7
    // }
    // isVersioningEnabled: true
    // lastAccessTimeTrackingPolicy: {
    //   name: 'AccessTimeTracking'
    //   enable: true
    //   blobType: [
    //     'blockBlob'
    //   ]
    //   trackingGranularityInDays: 1
    // }
    // restorePolicy: {
    //   enabled: true
    //   days: 7
    // }
  }
}

resource storageContainers 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-02-01' = [for storageContainerName in storageContainerNames: {
  parent: storageBlobServices
  name: storageContainerName
  properties: {
    publicAccess: 'None'
    metadata: {}
  }
}]

resource storagePrivateEndpointBlob 'Microsoft.Network/privateEndpoints@2022-09-01' = if (!empty(subnetId)) {
  name: storagePrivateEndpointNameBlob
  location: location
  tags: tags
  properties: {
    applicationSecurityGroups: []
    customDnsConfigs: []
    customNetworkInterfaceName: '${storagePrivateEndpointNameBlob}-nic'
    ipConfigurations: []
    manualPrivateLinkServiceConnections: []
    privateLinkServiceConnections: [
      {
        name: storagePrivateEndpointNameBlob
        properties: {
          groupIds: [
            'blob'
          ]
          privateLinkServiceId: storage.id
          requestMessage: ''
        }
      }
    ]
    subnet: {
      id: subnetId
    }
  }
}

resource storagePrivateEndpointBlobARecord 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2022-09-01' = if (!empty(subnetId) && !empty(privateDnsZoneIdBlob)) {
  parent: storagePrivateEndpointBlob
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: '${storagePrivateEndpointBlob.name}-arecord'
        properties: {
          privateDnsZoneId: privateDnsZoneIdBlob
        }
      }
    ]
  }
}

resource storagePrivateEndpointDfs 'Microsoft.Network/privateEndpoints@2022-09-01' = if (!empty(subnetId)) {
  name: storagePrivateEndpointNameDfs
  location: location
  tags: tags
  properties: {
    applicationSecurityGroups: []
    customDnsConfigs: []
    customNetworkInterfaceName: '${storagePrivateEndpointNameDfs}-nic'
    ipConfigurations: []
    manualPrivateLinkServiceConnections: []
    privateLinkServiceConnections: [
      {
        name: storagePrivateEndpointNameDfs
        properties: {
          groupIds: [
            'dfs'
          ]
          privateLinkServiceId: storage.id
          requestMessage: ''
        }
      }
    ]
    subnet: {
      id: subnetId
    }
  }
}

resource storagePrivateEndpointDfsARecord 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2022-09-01' = if (!empty(subnetId) && !empty(privateDnsZoneIdDfs)) {
  parent: storagePrivateEndpointDfs
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: '${storagePrivateEndpointDfs.name}-arecord'
        properties: {
          privateDnsZoneId: privateDnsZoneIdDfs
        }
      }
    ]
  }
}

resource synapse 'Microsoft.Synapse/workspaces@2021-06-01' = {
  name: synapseName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    azureADOnlyAuthentication: true
    defaultDataLakeStorage: {
      accountUrl: 'https://${storage.name}.dfs.${environment().suffixes.storage}'
      filesystem: storageContainers[0].name
      createManagedPrivateEndpoint: true
      resourceId: storage.id
    }
    managedResourceGroupName: synapseName
    managedVirtualNetwork: 'default'
    managedVirtualNetworkSettings: {
      allowedAadTenantIdsForLinking: []
      linkedAccessCheckOnTargetResource: true
      preventDataExfiltration: true
    }
    publicNetworkAccess: 'Disabled'
    purviewConfiguration: empty(purviewId) ? {} : {
      purviewResourceId: purviewId
    }
    sqlAdministratorLogin: administratorUsername
    sqlAdministratorLoginPassword: administratorPassword == '' ? null : administratorPassword
    virtualNetworkProfile: {
      computeSubnetId: ''
    }
  }
}

resource synapseSqlPool001 'Microsoft.Synapse/workspaces/sqlPools@2021-06-01' = if(enableSqlPool) {
  parent: synapse
  name: 'sqlPool001'
  location: location
  tags: tags
  sku: {
    name: 'DW100c'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    createMode: 'Default'
    storageAccountType: 'GRS'
  }
}

resource synapseBigDataPool001 'Microsoft.Synapse/workspaces/bigDataPools@2021-06-01' = {
  parent: synapse
  name: 'bigDataPool001'
  location: location
  tags: tags
  properties: {
    autoPause: {
      enabled: true
      delayInMinutes: 15
    }
    autoScale: {
      enabled: true
      minNodeCount: 3
      maxNodeCount: 10
    }
    // cacheSize: 100  // Uncomment to set a specific cache size
    customLibraries: []
    defaultSparkLogFolder: 'logs/'
    dynamicExecutorAllocation: {
      enabled: true
      #disable-next-line BCP037
      minExecutors: 1
      #disable-next-line BCP037
      maxExecutors: 9
    }
    // isComputeIsolationEnabled: true  // Uncomment to enable compute isolation (only available in selective regions)
    // libraryRequirements: {  // Uncomment to install pip dependencies on the Spark cluster
    //   content: ''
    //   filename: 'requirements.txt'
    // }
    nodeSize: 'Small'
    nodeSizeFamily: 'MemoryOptimized'
    sessionLevelPackagesEnabled: true
    // sparkConfigProperties: {  // Uncomment to set spark conf on the Spark cluster
    //   content: ''
    //   filename: 'spark.conf'
    // }
    sparkEventsFolder: 'events/'
    sparkVersion: '3.2'
  }
}

resource synapseManagedIdentitySqlControlSettings 'Microsoft.Synapse/workspaces/managedIdentitySqlControlSettings@2021-06-01' = {
  parent: synapse
  name: 'default'
  properties: {
    grantSqlControlToManagedIdentity: {
      desiredState: 'Enabled'
    }
  }
}

resource synapseAadAdministrators 'Microsoft.Synapse/workspaces/administrators@2021-06-01' = if (!empty(synapseSqlAdminGroupName) && !empty(synapseSqlAdminGroupObjectID)) {
  parent: synapse
  name: 'activeDirectory'
  properties: {
    administratorType: 'ActiveDirectory'
    login: synapseSqlAdminGroupName
    sid: synapseSqlAdminGroupObjectID
    tenantId: subscription().tenantId
  }
}

resource synapsePrivateEndpointSql 'Microsoft.Network/privateEndpoints@2022-09-01' = if (!empty(subnetId)) {
  name: synapsePrivateEndpointNameSql
  location: location
  tags: tags
  properties: {
    applicationSecurityGroups: []
    customDnsConfigs: []
    customNetworkInterfaceName: '${synapsePrivateEndpointNameSql}-nic'
    ipConfigurations: []
    manualPrivateLinkServiceConnections: []
    privateLinkServiceConnections: [
      {
        name: synapsePrivateEndpointNameSql
        properties: {
          groupIds: [
            'Sql'
          ]
          privateLinkServiceId: synapse.id
          requestMessage: ''
        }
      }
    ]
    subnet: {
      id: subnetId
    }
  }
}

resource synapsePrivateEndpointSqlARecord 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2022-09-01' = if (!empty(subnetId) && !empty(privateDnsZoneIdSynapseSql)) {
  parent: synapsePrivateEndpointSql
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: '${synapsePrivateEndpointSql.name}-arecord'
        properties: {
          privateDnsZoneId: privateDnsZoneIdSynapseSql
        }
      }
    ]
  }
}

resource synapsePrivateEndpointSqlOnDemand 'Microsoft.Network/privateEndpoints@2022-09-01' = if (!empty(subnetId)) {
  name: synapsePrivateEndpointNameSqlOnDemand
  location: location
  tags: tags
  properties: {
    applicationSecurityGroups: []
    customDnsConfigs: []
    customNetworkInterfaceName: '${synapsePrivateEndpointNameSqlOnDemand}-nic'
    ipConfigurations: []
    manualPrivateLinkServiceConnections: []
    privateLinkServiceConnections: [
      {
        name: synapsePrivateEndpointNameSqlOnDemand
        properties: {
          groupIds: [
            'SqlOnDemand'
          ]
          privateLinkServiceId: synapse.id
          requestMessage: ''
        }
      }
    ]
    subnet: {
      id: subnetId
    }
  }
}

resource synapsePrivateEndpointSqlOnDemandARecord 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2022-09-01' = if (!empty(subnetId) && !empty(privateDnsZoneIdSynapseSql)) {
  parent: synapsePrivateEndpointSqlOnDemand
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: '${synapsePrivateEndpointSqlOnDemand.name}-arecord'
        properties: {
          privateDnsZoneId: privateDnsZoneIdSynapseSql
        }
      }
    ]
  }
}

resource synapsePrivateEndpointDev 'Microsoft.Network/privateEndpoints@2022-09-01' = if (!empty(subnetId)) {
  name: synapsePrivateEndpointNameDev
  location: location
  tags: tags
  properties: {
    applicationSecurityGroups: []
    customDnsConfigs: []
    customNetworkInterfaceName: '${synapsePrivateEndpointNameDev}-nic'
    ipConfigurations: []
    manualPrivateLinkServiceConnections: []
    privateLinkServiceConnections: [
      {
        name: synapsePrivateEndpointNameDev
        properties: {
          groupIds: [
            'Dev'
          ]
          privateLinkServiceId: synapse.id
          requestMessage: ''
        }
      }
    ]
    subnet: {
      id: subnetId
    }
  }
}

resource synapsePrivateEndpointDevARecord 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2022-09-01' = if (!empty(subnetId) && !empty(privateDnsZoneIdSynapseDev)) {
  parent: synapsePrivateEndpointDev
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: '${synapsePrivateEndpointDev.name}-arecord'
        properties: {
          privateDnsZoneId: privateDnsZoneIdSynapseDev
        }
      }
    ]
  }
}

// Outputs
output synapseId string = synapse.id
output synapseName string = synapse.name
output synapseBigDataPool001Id string = synapseBigDataPool001.id
output synapseBigDataPool001Name string = synapseBigDataPool001.name
output synapseSqlPool001Name string = synapseSqlPool001.name
