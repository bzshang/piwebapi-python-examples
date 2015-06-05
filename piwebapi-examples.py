import requests as req
import json
from bunch import bunchify, unbunchify

def get_pi_webapi_root(webapi_server):
    # verify=False is to ignore SSL verification but this will vary depending on environment
    root_response = req.get('https://' + webapi_server + '/piwebapi', verify=False)
    # deserialize json into python dictionary. then convert to dot-accessible dictionary
    return bunchify(json.loads(root_response.text))

def get_asset_server(webapi_root_dict, asset_server):
    asset_servers_response = req.get(webapi_root_dict.Links.AssetServers, verify=False)
    asset_servers_dict = bunchify(json.loads(asset_servers_response.text))
    asset_server_dict = next((x for x in asset_servers_dict.Items if x.Name == asset_server), None)
    return bunchify(asset_server_dict)

def get_database(asset_server_dict, asset_database):
    asset_databases_response = req.get(asset_server_dict.Links.Databases, verify=False)
    asset_databases_dict = bunchify(json.loads(asset_databases_response.text))
    asset_database_dict = next((x for x in asset_databases_dict.Items if x.Name == asset_database), None)
    return bunchify(asset_database_dict)

def get_element(asset_database_dict, element):
    asset_elements_response = req.get(asset_database_dict.Links.Elements, verify=False)
    asset_elements_dict = bunchify(json.loads(asset_elements_response.text))
    asset_element_dict = next((x for x in asset_elements_dict.Items if x.Name == element), None)
    return bunchify(asset_element_dict)

def get_attribute(asset_element_dict, attribute):
    asset_attributes_response = req.get(asset_element_dict.Links.Attributes, verify=False)
    asset_attributes_dict = bunchify(json.loads(asset_attributes_response.text))
    asset_attribute_dict = next((x for x in asset_attributes_dict.Items if x.Name == attribute), None)
    return bunchify(asset_attribute_dict)

def get_attribute_by_path(webapi_root_dict, params):
    attribute_url = webapi_root_dict.Links.Self + 'attributes'
    asset_attributes_response = req.get(attribute_url, params=params, verify=False)
    return bunchify(json.loads(asset_attributes_response.text))

def get_stream_value(af_attribute_dict, params):
    attribute_value_response = req.get(af_attribute_dict.Links.Value, params=params, verify=False)
    return bunchify(json.loads(attribute_value_response.text))

def post_stream_value(af_attribute_dict, json_data, headers):
    attribute_value_response = req.post(af_attribute_dict.Links.Value,
                                        json=json_data,
                                        headers=headers,
                                        verify=False)
    return attribute_value_response

def update_af_attribute(af_attribute_dict, json_data, headers):
    attribute_update_response = req.patch(af_attribute_dict.Links.Self,
                                          json=json_data,
                                          headers=headers,
                                          verify=False)
    return attribute_update_response

if __name__ == "__main__":

    pi_webapi_server = 'SECRETWEBSERVER'
    pi_asset_server = 'SECRETAFSERVER'
    pi_asset_database = 'Sandbox'

    # 1.0 --------------------------------------------------------------------------------------------------------------
    # Get the root level PI Web API
    pi_webapi_root = get_pi_webapi_root(pi_webapi_server)
    print unbunchify(pi_webapi_root)

    # 2.0 --------------------------------------------------------------------------------------------------------------
    # Get AF server
    af_server = get_asset_server(pi_webapi_root, pi_asset_server)

    # 3.0 --------------------------------------------------------------------------------------------------------------
    # Get AF database from server
    af_database = get_database(af_server, pi_asset_database)

    # Get AF element from database
    af_element = get_element(af_database, "MyElement")

    # Get AF attribute from element
    af_attribute = get_attribute(af_element, "MyAttribute")

    # 4.0 --------------------------------------------------------------------------------------------------------------
    # Retrieve the same attribute by path
    req_params = {'path': '\\\\SECRETAFSERVER\\SandBox\\MyElement|MyAttribute'}
    af_attribute = get_attribute_by_path(pi_webapi_root, req_params)

    # 5.0 --------------------------------------------------------------------------------------------------------------
    # Get AF value for attribute
    af_value = get_stream_value(af_attribute, None)

    print unbunchify(af_value)
    # output:
    # {u'Questionable': False,
    # u'Good': True,
    # u'UnitsAbbreviation': u'',
    # u'Timestamp': u'2015-06-02T21:05:19Z',
    # u'Value': 1.0,
    # u'Substituted': False}

    # 6.0 --------------------------------------------------------------------------------------------------------------
    # Write a value to MyAttribute
    req_data = {'Timestamp': '2015-06-03T00:00:00', 'Value': '25.0'}
    req_headers = {'Content-Type': 'application/json'}
    post_result = post_stream_value(af_attribute, req_data, req_headers)
    print post_result.status_code
    # output:
    # 202

    # Read back the value just written
    req_params = {'time': '2015-06-03T00:00:00'}
    af_value = get_stream_value(af_attribute, req_params)
    print unbunchify(af_value)
    # output:
    # {u'Questionable': False,
    # u'Good': True,
    # u'UnitsAbbreviation': u'',
    # u'Timestamp': u'2015-06-02T21:05:19Z',
    # u'Value': 1.0,
    # u'Substituted': False}

    # 7.0 --------------------------------------------------------------------------------------------------------------
    # Add a description to MyAttribute
    req_data = {'Description': 'Hello world'}
    req_headers = {'Content-Type': 'application/json'}
    patch_result = update_af_attribute(af_attribute, req_data, req_headers)
    print patch_result.status_code
    # output:
    # 204

    # Read the attribute description
    af_attribute = get_attribute(af_element, "MyAttribute")
    print af_attribute.Description
    # output:
    # Hello world




