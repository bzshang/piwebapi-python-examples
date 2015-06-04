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

It accepts the name of the web API server. Then, I issue an HTTP GET to the base URL using `req.get()`

```Python
root_response = req.get('https://' + webapi_server + '/piwebapi', verify=False)
```

The `verify=False` is to ignore SSL certificate validation by the client, as in this case, I have a self-signed 
certificate.

The `root_response` object contains the details of the HTTP response, such as the status code, response body, headers,
cookies, etc. See the [reqests documentation](http://docs.python-requests.org/en/latest/user/quickstart/)
for more details about this object.

`root_response.text` returns the response body as a string. I want to convert this into a Python dictionary, so I can
more easily work with the response and not worry about parsing JSON strings. However, I am also greedy (or lazy) :wink:
and don't want to access the response type using `dict["Key"]` syntax. Instead, I prefer `dict.Key`, evocative  of 
C# anonymous types. The [`bunch`](https://pypi.python.org/pypi/bunch/1.0.1) library allows me to do this, and `bunchify`
converts the ordinary dictionary into a dot-accessible dictionary.



## Get AF server

Now that I have the root level response (as a dictionary), I want to target a specific AF server. I use the 
helper function below to do so.

```Python
    af_server = get_asset_server(pi_webapi_root, pi_asset_server)
```

The function accepts the root object and also the name of the AF server I want. Let's look at this function.

```Python
def get_asset_server(webapi_root_dict, asset_server):
    asset_servers_response = req.get(webapi_root_dict.Links.AssetServers, verify=False)
    asset_servers_dict = bunchify(json.loads(asset_servers_response.text))
    asset_server_dict = next((x for x in asset_servers_dict.Items if x.Name == asset_server), None)
    return bunchify(asset_server_dict)
```

My ultimate goal is to obtain an object representing the target AF server. From the root dictionary, I issue an HTTP
GET, passing in the URL `webapi_root_dict.Links.AssetServers`, whichs returns a JSON with a list of
available AF servers. Again I also `bunchify()` the response into a dot-accessible dictionary.

Now, I need just the part of the dictionary that contains the AF server I'm interested in. I will use the `next()`
function to retrieve the first matching entry in the list of AF servers, and default to `None`. I could have written the
`for` loop and conditional check on separate lines, but I just want to show off Python's awesome support for list
comprehensions. It is also more evocative of LINQ's `Select(x => x.Name == asset_server)` that I am accustomed to in C#.

```
Short diversion: By using links, I'm inherently using the RESTful PI Web API's support for HATEOAS (Hypermedia as the 
Engine of Application State). I simply need to understand the media types and link relations among the response 
hypermedia, and can use hyperlinks to obtain other resources. Contrast this with SOAP, in which I would need to 
understand the interface contracts, object models, and application logic exposed by the service.
```


