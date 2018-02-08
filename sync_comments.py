from datetime import datetime, timedelta
from pistonapi.steemnoderpc import SteemNodeRPC
from piston.steem import Post
from pymongo import MongoClient
from pprint import pprint
import collections
import json
import time
import sys
import os
from tqdm import tqdm
# import pistonapi as steemapi

# Golos node params
rpc = SteemNodeRPC("ws://localhost:8090", apis=["follow", "database"])
# MongoDB params
mongo = MongoClient()
# Database name in MongoDB
db = mongo.golos_comments

# Calculated last block
init = db.status.find_one({'_id': 'height'})
if(init):
  last_block = init['value']
else:
  last_block = 1

# ------------
# For development:
#
# If you're looking for a faster way to sync the data and get started,
# uncomment this line with a more recent block, and the chain will start
# to sync from that point onwards. Great for a development environment
# where you want some data but don't want to sync the entire blockchain.
# ------------

# last_block = 5298239

def process_op(opObj, block, blockid):
    opType = opObj[0]
    op = opObj[1]
    if opType == "comment":
        # Update the comment
        update_comment(op['author'], op['permlink'])
    if opType == "vote":
        # Update the comment and vote
        update_comment(op['author'], op['permlink'])
    if opType == "author_reward":
        update_comment(op['author'], op['permlink'])

def save_block(block, blockid):
    doc = block.copy()
    doc.update({
        '_id': blockid,
        '_ts': datetime.strptime(doc['timestamp'], "%Y-%m-%dT%H:%M:%S"),
    })
    db.block.update({'_id': blockid}, doc, upsert=True)
#    db.block_30d.update({'_id': blockid}, doc, upsert=True)


def process_block(block, blockid):
    save_block(block, blockid)
    ops = rpc.get_ops_in_block(blockid, False)
    for tx in block['transactions']:
      for opObj in tx['operations']:
        process_op(opObj, block, blockid)
    for opObj in ops:
      process_op(opObj['op'], block, blockid)

#    queue_update_account(witness_vote['account'])
#    if witness_vote['account'] != witness_vote['witness']:
#        queue_update_account(witness_vote['witness'])


def update_comment(author, permlink):
    _id = author + '/' + permlink
    comment = rpc.get_content(author, permlink).copy()
    comment.update({
        '_id': _id,
    })

    # fix all values on active votes
    active_votes = []
    for vote in comment['active_votes']:
        vote['rshares'] = float(vote['rshares'])
        vote['weight'] = float(vote['weight'])
        vote['time'] = datetime.strptime(vote['time'], "%Y-%m-%dT%H:%M:%S")
        active_votes.append(vote)
    comment['active_votes'] = active_votes

    for key in ['author_reputation', 'net_rshares', 'children_abs_rshares', 'abs_rshares', 'children_rshares2', 'vote_rshares']:
        comment[key] = float(comment[key])
    for key in ['total_pending_payout_value', 'pending_payout_value', 'max_accepted_payout', 'total_payout_value', 'curator_payout_value']:
        comment[key] = float(comment[key].split()[0])
    for key in ['active', 'created', 'cashout_time', 'last_payout', 'last_update', 'max_cashout_time']:
        comment[key] = datetime.strptime(comment[key], "%Y-%m-%dT%H:%M:%S")
    for key in ['json_metadata']:
        try:
          comment[key] = json.loads(comment[key])
        except ValueError:
          comment[key] = comment[key]

    comment['scanned'] = datetime.now()
    results = db.comment.update({'_id': _id}, {'$set': comment}, upsert=True)

    if comment['depth'] > 0 and not results['updatedExisting'] and comment['url'] != '':
        url = comment['url'].split('#')[0]
        parts = url.split('/')
        original_id = parts[2].replace('@', '') + '/' + parts[3]
        db.comment.update(
            {
                '_id': original_id
            },
            {
                '$set': {
                    'last_reply': comment['created'],
                    'last_reply_by': comment['author']
                }
            }
        )

if __name__ == '__main__':
    # Let's find out how often blocks are generated!
    config = rpc.get_config()
    block_interval = config["STEEMIT_BLOCK_INTERVAL"]
    # We are going to loop indefinitely
    while True:

        # # -- Process Queue
        # queue_length = 100
        # # Don't update automatically if it's older than 3 days (let it update when votes occur)
        # max_date = datetime.now() + timedelta(-3)
        # # Don't update if it's been scanned within the six hours
        # scan_ignore = datetime.now() - timedelta(hours=6)
        #
        # # -- Process Queue - Find 100 previous comments to update
        # queue = db.comment.find({
        #     'created': {'$gt': max_date},
        #     'scanned': {'$lt': scan_ignore},
        # }).sort([('scanned', 1)]).limit(queue_length)
        # pprint("[Queue] Comments - " + str(queue_length) + " of " + str(queue.count()))
        # for item in queue:
        #     update_comment(item['author'], item['permlink'])
        #
        # # -- Process Queue - Find 100 comments that have past the last payout and need an update
        # queue = db.comment.find({
        #     'cashout_time': {
        #       '$lt': datetime.now()
        #     },
        #     'mode': {
        #       '$in': ['first_payout', 'second_payout']
        #     },
        #     'depth': 0,
        #     'pending_payout_value': {
        #       '$gt': 0
        #     }
        # }).limit(queue_length)
        # pprint("[Queue] Past Payouts - " + str(queue_length) + " of " + str(queue.count()))
        # for item in tqdm(queue, total=queue_length):
        #     update_comment(item['author'], item['permlink'])

        # Process New Blocks
        props = rpc.get_dynamic_global_properties()
        block_number = props['last_irreversible_block_num']
        while (block_number - last_block) > 0:
            last_block += 1
            # Get full block
            block = rpc.get_block(last_block)
            # Process block
            process_block(block, last_block)
            # Update our block height
            db.status.update({'_id': 'height'}, {"$set" : {'value': last_block}}, upsert=True)
            if last_block % 100 == 0:
                pprint("Processed up to Block #" + str(last_block))

        sys.stdout.flush()

        # Sleep for one block
        time.sleep(block_interval)
