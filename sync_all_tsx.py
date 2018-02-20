from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from pprint import pprint
from tqdm import tqdm
import json
import time
import sys
from connectors import MongoConnector
from blocks import create_block

# Golos node params
rpc = SteemNodeRPC("ws://localhost:8090", apis=["follow", "database"])
connector = MongoConnector(database=sys.argv[1])

def process_op(opObj, block, blockid):
    opType = opObj[0]
    op = opObj[1]
    block_object = create_block(blockid, block, opType, op)
    connector.save_block(block_object)

def process_block(block, blockid):
    # save_block(block, blockid)
    # ops = rpc.get_ops_in_block(blockid, False)
    for tx in block['transactions']:
      for opObj in tx['operations']:
        process_op(opObj, block, blockid)
    # for opObj in ops:
    #   process_op(opObj['op'], block, blockid)


# def save_block(block, blockid):
#     doc = block.copy()
#     doc.update({
#         '_id': blockid,
#         'ts': datetime.strptime(doc['timestamp'], "%Y-%m-%dT%H:%M:%S"),
#     })
#     db.block.update({'_id': blockid}, doc, upsert=True)

def sync_all_tsx():
    # Let's find out how often blocks are generated!
    config = rpc.get_config()
    block_interval = config["STEEMIT_BLOCK_INTERVAL"]

    # Last block in the MongoDB
    last_block = connector.find_last_block()
    # ------------
    # For development:
    #
    # If you're looking for a faster way to sync the data and get started,
    # uncomment this line with a more recent block, and the chain will start
    # to sync from that point onwards. Great for a development environment
    # where you want some data but don't want to sync the entire blockchain.
    # ------------
    # last_block = max(13000000, last_block)

    # We are going to loop indefinitely
    while True:

        # Last block in the Golos node
        props = rpc.get_dynamic_global_properties()
        block_number = props['last_irreversible_block_num']

        # Message
        if (block_number - last_block) < 0:
            print('Synchronization from {:>,} to {:>,} blocks'.format(last_block, block_number))
        else:
            print('All blocks are synchronized.')
            print('Last block number in MongoDB: {:>,} in Golos node: {:>,}.'.format(last_block, block_number))

        # Process New Blocks
        tqdm_bar = tqdm(total=block_number-last_block+1)
        while (block_number - last_block) > 0:
            tqdm_bar.update(1)
            # Get full block
            block = rpc.get_block(last_block)
            # Process block
            process_block(block, last_block)
            # Update our block height
            connector.update_last_block(last_block)
            last_block += 1

        tqdm_bar.close()
        pprint("Processed up to Block #" + str(last_block))
        sys.stdout.flush()

        # Sleep for one block
        time.sleep(block_interval)

if __name__ == '__main__':
    sync_all_tsx()
