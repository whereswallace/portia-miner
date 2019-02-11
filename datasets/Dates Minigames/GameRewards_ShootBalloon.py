{'name': 'GameRewards_ShootBalloon',
 'columns': [('Score', None, {'label': 'Balloon score'}),
             ('Mood', None, {'label': 'Mood Points earned'}),
             ('Rewards', Lookup.ITEM_DROP_RANDOM, {'label': 'Reward earned',
                                                   'quantity_post': ','}),
             ('Rewards', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Amount of reward earned'})]}