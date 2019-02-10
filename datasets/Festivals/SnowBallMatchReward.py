{'name': 'SnowBallMatchReward',
 'columns': [('Rank', None, {'label': 'Rank in Snowball Fight'}),
             ('Reward_Day1', Lookup.PROP, {'split': ',',
                                           'quantity_post': '_',
                                           'label': 'Day 1 rewards'}),
             ('Reward_Day2', Lookup.PROP, {'split': ',',
                                           'quantity_post': '_',
                                           'label': 'Day 2 rewards'})]}