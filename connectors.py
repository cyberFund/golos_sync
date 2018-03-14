from pymongo import MongoClient, ASCENDING
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
import pdb

class Connector:
  def __init__(self):
    pass

  def save_block(self, block):
    block.use_connector(self)

  def find_last_block(self):
    pass

  def update_last_block(self, last_block):
    pass

  def save_instance(self, instance):
    pass

  def get_instances_to_update(self, collection):
    pass

  def update_instances(self, collection, instances):
    pass

class MongoConnector(Connector):
  def __init__(self, database, host="localhost:27017"):
    self.client = MongoClient(host)
    self.database = self.client[database]
    self.create_indices()

  def create_indices(self):
    self.database.reblog.create_index([('blockid', ASCENDING), ('permlink', ASCENDING), ('account', ASCENDING)])
    self.database.follow.create_index([('blockid', ASCENDING), ('follower', ASCENDING), ('following', ASCENDING)])

  def save_block(self, block):
    super().save_block(block)
    collection = block.get_collection()
    dictionary = block.to_dict()
    query = block.get_query()
    self.database[collection].update(query, {"$set": dictionary}, upsert=True)    

  def find_last_block(self):
    init = self.database.status.find_one({'_id': 'height_all_tsx'})
    if (init):
      return init['value']
    else: 
      return 1

  def update_last_block(self, last_block):
    self.database.status.update({'_id': 'height_all_tsx'}, {"$set": {'value': last_block}}, upsert=True)

  # TODO join method with save_block
  def save_instance(self, instance):
    dictionary = instance.to_dict()
    instance_id = instance.get_id()
    collection = instance.get_collection()
    instance.use_connector(self)
    self.database[collection].update({'_id': instance_id}, {"$set": dictionary}, upsert=True)

  def get_instances_to_update(self, collection):
    return list(self.database[collection].find({'need_update': True}))

  def update_instances(self, collection, instances):
    for instance in instances:
      self.database[collection].update_one({'_id': instance['_id']}, {"$set": {'need_update': False}})

class ElasticConnector(Connector):
  def __init__(self, index, host='http://localhost:9200/'):
    self.client = ElasticSearch(host)
    self.index = index
    self.create_index()

  def create_index(self):
    try:
      self.client.create_index(self.index)
    except Exception as e:
      pass

  def save_block(self, block):
    super().save_block(block)
    collection = block.get_collection()
    dictionary = block.to_dict()
    query = block.get_query()
    self.update_by_query(collection, query, block)

  def update_by_query(self, collection, query, document):
    document_id = document.get_id()
    document_body = document.to_dict()
    del document_body['_id']
    self.client.index(self.index, collection, document_body, id=document_id)

  def find_last_block(self):
    try:
      document = self.client.get(self.index, 'status', 'height_all_tsx')['_source']
      return document['value']
    except ElasticHttpNotFoundError as e:
      return 0

  def update_last_block(self, last_block):
    self.client.index(self.index, 'status', {'value': last_block}, id='height_all_tsx')

  def save_instance(self, instance):
    self.update_by_query(collection, query, block)

  def get_instances_to_update(self, collection):
    hits = self.client.search("need_update:true", index=self.index, doc_type=collection)['hits']['hits']
    return [hit['_source'] for hit in hits]

  def update_instances(self, collection, instances):
    for instance in instances:
      self.client.index(self.index, collection, {'need_update': False}, id=instance['_id'])
