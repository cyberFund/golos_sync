# Synchronization Golos node to MongoDB
## How to use
Add tasks to synchronize golos operations
```bash
$ sync_all_tsx.py --database DATABASE --connector mongo/elasticsearch
```
Add tasks to synchronize golos comments
```bash
$ sync_comments.py --database DATABASE --connector mongo/elasticsearch
```
Add tasks to synchronize golos accounts
```bash
$ sync_accounts.py --database DATABASE --connector mongo/elasticsearch
```
Run celery workers
```bash
$ celery -A sync_all_tsx worker
$ celery -A sync_comments worker
$ celery -A sync_accounts worker
```
## Watch everything
```bash
$ celery flower
```
## Block structure
> example: 
```javascript 
{'timestamp': '2017-03-06T13:43:57', 
 'transaction_merkle_root': '99b38ce3abff295700ab58b79e83c7ec9ca57f71', 
 'transactions': [{'operations': [['vote', 
                                   {'weight': NumberInt(10000), 
                                    'permlink': 'tashkent-glazami-moskvicha-den-2', 
                                    'voter': 'belkino', 
                                    'author': 'shchukinvlad'}]], 
                   'signatures': ['1f5f0d8f2654714716238ee8c5746bbc51488448d9a2fa81c265ef398d1114de9c2efb8dd355fbf6d437ff4d190df9a6b49b7edc68a5d8156938e3ef7cdaa0fab4'], 
                   'expiration': '2017-03-06T13:44:09', 
                   'ref_block_prefix': NumberInt(765597399), 
                   'ref_block_num': NumberInt(2327), 
                   'extensions': []}, 
                  {'operations': [['comment', 
                                   {'parent_permlink': 'ru--debaty', 
                                    'json_metadata': '{\'tags\':[\'ru--debaty\'],\'app\':\'steemit/0.1\',\'format\':\'html\'}', 
                                    'author': 'redhat', 
                                    'parent_author': '', 
                                    'title': 'Пусть @hipster меня флагует, но правда дороже.', 
                                    'permlink': 'pust-hipster-menya-flaguet-no-pravda-dorozhe', 
                                    'body': '<html>\n<p>ICO голоса началось 15.10.2016 при курсе 638$ за 1 биткойн.</p>\n<p>Сегодня 1 биткойн стоит 1271$, т.е. доходность составляет 49,8%</p>\n<p>На 1 биткойн на ICO по цене 0,000022 можно было приобрести 45454 токенов.</p>\n<p>Сегодня вы их сможете продать 0,00001825 и выручить 0,83 биткойна, отрицательная доходность - 17%</p>\n<p>Поскольку суточный объем торгов 0,65 btc, то по факту даже по 0,00001825 их продать не получиться не обрушив цену в несколько раз.</p>\n<p>Таким образом, все кто участвовал в ICO на сегодняшний день в пролете.</p>\n<p><br></p>\n<p><br></p>\n</html>'}], 
                                  ['comment_options', 
                                   {'allow_votes': true, 
                                    'author': 'redhat', 
                                    'allow_curation_rewards': true, 
                                    'percent_steem_dollars': NumberInt(0), 
                                    'permlink': 'pust-hipster-menya-flaguet-no-pravda-dorozhe', 
                                    'max_accepted_payout': '1000000.000 GBG', 
                                    'extensions': []}]], 
                   'signatures': ['1f7130091ce60c651b0a015e9efbd1955a8a144b302ee924595323082f26bac7802e922826fd971ccda6e3c84047973fb889f0abe2cefcb095a2f19a6b53cd3fa4'], 
                   'expiration': '2017-03-06T13:44:06', 
                   'ref_block_prefix': NumberLong(2267427394), 
                   'ref_block_num': NumberInt(2118), 
                   'extensions': []}], 
 'previous': '003d091aae6c250a62a683d4ffa37b893a589717', 
 'extensions': [], 
 'witness_signature': '2059e77afda765de986708be231a7f3bcc0619446dba3412cdcb1d06ab6982465b74a0eb8574ba72e8d8d62dce464045e6a4b9d6c09b416f920160490253098c27', 
 'witness': 'pfunk'}
```
## Operations in Golos
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
- author_reward
> example: 
```javascript 

```
- block2
> example: 
```javascript 

```
- cancel_transfer_from_savings
> example: 
```javascript 

```
- change_recovery_accounts
> example: 
```javascript 

```
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
- convert
> example: 
```javascript 

```
- curation_reward
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
- delete_comment
> example: 
```javascript 
{'author': 'dailis', 
 'permlink': 'testovyi-post'}
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
- feed_publish
> example: 
```javascript 
{'exchange_rate': {'base': '0.050 GBG', 
                   'quote': '1.000 GOLOS'}
```
- follow
> example: 
```javascript 

```
- fill_vesting_withdraw
> example: 
```javascript 

```
- limit_order_cancel
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
- reblog
> example: 
```javascript 
{'account': 'christoryan',
 'permlink': 'vydvigaem-pfunk-v-delegaty-golosa', 
 'author': 'pfunk'}
 ```
 - recover_account
> example: 
```javascript 

```
 - recover_account_recovery
> example: 
```javascript 

```
- set_withdraw_vesting_route
> example: 
```javascript 

```
- transfer
> example: 
```javascript 
{'from': 'phenom', 
 'memo': 'You have been mentioned by on0tole in the post http://golos.io/ru--delegaty/@on0tole/predstavlyayu-skript-dlya-avtomaticheskogo-obnovleniya-price-feed-dlya-delegatov', 
 'type': 'GOLOS', 
 'amount': 0.001, 
 'to': 'primus'}
```
- transfer_from_savings
> example: 
```javascript 
{'request_id': NumberInt(1489186057), 
 'from': 'oxygendependant', 
 'to': 'oxygendependant', 
 'amount': '7480.680 GOLOS', 
 'memo': ''}
```
- transfer_to_savings
> example: 
```javascript 

```
- transfer_to_vesting
> example: 
```javascript 

```
 - vesting_deposit
> example: 
```javascript 

```
- vote
> example: 
```javascript 
{"weight": NumberInt(10000), 
 "permlink": "post-zagadka-opredelite-storony-sveta-po-fotografii-priz-10-zolotykh", 
 "voter": "karton", 
 "author": "antonkostroma"}
```
 - withdraw_vesting
> example: 
```javascript 
{'account': 'gliten', 
 'vesting_shares': '50000.000000 GESTS'}
```
 - withdraw_vesting_route
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
- witness_vote
> example: 
```javascript 

```
