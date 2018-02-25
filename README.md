# Synchronization Golos node to MongoDB

## Synchronization comments
sync_comments.py
## Synchronization all operations
sync_all_tsx.py
## Operations in Golos
- comment
> example: 
```javascript 
{'parent_permlink': 'ru--konkurs', 
 'json_metadata' : '{\'tags\':[\'ru--konkurs\',\'ru--foto\',\'ru--fotografiya\',\'ru--golos\'],\'image\':[\'http://i.imgur.com/QGuqzox.jpg\'],\'links\':[\'http://i.imgur.com/QGuqzox.jpg\',\'https://golos.io/@antonkostroma\'],\'app\':\'steemit/0.1\',\'format\':\'markdown\'}', 
 'author' : 'antonkostroma', 
 'parent_author' : '', 
 'title' : 'Пост-загадка. Определите стороны света по фотографии. Приз 10 золотых.', 
 'permlink' : 'post-zagadka-opredelite-storony-sveta-po-fotografii-priz-10-zolotykh', 
 'body' : '@@ -468,16 +468,57 @@\n %D0%B8%D1%82%D0%B5 :)%0A%0A\n+### %D0%90%D0%BF%D0%B4. %D0%9E%D1%82 %D0%BE%D0%B4%D0%BD%D0%BE%D0%B3%D0%BE %D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%B0 - %D0%BE%D0%B4%D0%B8%D0%BD %D0%B2%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82%0A\n ________\n'}
```
- comment_options
> example: 
```javascript 
{'allow_curation_rewards': True,
 'allow_votes': True,
 'author': 'natka2',
 'extensions': [],
 'max_accepted_payout': '1000000.000 GBG',
 'percent_steem_dollars': 0,
 'permlink': 'pervyi-den-na-golose-davaite-znakomitsya'}
```
- delete_comment
> example: 
```javascript 
{'author': 'dailis', 
 'permlink': 'testovyi-post'}
```
- vote
> example: 
```javascript 

```
- convert
> example: 
```javascript 

```
- pow
> example: 
```javascript 
{'props': {'account_creation_fee': '0.001 GOLOS', 
           'maximum_block_size': NumberInt(131072), 
           'sbd_interest_rate': NumberInt(1000)}, 
 'work': [NumberInt(0), 
          {'input': {'nonce': '5943031280727640119', 
                     'prev_block': '00000042de39aa258191cec02d446d95e8b61e4a', 
                     'worker_account': 'ij80'}, 
           'pow_summary' : NumberLong(4168836458)}]}
```
- pow2
> example: 
```javascript 

```
- transfer
> example: 
```javascript 

```
- curation_reward
> example: 
```javascript 

```
- author_reward
> example: 
```javascript 

```
- transfer_to_vesting
> example: 
```javascript 

```
- fill_vesting_withdraw
> example: 
```javascript 

```
- feed_publish
> example: 
```javascript 
{'exchange_rate': {'base': '0.050 GBG', 
                   'quote': '1.000 GOLOS'}
```
- account_create
> example: 
```javascript 
{'active': {'account_auths': [],
            'key_auths': [['GLS8hXSmdaLse5w8ThcfYhvcU2M9sZaCtjL4xRbUQVv29XoN5YvYf',
                           1]],
            'weight_threshold': 1},
 'creator': 'golos',
 'fee': '5.000 GOLOS',
 'json_metadata': '{"ico_address":"1P4DB2UnrhFJ9hWhrspeRxNemxEmEsDhGP"}',
 'memo_key': 'GLS7gEX7JCHpst6HGhicyW5bLnfHou41dyNxNHcX1UdQ1yG6KgRg6',
 'new_account_name': 'dailis',
 'owner': {'account_auths': [],
           'key_auths': [['GLS8EJCeNYBqYXXFZWZ2KE3HQQskYS2gH21vV9mhZPQF1unnB7TTs',
                          1]],
           'weight_threshold': 1},
 'posting': {'account_auths': [],
             'key_auths': [['GLS6nozFcpWDPvBbzVMeqwBRoEj1cLZt2Jtn1Couxx2KE222XmSfL',
                            1]],
             'weight_threshold': 1}}
```
- account_update
> example: 
```javascript 
{'account': 'chitty',
 'active': {'account_auths': [],
            'key_auths': [['GLS8htkt7hnbn98oYs9AwE4h4XcVmRkwB86xA3aB9mMHSZ7Uq78KP',
                           1]],
            'weight_threshold': 1},
 'json_metadata': '{}',
 'memo_key': 'GLS6SdvWW4FqmsrLEqkS53dkcaqmTYWX7rUzNQAZSiFwpQaxFMxbT',
 'owner': {'account_auths': [],
           'key_auths': [['GLS6szWbaKgCBGwg5fcYF8PyqcNkXTZJxbbEcGZETP3FJwMiH1bC5',
                          1]],
           'weight_threshold': 1},
 'posting': {'account_auths': [],
             'key_auths': [['GLS5UoyiV2imf3xrVabjCqzbTh5Fn4zwjuD2brJdys9LzJXBY8KH8',
                            1]],
             'weight_threshold': 1}}
```
- account_witness_proxy
> example: 
```javascript 
{'account': 'penguin-09', 
 'proxy': 'penguin'}
```
- account_witness_vote
> example: 
```javascript 

```
- witness_update
> example: 
```javascript 
{'block_signing_key': 'GLS6DpEiFL9wUCcU5i1px32bg3JRfuj6b2cAQJDe6LXEAEau3h4Hu',
 'fee': '0.000 GOLOS',
 'owner': 'dark.sun',
 'props': {'account_creation_fee': '3.000 GOLOS',
           'maximum_block_size': 65536,
           'sbd_interest_rate': 1000},
 'url': 'https://stm/witness-category/@dark.sun'}
```
- withdraw_vesting
> example: 
```javascript 
{'account': 'gliten', 
 'vesting_shares': '50000.000000 GESTS'}
```
- set_withdraw_vesting_route
> example: 
```javascript 

```
- limit_order_create
> example: 
```javascript 

```
- limit_order_create2
> example: 
```javascript 

```
- transfer_from_savings
> example: 
```javascript 

```
- transfer_to_savings
> example: 
```javascript 

```
- custom
> example: 
```javascript 

```
- custom_json
> example: 
```javascript 

```
- escrow_transfer  
> example: 
```javascript 
{'from': 'xtar', 
 'sbd_amount': '0.000 GBG', 
 'json_meta': '', 
 'escrow_expiration': '2017-02-16T15:04:24', 
 'steem_amount': '0.001 GOLOS', 
 'to': 'lisazarova', 
 'ratification_deadline': '2017-02-16T15:03:24', 
 'escrow_id': 89083512, 
 'fee': '0.001 GOLOS', 
 'agent': 'kosmos'} 
```
- escrow_approve  
> example: 
```javascript 
{'who': 'kosmos', 
 'from': 'xtar', 
 'to': 'lisazarova', 
 'approve': False, 
 'escrow_id': 89083512, 
 'agent': 'kosmos'} 
```
- escrow_dispute  
> example: 
```javascript 
{'who': 'xtar', 
 'from': 'xtar', 
 'to': 'lisazarova', 
 'escrow_id': 75654131, 
 'agent': 'kosmos'} 
```
- escrow_release  
> example: 
```javascript 
{'who': 'on0tole', 
 'from': 'xtar', 
 'sbd_amount': '0.000 GBG', 
 'steem_amount': '0.001 GOLOS', 
 'to': 'kosmos', 
 'receiver': 'kosmos', 
 'escrow_id': 59796593, 
 'agent': 'on0tole'} 
```
- reblog
> example: 
```javascript 
{'account': 'christoryan',
 'permlink': 'vydvigaem-pfunk-v-delegaty-golosa', 
 'author': 'pfunk'}
 ```
