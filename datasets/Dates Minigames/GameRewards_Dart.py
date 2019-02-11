{'name': 'GameRewards_Dart',
 'columns': [('score', None, {'label': 'Darts score'}),
             ('Mood', None, {'label': 'Mood points earned'}),
             ('rewards', Lookup.ITEM_DROP_RANDOM, {'label': 'Reward earned',
                                                   'quantity_post': ','}),
             ('rewards', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Amount of reward earned'})]}