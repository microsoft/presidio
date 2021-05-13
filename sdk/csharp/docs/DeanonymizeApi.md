# Presidio.Api.DeanonymizeApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DeanonymizePost**](DeanonymizeApi.md#deanonymizepost) | **POST** /deanonymize | Deanonymize Text


<a name="deanonymizepost"></a>
# **DeanonymizePost**
> DeanonymizeResponse DeanonymizePost (DeanonymizeRequest deanonymizeRequest)

Deanonymize Text

### Example
```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Presidio.Api;
using Presidio.Client;
using Presidio.Model;

namespace Example
{
    public class DeanonymizePostExample
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.BasePath = "http://localhost";
            var apiInstance = new DeanonymizeApi(config);
            var deanonymizeRequest = new DeanonymizeRequest(); // DeanonymizeRequest | 

            try
            {
                // Deanonymize Text
                DeanonymizeResponse result = apiInstance.DeanonymizePost(deanonymizeRequest);
                Debug.WriteLine(result);
            }
            catch (ApiException  e)
            {
                Debug.Print("Exception when calling DeanonymizeApi.DeanonymizePost: " + e.Message );
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
 **deanonymizeRequest** | [**DeanonymizeRequest**](DeanonymizeRequest.md)|  | 

### Return type

[**DeanonymizeResponse**](DeanonymizeResponse.md)

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

