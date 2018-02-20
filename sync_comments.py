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

def sync_comments():
    # TODO
    # Get all comments with flag
    # For each comment: 
        # Get rpc
        # Create and save comment object


if __name__ == '__main__':
    sync_comments()
