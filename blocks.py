from datetime import datetime
import pdb
import json
from comments import NeedUpdateComment
from accounts import NeedUpdateAccount

def create_block(block_id, block, operation_type, operation):
  if operation_type in operations_blocks.keys():
    return operations_blocks[operation_type](block_id, block, operation_type, operation)
  else:
    return OtherBlock(block_id, block, operation_type, operation)

class Block:
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
    _id = self.get_id()
    timestamp = self.get_timestamp()
    self.operation.update({
      "_id": _id,
      "ts": timestamp,
      "blockid": self.block_id
    })

  def get_timestamp(self):
    return datetime.strptime(self.block['timestamp'], "%Y-%m-%dT%H:%M:%S")

  def get_id(self):
    return str(self.block_id) + ''.join('/' + str(self.operation[item]) for item in self.fields_to_id)

  def convert_fields(self):
    for key in self.fields_to_float:
      self.operation[key] = float(self.operation[key].split()[0])

  def to_dict(self):
    return self.operation

  def get_collection(self):
    return self.operation_type

  def get_query(self):
    return {"_id": self.operation["_id"]}

  def use_connector(self, connector):
    pass

class UpdateCommentBlock(Block):
  def use_connector(self, connector):
    super().use_connector(connector)
    comment = NeedUpdateComment({
      'author': self.operation['author'],
      'permlink': self.operation['permlink']
    })
    connector.save_instance(comment)

class UpdateAuthorBlock(UpdateCommentBlock):
  def use_connector(self, connector):
    super().use_connector(connector)
    account = NeedUpdateAccount({
      'name': self.operation['author']
    })
    connector.save_instance(account)

class CommentBlock(UpdateCommentBlock):
  fields_to_id = ['author', 'permlink']

class ConvertBlock(Block):
  fields_to_id = ['requestid']

  def convert_fields(self):
    self.operation.update({
      "amount": float(self.operation["amount"].split()[0]),
      "type": self.operation["amount"].split()[1]
    })

class PowBlock(Block):
  fields_to_id = ['worker_account']

  def get_id(self):
    if isinstance(self.operation['work'], list):
      return str(self.block_id) + '/' + self.operation['work'][1]['input']['worker_account']
    else:
      return super().get_id()

  def get_collection(self):
    return "pow"


class TransferBlock(Block):
  fields_to_id = ['from', 'to']

  def convert_fields(self):
    self.operation.update({
      "amount": float(self.operation["amount"].split()[0]),
      "type": self.operation["amount"].split()[1]
    })

class CustomJSONBlock(Block):
  def convert_fields(self):
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
      if self.data[0] == 'follow':
          self.convert_follow()

  def convert_reblog(self):
    self.collection = "reblog"
    self.query = {
      'blockid': self.block_id,
      'permlink': self.operation['permlink'],
      'account': self.operation['account']
    }

  def convert_follow(self):
    self.collection = "follow"
    self.query = {
      'blockid': self.block_id,
      'follower': self.operation['follower'],
      'following': self.operation['following']
    }

  def get_collection(self):
    return self.collection

  def get_query(self):
    return self.query

class VoteBlock(UpdateAuthorBlock):
  fields_to_id = ['voter', 'author', 'permlink']

class AccountWitnessVoteBlock(Block):
  fields_to_id = ['account', 'witness']

class CurationRewardBlock(Block):
  fields_to_id = ['curator', 'comment_author', 'comment_permlink']
  fields_to_float = ['reward']

class AuthorRewardBlock(UpdateCommentBlock):
  fields_to_id = ['curator', 'comment_author', 'comment_permlink']
  fields_to_float = ['reward']

class TransferToVestingBlock(Block):
  fields_to_id = ['from', 'to']
  fields_to_float = ['amount']

class FillVestingWithdrawBlock(Block):
  fields_to_id = ['from_account', 'to_account']
  fields_to_float = ['deposited', 'withdrawn']

class FeedPublishBlock(Block):
  pass

class AccountWitnessProxyBlock(Block):
  fields_to_id = ['account']

class AccountCreateBlock(Block):
  fields_to_id = ['new_account_name']

class WitnessUpdateBlock(Block):
  fields_to_id = ['block_signing_key']

class CommentOptionsBlock(Block):
  fields_to_id = ['author', 'permlink']

class AccountUpdateBlock(Block):
  fields_to_id = ['account']

class WithdrawVestingBlock(Block):
  fields_to_id = ['account']

class DeleteCommentBlock(Block):
  fields_to_id = ['author', 'permlink']

class SetWithdrawVestingRouteBlock(Block):
  fields_to_id = ['from_account', 'to_account']

class CustomBlock(Block):
  fields_to_id = ['id', 'required_auths']

class LimitOrderCreateBlock(Block):
  fields_to_id = ['owner', 'orderid']

class LimitOrderCreate2Block(Block):
  fields_to_id = ['owner', 'orderid']

class LimitOrderCancelBlock(Block):
  fields_to_id = ['owner', 'orderid']

class EscrowTransferBlock(Block):
  fields_to_id = ['escrow_id', 'from', 'to']

class EscrowApproveBlock(Block):
  fields_to_id = ['escrow_id', 'from', 'to']

class EscrowDisputeBlock(Block):
  fields_to_id = ['escrow_id', 'from', 'to']

class EscrowReleaseBlock(Block):
  fields_to_id = ['escrow_id', 'from', 'to']

class TransferToSavingsBlock(Block):
  fields_to_id = ['from', 'to', 'amount']

class TransferFromSavingsBlock(Block):
  fields_to_id = ['request_id', 'from', 'to']

class CancelTransferFromSavingsBlock(Block):
  fields_to_id = ['request_id', 'from']

class RequestAccountRecoveryBlock(Block):
  fields_to_id = ['recovery_account', 'account_to_recover']

class RecoverAccountBlock(Block):
  fields_to_id = ['account_to_recover']

class ChangeRecoveryAccountBlock(Block):  
  fields_to_id = ['account_to_recover']  

class OtherBlock(Block):
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
}
