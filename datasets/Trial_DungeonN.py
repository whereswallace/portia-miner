{'name': 'Trial_DungeonN',
 'columns': [('Description', Lookup.TRANSLATION, {'label': 'Ruin name'}),
             ('Level', None, {'label': 'Level'}),
             ('Spend_Time', None, {'label': 'Time required to complete level'}),
             ('Grade', None, {'label': 'Recommended player level'}),
             ('Little_MonsterID', Lookup.DUNGEON_MONSTER, {'split': ';',
                                                           'quantity_post': ',',
                                                           'label': 'Common enemies'}),
             ('Boss_ID', Lookup.DUNGEON_MONSTER, {'split': ';',
                                                  'quantity_post': ',',
                                                  'label': 'Boss enemies'}),
             ('Common_ChestID', Lookup.DUNGEON_CHEST_FIXED, {'split': ';',
                                                             'quantity_post': ',',
                                                             'label': 'Common chest fixed drops'}),
             ('Common_ChestID', Lookup.DUNGEON_CHEST_RANDOM, {'split': ';',
                                                              'quantity_post': ',',
                                                              'label': 'Common chest random drops'}),
             ('Best_ChestID', Lookup.DUNGEON_CHEST_FIXED, {'split': ';',
                                                           'quantity_post': ',',
                                                           'label': 'Special chest fixed drops'}),
             ('Best_ChestID', Lookup.DUNGEON_CHEST_RANDOM, {'split': ';',
                                                            'quantity_post': ',',
                                                            'label': 'Special chest random drops'}),
             ('First_Reward', Lookup.PROP, {'split': ',',
                                            'quantity_post': '_',
                                            'label': 'Reward for first time through'}),
             ('Reward', Lookup.PROP, {'split': ',',
                                      'quantity_post': '_',
                                      'label': 'Reward after first time'}),
             ('Life', None)]}