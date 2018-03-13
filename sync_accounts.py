from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from connectors import MongoConnector
from pprint import pprint
import json
import time
import sys
from tqdm import tqdm
from accounts import UpdatedAccount
from utils import get_connectors
from celery import Celery

MAX_ACCOUNTS_PER_TASK = 1000
MIN_ACCOUNTS_PER_TASK = 1

app = Celery('sync_accounts', broker='redis://localhost:6379')

@app.task
def sync_accounts(mongo_database, accounts):
  rpc, connector = get_connectors(mongo_database)
  for account in tqdm(accounts):
    account.update(rpc.get_account(account['name']))
    account_object = UpdatedAccount(account)
    connector.save_instance(account_object)

if __name__ == '__main__':
  rpc, connector = get_connectors(sys.argv[1])
  config = rpc.get_config()
  block_interval = config["STEEMIT_BLOCK_INTERVAL"]
  while True: 
    accounts_per_task = MAX_ACCOUNTS_PER_TASK
    accounts = connector.get_instances_to_update('account')
    while len(accounts) < accounts_per_task:
      sleep(block_interval)
      accounts = connector.get_instances_to_update('account')
      accounts_per_task = max(accounts_per_task / 10, MIN_ACCOUNTS_PER_TASK)
    task_accounts = []
    for account in tqdm(accounts):
      task_accounts.append(account)
      if len(task_accounts) >= accounts_per_task:
        sync_accounts.delay(sys.argv[1], task_accounts)
        task_accounts = []
    if len(task_accounts):
      sync_accounts.delay(sys.argv[1], task_accounts)
