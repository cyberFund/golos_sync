from datetime import datetime
import pdb
import json
from comments import NeedUpdateComment
from accounts import NeedUpdateAccount

def create_block(block_id, block, operation_type, operation):
  """
    Creates operation of a specified type, 
    or OtherBlock, if unknown type specified
  """
  if operation_type in operations_blocks.keys():
    return operations_blocks[operation_type](block_id, block, operation_type, operation)
  else:
    return OtherBlock(block_id, block, operation_type, operation)

class Block:
  """
    Abstract class that represents operations
    created from JSON object received from API
  """
  fields_to_id = []
  fields_to_float = []

  def __init__(self, block_id, block, operation_type, operation):
    self.block_id = block_id
    self.block = block
    self.operation_type = operation_type
    self.operation = operation.copy()
    self.add_base_fields()
    self.convert_fields()

  def add_base_fields(self):
    """
      Adds some base fields to an operation object
    """
    _id = self.get_id()
    timestamp = self.get_timestamp()
    self.operation.update({
      "_id": _id,
      "ts": timestamp,
      "blockid": self.block_id
    })

  def get_timestamp(self):
    """
      Returns block generation timestamp for an operation
    """
    return datetime.strptime(self.block['timestamp'], "%Y-%m-%dT%H:%M:%S")

  def get_id(self):
    """
      Returns unique id of an entity 
    """
    return str(self.block_id) + ''.join('/' + str(self.operation[item]) for item in self.fields_to_id)

  def convert_fields(self):
    """
      Convert fields, that are specified in fields_to_float array,
      to float type
    """
    for key in self.fields_to_float:
      self.operation[key] = float(self.operation[key].split()[0])

  def to_dict(self):
    """
      Returns dictionary that represents entity that should be stored
      in a database
    """
    return self.operation

  def get_collection(self):
    """
      Returns collection where operation should be stored
    """
    return self.operation_type

  def get_query(self):
    """
      Returns unique query to find operation
    """
    return {"_id": self.operation["_id"]}

  def use_connector(self, connector):
    """
      Abstract method to do something with the connector before save 
    """
    pass

class UpdateCommentBlock(Block):
  """
    Abstract class that represents operations that are connected
    with comment modification
  """
  def use_connector(self, connector):
    """
      Pre-save connected comment into a database
    """
    super().use_connector(connector)
    comment = NeedUpdateComment({
      'author': self.operation['author'],
      'permlink': self.operation['permlink']
    })
    connector.save_instance(comment)

class UpdateAuthorBlock(UpdateCommentBlock):
  """
    Abstract class that represents operations that are connected
    with account modification
  """
  def use_connector(self, connector):
    """
      Pre-save connected account into a database
    """
    super().use_connector(connector)
    account = NeedUpdateAccount({
      'name': self.operation['author']
    })
    connector.save_instance(account)

class CommentBlock(UpdateCommentBlock):
  """
    Class to save comment operation
  """
  fields_to_id = ['author', 'permlink']

class ConvertBlock(Block):
  """
    Class to save convert operation
  """
  fields_to_id = ['requestid']

  def convert_fields(self):
    """
      Parses amount field, saves amount as float
      and type as string
    """
    self.operation.update({
      "amount": float(self.operation["amount"].split()[0]),
      "type": self.operation["amount"].split()[1]
    })

class PowBlock(Block):
  """
    Class to save pow and pow2 operations
  """
  fields_to_id = ['worker_account']

  def get_id(self):
    """
      Returns id generated from worker accounts
    """
    if isinstance(self.operation['work'], list):
      return str(self.block_id) + '/' + self.operation['work'][1]['input']['worker_account']
    else:
      return super().get_id()

  def get_collection(self):
    """
      Returns pow collection for either pow or pow2 operations
    """
    return "pow"


class TransferBlock(Block):
  """
    Class to save transfer operations
  """
  fields_to_id = ['from', 'to']

  def convert_fields(self):
    """
      Parses amount field, saves amount as float
      and type as string
    """
    self.operation.update({
      "amount": float(self.operation["amount"].split()[0]),
      "type": self.operation["amount"].split()[1]
    })

