from connectors import MongoConnector, ElasticConnector
from pistonapi.steemnoderpc import SteemNodeRPC
from functools import wraps
import celery

RESTART_INTERVAL = 60 * 5

connectors = {
  'mongo': MongoConnector,
  'elasticsearch': ElasticConnector
}

def get_connectors(database, connector_type='mongo'):
  rpc = SteemNodeRPC("wss://api.golos.cf", apis=["follow", "database"])
  connector = connectors[connector_type](database)
  return rpc, connector

class RestartableTask(celery.Task):
  def on_failure(self, exc, task_id, args, kwargs, einfo):
    self.retry(countdown=RESTART_INTERVAL, exc=exc)