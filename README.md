# Synchronization Golos node to MongoDB

## Synchronization comments
sync_comments.py
## Synchronization all operations
sync_all_tsx.py
## Operations in Golos
- comment
- comment_options
- delete_comment
- vote
- convert
- pow
- pow2
- transfer
- curation_reward
- author_reward
- transfer_to_vesting
- fill_vesting_withdraw
- feed_publish
- account_create
- account_update
- account_witness_proxy
> example: 
```javascript 
{'account': 'penguin-09', 'proxy': 'penguin'}
```
- account_witness_vote
- witness_update
- withdraw_vesting
- set_withdraw_vesting_route
- limit_order_create
- limit_order_create2
- transfer_from_savings
- transfer_to_savings
- custom
- custom_json
- escrow_transfer  
> example: 
```javascript 
{'from': 'xtar', 'sbd_amount': '0.000 GBG', 'json_meta': '', 'escrow_expiration': '2017-02-16T15:04:24', 'steem_amount': '0.001 GOLOS', 'to': 'lisazarova', 'ratification_deadline': '2017-02-16T15:03:24', 'escrow_id': 89083512, 'fee': '0.001 GOLOS', 'agent': 'kosmos'} 
```
- escrow_approve  
> example: 
```javascript 
{'who': 'kosmos', 'from': 'xtar', 'to': 'lisazarova', 'approve': False, 'escrow_id': 89083512, 'agent': 'kosmos'} 
```
- escrow_dispute  
> example: 
```javascript 
{'who': 'xtar', 'from': 'xtar', 'to': 'lisazarova', 'escrow_id': 75654131, 'agent': 'kosmos'} 
```
- escrow_release  
> example: 
```javascript 
{'who': 'on0tole', 'from': 'xtar', 'sbd_amount': '0.000 GBG', 'steem_amount': '0.001 GOLOS', 'to': 'kosmos', 'receiver': 'kosmos', 'escrow_id': 59796593, 'agent': 'on0tole'} 
```
