{'name': 'Conversation_list',
 'columns': [('dialogue_id', None, {'label': 'Dialogue ID'}),
             ('dialogue_id', Lookup.CONVERSATION_BASE, {'split': ',',
                                                        'label': 'Dialogue (split by ,)'}),
             ('dialogue_id', Lookup.CONVERSATION_BASE, {'split': ';',
                                                        'label': 'Dialogue (split by ;)'}),
             ('Task_id', None, {'label': 'Task ID'})]}