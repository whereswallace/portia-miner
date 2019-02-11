{'name': 'General_Dialog',
 'columns': [('NPCid', Lookup.REPOSITORY, {'label': 'NPC name',
                                           'ignore_if_equals': ['-1']}),
             ('First_Dialog', Lookup.CONVERSATION_BASE, {
                 'label': 'Dialogue upon first meeting', 'ignore_if_equals': ['-1']}),
             ('Area_Dialog', None, {'label': 'Area'}),  # need transform here
             ('Weather_Dialog', None, {'label': 'Weather'}),  # need transform here
             ('Season_Dialog', None, {'label': 'Season'}),  # need transform here
             ('Social_Dialog', None, {'label': 'Typical day dialogue'}),
             ('Festival_Dialog', None, {'label': 'Festival'}),  # need transform here
             ('Jealous_Dialog', Lookup.CONVERSATION_BASE, {'label': 'Jealous dialogue',
                                                           'ignore_if_equals': ['-1']}),
             ('Unhappy_Dialog', Lookup.CONVERSATION_BASE, {'label': 'Unhappy dialogue',
                                                           'split': ';',
                                                           'ignore_if_equals': ['-1']})]}