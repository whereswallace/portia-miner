{'name': 'Mission_Rewards',
 'columns': [('missionId', None, {'label': 'Mission ID'}),
             ('missionId', Lookup.IN_MISSION_DIALOG, {'label': 'Mission dialogue'}),
             ('money', None, {'label': 'Gol earned'}),
             ('itemList', Lookup.PROP, {'split': ',',
                                        'quantity_post': '_',
                                        'label': 'Item earned'}),
             ('favor', Lookup.NPC_ID_TO_NAME, {'split': ',',
                                               'quantity_post': '_',
                                               'label': 'Relationship Points earned'}),
             ('Exp', None, {'label': 'Experience earned'}),
             ('reputation', None, {'label': 'Workshop Points earned'})]}