from datetime import datetime
from pistonapi.steemnoderpc import SteemNodeRPC
from connectors import MongoConnector
from pprint import pprint
import json
import time
import sys
from tqdm import tqdm
from comments import UpdatedComment
from utils import get_connectors, RestartableTask
from celery import Celery
import click
from time import sleep

MAX_COMMENTS_PER_TASK = 1000
MIN_COMMENTS_PER_TASK = 1

app = Celery('sync_comments', broker='redis://localhost:6379')

@app.task(base=RestartableTask)
def sync_comments(mongo_database, comments):
  rpc, connector = get_connectors(mongo_database)
  for comment in tqdm(comments):
    comment.update(rpc.get_content(comment['author'], comment['permlink']))
    comment_object = UpdatedComment(comment)
    connector.save_instance(comment_object)

@click.command()
@click.option('--connector', help='Type of connector (mongo/elasticsearch).', default='mongo')
@click.option('--database', help='Name of database', default='golos_transactions')
def sync_all_comments(connector, database):
  rpc, connector = get_connectors(database, connector)
  config = rpc.get_config()
  block_interval = config["STEEMIT_BLOCK_INTERVAL"]
  while True:
    comments_per_task = MAX_COMMENTS_PER_TASK
    comments = connector.get_instances_to_update('comment_object')
    while len(comments) < comments_per_task:
      sleep(block_interval)
      comments = connector.get_instances_to_update('comment_object')
      comments_per_task = max(comments_per_task / 10, MIN_COMMENTS_PER_TASK)
    task_comments = []
    for comment in tqdm(comments):
      task_comments.append(comment)
      if len(task_comments) >= comments_per_task:
        sync_comments.delay(database, task_comments)
        connector.update_instances('comment_object', task_comments)
        task_comments = []
    if len(task_comments):
      sync_comments.delay(database, task_comments)
      connector.update_instances('comment_object', task_comments)

if __name__ == '__main__':
  sync_all_comments()
