from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from pprint import pprint
from tqdm import tqdm
import json
import time
import sys
from connectors import MongoConnector
from blocks import create_block
import numpy as np
from celery import Celery
from time import sleep

BLOCKS_PER_TASK = 1000

rpc = SteemNodeRPC("ws://localhost:8090", apis=["follow", "database"])
connector = MongoConnector(database=sys.argv[1])
app = Celery('sync_all_tsx', broker='redis://localhost:6379')

def process_op(opObj, block, blockid):
  opType = opObj[0]
  op = opObj[1]
  block_object = create_block(blockid, block, opType, op)
  connector.save_block(block_object)

def process_block(block, blockid):
  for tx in block['transactions']:
    for opObj in tx['operations']:
      process_op(opObj, block, blockid)

@app.task
def sync_tsx(blocks):
  for block_number in tqdm(blocks):
    block = rpc.get_block(block_number)
    process_block(block, block_number)
  sys.stdout.flush()

if __name__ == '__main__':
  config = rpc.get_config()
  block_interval = config["STEEMIT_BLOCK_INTERVAL"]
  last_block = connector.find_last_block()
  current_block = last_block
  while True:
    while current_block - last_block < BLOCKS_PER_TASK:
      sleep(block_interval)
      props = rpc.get_dynamic_global_properties()
      current_block = props['last_irreversible_block_num']

    new_blocks = list(range(last_block, current_block))
    for chunk in tqdm(np.array_split(new_blocks, round((current_block - last_block) / BLOCKS_PER_TASK))):
      sync_tsx.delay(chunk.tolist())
    connector.update_last_block(current_block)
    last_block = current_block
