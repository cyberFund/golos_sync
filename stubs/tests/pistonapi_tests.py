import unittest
from pistonapi import SteemNodeRPC
from time import sleep

class PistonapiTestCase(unittest.TestCase):
  def setUp(self):
    self.client = SteemNodeRPC("http://localhost:8090")

  def test_create_method_call_request(self):
    request = self.client._create_method_call_request("custom_api", "custom_method", ["param1", "param2"])
    assert request["jsonrpc"] == "2.0"
    assert request["method"] == "call"
    assert request["id"] == 1
    assert request["params"][0] == "custom_api"
    assert request["params"][1] == "custom_method"
    self.assertSequenceEqual(request["params"][2], ["param1", "param2"])

  def test_send_request(self):
    response = self.client._send_request({})
    assert response

  def test_get_config(self):
    config = self.client.get_config()
    assert "STEEMIT_BLOCK_INTERVAL" in config.keys()

  def test_get_dynamic_global_properties(self):
    properties = self.client.get_dynamic_global_properties()
    assert "last_irreversible_block_num" in properties.keys()

  def test_get_block(self):
    block = self.client.get_block(TEST_BLOCK_NUMBER)
    operation = block['transactions'][0]['operations'][0]
    assert len(block['transactions'][0]['operations'])
    assert len(operation) == 2

  def test_get_content(self):
    content = self.client.get_content(*TEST_COMMENT)
    assert "root_title" in content.keys()

  def test_get_account(self):
    account = self.client.get_account(TEST_ACCOUNT)
    assert account

TEST_BLOCK_NUMBER = 10000000
TEST_COMMENT = '@goldvoice/new-public-nodes'[1:].split('/')
TEST_ACCOUNT = "litvintech"

# ssh -L 8090:localhost:8090 root@78.46.57.29
# Как затестить эксепшен и рестарт на эксепшен?