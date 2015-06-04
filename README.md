# Introduction

These examples show how to browse the AF object hierarchy, read/write values, and update attribute metadata.

For these examples, I've created an AF attribute at the path `\\SECRETAFSERVER\Sandbox\MyElement|MyAttribute`. 
The attribute is configured as a PI Point DR.

I've set these variables in the code as shown below:

```Python
pi_webapi_server = 'SECRETWEBSERVER'
pi_asset_server = 'SECRETAFSERVER'
pi_asset_database = 'Sandbox'
```

In the header, you will see I've imported the relevant packages and functions that I need.

```Python
import requests as req
import json
from bunch import bunchify, unbunchify
```


The example file is structured with a set of helper functions in the beginning and the usage of these functions 
afterward. These helper methods are merely used to encapsulate basic operations on AF objects and hide away some 
implementation details. Please do not take these functions as best practice or a guide for designing Python wrappers
for PI Web API calls. My experience with Python can be measured in units of days, rather than years...

## Get the root level PI Web API response

To make things transparent, I will show how to get the root level response from a PI Web API call, which can be obtained
also by going to `https://<piwebapiserver>/piwebapi/` in the browser.

I make the call

```Python
pi_webapi_root = get_pi_webapi_root(pi_webapi_server)
```

Now, let's see what the `get_pi_webapi_root` function does.

```Python
def get_pi_webapi_root(webapi_server):
    # verify=False is to ignore SSL verification but this will vary depending on environment
    root_response = req.get('https://' + webapi_server + '/piwebapi', verify=False)
    # deserialize json into python dictionary
    return bunchify(json.loads(root_response.text))
```

It accepts the name of the web API server. Then, I issue an HTTP GET to the base URL using

```Python
root_response = req.get('https://' + webapi_server + '/piwebapi', verify=False)
```

The `verify=False` is to ignore SSL certificate validation by the client, as in this case, I have a self-signed 
certificate.

The `root_response` object contains the details of the HTTP response, such as the status code, response body, headers,
cookies, etc. See the [reqests documentation](http://docs.python-requests.org/en/latest/user/quickstart/)
for more details about this object.

`root_response.text` returns the response body as a string. I want to convert this into a Python dictionary, so I can
more easily work with the response and not worry about parsing JSON strings. However, I am also greedy (or lazy) and
don't want to access the response type using `dict["Key"]` syntax. Instead, I prefer `dict.Key`, evocative  of 
C# anonymous types. The [`bunch`](https://pypi.python.org/pypi/bunch/1.0.1) library allows me to do this, and `bunchify`
converts the ordinary dictionary into a dot-accessible dictionary.

