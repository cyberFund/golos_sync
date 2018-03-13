import unittest
from ..connectors import ElasticConnector
from ..blocks import Block
from pyelasticsearch import ElasticSearch
import pdb
from datetime import datetime

class TestBlock(Block):
    def __init__(self):
        block = {
            'timestamp': "2017-11-01T00:00:00"
        }
        operation = {
            'content': "test"
        }
        super().__init__(0, block, 'test_operation', operation)


class TestElasticConnectorCase(unittest.TestCase):
    def delete_test_index(self):
        try:
            self.elastic.delete_index('test')
        except Exception as e:
            pass
        
    def setUp(self):
        self.elastic = ElasticSearch('http://localhost:9200/')
        self.delete_test_index()
        self.connector = ElasticConnector('test')
        
    # def test_new_index(self):
    #     self.assertEqual(self.elastic.open_index('test')['acknowledged'], True)

    # def test_existed_index(self):
    #     self.delete_test_index()
    #     self.elastic.create_index('test')
    #     self.connector = ElasticConnector('test')
    #     self.assertEqual(self.elastic.open_index('test')['acknowledged'], True)

    # def test_update_last_block_first_time(self):
    #     self.connector.update_last_block(100)
    #     document = self.elastic.get('test', 'status', 'height_all_tsx')['_source']
    #     self.assertEqual(document['value'], 100)

    # def test_update_last_block(self):
    #     self.connector.update_last_block(100)
    #     self.connector.update_last_block(101)
    #     document = self.elastic.get('test', 'status', 'height_all_tsx')['_source']
    #     self.assertEqual(document['value'], 101)

    # def test_find_last_block_first_time(self):
    #     value = self.connector.find_last_block()
    #     self.assertEqual(value, 0)

    # def test_find_last_block(self):
    #     self.elastic.index('test', 'status', {'value': 10}, id='height_all_tsx')
    #     value = self.connector.find_last_block()
    #     self.assertEqual(value, 10)

    # def test_save_block(self):
    #     block = TestBlock()
    #     self.connector.save_block(block)
    #     document = self.elastic.get('test', block.get_collection(), block.get_id())['_source']
    #     self.assertEqual(document['blockid'], block.to_dict()['blockid'])
    #     self.assertEqual(document['content'], block.to_dict()['content'])

    def test_get_instances_to_update(self):
        self.elastic.index('test', 'test_collection', {'need_update': True, 'content': 0}, id=0)
        self.elastic.index('test', 'test_collection', {'need_update': False, 'content': 1}, id=1)
        instances = self.connector.get_instances_to_update('test_collection')
        self.assertEqual(instances[0]['content'], 0)