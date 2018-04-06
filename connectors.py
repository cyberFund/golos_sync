from pymongo import MongoClient, ASCENDING
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
import pdb

class Connector:
  def __init__(self):
    pass

  def save_block(self, block):
    """
      Method to save specified operation
      just calls use_connector method of an entity
    """
    block.use_connector(self)

  def find_last_block(self):
    """
      Abstract method to find index of last block
      pushed to a celery queue
    """
    pass

  def update_last_block(self, last_block):
    """
      Abstract method to update index of last block
      pushed to a celery queue
    """
    pass

  def save_instance(self, instance):
    """
      Abstract method to save comment or account instance
      Will be joined with save_block method in future releases
    """
    pass

  def get_instances_to_update(self, collection):
    """
      Abstract method to return instances with 
      activated need_update flag
    """
    pass

  def update_instances(self, collection, instances):
    """
      Abstract method to reset need_update flag
      of an entities
    """
    pass

class MongoConnector(Connector):
  """
    Class for connectors that are operate with mongo database
  """
  def __init__(self, database, host="localhost:27017"):
    self.client = MongoClient(host)
    self.database = self.client[database]
    self.create_indices()

  def create_indices(self):
    """
      Creates indices for some special oprations
    """
    self.database.reblog.create_index([('blockid', ASCENDING), ('permlink', ASCENDING), ('account', ASCENDING)])
    self.database.follow.create_index([('blockid', ASCENDING), ('follower', ASCENDING), ('following', ASCENDING)])

  def save_block(self, block):
    """
      Updates or inserts operation in a mongo database
    """
    super().save_block(block)
    collection = block.get_collection()
    dictionary = block.to_dict()
    query = block.get_query()
    self.database[collection].update(query, {"$set": dictionary}, upsert=True)    

  def find_last_block(self):
    """
      Finds last block index as a value field of a document 
      in a status collection with specified id
    """
    init = self.database.status.find_one({'_id': 'height_all_tsx'})
    if (init):
      return init['value']
    else: 
      return 1

  def update_last_block(self, last_block):
    """
      Updates last block index as a value field of a document 
      in a status collection with specified id
    """
    self.database.status.update({'_id': 'height_all_tsx'}, {"$set": {'value': last_block}}, upsert=True)

  def save_instance(self, instance):
    """
      Updates or inserts account or comment in a mongo database
      by instance id
    """
    dictionary = instance.to_dict()
    instance_id = instance.get_id()
    collection = instance.get_collection()
    instance.use_connector(self)
    self.database[collection].update({'_id': instance_id}, {"$set": dictionary}, upsert=True)

  def get_instances_to_update(self, collection):
    """
      Finds and returns all dictionaries with objects that should be updated
    """
    return list(self.database[collection].find({'need_update': True}))

  def update_instances(self, collection, instances):
    """
      Resets need_update flag for all instances in a list by their ids in _id field
    """
    for instance in instances:
      self.database[collection].update_one({'_id': instance['_id']}, {"$set": {'need_update': False}})

class ElasticConnector(Connector):
  """
    Class for connectors that are operate with elasticsearch database
  """
  MAX_SIZE = 1000
  def __init__(self, database, host='http://localhost:9200/'):
    self.client = ElasticSearch(host)
    self.index = database
    self.create_index()

  def query_to_id(self, query):
    """
      Returns id representation of a specified query
      This is a temporary method as a replacement of elasticsearch query search
    """
    return "_".join(str(k) + "_" + str(v) for k,v in query.items()).replace("/", "_")

  def create_index(self):
    """
      Creates specified index or catches an exception if it has already been created
    """
    try:
      self.client.create_index(self.index)
    except Exception as e:
      pass

  def set_dynamic_mapping(self, collection):
    """
      Sets dynamic mapping for a specified document type
    """
    self.client.put_mapping(self.index, collection, {'dynamic': True})

  def save_block(self, block):
    """
      Saves operation info in a database
    """
    super().save_block(block)
    collection = block.get_collection()
    dictionary = block.to_dict()
    query = block.get_query()
    self.update_by_query(collection, query, block)

  def update_by_query(self, collection, query, document):
    """
      Sets dynamic mapping for a specified collection,
      then creates a new id for a document depending on query for it.
      Saves a new object in a database as a new one
    """
    try:
      self.set_dynamic_mapping(collection)
      document_id = document.get_id()
      document_body = document.to_dict()
      if "_id" in document_body.keys():
        del document_body['_id']
      self.client.index(
        self.index, 
        collection, 
        document_body,
        id=self.query_to_id(query)
      )
    except Exception as e:
      print(e)
      pass

  def find_last_block(self):
    """
      Finds last block index as a value field of a document 
      in a status collection with specified id
    """
    try:
      document = self.client.get(
        self.index, 
        'status', 
        'height_all_tsx'
      )['_source']
      return document['value']
    except ElasticHttpNotFoundError as e:
      return 0

  def update_last_block(self, last_block):
    """
      Updates last block index as a value field of a document 
      in a status collection with specified id
    """
    self.client.index(
      self.index, 
      'status', 
      {'value': last_block}, 
      id='height_all_tsx'
    )

  def save_instance(self, instance):
    """
      Saves account or comment object
    """
    self.update_by_query(instance.get_collection(), instance.get_query(), instance)

  def get_instances_to_update(self, collection):
    """
      Finds and returns all dictionaries with objects that should be updated
    """
    hits = self.client.search(
      "need_update:true", 
      index=self.index, 
      doc_type=collection,
      size=self.MAX_SIZE
    )['hits']['hits']
    return [{**hit['_source'], **{"_id": hit["_id"]}} for hit in hits]

  def update_instances(self, collection, instances):
    """
      Resets need_update flag for all instances in a list by their ids in _id field
    """
    for instance in instances:
      self.client.update(
        self.index, 
        collection, 
        instance["_id"],
        doc={'need_update': False}
      )