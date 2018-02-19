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

def create_block(operation_type, operation):
  if operation_type in operations_blocks.keys():
    return operations_blocks[operation_type](operation)
  else:
    return OtherBlock(operation)

class Block:
  def __init__(operation):
    pass

  def generate_id():
    pass

  def convert_fields():
    pass

  def to_dict():
    pass

  def get_collection():
    pass

class OtherBlock(Block):
  def __init__(operation):
    super().__init__(operation)
    print('Unsupported operation. Operation data: {}'.format(operation))

class CommentBlock(Block):
  pass