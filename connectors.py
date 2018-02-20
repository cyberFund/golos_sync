from pymongo import MongoClient

class Connector:
  def __init__(self):
    pass

  def save_block(self, block):
    pass

  def find_last_block(self):
    pass

  def update_last_block(self, last_block):
    pass

class MongoConnector(Connector):
  def __init__(self, database, host="localhost:27017"):
    self.client = MongoClient(host)
    self.database = self.client[database]

  def save_block(self, block):
    collection = block.get_collection()
    dictionary = block.to_dict()
    query = block.get_query()
    self.database[collection].insert(query, dictionary)    

  def find_last_block(self):
    init = self.database.status.find_one({'_id': 'height_all_tsx'})
    if (init):
      return init['value']
    else: 
      return 1

  def update_last_block(self, last_block):
    self.database.status.update({'_id': 'height_all_tsx'}, {"$set": {'value': last_block}}, upsert=True)
