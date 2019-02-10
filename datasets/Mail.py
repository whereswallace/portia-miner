{'name': 'Mail',
 'columns': [('Title', Lookup.TRANSLATION, {'label': 'Mail title'}),
             ('Content', Lookup.TRANSLATION, {'label': 'Mail message'}),
             ('Attachment', Lookup.PROP, {'split': ':',
                                          'label': 'Attached item'}),
             ('missionid', None, {'label': 'Related mission'}),
             ('MissionAutoReceive', None, {'label': 'Mission attached'}),
             ('appear', None, {'label': 'Envelope type'})]}