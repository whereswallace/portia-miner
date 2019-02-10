{'name': 'Conversation_Segment',
 'columns': [('SegmentID', None, {'label': 'Segment ID'}),
             ('BaseID', Lookup.CONVERSATION_BASE, {'split': ',',
                                                   'label': 'Dialogue'}),
             ('SpeakerID', Lookup.NPC_ID_TO_NAME, {'ignore_if_equals': ['-1', '-2', '-3'],
                                                   'label': 'NPC speaking'})]}