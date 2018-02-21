from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from connectors import MongoConnector
from pprint import pprint
import json
import time
import sys
from tqdm import tqdm
from comments import UpdatedComment

# Golos node params
rpc = SteemNodeRPC("ws://localhost:8090", apis=["follow", "database"])
connector = MongoConnector(database=sys.argv[1])

def sync_comments():
    comments = connector.get_comments_to_update()
    for comment in comments:
        comment.update(rpc.get_content(comment['author'], comment['permlink']))
        comment_object = UpdatedComment(comment)
        connector.save_comment(comment_object)

if __name__ == '__main__':
    sync_comments()
