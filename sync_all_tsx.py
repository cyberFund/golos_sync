from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from pymongo import MongoClient
from pprint import pprint
from tqdm import tqdm
import json
import time
import sys


# Golos node params
rpc = SteemNodeRPC("ws://localhost:8090", apis=["follow", "database"])
# MongoDB params
mongo = MongoClient()
# Database name in MongoDB
db = mongo[sys.argv[1]]


def process_op(opObj, block, blockid):
    opType = opObj[0]
    op = opObj[1]
    fields_to_float = []
    if opType == "comment":
        fields_to_id = ['author', 'permlink']
    elif opType =="convert":
        # fields_to_id = ['requestid']
        # fields_to_float = ['amount']
        save_convert(op, block, blockid)
        return 1
    elif opType == "custom_json":
        # fields_to_id = []
        save_custom_json(op, block, blockid)
        return 1
    elif opType == "pow" or opType == "pow2":
        # fields_to_id = []
        save_pow(op, block, blockid)
        return 1
    elif opType == "transfer":
        # fields_to_id = ['from', 'to']
        # fields_to_float = ['amount']
        save_transfer(op, block, blockid)
        return 1
    elif opType == "vote":
        fields_to_id = ['voter', 'author', 'permlink']
    elif opType == "account_witness_vote":
        fields_to_id = ['account', 'witness']
    elif opType == "curation_reward":
        fields_to_id = ['curator', 'comment_author', 'comment_permlink']
        fields_to_float = ['reward']
    elif opType == "author_reward":
        fields_to_id = ['author', 'permlink']
        fields_to_float = ['sbd_payout', 'steem_payout', 'vesting_payout']
    elif opType == "transfer_to_vesting":
        fields_to_id = ['from', 'to']
        fields_to_float = ['amount']
    elif opType == "fill_vesting_withdraw":
        fields_to_id = ['from_account', 'to_account']
        fields_to_float = ['deposited', 'withdrawn']
    elif opType == "feed_publish":
        fields_to_id = []
    elif opType == "account_witness_proxy":
        fields_to_id = ['account']
    elif opType == "account_create":
        fields_to_id = ['new_account_name']
    elif opType == "witness_update":
        fields_to_id = ['block_signing_key']
    elif opType == "comment_options":
        fields_to_id = ['author', 'permlink']
    elif opType == "account_update":
        fields_to_id = ['account']
    elif opType == "withdraw_vesting":
        fields_to_id = ['account']
    elif opType == "delete_comment":
        fields_to_id = ['author', 'permlink']
    elif opType == "set_withdraw_vesting_route":
        fields_to_id = ['from_account', 'to_account']
    elif opType == "custom":
        fields_to_id = ['id', 'required_auths']
    elif opType == "limit_order_create":
        fields_to_id = ['owner', 'orderid']
    elif opType == "limit_order_create2":
        fields_to_id = ['owner', 'orderid']
    elif opType == "limit_order_cancel":
        fields_to_id = ['owner', 'orderid']
    elif opType == "escrow_transfer":
        fields_to_id = ['escrow_id', 'from', 'to']
    elif opType == "escrow_approve":
        fields_to_id = ['escrow_id', 'from', 'to']
    elif opType == "escrow_dispute":
        fields_to_id = ['escrow_id', 'from', 'to']
    elif opType == "escrow_release":
        fields_to_id = ['escrow_id', 'from', 'to']
    elif opType == "transfer_to_savings":
        fields_to_id = ['from', 'to', 'amount']
    elif opType == "transfer_from_savings":
        fields_to_id = ['request_id', 'from', 'to']
    elif opType == "cancel_transfer_from_savings":
        fields_to_id = ['request_id', 'from']
    elif opType == "request_account_recovery":
        fields_to_id = ['recovery_account', 'account_to_recover']
    elif opType == "recover_account":
        fields_to_id = ['account_to_recover']
    elif opType == "change_recovery_account":
        fields_to_id = ['account_to_recover']

    else:
        print('Other opType: {}'.format(opType))
        print('op data: {}'.format(op))
        return 1
    save_doc(op, block, blockid, fields_to_id, fields_to_float, opType)

def save_doc(op, block, blockid, fields_to_id, fields_to_float, name_doc):
    try:
        op_to_save = op.copy()
        _id = str(blockid) + ''.join('/' + str(op_to_save[item]) for item in fields_to_id)
        op_to_save.update({
            '_id': _id,
            'blockid': blockid,
            'ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
        })
        for key in fields_to_float:
            op_to_save[key] = float(op_to_save[key].split()[0])
        db[name_doc].update({'_id': _id}, op_to_save, upsert=True)
    except KeyError:
        print("Processing failure. KeyError. {}.".format(name_doc))
        print("Block id: {}".format(blockid))
        print("{}".format(op))
    except ValueError:
        print("Processing failure. ValueError. {}.".format(name_doc))
        print("Block id: {}".format(blockid))
        print("{}".format(op))


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
        db.convert.update({'_id': _id}, convert, upsert=True)
    except KeyError:
        print("Processing failure. KeyError. {}.".format('Convert'))
        print("Block id: {}".format(blockid))
        print("{}".format(convert))


def save_transfer(op, block, blockid):
    transfer = op.copy()
    _id = str(blockid) + '/' + op['from'] + '/' + op['to']
    transfer.update({
        '_id': _id,
        'ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        'amount': float(transfer['amount'].split()[0]),
        'type': transfer['amount'].split()[1]
    })
    db.transfer.update({'_id': _id}, transfer, upsert=True)


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
        db.follow.update(query, doc, upsert=True)
    except KeyError:
        pprint("Processing failure. KeyError. Save_follow")
        pprint("Block id: {}".format(blockid))
        pprint(doc)


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
        db.reblog.update(query, doc, upsert=True)
    except KeyError:
        pprint("Processing failure. KeyError.")
        pprint("Block id: {}".format(blockid))
        pprint(doc)


def save_pow(op, block, blockid):
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
    db.pow.update({'_id': _id}, doc, upsert=True)


def sync_all_tsx():
    # Let's find out how often blocks are generated!
    config = rpc.get_config()
    block_interval = config["STEEMIT_BLOCK_INTERVAL"]

    # Last block in the MongoDB
    init = db.status.find_one({'_id': 'height_all_tsx'})
    last_block = 1
    if (init):
        last_block = init['value']
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
            db.status.update({'_id': 'height_all_tsx'}, {"$set": {'value': last_block}}, upsert=True)
            last_block += 1

        tqdm_bar.close()
        pprint("Processed up to Block #" + str(last_block))
        sys.stdout.flush()

        # Sleep for one block
        time.sleep(block_interval)

if __name__ == '__main__':
    sync_all_tsx()
