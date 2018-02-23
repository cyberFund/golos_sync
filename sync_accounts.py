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

ACCOUNTS_PER_TASK = 10000

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
    accounts = connector.get_instances_to_update('account')
    task_accounts = []
    for account in tqdm(accounts):
      task_accounts.append(account)
      if len(task_accounts) >= ACCOUNTS_PER_TASK:
        sync_accounts.delay(sys.argv[1], task_accounts)
        task_accounts = []
    if len(task_accounts):
      task_accounts.delay(sys.argv[1], task_accounts)
