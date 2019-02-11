{'name': 'Conversation_Talk',
 'columns': [('SegmentID', None, {'label': 'Segment ID'}),
             ('SegmentID', Lookup.CONVERSATION_SEGMENT_SPEAKER, {'ignore_if_equals': ['-1', '-2', '-3'],
                                                                 'label': 'NPC speaking'}),
             ('SegmentID', Lookup.CONVERSATION_SEGMENT_BASE, {'split': ',',
                                                              'label': 'Spoken line'})]}