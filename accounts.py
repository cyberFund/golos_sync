from datetime import datetime
import json

class Account:
  """
    Abstract class that represents account entities
    created from JSON object received from API
  """
  def __init__(self, account):
    self.account = account
    self.add_base_fields()

  def add_base_fields(self):
    """
      Adds some base fields to an account object
    """
    _id = self.get_id()
    self.account.update({
      "_id": _id,
    })

  def get_id(self):
    """
      Returns unique id of an entity
    """
    return self.account['name']

  def to_dict(self):
    """
      Returns dictionary that represents entity that should be stored
      in a database
    """
    return self.account

  def use_connector(self, connector):
    """
      Abstract method to do something with the connector before save 
    """
    pass

  def get_collection(self):
    """
      Returns collection where accounts should be stored
    """
    return "account_object"

  def get_query(self):
    """
      Returns unique query to find account
    """
    return {"_id": self.get_id()}

class NeedUpdateAccount(Account):
  """
    Class to pre-save partial JSON object 
    in the operation object received from API
  """
  def __init__(self, account):
    super().__init__(account)
    account['need_update'] = True

class UpdatedAccount(Account):
  """
    Class to prepare JSON object received from API
    to transfer to a database.
  """
  BLACKLIST = ['posting', 'owner', 'active']
  def __init__(self, account):
    super().__init__(account)
    self.set_need_update()
    self.remove_blacklisted_fields()

  def set_need_update(self):
    """
      Resets need_update flag of an account
    """
    account['need_update'] = False

  def remove_blacklisted_fields(self):
    """
      Removes blacklisted fields from JSON object.
      This method is temporary, will be removed in next releases
    """
    for key in self.BLACKLIST:
      if key in account.keys():
        del account[key]