class CustomJSONBlock(Block):
  """
    Class to save custom json operations
  """
  def convert_fields(self):
    """
      Parses JSON from given operation object,
      prepares collections and queries depends on it type
      The types are given below:
      - reblog
      - follow
      - other custom_json
    """
    self.data = json.loads(self.operation['json'])
    if type(self.data) is list:
      document = self.data[1].copy()
      document.update({
          'blockid': self.block_id,
          'ts': self.get_timestamp(),
      })
      self.operation = document
      if self.data[0] == 'reblog':
          self.convert_reblog()
      elif self.data[0] == 'follow':
          self.convert_follow()
      else:
          self.convert_custom_json()

  def convert_reblog(self):
    """
      Sets collection and query for reblog operation
    """
    self.collection = "reblog"
    self.query = {
      'blockid': self.block_id,
      'permlink': self.operation['permlink'],
      'account': self.operation['account']
    }

  def convert_follow(self):
    """
      Sets collection and query for follow operation
    """
    self.collection = "follow"
    self.query = {
      'blockid': self.block_id,
      'follower': self.operation['follower'],
      'following': self.operation['following']
    }

  def convert_custom_json(self):
    """
      Sets collection and query for other custom_json operation
    """
    document = self.operation.copy()
    del document['blockid']
    del document['ts']
    self.collection = "custom_json"
    self.query = {
      'blockid': self.block_id,
      'json': json.dumps(document)
    }

  def get_collection(self):
    return self.collection

  def get_query(self):
    return self.query

class VoteBlock(UpdateAuthorBlock):
  """
    Class to save vote operation
  """
  fields_to_id = ['voter', 'author', 'permlink']

class AccountWitnessVoteBlock(Block):
  """
    Class to save account_witness_vote operation
  """
  fields_to_id = ['account', 'witness']

class CurationRewardBlock(Block):
  """
    Class to save curation_reward operation
  """
  fields_to_id = ['curator', 'comment_author', 'comment_permlink']
  fields_to_float = ['reward']

class AuthorRewardBlock(UpdateCommentBlock):
  """
    Class to save author_reward operation
  """
  fields_to_id = ['curator', 'comment_author', 'comment_permlink']
  fields_to_float = ['reward']

class TransferToVestingBlock(Block):
  """
    Class to save transfer_to_vesting operation
  """
  fields_to_id = ['from', 'to']
  fields_to_float = ['amount']

class FillVestingWithdrawBlock(Block):
  """
    Class to save fill_vesting_withdraw operation
  """
  fields_to_id = ['from_account', 'to_account']
  fields_to_float = ['deposited', 'withdrawn']

class FeedPublishBlock(Block):
  """
    Class to save feed_publish operation
  """
  pass

class AccountWitnessProxyBlock(Block):
  """
    Class to save account_witness_proxy operation
  """
  fields_to_id = ['account']

class AccountCreateBlock(Block):
  """
    Class to save account_create operation
  """
  fields_to_id = ['new_account_name']

class WitnessUpdateBlock(Block):
  """
    Class to save witness_update operation
  """
  fields_to_id = ['block_signing_key']

class CommentOptionsBlock(Block):
  """
    Class to save comment_options operation
  """
  fields_to_id = ['author', 'permlink']

class AccountUpdateBlock(Block):
  """
    Class to save account_update operation
  """
  fields_to_id = ['account']

class WithdrawVestingBlock(Block):
  """
    Class to save withdraw_vesting operation
  """
  fields_to_id = ['account']

class DeleteCommentBlock(Block):
  """
    Class to save delete_comment operation
  """
  fields_to_id = ['author', 'permlink']

class SetWithdrawVestingRouteBlock(Block):
  """
    Class to save set_withdraw_vesting_route operation
  """
  fields_to_id = ['from_account', 'to_account']

class CustomBlock(Block):
  """
    Class to save custom operation
  """
  fields_to_id = ['id', 'required_auths']

class LimitOrderCreateBlock(Block):
  """
    Class to save limit_order_create operation
  """
  fields_to_id = ['owner', 'orderid']

class LimitOrderCreate2Block(Block):
  """
    Class to save limit_oreder_create2 operation
  """
  fields_to_id = ['owner', 'orderid']

class LimitOrderCancelBlock(Block):
  """
    Class to save limit_order_cancel operation
  """
  fields_to_id = ['owner', 'orderid']

