{'name': 'Achievement',
 'sort': ['sid', Transform.INT],
 'columns': [('sid', None, {'label': 'Sort index'}),
             ('id', None, {'label': 'ID'}),
             ('name', Lookup.TRANSLATION, {'label': 'Name'}),
             ('description', Lookup.TRANSLATION, {'label': 'Description'}),
             ('isSecret', Transform.BOOL, {'label': 'Is secret?'}),
             ('platformTag', None, {'label': 'Platform Tag'}),
             ('type', None, {'label': 'Action Type'}),
             ('subPara', None, {'label': 'Action Type Parameter'}),
             ('checkType', None, {'label': 'Action Comparison'}),
             ('mainPara', None, {'label': 'Action Comparison Value'})]}