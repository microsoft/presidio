# Monitor your data with periodic scans

When running Presidio on a Kubernetes cluster you can set a Kubernetes [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) to scan your data periodicly.
You will need to configure the scan's input and the destination to which the analyzed and anonymized results will be stored.

![Design](https://user-images.githubusercontent.com/13463870/43763824-70493396-9a34-11e8-9aa7-090057012369.jpg)

* A detailed design of the Ingerss Control and the API Serivce can be found  [here](./design.md).

## Job stages

1. Retrieves all new items in the provided storage.
2. Analyzes/anonymizes these new items.
3. Outputs the data into a configured destination.
4. Marks the items as scanned using a Redis cache.

## Supported Input Sources

* Supported storage solutions:
  * Azure Blob Storage
  * AWS S3
  * More data types will be added soon!

## Supported Output Destinations

* Supported storage solutions:
  * Azure Blob Storage
  * AWS S3
* Supported database solutions:
  * MySQL
  * SQL Server
  * SQLite3
  * PostgreSQL
  * Oracle

## Job Configuration

To schedule a predioc data scan the following objects should be set.  
**Note:** Examples are given using the [HTTPie](https://httpie.org/) syntax.

### 1. Analyzer Template

Defines which fields the input should be scanned for.  
A list of all the supported fields can be found [here](./field_types.md).
```
echo -n '{"fields":[]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-analyzer-template-name>
```

### 2. Anoynimzer Template

Defines the anonymization method that should be executed per each field.  
If not provided, anonymization will not be done.
```
echo -n '{
  "name": "ANONYMIZER",
  "displayName": "Phone number and Credit card",
  "fieldTypeTransformations": [
    {
      "fields": [
        {
          "name": "PHONE_NUMBER"
        }
      ],
      "transformation": {
        "replaceValue": {
          "newValue": "<phone-number>"
        }
      }
    },
    {
      "fields": [
        {
          "name": "CREDIT_CARD"
        }
      ],
      "transformation": {
        "redactValue": {}
      }
    }
  ]
}' | http <api-service-address>/api/v1/templates/<my-project>/anonymize/<my-anonymizer-template-name>
```

### 3. Databinder Template

Defines the job's output destination.  

#### Example

```
echo -n '{
  "analyzerKind": "<analyzerKind>",
  "anonymizerKind": "<anonymizerKind>",
  "databinder": {
    "cloudStorageConfig": {
      "blobStorageConfig": {
        "accountName": "<AccountName>",
        "accountKey": "<AccountKey>",
        "containerName": "<ContainerName>"
      }
    },
    "dbConfig": {
      "connectionString": "odbc:server=<serverName>.database.windows.net;user id=<userId>;password=<password>;port=1433;database=<databaseName>",
      "tableName": "<tableName>"
    }
  }
}' | http <api-service-address>/api/v1/templates/<my-project>/databinder/<my-databinder-template-name>
```

#### Analyzer and Anonymizer Kind

Use one of the following values for \<analyzerKind> and \<anonymizerKind>:  
azureblob, s3, mysql, mssql, postgres, sqlite3, oracle.

#### Storage configuration

For AWS S3, use the following configuration:
```
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
```
"cloudStorageConfig": {
    "blobStorageConfig": {
      "accountName": "<AccountName>",
      "accountKey": "<AccountKey>",
      "containerName": "<ContainerName>"
          }
}
```

#### Databases configuration

We are using [Xorm](http://xorm.io/docs/) library for DB operations.  
Please refer to Xorm's documentation for additonal information regarding the DB configuration. 

##### Connection strings

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

### 4. Scanner Template

Defines the job's input source.  

```
echo -n '{
  "kind": "<ScannerKind>",
  "cloudStorageConfig": {
    "blobStorageConfig": {
      "accountName": "<AccountName>",
      "accountKey": "<AccountKey>",
      "containerName": "<ContainerName>"
    }
  }
}' | http <api-service-address>/api/v1/templates/<my-project>/databinder/<my-scanner-template-name>
```

#### Scanner Kind

Use one of the following values for \<scannerKind>:  
azureblob, s3.

#### Cloud Storage Configuration

Set \<cloudStorageConfig> as shown [here](#Storage-configuration).

### 5. Scheduler Template

Defines the Cron job scheduler's configuration.

```
echo -n '{
{
  "name": "<schedulerName>",
  "description": "<schedulerDescription>",
  "trigger": {
    "schedule": {
      "recurrencePeriodDuration": "* * * * *"
    }
  },
  "scanTemplateId": "<my-scanner-template-name>",
  "analyzeTemplateId": "<my-analyzer-template-name>",
  "anonymizeTemplateId": "<my-anonymizer-template-name>",
  "databinderTemplateId": "<my-databinder-template-name>"
}' | http <api-service-address>/api/v1/templates/<my-project>/schedule-cronjob/<my-scheduler-template-name>
```

#### Analyzer, Anonymizer, Scanner and Databinder IDs

Set \<AnalyzerTemplateId>, \<AnonymizerTemplateId>, \<ScanTemplateId> and \<DatabinderTemplateId> according to the values provided in the previous configurations' http requests.  

#### Recurrence Configuration

Set the '\<recurrencePeriodDuration>' according to the execution [interval](https://crontab.guru/every-1-minute) you'd like.  
**Parallelism is not supported!** A new job won't be triggered until the previous job is finished.

### 6. Trigger the Cron Job

Activates the Cron job with the above configuration.

```
echo -n '{"CronJobTemplateId": "<my-scheduler-template-name>" }' | http <api-service-address>/api/v1/projects/proj1/schedule-cronjob
```
