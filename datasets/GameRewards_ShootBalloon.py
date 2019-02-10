{'name': 'GameRewards_ShootBalloon',
 'columns': [('Score', None, {'label': 'Balloon score'}),
             ('Mood', None, {'label': 'Mood Points earned'}),
             ('Rewards', Lookup.ITEM_DROP_RANDOM, {'label': 'Random rewards dropped',
                                                   'quantity_post': ','}),
             ('Rewards', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random rewards dropped'})]}