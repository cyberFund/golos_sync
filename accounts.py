from datetime import datetime
import json

class Account:
  def __init__(self, account):
    self.account = account
    self.add_base_fields()

  def add_base_fields(self):
    _id = self.get_id()
    self.account.update({
      "_id": _id,
    })

  def get_id(self):
    return self.account['name']

  def to_dict(self):
    return self.account

  def use_connector(self, connector):
    pass

  def get_collection(self):
    return "account_object"

  def get_query(self):
    return {"_id": self.get_id()}

class NeedUpdateAccount(Account):
  def __init__(self, account):
    super().__init__(account)
    account['need_update'] = True

class UpdatedAccount(Account):
  def __init__(self, account):
    super().__init__(account)
    account['need_update'] = False
