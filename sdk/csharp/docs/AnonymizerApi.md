# Presidio.Api.AnonymizerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AnonymizePost**](AnonymizerApi.md#anonymizepost) | **POST** /anonymize | Anonymize Text
[**AnonymizersGet**](AnonymizerApi.md#anonymizersget) | **GET** /anonymizers | Get supported anonymizers
[**DeanonymizersGet**](AnonymizerApi.md#deanonymizersget) | **GET** /deanonymizers | Get supported deanonymizers
[**HealthGet**](AnonymizerApi.md#healthget) | **GET** /health | Healthcheck


<a name="anonymizepost"></a>
# **AnonymizePost**
> AnonymizeResponse AnonymizePost (AnonymizeRequest anonymizeRequest)

Anonymize Text

### Example
```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Presidio.Api;
using Presidio.Client;
using Presidio.Model;

namespace Example
{
    public class AnonymizePostExample
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.BasePath = "http://localhost";
            var apiInstance = new AnonymizerApi(config);
            var anonymizeRequest = new AnonymizeRequest(); // AnonymizeRequest | 

            try
            {
                // Anonymize Text
                AnonymizeResponse result = apiInstance.AnonymizePost(anonymizeRequest);
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling AnonymizerApi.AnonymizePost: " + e.Message );
                Debug.Print("Status Code: "+ e.ErrorCode);
                Debug.Print(e.StackTrace);
            }
        }
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **anonymizeRequest** | [**AnonymizeRequest**](AnonymizeRequest.md)|  | 

### Return type

[**AnonymizeResponse**](AnonymizeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |
| **400** | Bad request |  -  |
| **422** | Unprocessable Entity |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

<a name="anonymizersget"></a>
# **AnonymizersGet**
> List&lt;string&gt; AnonymizersGet ()

Get supported anonymizers

### Example
```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Presidio.Api;
using Presidio.Client;
using Presidio.Model;

namespace Example
{
    public class AnonymizersGetExample
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.BasePath = "http://localhost";
            var apiInstance = new AnonymizerApi(config);

            try
            {
                // Get supported anonymizers
                List<string> result = apiInstance.AnonymizersGet();
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling AnonymizerApi.AnonymizersGet: " + e.Message );
                Debug.Print("Status Code: "+ e.ErrorCode);
                Debug.Print(e.StackTrace);
            }
        }
    }
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

**List<string>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

<a name="deanonymizersget"></a>
# **DeanonymizersGet**
> List&lt;string&gt; DeanonymizersGet ()

Get supported deanonymizers

### Example
```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Presidio.Api;
using Presidio.Client;
using Presidio.Model;

namespace Example
{
    public class DeanonymizersGetExample
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.BasePath = "http://localhost";
            var apiInstance = new AnonymizerApi(config);

            try
            {
                // Get supported deanonymizers
                List<string> result = apiInstance.DeanonymizersGet();
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling AnonymizerApi.DeanonymizersGet: " + e.Message );
                Debug.Print("Status Code: "+ e.ErrorCode);
                Debug.Print(e.StackTrace);
            }
        }
    }
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

**List<string>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

<a name="healthget"></a>
# **HealthGet**
> string HealthGet ()

Healthcheck

### Example
```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Presidio.Api;
using Presidio.Client;
using Presidio.Model;

namespace Example
{
    public class HealthGetExample
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.BasePath = "http://localhost";
            var apiInstance = new AnonymizerApi(config);

            try
            {
                // Healthcheck
                string result = apiInstance.HealthGet();
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling AnonymizerApi.HealthGet: " + e.Message );
                Debug.Print("Status Code: "+ e.ErrorCode);
                Debug.Print(e.StackTrace);
            }
        }
    }
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

**string**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

