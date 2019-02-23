{'name': 'Mail',
 'columns': [('appear', None, {'label': 'Envelope image type'}),
             ('Title', Lookup.TRANSLATION, {'label': 'Mail title'}),
             ('Content', Lookup.TRANSLATION, {'label': 'Mail message'}),
             ('Attachment', Lookup.PROP, {'split': ':',
                                          'label': 'Attached item'}),
             ('missionid', None, {'label': 'Related mission'}),
             ('MissionAutoReceive', Transform.BOOL, {'label': 'Mission starts upon opening mail?'})]}