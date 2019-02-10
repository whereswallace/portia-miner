{'name': 'Actor',
 'columns': [('faction', Transform.FACTION, {'label': 'Character type'}),
             ('name', Lookup.TRANSLATION, {'label': 'Character'}),
             ('Lv', None, {'label': 'Character level'}),
             ('IsBoss', Transform.BOOL, {'label': 'Is a boss?'})]}