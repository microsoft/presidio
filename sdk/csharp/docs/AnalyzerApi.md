# Presidio.Api.AnalyzerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AnalyzePost**](AnalyzerApi.md#analyzepost) | **POST** /analyze | Analyze Text
[**HealthGet**](AnalyzerApi.md#healthget) | **GET** /health | Healthcheck
[**RecognizersGet**](AnalyzerApi.md#recognizersget) | **GET** /recognizers | Get Recognizers
[**SupportedentitiesGet**](AnalyzerApi.md#supportedentitiesget) | **GET** /supportedentities | Get supported entities


<a name="analyzepost"></a>
# **AnalyzePost**
> List&lt;RecognizerResultWithAnalysis&gt; AnalyzePost (AnalyzeRequest analyzeRequest)

Analyze Text

Recognizes PII entities in a given text and returns their types, locations and score

### Example
```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Presidio.Api;
using Presidio.Client;
using Presidio.Model;

namespace Example
{
    public class AnalyzePostExample
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.BasePath = "http://localhost";
            var apiInstance = new AnalyzerApi(config);
            var analyzeRequest = new AnalyzeRequest(); // AnalyzeRequest | 

            try
            {
                // Analyze Text
                List<RecognizerResultWithAnalysis> result = apiInstance.AnalyzePost(analyzeRequest);
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling AnalyzerApi.AnalyzePost: " + e.Message );
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
 **analyzeRequest** | [**AnalyzeRequest**](AnalyzeRequest.md)|  | 

### Return type

[**List&lt;RecognizerResultWithAnalysis&gt;**](RecognizerResultWithAnalysis.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
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
            var apiInstance = new AnalyzerApi(config);

            try
            {
                // Healthcheck
                string result = apiInstance.HealthGet();
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling AnalyzerApi.HealthGet: " + e.Message );
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

<a name="recognizersget"></a>
# **RecognizersGet**
> List&lt;string&gt; RecognizersGet (string language = null)

Get Recognizers

Get the available PII recognizers for a given language

### Example
```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Presidio.Api;
using Presidio.Client;
using Presidio.Model;

namespace Example
{
    public class RecognizersGetExample
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.BasePath = "http://localhost";
            var apiInstance = new AnalyzerApi(config);
            var language = en;  // string | Two characters for the desired language in ISO_639-1 format (optional) 

            try
            {
                // Get Recognizers
                List<string> result = apiInstance.RecognizersGet(language);
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling AnalyzerApi.RecognizersGet: " + e.Message );
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
 **language** | **string**| Two characters for the desired language in ISO_639-1 format | [optional] 

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

<a name="supportedentitiesget"></a>
# **SupportedentitiesGet**
> List&lt;string&gt; SupportedentitiesGet (string language = null)

Get supported entities

Get the list of PII entities Presidio-Analyzer is capable of detecting

### Example
```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Presidio.Api;
using Presidio.Client;
using Presidio.Model;

namespace Example
{
    public class SupportedentitiesGetExample
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.BasePath = "http://localhost";
            var apiInstance = new AnalyzerApi(config);
            var language = en;  // string | Two characters for the desired language in ISO_639-1 format (optional) 

            try
            {
                // Get supported entities
                List<string> result = apiInstance.SupportedentitiesGet(language);
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling AnalyzerApi.SupportedentitiesGet: " + e.Message );
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
 **language** | **string**| Two characters for the desired language in ISO_639-1 format | [optional] 

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

