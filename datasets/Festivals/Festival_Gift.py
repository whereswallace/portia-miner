{'name': 'Festival_Gift',
 'columns': [('npc_name', Lookup.TRANSLATION, {'label': 'NPC who is giving the gift'}),
             ('translationid', Lookup.TRANSLATION, {'label': 'Note attached to the gift'}),
             ('gift_drop', Lookup.PROP, {'label': 'Gift',
                                         'quantity_post': '_'}),
             ('Gift_Model_Path', None, {'label': 'Event where gift is given'})]}