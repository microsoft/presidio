param redisCacheName string
param location string
param redisCapacity int

resource redisCache 'Microsoft.Cache/Redis@2023-08-01' = {
  name: redisCacheName
  location: location
  properties: {
    sku: {
      name: 'Standard'
      family: 'C'
      capacity: redisCapacity
    }
    enableNonSslPort: false
  }
}
