from connectors import MongoConnector, ElasticConnector
from pistonapi.steemnoderpc import SteemNodeRPC

connectors = {
  'mongo': MongoConnector,
  'elasticsearch': ElasticConnector
}

def get_connectors(database, connector_type='mongo'):
  rpc = SteemNodeRPC("wss://api.golos.cf", apis=["follow", "database"])
  connector = connectors[connector_type](database)
  return rpc, connector
