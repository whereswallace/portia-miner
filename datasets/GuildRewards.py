{'name': 'GuildRewards',
 'columns': [('ID', None, {'label': 'ID*'}),
             ('RewardsID', [Lookup.ITEM_DROP_FIXED, Lookup.ITEM_DROP_RANDOM], {'split': ',',
                                                                               'label': 'End of season rewards'}),
             ('AnnualRewardsID', [Lookup.ITEM_DROP_FIXED, Lookup.ITEM_DROP_RANDOM], {'split': ',',
                                                                                     'label': 'Annual rewards'})]}