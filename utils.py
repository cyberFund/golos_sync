from connectors import MongoConnector, ElasticConnector
from pistonapi.steemnoderpc import SteemNodeRPC
from functools import wraps

RESTART_INTERVAL = 60 * 5

connectors = {
  'mongo': MongoConnector,
  'elasticsearch': ElasticConnector
}

def get_connectors(database, connector_type='mongo'):
  # rpc = SteemNodeRPC("wss://api.golos.cf", apis=["follow", "database"])
  rpc = SteemNodeRPC("wss://ws.goldvoice.club/", apis=["follow", "database"])
  connector = connectors[connector_type](database)
  return rpc, connector

def restart_on_error(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    try:
      print("Running in safe mode")
      return f(*args, **kwargs)
    except Exception as e:
      print("Exception occured.")
      f.retry(countdown=RESTART_INTERVAL, exc=e)
  return wrapper

