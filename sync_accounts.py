from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from connectors import MongoConnector
from pprint import pprint
import json
import time
import sys
from tqdm import tqdm
from accounts import UpdatedAccount
from utils import get_connectors, RestartableTask
from celery import Celery
import click
from time import sleep

MAX_ACCOUNTS_PER_TASK = 1000
MIN_ACCOUNTS_PER_TASK = 1

app = Celery('sync_accounts', broker='redis://localhost:6379/2')

@app.task(base=RestartableTask)
def sync_accounts(connector, database, accounts):
  """
    Celery task that extends accounts with a new info from API and saves it to a database
  """
  rpc, connector = get_connectors(database, connector)
  for account in tqdm(accounts):
    account.update(rpc.get_account(account['name']))
    account_object = UpdatedAccount(account)
    connector.save_instance(account_object)

@click.command()
@click.option('--connector', help='Type of connector (mongo/elasticsearch).', default='mongo')
@click.option('--database', help='Name of database', default='golos_transactions')
def sync_all_accounts(connector, database):
  """
    Creates multiple celery tasks to process all accounts that are waiting for an update 
  """
  connector_type = connector
  rpc, connector = get_connectors(database, connector)
  config = rpc.get_config()
  block_interval = config["STEEMIT_BLOCK_INTERVAL"]
  while True: 
    accounts_per_task = MAX_ACCOUNTS_PER_TASK
    accounts = connector.get_instances_to_update('account_object')
    while len(accounts) < accounts_per_task:
      sleep(block_interval)
      accounts = connector.get_instances_to_update('account_object')
      accounts_per_task = max(accounts_per_task / 10, MIN_ACCOUNTS_PER_TASK)
    task_accounts = []
    for account in tqdm(accounts):
      task_accounts.append(account)
      if len(task_accounts) >= accounts_per_task:
        sync_accounts.delay(connector_type, database, task_accounts)
        connector.update_instances('account_object', task_accounts)
        task_accounts = []
    if len(task_accounts):
      connector.update_instances('account_object', task_accounts)
      sync_accounts.delay(connector_type, database, task_accounts)

if __name__ == '__main__':
  sync_all_accounts()
