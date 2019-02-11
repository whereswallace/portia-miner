{'name': 'Cabinet',
 'columns': [('ID', Lookup.PROP, {'label': 'Name of furniture that stores items'}),
             ('MaxCount', None, {'label': 'Capacity'}),
             ('TypeList', Lookup.CABINET_TYPE_LIST, {'split': ',',
                                                     'label': 'Type of contents'})]}