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
db = mongo.golos_all_tsx


def process_op(opObj, block, blockid):
    opType = opObj[0]
    op = opObj[1]
    if opType == "comment":
        # Update the comment
        # update_comment(op['author'], op['permlink'])
        save_comment(op, block, blockid)
    elif opType == "vote":
        save_vote(op, block, blockid)
    elif opType =="convert":
        save_convert(op, block, blockid)
    elif opType == "custom_json":
        save_custom_json(op, block, blockid)
    elif opType == "account_witness_vote":
        save_witness_vote(op, block, blockid)
        update_witness_vote(op, block, blockid)
    elif opType == "pow" or opType == "pow2":
        save_pow(op, block, blockid)
    elif opType == "transfer":
        save_transfer(op, block, blockid)
    elif opType == "curation_reward":
        save_curation_reward(op, block, blockid)
    elif opType == "author_reward":
        save_author_reward(op, block, blockid)
    elif opType == "transfer_to_vesting":
        save_vesting_deposit(op, block, blockid)
    elif opType == "fill_vesting_withdraw":
        save_vesting_withdraw(op, block, blockid)
    elif opType == "feed_publish":
        save_feed_publish(op, block, blockid)
    elif opType == "account_witness_proxy":
        save_account_witness_proxy(op, block, blockid)
    elif opType == "account_create":
        save_account_create(op, block, blockid)
    elif opType == "witness_update":
        save_witness_update(op, block, blockid)
    elif opType == "comment_options":
        save_comment_options(op, block, blockid)
    elif opType == "account_update":
        save_account_update(op, block, blockid)
    elif opType == "withdraw_vesting":
        save_withdraw_vesting(op, block, blockid)
    elif opType == "delete_comment":
        save_delete_comment(op, block, blockid)
    elif opType == "set_withdraw_vesting_route":
        save_withdraw_vesting_route(op, block, blockid)
    elif opType == "custom":
        save_custom(op, block, blockid)
    elif opType == "limit_order_create":
        save_limit_order_create(op, block, blockid)
    else:
        print('Other opType: {}'.format(opType))
        print('op data: {}'.format(op))

def process_block(block, blockid):
    save_block(block, blockid)
    ops = rpc.get_ops_in_block(blockid, False)
    for tx in block['transactions']:
      for opObj in tx['operations']:
        process_op(opObj, block, blockid)
    for opObj in ops:
      process_op(opObj['op'], block, blockid)


def save_convert(op, block, blockid):
    try:
        convert = op.copy()
        _id = str(blockid) + '/' + str(op['requestid'])
        convert.update({
            '_id': _id,
            '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
            'amount': float(convert['amount'].split()[0]),
            'type': convert['amount'].split()[1]
        })
        db.convert.update({'_id': _id}, convert, upsert=True)
    except KeyError:
        pprint("Processing failure. KeyError. {}.".format('Convert'))
        pprint("Block id: {}".format(blockid))


def save_transfer(op, block, blockid):
    transfer = op.copy()
    _id = str(blockid) + '/' + op['from'] + '/' + op['to']
    transfer.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        'amount': float(transfer['amount'].split()[0]),
        'type': transfer['amount'].split()[1]
    })
    db.transfer.update({'_id': _id}, transfer, upsert=True)


def save_curation_reward(op, block, blockid):
    reward = op.copy()
    _id = str(blockid) + '/' + op['curator'] + '/' + op['comment_author'] + '/' + op['comment_permlink']
    reward.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        'reward': float(reward['reward'].split()[0])
    })
    db.curation_reward.update({'_id': _id}, reward, upsert=True)


def save_author_reward(op, block, blockid):
    reward = op.copy()
    _id = str(blockid) + '/' + op['author'] + '/' + op['permlink']
    reward.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    for key in ['sbd_payout', 'steem_payout', 'vesting_payout']:
        reward[key] = float(reward[key].split()[0])
    db.author_reward.update({'_id': _id}, reward, upsert=True)


def save_vesting_deposit(op, block, blockid):
    vesting = op.copy()
    _id = str(blockid) + '/' + op['from'] + '/' + op['to']
    vesting.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        'amount': float(vesting['amount'].split()[0])
    })
    db.vesting_deposit.update({'_id': _id}, vesting, upsert=True)


def save_vesting_withdraw(op, block, blockid):
    vesting = op.copy()
    _id = str(blockid) + '/' + op['from_account'] + '/' + op['to_account']
    vesting.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    for key in ['deposited', 'withdrawn']:
        vesting[key] = float(vesting[key].split()[0])
    db.vesting_withdraw.update({'_id': _id}, vesting, upsert=True)


def save_withdraw_vesting_route(op, block, blockid):
    withdraw_vesting_route = op.copy()
    _id = str(blockid) + '/' + op['from_account'] + '/' + op['to_account']
    withdraw_vesting_route.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.withdraw_vesting_route.update({'_id': _id}, withdraw_vesting_route, upsert=True)


def save_custom(op, block, blockid):
    custom = op.copy()
    _id = str(blockid) + '/' + op['id'] + '/' + op['required_auths']
    custom.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.custom.update({'_id': _id}, custom, upsert=True)

def save_custom_json(op, block, blockid):
    try:
        data = json.loads(op['json'])
        if type(data) is list:
            if data[0] == 'reblog':
                save_reblog(data, op, block, blockid)
            if data[0] == 'follow':
                save_follow(data, op, block, blockid)
    except ValueError:
        pprint("Processing failure")
        pprint(blockid)
        pprint(op['json'])

