{'name': 'CloseInteract',
 'columns': [('ID', None, {'label': 'Interaction type 0=Hug?|1=Kiss?|2=Pet?|3=?|4=?'}),
             ('Favor_Level', Lookup.FAVOR_RELATION, {'label': 'Friendship required'}),
             ('CpCost', None, {'label': 'SP cost'}),
             ('Favor_Value', None, {'label': 'Relationship Points earned'}),
             ('TimesPerDay', None, {'label': 'Max interactions per day'}),
             ('IsJealous', None, {'label': 'Cannot do if jealous*'}),
             ('JealousStart', None, {'label': 'Causes jealousy*'})]}