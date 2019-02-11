{'name': 'CloseInteract',
 'columns': [('ID', None, {'label': 'Interaction type 0=Hug?|1=Kiss?...'}),
             ('Favor_Level', Lookup.FAVOR_RELATION, {'label': 'Interaction unlocked at...'}),
             ('CpCost', None, {'label': 'SP cost'}),
             ('Favor_Value', None, {'label': 'Relationship Points earned'}),
             ('TimesPerDay', None, {'label': 'Max interactions per day'}),
             ('IsJealous', Transform.BOOL, {'label': '**IsJealous**'}),
             ('JealousStart', None, {'label': '**JealousStart**'})]}