def save_follow(data, op, block, blockid):
    doc = data[1].copy()
    try:
        query = {
            '_block': blockid,
            'follower': doc['follower'],
            'following': doc['following']
        }
        doc.update({
            '_block': blockid,
            '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        })
        db.follow.update(query, doc, upsert=True)
    except KeyError:
        pprint("Processing failure. KeyError. save_follow")
        pprint("Block id: {}".format(blockid))
        pprint(doc)


def save_reblog(data, op, block, blockid):
    try:
        doc = data[1].copy()
        query = {
            '_block': blockid,
            'permlink': doc['permlink'],
            'account': doc['account']
        }
        doc.update({
            '_block': blockid,
            '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        })
        db.reblog.update(query, doc, upsert=True)
    except KeyError:
        pprint("Processing failure. KeyError.")
        pprint("Block id: {}".format(blockid))
        pprint(doc)


def save_block(block, blockid):
    doc = block.copy()
    doc.update({
        '_id': blockid,
        '_ts': datetime.strptime(doc['timestamp'], "%Y-%m-%dT%H:%M:%S"),
    })
    db.block.update({'_id': blockid}, doc, upsert=True)


def save_pow(op, block, blockid):
    _id = "unknown"
    if isinstance(op['work'], list):
        _id = str(blockid) + '/' + op['work'][1]['input']['worker_account']
    else:
        _id = str(blockid) + '/' + op['worker_account']
    doc = op.copy()
    doc.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        'block': blockid,
    })
    db.pow.update({'_id': _id}, doc, upsert=True)


def save_vote(op, block, blockid):
    vote = op.copy()
    _id = str(blockid) + '/' + op['voter'] + '/' + op['author'] + '/' + op['permlink']
    vote.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.vote.update({'_id': _id}, vote, upsert=True)


def save_feed_publish(op, block, blockid):
    feed_publish = op.copy()
    _id = str(blockid)
    feed_publish.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.feed_publish.update({'_id': _id}, feed_publish, upsert=True)


def save_witness_vote(op, block, blockid):
    witness_vote = op.copy()
    _id = str(blockid) + '/' + witness_vote['account'] + '/' + witness_vote['witness']
    witness_vote.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        '_blockid': blockid
    })
    db.witness_vote.update({'_id': _id}, witness_vote, upsert=True)


def update_witness_vote(op, block, blockid):
    witness_vote = op.copy()
    query = {
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        'account': witness_vote['account'],
        'witness': witness_vote['witness']
    }
    witness_vote.update({
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S"),
        '_blockid': blockid
    })
    db.witness_vote_current.update(query, witness_vote, upsert=True)


def save_account_witness_proxy(op, block, blockid):
    account_witness_proxy = op.copy()
    _id = str(blockid) + '/' + account_witness_proxy['account']
    account_witness_proxy.update({
        '_id': _id,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.account_witness_proxy.update({'_id': _id}, account_witness_proxy, upsert=True)


def save_account_create(op, block, blockid):
    account_create = op.copy()
    _id = account_create['new_account_name']
    account_create.update({
        '_id': _id,
        '_blockid': blockid,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.account.update({'_id': _id}, account_create, upsert=True)


def save_witness_update(op, block, blockid):
    witness_update = op.copy()
    _id = str(blockid) + '/' + str(witness_update['block_signing_key'])
    witness_update.update({
        '_id': _id,
        '_blockid': blockid,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.witness_update.update({'_id': _id}, witness_update, upsert=True)


def save_comment_options(op, block, blockid):
    comment_options = op.copy()
    _id = str(blockid) + '/' + comment_options['author'] + '/' + comment_options['permlink']
    comment_options.update({
        '_id': _id,
        '_blockid': blockid,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.comment_options.update({'_id': _id}, comment_options, upsert=True)


def save_account_update(op, block, blockid):
    account_update = op.copy()
    _id = str(blockid) + '/' + account_update['account']
    account_update.update({
        '_id': _id,
        '_blockid': blockid,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.account_update.update({'_id': _id}, account_update, upsert=True)


def save_withdraw_vesting(op, block, blockid):
    withdraw_vesting = op.copy()
    _id = str(blockid) + '/' + withdraw_vesting['account']
    withdraw_vesting.update({
        '_id': _id,
        '_blockid': blockid,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.withdraw_vesting.update({'_id': _id}, withdraw_vesting, upsert=True)


def save_limit_order_create(op, block, blockid):
    limit_order_create = op.copy()
    _id = str(blockid) + '/' + limit_order_create['owner'] + '/' + limit_order_create['orderid']
    limit_order_create.update({
        '_id': _id,
        '_blockid': blockid,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.limit_order_create.update({'_id': _id}, limit_order_create, upsert=True)



def save_delete_comment(op, block, blockid):
    delete_comment = op.copy()
    _id = str(blockid) + '/' + delete_comment['author'] + '/' + delete_comment['permlink']
    delete_comment.update({
        '_id': _id,
        '_blockid': blockid,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.delete_comment.update({'_id': _id}, delete_comment, upsert=True)


def save_comment(op, block, blockid):
    _id = op['author'] + '/' + op['permlink']
    comment = op.copy()
    comment.update({
        '_id': _id,
        '_blockid': blockid,
        '_ts': datetime.strptime(block['timestamp'], "%Y-%m-%dT%H:%M:%S")
    })
    db.comment.update({'_id': _id}, {'$set': comment}, upsert=True)


def sync_all_tsx():
    # Let's find out how often blocks are generated!
    config = rpc.get_config()
    block_interval = config["STEEMIT_BLOCK_INTERVAL"]

    # Last block in the MongoDB
    init = db.status.find_one({'_id': 'height'})
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
    # last_block = 13,000,000

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
