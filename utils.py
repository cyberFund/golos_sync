from connectors import MongoConnector, ElasticConnector
from stubs.pistonapi import SteemNodeRPC
from functools import wraps
import celery
import logging

logging.basicConfig(filename='log.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

RESTART_INTERVAL = 60 * 5

connectors = {
  'mongo': MongoConnector,
  'elasticsearch': ElasticConnector
}

def get_connectors(database, connector_type='mongo'):
  """
    Returns connectors to a golos node and to a specified database
    Database type should be selected from a list:
    - Mongo
    - Elasticsearch
  """
  rpc = SteemNodeRPC("http://localhost:8090")
  connector = connectors[connector_type](database)
  return rpc, connector

class RestartableTask(celery.Task):
  """
    Class to make all celery tasks restartable
  """
  def on_failure(self, exc, task_id, args, kwargs, einfo):
    """
      Puts log entry abount an exception
      and restarts task when RESTART_INTERVAL ends
    """
    logging.warning("Task {} ({}): {}".format(task_id, args, exc))
    self.retry(countdown=RESTART_INTERVAL, exc=exc)
