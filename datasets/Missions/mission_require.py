{'name': 'mission_require',
 'columns': [('missionId', Lookup.IN_MISSION_DIALOG, {'label': 'Mission'}),
             ('missionId', None, {'label': 'Mission ID'}),
             ('requireItems', Lookup.PROP, {'split': ',',
                                            'label': 'Mission items'})]}