# Monitor your data with periodic scans

When running Presidio on a Kubernetes cluster you can set a Kubernetes [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) to scan your data periodically.
You will need to configure the scan's input and the destination to which the analyzed and anonymized results will be stored.

* A detailed design of the Ingress Control and the API Service can be found  [here](./design.md).

## Job stages

1. Retrieves all new items in the provided storage.
2. Analyzes/anonymizes these new items.
3. Outputs the data into a configured destination.
4. Marks the items as scanned using a Redis cache.

## Job Configuration

To schedule a periodic data scan create the following json.
**Note:** Example is given using the [HTTPie](https://httpie.org/) syntax.

```json
echo -n '{
  "scannerCronJobRequest": {
    "Name": "scan-job",
    "trigger": {
      "schedule": {
        "recurrencePeriod": "* * * * *"
      }
    },
    "scanRequest": {
      "analyzeTemplate": {
        "fields": [
          {
            "name": "PHONE_NUMBER"
          },
          {
            "name": "LOCATION"
          },
          {
            "name": "EMAIL_ADDRESS"
          }
        ]
      },
      "anonymizeTemplate": {
        "fieldTypeTransformations": [
          {
            "fields": [
              {
                "name": "PHONE_NUMBER"
              }
            ],
            "transformation": {
              "replaceValue": {
                "newValue": "<PHONE_NUMBER>"
              }
            }
          },
          {
            "fields": [
              {
                "name": "LOCATION"
              }
            ],
            "transformation": {
              "redactValue": {}
            }
          },
          {
            "fields": [
              {
                "name": "EMAIL_ADDRESS"
              }
            ],
            "transformation": {
              "hashValue": {}
            }
          }
        ]
      },
      "scanTemplate": {
        "cloudStorageConfig": {
          "blobStorageConfig": {
            "accountName": "<ACCOUNT_NAME>",
            "accountKey": "<ACCOUNT_KEY>",
            "containerName": "<CONTAINER_NAME>"
          }
        }
      },
      "datasinkTemplate": {
        "analyzeDatasink": [
          {
            "dbConfig": {
              "connectionString": "<CONNECTION_STRING>",
              "tableName": "<TABLE_NAME>",
              "type": "<DB_TYPE>"
            }
          }
        ],
        "anonymizeDatasink": [
          {
            "cloudStorageConfig": {
              "blobStorageConfig": {
                "accountName": "<ACCOUNT_NAME>",
                "accountKey": "<ACCOUNT_KEY",
                "containerName": "<CONTAINER_NAME>"
              }
            }
          }
        ]
      }
    }
  }
}' | http <api-service-address>/api/v1/projects/<my-project>/schedule-scanner-cronjob
```


### 1. Analyzer Template

Defines which fields the input should be scanned for.
A list of all the supported fields can be found [here](./field_types.md).

### 2. Anoynimzer Template

Defines the anonymization method that should be executed per each field.
If not provided, anonymization will not be done.

### 3. Scanner Template

Defines the job's input source.
Use the following [configuration](#input-and-output-configurations) to define the desired input.

#### Supported Input Sources

* Supported storage solutions:
  * Azure Blob Storage
  * AWS S3
  * More data types will be added soon!

### 4. Datasink Template

Defines the job's output destination.

#### Analyzer and Anonymizer Datasink

Analyzer and anonymizer data sink arrays defines the output destination of analyze and anonymize results respectively.
Use the following [configuration](#Input-&-Output-Configurations) defending on the desired output.

#### Supported Output Destinations

* Supported storage solutions:
  * Azure Blob Storage
  * AWS S3
* Supported database solutions:
  * MySQL
  * SQL Server
  * SQLite3
  * PostgreSQL
  * Oracle
* Supported streams solutions:
  * Azure EventHub
  * Kafka

## Input and Output Configurations
### Storage configuration

For AWS S3, use the following configuration:
```json
"cloudStorageConfig": {
	"S3Config": {
		"accessId": "<AccessId>",
		"accessKey": "<AccessKey>",
		"region": "<Region>",
		"bucketName": "<BucketName>"
	}
}
```

For Azure Blob Storage, use the following configuration:
```json
"cloudStorageConfig": {
    "blobStorageConfig": {
      "accountName": "<AccountName>",
      "accountKey": "<AccountKey>",
      "containerName": "<ContainerName>"
          }
}
```

### Databases configuration

We are using [Xorm](http://xorm.io/docs/) library for DB operations.
Please refer to Xorm's documentation for additional information regarding the DB configuration.

#### Connection strings

- MySql

```
<userName>@<serverName>:<password>@tcp(<serverName>.<hostName>:3306)/<databaseName>?allowNativePasswords=true&tls=true
```

- PostgreSQL

```
 postgres://<userName>@<serverName>:<password>@<serverName>.<hostName>/<databaseName>?sslmode=verify-full
 ```

- SQL Server

```
odbc:server=<serverName>.database.windows.net;user id=<userId>;password=<password>;port=1433;database=<databaseName>
```

### Stream configuration
For Azure Event Hub, use the following configuration:

```json
  "streamConfig": {
    "ehConfig": {
      "ehConnectionString": "<EHConnectionString>", // EH connection string. It is recommended to generate a connection string from EH and NOT from EH namespace.
      "storageAccountName": "<StorageAccountName>", // Storage account name for Azure EH EPH pattern
      "storageAccountKeyValue": "<StorageAccountKeyValue>", // Storage account key for Azure EH EPH pattern
      "containerValue": "<ContainerValue>" // Storage container name for Azure EH EPH pattern
    }
  }
```

For Kafka use the following configuration:

```json
  "streamConfig": {
    "kafkaConfig": {
      "address": "<Address>",
      "topic": "<Topic>",
      "saslUsername": "<SASLUsername>",
      "saslPassword": "<SASLPassword>"
    }
  }
```

### Recurrence Configuration

Set the '\<recurrencePeriod>' according to the execution [interval](https://crontab.guru/every-1-minute) you'd like.
**Parallelism is not supported!** A new job won't be triggered until the previous job is finished.

