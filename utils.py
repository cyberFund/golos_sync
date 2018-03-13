from connectors import MongoConnector
from pistonapi.steemnoderpc import SteemNodeRPC

def create_connector(connector, database):
  if connector == 'mongo':
    connector = MongoConnector(database=database)
  elif connector == 'elasticsearch':
    connector = ElasticConnector(database=database)


def get_connectors(database, connector_type='mongo'):
  rpc = SteemNodeRPC("wss://ws.golos.io", apis=["follow", "database"])
  connector = create_connector(connector_type, database)
  return rpc, connector
