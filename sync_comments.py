from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from pymongo import MongoClient
from pprint import pprint
import json
import time
import sys
from tqdm import tqdm

# Golos node params
rpc = SteemNodeRPC("ws://localhost:8090", apis=["follow", "database"])
# MongoDB params
mongo = MongoClient()
# Database name in MongoDB
db = mongo.golos_comments


def process_op(opObj, block, blockid):
    opType = opObj[0]
    op = opObj[1]
    if opType == "comment":
        # Update the comment after adding comment
        update_comment(op['author'], op['permlink'])
    if opType == "vote":
        # Update the comment after voting
        update_comment(op['author'], op['permlink'])
    if opType == "author_reward":
        # Update the comment after comment reward
        update_comment(op['author'], op['permlink'])

def save_block(block, blockid):
    doc = block.copy()
    doc.update({
        '_id': blockid,
        '_ts': datetime.strptime(doc['timestamp'], "%Y-%m-%dT%H:%M:%S"),
    })
    db.block.update({'_id': blockid}, doc, upsert=True)


def process_block(block, blockid):
    save_block(block, blockid)
    ops = rpc.get_ops_in_block(blockid, False)
    for tx in block['transactions']:
      for opObj in tx['operations']:
        process_op(opObj, block, blockid)
    for opObj in ops:
      process_op(opObj['op'], block, blockid)


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
def sync_comments():
    # Let's find out how often blocks are generated!
    config = rpc.get_config()
    block_interval = config["STEEMIT_BLOCK_INTERVAL"]

    # Last block in the MongoDB
    init = db.status.find_one({'_id': 'height_comments'})
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
        tqdm_bar = tqdm(total=block_number - last_block + 1)
        while (block_number - last_block) > 0:
            last_block += 1
            tqdm_bar.update(1)
            # Get full block
            block = rpc.get_block(last_block)
            # Process block
            process_block(block, last_block)
            # Update our block height
            db.status.update({'_id': 'height_comments'}, {"$set": {'value': last_block}}, upsert=True)

        tqdm_bar.close()
        pprint("Processed up to Block #" + str(last_block))
        sys.stdout.flush()

        # Sleep for one block
        time.sleep(block_interval)


if __name__ == '__main__':
    sync_comments()
