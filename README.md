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

In the header, I've imported the relevant packages and functions that I need.

```Python
import requests as req
import json
from bunch import bunchify, unbunchify
```

* [requests](http://docs.python-requests.org/en/latest/) is used as the HTTP client library. 
* [json](https://docs.python.org/2/library/json.html) as the name suggests helps me deserialize JSON text into Python 
dictionaries and vice versa. 
* [bunch](https://pypi.python.org/pypi/bunch/1.0.1) is a package that provides a wrapper class around Python dictionaries 
so I can browse the dictionary using dot notation (e.g. dict.key instead of dict["key"]), evocative of the C# anonymous 
type.

The example file is structured with a set of helper functions in the beginning and the usage of these functions 
afterward. These helper functions are merely used to encapsulate basic operations on AF objects and hide away some 
implementation details. These functions do not represent best practices or offer a guide for designing Python wrappers
for PI Web API calls. My experience with Python can be measured in units of days, rather than years...

## Examples

Follow along in the code in [piwebapi-examples.py](https://github.com/bzshang/piwebapi-python-examples/blob/master/piwebapi-examples.py).

### 1.0 Get the root level PI Web API response

To make things transparent, I will show how to get the root level response from a PI Web API call, which can be obtained
also by going to `https://<piwebapiserver>/piwebapi/` in the browser.

I make the call

```Python
pi_webapi_root = get_pi_webapi_root(pi_webapi_server)
```

Now, let's see what the `get_pi_webapi_root()` function does.

```Python
def get_pi_webapi_root(webapi_server):
    # verify=False is to ignore SSL verification but this will vary depending on environment
    root_response = req.get('https://' + webapi_server + '/piwebapi', verify=False)
    # deserialize json into python dictionary. then convert to dot-accessible dictionary
    return bunchify(json.loads(root_response.text))
```

It accepts the name of the web API server. Then, I issue an HTTP GET to the base URL using `req.get()`

```Python
root_response = req.get('https://' + webapi_server + '/piwebapi', verify=False)
```

```
    Note that the full function call is requests.get(), but because I've imported the package using 
    'import requests as req', I can use this naming shortcut.
```

The `verify=False` is to ignore SSL certificate validation by the client, as in this case, I have a self-signed 
certificate.

The `root_response` object contains the details of the HTTP response, such as the status code, response body, headers,
cookies, etc. See the [reqests documentation](http://docs.python-requests.org/en/latest/user/quickstart/)
for more details about this object.

`root_response.text` returns the response body as a string. I want to convert this into a Python dictionary, so I can
more easily work with the response and not worry about parsing JSON strings. `json.loads()` allows me to do this. 
However, I am also greedy (or lazy) :wink:and don't want to access the response type using `dict["Key"]` syntax. 
Instead, I prefer `dict.Key`, evocative  of C# anonymous types. The [`bunch`](https://pypi.python.org/pypi/bunch/1.0.1) 
library allows me to do this, and `bunchify()` converts the ordinary dictionary into a dot-accessible dictionary.

### 2.0 Get AF server

Now that I have the root level response (as a dot-accessible dictionary), I want to target a specific AF server. I use 
the helper function below to do so.

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
available AF servers. Again, I also `bunchify()` the response into a dot-accessible dictionary.

Now, I need just the part of the dictionary that contains the AF server I'm interested in. I will use the `next()`
function to retrieve the first matching entry in the list of AF servers, and default to `None`. I could have written the
`for` loop and `if` check on separate lines, but I just want to show off Python's awesome support for [list
comprehensions](https://docs.python.org/2/tutorial/datastructures.html). It is also more evocative of LINQ's 
`Select(x => x.Name == asset_server)` that I am accustomed to in C#.

**Short diversion:** By using links, I'm inherently using the RESTful PI Web API's support for [HATEOAS]
(http://en.wikipedia.org/wiki/HATEOAS) (Hypermedia as the Engine of Application State). I simply need to understand the 
media types and link relations among the response hypermedia, and can use hyperlinks to obtain other resources. Contrast
this with SOAP, in which I would need to understand the interface contracts, object models, and application logic 
exposed by the service.


### 3.0 Get AF database, element, attribute

Now that I have the AF server, I want to "drill down" to the AF attribute of interest. The rest of the functions are 
similar to what I did to grab the AF server.

```Python
    af_database = get_database(af_server, pi_asset_database)
    af_element = get_element(af_database, "MyElement")
    af_attribute = get_attribute(af_element, "MyAttribute")
```

You will notice `get_database()` is very similar to `get_asset_server()`. I wasn't kidding when I said I wasn't a Python
developer, and that these helper functions do not expose elegant class library design...

### 4.0 Get AF attribute by path: Setting the query string in `requests`

We made a lot of round-trips to the server just to get an attribute, which is a poor practice. What we could have done 
is get the attribute in one HTTP call by passing in the attribute path as a query string, using the PI Web API call
`GET attributes`. See the [PI Web API Online Documentation](https://techsupport.osisoft.com/Documentation/PI-Web-API/help.html) for details.
In Python, I use

```Python
    req_params = {'path': '\\\\SECRETAFSERVER\\SandBox\\MyElement|MyAttribute'}
    af_attribute = get_attribute_by_path(pi_webapi_root, req_params)
```

First, I set the query string parameters by creating a Python dictionary to store them. I created a helper function
`get_attribute_by_path()` to find the attribute based on path. Here is that function.

```Python
def get_attribute_by_path(webapi_root_dict, params):
    attribute_url = webapi_root_dict.Links.Self + 'attributes'
    asset_attributes_response = req.get(attribute_url, params=params, verify=False)
    return bunchify(json.loads(asset_attributes_response.text))
```

Using `req.get()` from the `requests` package, I simply issue a GET request passing in the URL
`https://SECRETWEBSERVER/piwebapi/attributes`, and the query string as a function argument as `params=params`. The 
response is the same as if I went to 

```
    https://SECRETWEBSERVER/piwebapi/attributes?path=\\\\SECRETAFSERVER\\SandBox\\MyElement|MyAttribute
```

in the browser.

Perhaps a better way to obtain the attribute is to use PI Indexed Search via `GET search/query`, but I will leave it up
to the reader :wink:

### 5.0 Get the current value of MyAttribute

I use a helper function `get_stream_value()` and `req.get()` function from the `requests` library. Nothing new here.

### 6.0 Write a value to MyAttribute: POST JSON using `requests`

Something new here. Here is the code I use to formulate the request.

```Python
    req_data = {'Timestamp': '2015-06-03T00:00:00', 'Value': '25.0'}
    req_headers = {'Content-Type': 'application/json'}
    post_result = post_stream_value(af_attribute, req_data, req_headers)
```

First, I set the query string in the URL via the `req_data` dictionary I created. Then, I set the HTTP request header
using the `req_headers` dictionary. I pass both of these variables into my helper function `post_stream_value` along with
my (dot-accessible) AF attribute dictionary. Here is the helper function.

```Python
def post_stream_value(af_attribute_dict, json_data, headers):
    attribute_value_response = req.post(af_attribute_dict.Links.Value,
                                        json=json_data,
                                        headers=headers,
                                        verify=False)
    return attribute_value_response
```

To issue a POST in `requests`, it is very simple. Just use `req.post()`. I pass in the relevant URL, JSON body, and
header information. Note I am returning the raw response object, as there is no JSON returned and I can inspect the
status code later using `print post_result.status_code`.

Just as an additional check, I read back in the value I just wrote using `get_stream_value()` but this time pass in a 
query string denoting the timestamp.

### 7.0 Add a description to MyAttribute: PATCH using `requests`

These examples would not be complete if I hadn't snuck in `Hello world` somewhere in here. So we will allow our
attribute to introduce herself to the world. Here is how to do so.

```Python
    req_data = {'Description': 'Hello world'}
    req_headers = {'Content-Type': 'application/json'}
    patch_result = update_af_attribute(af_attribute, req_data, req_headers)
```

It is the same dog but maybe a new trick. I formulate the request JSON in `req_data`, set the header in `req_headers`
and then call by helper function `update_af_attribute()`, shown below.

```Python
    attribute_update_response = req.patch(af_attribute_dict.Links.Self,
                                          json=json_data,
                                          headers=headers,
                                          verify=False)
```

To update attribute metadata, I need to issue an HTTP PATCH request, which I can do using `req.patch()`. Lastly, I read
back in the attribute to verify that I've updated successfully, using my helper function `get_attribute()` and storing 
the result in `af_attribute`. Because of the work I've done to return a dot-accessible dictionary, I can easily inspect 
the attribute description simply via `af_attribute.Description`. Hello world!

## Summary

In these examples, we've demonstrated the basic usage of PI Web API with the `requests` package in Python. Being able to
access PI System data within Python brings the rich features of Python into PI, such as its numerical and scientific libraries
(numpy, scipy, pandas, scikit-learn, etc.) and also its web application framework (Django).

For questions or comments, pelase visit the associated blog post in 
[PI Developer's Club](https://pisquare.osisoft.com/community/developers-club/blog/2015/06/04/using-pi-web-api-with-python).

