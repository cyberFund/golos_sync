from datetime import datetime
import json

class Comment:
  def __init__(self, comment):
    self.comment = comment
    self.add_base_fields()

  def add_base_fields(self):
    _id = self.get_id()
    self.comment.update({
      "_id": _id,
    })

  def get_id(self):
    return self.comment['author'] + '/' + self.comment['permlink']

  def to_dict(self):
    return self.comment

  def use_connector(self, connector):
    pass

  def get_collection(self):
    return "comment_object"

  def get_query(self):
    return {"_id": self.get_id()}

class ParentComment(Comment):
  pass

class NeedUpdateComment(Comment):
  def __init__(self, comment):
    super().__init__(comment)
    comment['need_update'] = True

class UpdatedComment(Comment):
  def __init__(self, comment):
    super().__init__(comment)
    self.fix_active_votes()
    self.convert_fields()
    self.add_scanned()
    self.remove_need_update()

  def fix_active_votes(self):
    active_votes = []
    for vote in self.comment['active_votes']:
      vote['rshares'] = float(vote['rshares'])
      vote['weight'] = float(vote['weight'])
      vote['time'] = datetime.strptime(vote['time'], "%Y-%m-%dT%H:%M:%S")
      active_votes.append(vote)
    self.comment['active_votes'] = active_votes

  def convert_fields(self):
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
    self.comment['scanned'] = datetime.now()

  def remove_need_update(self):
    self.comment['need_update'] = False

  def use_connector(self, connector):
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
