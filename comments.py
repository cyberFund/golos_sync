from datetime import datetime
import json

class Comment:
  """
    Abstract class that represents comment entities
    created from JSON object received from API
  """
  def __init__(self, comment):
    self.comment = comment
    self.add_base_fields()

  def add_base_fields(self):
    """
      Adds some base fields to a comment object
    """
    _id = self.get_id()
    self.comment.update({
      "_id": _id,
    })

  def get_id(self):
    """
      Returns unique id of an entity
    """
    return self.comment['author'] + '/' + self.comment['permlink']

  def to_dict(self):
    """
      Returns dictionary that represents entity that should be stored
      in a database
    """
    return self.comment

  def use_connector(self, connector):
    """
      Abstract method to do something with the connector after save 
    """
    pass

  def get_collection(self):
    """
      Returns collection where comment should be stored
    """
    return "comment_object"

  def get_query(self):
    """
      Returns unique query to find comment
    """
    return {"_id": self.get_id()}

class ParentComment(Comment):
  """
    Class to pre-save info about parent comment
    in some operations
  """
  pass

class NeedUpdateComment(Comment):
  """
    Class to pre-save partial JSON object 
    in the operation object received from API
  """
  def __init__(self, comment):
    super().__init__(comment)
    comment['need_update'] = True

class UpdatedComment(Comment):
  """
    Class to prepare JSON object received from API
    to transfer to a database.
  """
  def __init__(self, comment):
    super().__init__(comment)
    self.fix_active_votes()
    self.convert_fields()
    self.add_scanned()
    self.remove_need_update()
    self.fix_metadata()

  def fix_metadata(self):
    """
      Removes metadata field from an object
      This method is temporary, will be removed in next releases
    """
    del self.comment['json_metadata']

  def fix_active_votes(self):
    """
      Converts a format of active votes of a comment
    """
    active_votes = []
    for vote in self.comment['active_votes']:
      vote['rshares'] = float(vote['rshares'])
      vote['weight'] = float(vote['weight'])
      vote['time'] = datetime.strptime(vote['time'], "%Y-%m-%dT%H:%M:%S")
      active_votes.append(vote)
    self.comment['active_votes'] = active_votes

  def convert_fields(self):
    """
      Convert fields to their real types
    """
    for key in ['author_reputation', 'net_rshares', 'children_abs_rshares', 'abs_rshares', 'children_rshares2', 'vote_rshares']:
      self.comment[key] = float(self.comment[key])
    for key in ['total_pending_payout_value', 'pending_payout_value', 'max_accepted_payout', 'total_payout_value', 'curator_payout_value']:
      self.comment[key] = float(self.comment[key].split()[0])
    for key in ['active', 'created', 'cashout_time', 'last_payout', 'last_update', 'max_cashout_time']:
      self.comment[key] = datetime.strptime(self.comment[key], "%Y-%m-%dT%H:%M:%S")
    for key in ['json_metadata']:
      try:
        self.comment[key] = json.loads(self.comment[key])
      except ValueError:
        self.comment[key] = self.comment[key]

  def add_scanned(self):
    """
      Adds date of scam
    """
    self.comment['scanned'] = datetime.now()

  def remove_need_update(self):
    """
      Removes need_update flag
    """
    self.comment['need_update'] = False

  def use_connector(self, connector):
    """
      Uses database connector to save parent comment
      if it's exists
    """
    if self.comment['depth'] > 0 and self.comment['url'] != '':
      url = self.comment['url'].split('#')[0]
      parts = url.split('/')
      parent_comment = ParentComment({
        'author': parts[2].replace('@', ''),
        'permlink': parts[3],
        'last_reply': self.comment['created'],
        'last_reply_by': self.comment['author']
      })
      connector.save_instance(parent_comment)
