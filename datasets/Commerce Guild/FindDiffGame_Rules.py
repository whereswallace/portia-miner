{'name': 'FindDiffGame_Rules',
 'columns': [('workshopLevel', Lookup.GUILD_LEVEL, {'label': 'Player Workshop Level'}),
             ('diffItemId', Lookup.FIND_DIFF_GAME_ITEMS, {'split': ',',
                                                          'label': 'Items can inspect'}),
             ('rewards', Transform.REWARDS, {'split': ';',
                                             'label': 'Mailed rewards})]}