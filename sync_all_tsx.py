from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from pprint import pprint
from tqdm import tqdm
import json
import time
import sys
from .connectors import MongoConnector
from .blocks import create_block

# Golos node params
rpc = SteemNodeRPC("ws://localhost:8090", apis=["follow", "database"])
connector = MongoConnector(database=sys.argv[1])

def process_op(opObj, block, blockid):
    opType = opObj[0]
    op = opObj[1]
    block = create_block(blockid, opType, op)
    connector.save_block(block)
    save_doc(op, block, blockid, fields_to_id, fields_to_float, opType)

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


def save_convert(op, block, blockid):
    try:
        convert = op.copy()
        _id = str(blockid) + '/' + str(op['requestid'])
        convert.update({
            '_id': _id,
            'ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
            'amount': float(convert['amount'].split()[0]),
            'type': convert['amount'].split()[1]
        })
        db.convert.insert({'_id': _id}, convert)
    except KeyError:
        print("Processing failure. KeyError. {}.".format('Convert'))
        print("Block id: {}".format(blockid))
        print("{}".format(convert))
    except:
        pass


def save_transfer(op, block, blockid):
    try:
        transfer = op.copy()
        _id = str(blockid) + '/' + op['from'] + '/' + op['to']
        transfer.update({
            '_id': _id,
            'ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
            'amount': float(transfer['amount'].split()[0]),
            'type': transfer['amount'].split()[1]
        })
        db.transfer.insert({'_id': _id}, transfer)
    except:
        pass

def save_custom_json(op, block, blockid):
    try:
        data = json.loads(op['json'])
        if type(data) is list:
            if data[0] == 'reblog':
                save_reblog(data, op, block, blockid)
            if data[0] == 'follow':
                save_follow(data, op, block, blockid)
    except ValueError:
        print("Processing failure. ValueError. {}.".format('Custom_json'))
        print("Block id: {}".format(blockid))
        print("{}".format(op))
    except:
        pass

def save_follow(data, op, block, blockid):
    doc = data[1].copy()
    try:
        query = {
            'blockid': blockid,
            'follower': doc['follower'],
            'following': doc['following']
        }
        doc.update({
            'blockid': blockid,
            'ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        })
        db.follow.insert(query, doc)
    except KeyError:
        pprint("Processing failure. KeyError. Save_follow")
        pprint("Block id: {}".format(blockid))
        pprint(doc)
    except:
        pass


def save_reblog(data, op, block, blockid):
    try:
        doc = data[1].copy()
        query = {
            'blockid': blockid,
            'permlink': doc['permlink'],
            'account': doc['account']
        }
        doc.update({
            'blockid': blockid,
            'ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        })
        db.reblog.insert(query, doc)
    except KeyError:
        pprint("Processing failure. KeyError.")
        pprint("Block id: {}".format(blockid))
        pprint(doc)
    except:
        pass


def save_pow(op, block, blockid):
    try:
        if isinstance(op['work'], list):
            _id = str(blockid) + '/' + op['work'][1]['input']['worker_account']
        else:
            _id = str(blockid) + '/' + op['worker_account']
        doc = op.copy()
        doc.update({
            '_id': _id,
            'ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
            'blockid': blockid,
        })
        db.pow.insert({'_id': _id}, doc)
    except:
        pass


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
