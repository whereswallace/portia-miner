{'name': 'InMission_Dialog',
 'columns': [('Dialog', None, {'label': 'Dialog ID'}),
             ('MissionID', None, {'label': 'Mission ID'}),
             ('Dialog', Lookup.CONVERSATION_BASE, {'split': ';',
                                                   'label': 'Dialogue when in middle of mission'})]}