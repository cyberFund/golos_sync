from connectors import MongoConnector
from pistonapi.steemnoderpc import SteemNodeRPC

def get_connectors(mongo_database):
  rpc = SteemNodeRPC("wss://ws.golos.io", apis=["follow", "database"])
  connector = MongoConnector(database=mongo_database)
  return rpc, connector
