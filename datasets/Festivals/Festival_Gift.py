{'name': 'Festival_Gift',
 'columns': [('npc_name', Lookup.TRANSLATION, {'label': 'NPC gift giver'}),
             ('translationid', Lookup.TRANSLATION, {'label': 'Note from NPC'}),
             ('gift_drop', Lookup.PROP, {'label': 'Gift',
                                         'quantity_post': '_'}),
             ('Gift_Model_Path', None, {'label': 'Present type*'})]}