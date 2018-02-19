from pymongo import MongoClient

class Connector:
  def __init__():
    pass

  def save_block(block):
    pass

  def find_last_block():
    pass

  def update_last_block(last_block):
    pass

class MongoConnector(Connector):
  def __init__(database, host="localhost:27017"):
    self.client = MongoClient(host)
    self.database = self.client[database]

  def save_block(block):
    collection = block.get_collection()
    dictionary = block.to_dict()
    self.database[collection].insert(dictionary)    

  def find_last_block():
    init = self.database.status.find_one({'_id': 'height_all_tsx'})
    if (init):
      return init['value']
    else: 
      return 1

  def update_last_block(last_block):
    self.database.status.update({'_id': 'height_all_tsx'}, {"$set": {'value': last_block}}, upsert=True)
