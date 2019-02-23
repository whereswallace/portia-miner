{'name': 'Achievement',
 'columns': [('name', Lookup.TRANSLATION, {'label': 'Achievement'}),
             ('description', Lookup.TRANSLATION, {'label': 'Description'}),
             ('platformTag', None, {'label': 'Additional description'}),
             ('isSecret', Transform.BOOL, {'label': 'Hidden?'}),
             ('type', None, {'label': 'Action required'}),
             ('checkType', None, {'label': 'Check for...'}),
             ('mainpara', None, {'label': '...what'})]}