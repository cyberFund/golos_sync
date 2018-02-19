def create_block(block_id, operation_type, operation):
  if operation_type in operations_blocks.keys():
    return operations_blocks[operation_type](block_id, operation_type, operation)
  else:
    return OtherBlock(block_id, operation_type, operation)

class Block:
  fields_to_id = []
  fields_to_float = []

  def __init__(block_id, operation_type, operation):
    self.block_id = block_id
    self.operation_type = operation_type
    self.operation = operation.copy()
    self.generate_id()
    self.convert_fields()

  def generate_id():
    _id = str(self.block_id) + ''.join('/' + str(self.operation[item]) for item in self.fields_to_id)
    self.operation.update({"_id": _id})

  def convert_fields():
    for key in self.fields_to_float:
      self.operation[key] = float(self.operation[key].split()[0])

  def to_dict():
    return self.operation

  def get_collection():
    return self.operation_type

class CommentBlock(Block):
  fields_to_id = ['author', 'permlink']

class OtherBlock(Block):
  def __init__(block_id, operation_type, operation):
    super().__init__(block_id, operation_type, operation)
    print('Other operation type: {}'.format(operation_type))
    print('Operation data: {}'.format(operation))

operations_blocks = {
  "comment": CommentBlock,
  # "convert": ConvertBlock,
  # "custom_json": CustomJSONBlock,
  # "pow": PowBlock,
  # "pow2": Pow2Block,
  # "transfer": TransferBlock,
  # "vote": VoteBlock,
  # "account_witness_vote": AccountWitnessVoteBlock,
  # "curation_reward": CurationRewardBlock,
  # "author_reward": AuthorRewardBlock,
  # "transfer_to_vesting": TransferToVestingBlock,
  # "fill_vesting_withdraw": FullVestingWithdrawBlock,
  # "feed_publish": FeedPublishBlock,
  # "account_witness_proxy": AccountWitnessProxyBlock,
  # "account_create": AccountCreateBlock,
  # "witness_update": WitnessUpdateBlock,
  # "comment_options": CommentOptionsBlock,
  # "account_update": AccountUpdateBlock,
  # "withdraw_vesting": WithdrawVestingBlock,
  # "delete_comment": DeleteCommentBlock,
  # "set_withdraw_vesting_route": SetWithdrawVestingRouteBlock,
  # "custom": CustomBlock,
  # "limit_order_create": LimitOrderCreateBlock,
  # "limit_order_create2": LimitOrderCreate2Block,
  # "limit_order_cancel": LimitOrderCancelBlock,
  # "escrow_transfer": EscrowTransferBlock,
  # "escrow_approve": EscrowApproveBlock,
  # "escrow_dispute": EscrowDisputeBlock,
  # "escrow_release": EscrowReleaseBlock,
  # "transfer_to_savings": TransferToSavingsBlock,
  # "transfer_from_savings": TransferFromSavingsBlock,
  # "cancel_transfer_from_savings": CancelTransferFromSavingsBlock,
  # "request_account_recovery": RequestAccountRecoveryBlock,
  # "recover_account": RecoverAccountBlock,
  # "change_recovery_account": ChangeRecoveryAccountBlock,
}