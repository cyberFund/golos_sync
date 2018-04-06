import json
import requests

class SteemNodeRPC:
  def __init__(self, node_url):
    self.node_url = node_url

  def _create_method_call_request(self, api, method, params=[]):
    return {
      "jsonrpc": "2.0",
      "method": "call",
      "id": 1,
      "params": [
        api,
        method,
        params
      ]
    }

  def _send_request(self, request):
    request_string = json.dumps(request)
    response = requests.get(
      self.node_url,
      data=request_string,
      headers={"content-type": "application/json"}
    ).json()
    return response

  def get_config(self):
    request = self._create_method_call_request(
      "database_api", 
      "get_config"
    )
    return self._send_request(request)['result']

  def get_dynamic_global_properties(self):
    request = self._create_method_call_request(
      "database_api",
      "get_dynamic_global_properties"
    )
    return self._send_request(request)['result']

  def get_block(self, block_number):
    block_request = self._create_method_call_request(
      "database_api",
      "get_block",
      [block_number]
    )
    operations_request = self._create_method_call_request(
      "database_api",
      "get_ops_in_block",
      [block_number, False]
    )
    result = self._send_request(block_request)['result']
    result['transactions'] = [{
      'operations': self._send_request(operations_request)['result']
    }]
    return result

  def get_content(self, author, permlink):
    request = self._create_method_call_request(
      "social_network",
      "get_content",
      [author, permlink]
    )
    result = self._send_request(request)['result']
    return result

  def get_account(self, name):
    pass