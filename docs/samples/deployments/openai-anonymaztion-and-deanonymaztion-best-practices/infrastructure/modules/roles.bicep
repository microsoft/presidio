param principalId string
param acrId string

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(principalId, acrId, 'acrpull')
  scope: acrId
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull role
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}
