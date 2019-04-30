# Custom fields

Presidio supports custom fields. Managing the custom fields is done online via simple REST API.

The underlying object behind each field is called a 'Recognizer', in order to support custom fields the administrator must create new recognizers

## API

#### Getting a recoginzer
    GET <api-service-address>/api/v1/analyzer/recognizers/<recognizer_name>

#### Getting all recognizers
    GET <api-service-address>/api/v1/analyzer/recognizers

#### Creating a new recoginzer
    POST <api-service-address>/api/v1/analyzer/recognizers/<new_recognizer_name>

Form data:

| Field          | Description                                                       | Optional   |
| -------------- | ----------------------------------------------------------------- | ---------- |
| `value` | The recognizer json object                         | no        |

Recognizer format:

| Field          | Description                                                       | Optional   |
| -------------- | ----------------------------------------------------------------- | ---------- |
| `entity` | The name of the new field. e.g. 'ROCKET'                         | no        |
| `language` | The supported language                         | no        |
| `patterns` | A list of regular expressions objects                         | no        |

Regular expression format:

| Field          | Description                                                       | Optional   |
| -------------- | ----------------------------------------------------------------- | ---------- |
| `name` | The name of this pattern                         | no        |
| `regex` | A regular expression                         | no        |
| `score` | The score given to entities detected by this recognizer                         | no        |

##### Example
```json
{
    "value": {
        "entity": "ROCKET",
        "language": "en",
        "patterns": [
            {
                "name": "rocket-recognizer",
                "regex": "\\W*(rocket)\\W*",
                "score": 1
            },
            {
                "name": "projectile-recognizer",
                "regex": "\\W*(projectile)\\W*",
                "score": 1
            }
        ]
    }
}
```

#### Update a recoginzer
    PUT <api-service-address>/api/v1/analyzer/recognizers/<recognizer_name>

See the payload as defined in the [Create](#creating-a-new-recoginzer)

#### Delete a recoginzer
    DELETE <api-service-address>/api/v1/analyzer/recognizers/<recognizer_name>

## Using the custom field
After creating a new recognizer, either explicitly state in the templates the newly added entity name, or set allFields to true