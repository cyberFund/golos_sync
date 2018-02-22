from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from connectors import MongoConnector
from pprint import pprint
import json
import time
import sys
from tqdm import tqdm
from comments import UpdatedComment
from utils import get_connectors

COMMENTS_PER_TASK = 1000
app = Celery('sync_comments', broker='redis://localhost:6379')

@app.task
def sync_comments(mongo_database, comments):
  rpc, connector = get_connectors(mongo_database)
  for comment in tqdm(comments):
    comment.update(rpc.get_content(comment['author'], comment['permlink']))
    comment_object = UpdatedComment(comment)
    connector.save_comment(comment_object)

if __name__ == '__main__':
  rpc, connector = get_connectors(sys.argv[1])
  config = rpc.get_config()
  block_interval = config["STEEMIT_BLOCK_INTERVAL"]
  while True:
    comments = connector.get_comments_to_update()
    task_comments = []
    for comment in comments:
      task_comments.append(comment)
      if len(task_comments) >= COMMENTS_PER_TASK:
        sync_comments.delay(sys.argv[1], task_comments)
        task_comments = []
    if len(task_comments):
      sync_comments.delay(sys.argv[1], task_comments)
