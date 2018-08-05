# Monitor your data with periodic scans 


You can set a Kubernetes [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) to scan your data periodicly.
The scanner will look for new files in the provided storage and will analyzed/anonymize them and output the data into the selected output.

#### Scanner
Supported storage solutions: Azure blob storage, AWS S3. <br>
More data types will be added soon!

#### Output  
Supported storage solutions: Azure blob storage, AWS S3. <br>
Supported database solutions: MySQL, SQL Server, SQLite3, PostgreSQL and Oracle.



To schedule a predioc data scan you need to set the following objects. <br>
**Note:** Examples are made with [HTTPie](https://httpie.org/)

### Analyzer Template:
```
echo -n '{"fields":[]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
```

### Anoynimzer Template: 
Anoynimzer Template is not mandatory, use it only if anonymization is needed
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
}' | http <api-service-address>/api/v1/templates/<my-project>/anonymize/<my-anonymize-template-name>
```

### Databinder Template: 
Configures the scanner output:
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

Supported Analyzer and Anonymizer kinds: azureblob, s3, mysql, mssql, postgres, sqlite3, oracle. <br>

#### Storage configuration
For AWS S3 use the following configuration:
"cloudStorageConfig": {
	"S3Config": {
		"accessId": "<AccessId>",
		"accessKey": "<AccessKey>",
		"region": "<Region>",
		"bucketName": "<BucketName>"
	}
}

For Azure Blob Storage, use the configuration same as the example:
"cloudStorageConfig": {
	"blobStorageConfig": {
		"accountName": "<AccountName>",
		"accountKey": "<AccountKey>",
		"containerName": "<ContainerName>"
      	}
}

#### Databases configuration
We are using [Xorm](http://xorm.io/docs/) for DB connection. Please refer to the documentation for additonal information. 

Connection strings
* MySql
```
<userName>@<serverName>:<password>@tcp(<serverName>.<hostName>:3306)/<databaseName>?allowNativePasswords=true&tls=true
```
* PostgreSQL
```
 postgres://<userName>@<serverName>:<password>@<serverName>.<hostName>/<databaseName>?sslmode=verify-full
 ```
* SQL Server
``` 
odbc:server=<serverName>.database.windows.net;user id=<userId>;password=<password>;port=1433;database=<databaseName>
```

### Scanner Template:
 ```
echo -n '{
  "kind": "<ScannerKind>",
  "cloudStorageConfig": {
    "blobStorageConfig": {
      "accountName": "<AccountName>",
      "accountKey": "<AccountKey>",
      "containerName": "<ContainerName>"
    }
  },
  "analyzeTemplateId": "<AnalyzerTemplateId>",
  "anonymizeTemplateId": "<AnonymizerTemplateId>",
  "databinderTemplateId": "<DatabinderTemplateId>"
}' | http <api-service-address>/api/v1/templates/<my-project>/databinder/<my-databinder-template-name>
```

Anoynimzer Template is not mandatory, use it only if anonymization is needed. <br>
Supported Scanner kind:
* azureblob
* s3

Set cloudStorageConfig as shown [here](#Storage-configuration)

### Scheduler Template:
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
  "scanTemplateId": "<ScanTemplateId>"
}' | http <api-service-address>/api/v1/templates/<my-project>/schedule-cronjob/<my-scheduler-template-name>
```

You should define the 'recurrencePeriodDuration' according to the [interval](https://crontab.guru/every-1-minute) that you need. <br>
Parallelism is not supported, and a new job won't be triggered until the previous job is finished.


### Trigger new Cron Job:
```
echo -n '{"CronJobTemplateId": "<cronjob-scheduleId>" }' | http <api-service-address>/api/v1/projects/proj1/schedule-cronjob
```

