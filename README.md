# Introduction

These examples show how to browse the AF object hierarchy, read/write values, and update attribute metadata.

For these examples, I've created an AF attribute at the path `\\AFServer\Sandbox\MyElement|MyAttribute`. 
The attribute is configured as a PI Point DR.

I've set these variables in the code as shown below:

```Python
pi_webapi_server = 'BSHANG-WEB2'
pi_asset_server = 'BSHANGE6430S'
pi_asset_database = 'Sandbox'
```

The example file is structured with a set of helper functions in the beginning and the usage of these functions 
afterward. These helper methods are merely used to encapsulate basic operations on AF objects and hide away some 
implementation details. Please do not take these functions as best practice or a guide for designing Python wrappers
for PI Web API calls. My experience with Python can be measured in units of days, rather than years...

## Get the root level PI Web API response

To make things transparent, I will show how to get the root level response from a PI Web API call, which can be obtained
also by going to `https://<piwebapiserver>/piwebapi/` in the browser.