class EscrowTransferBlock(Block):
  """
    Class to save escrow_transfer operation
  """
  fields_to_id = ['escrow_id', 'from', 'to']

class EscrowApproveBlock(Block):
  """
    Class to save escrow_approve operation
  """
  fields_to_id = ['escrow_id', 'from', 'to']

class EscrowDisputeBlock(Block):
  """
    Class to save escrow_dispute operation
  """
  fields_to_id = ['escrow_id', 'from', 'to']

class EscrowReleaseBlock(Block):
  """
    Class to save escrow_release operation
  """
  fields_to_id = ['escrow_id', 'from', 'to']

class TransferToSavingsBlock(Block):
  """
    Class to save transfer_to_savings operation
  """
  fields_to_id = ['from', 'to', 'amount']

class TransferFromSavingsBlock(Block):
  """
    Class to save transfer_from_savings operation
  """
  fields_to_id = ['request_id', 'from', 'to']

class CancelTransferFromSavingsBlock(Block):
  """
    Class to save cancel_transfer_from_savings operation
  """
  fields_to_id = ['request_id', 'from']

class RequestAccountRecoveryBlock(Block):
  """
    Class to save request_account_recovery operation
  """
  fields_to_id = ['recovery_account', 'account_to_recover']

class RecoverAccountBlock(Block):
  """
    Class to save recover_account operation
  """
  fields_to_id = ['account_to_recover']

class ChangeRecoveryAccountBlock(Block):  
  """
    Class to save change_recovery_account operation
  """
  fields_to_id = ['account_to_recover']  

class VestingDepositBlock(Block):  
  """
    Class to save vesting_deposit operation
  """
  pass

class WithdrawVestingRouteBlock(Block):  
  """
    Class to save withdraw_vesting_route operation
  """
  pass

class WitnessVoteBlock(Block):  
  """
    Class to save witness_vote operation
  """
  pass

class OtherBlock(Block):
  """
    Class to save operation with unknown type
  """
  def __init__(self, block_id, block, operation_type, operation):
    super().__init__(block_id, block, operation_type, operation)
    print('Other operation type: {}'.format(operation_type))
    print('Operation data: {}'.format(operation))

operations_blocks = {
  "comment": CommentBlock,
  "convert": ConvertBlock,
  "custom_json": CustomJSONBlock,
  "pow": PowBlock,
  "pow2": PowBlock,
  "transfer": TransferBlock,
  "vote": VoteBlock,
  "account_witness_vote": AccountWitnessVoteBlock,
  "curation_reward": CurationRewardBlock,
  "author_reward": AuthorRewardBlock,
  "transfer_to_vesting": TransferToVestingBlock,
  "fill_vesting_withdraw": FillVestingWithdrawBlock,
  "feed_publish": FeedPublishBlock,
  "account_witness_proxy": AccountWitnessProxyBlock,
  "account_create": AccountCreateBlock,
  "witness_update": WitnessUpdateBlock,
  "comment_options": CommentOptionsBlock,
  "account_update": AccountUpdateBlock,
  "withdraw_vesting": WithdrawVestingBlock,
  "delete_comment": DeleteCommentBlock,
  "set_withdraw_vesting_route": SetWithdrawVestingRouteBlock,
  "custom": CustomBlock,
  "limit_order_create": LimitOrderCreateBlock,
  "limit_order_create2": LimitOrderCreate2Block,
  "limit_order_cancel": LimitOrderCancelBlock,
  "escrow_transfer": EscrowTransferBlock,
  "escrow_approve": EscrowApproveBlock,
  "escrow_dispute": EscrowDisputeBlock,
  "escrow_release": EscrowReleaseBlock,
  "transfer_to_savings": TransferToSavingsBlock,
  "transfer_from_savings": TransferFromSavingsBlock,
  "cancel_transfer_from_savings": CancelTransferFromSavingsBlock,
  "request_account_recovery": RequestAccountRecoveryBlock,
  "recover_account": RecoverAccountBlock,
  "change_recovery_account": ChangeRecoveryAccountBlock,
  'vesting_deposit': VestingDepositBlock,
  'withdraw_vesting_route': WithdrawVestingRouteBlock,
  'witness_vote': WitnessVoteBlock
}
