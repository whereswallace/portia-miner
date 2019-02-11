{'name': 'Quarrying',
 'columns': [('Stone_Path', None, {'label': 'Type of stone'}),
             ('Defence', None, {'label': 'Stone defense'}),
             ('HP_Max', None, {'label': 'Stone max HP'}),
             ('Drop_ID', Lookup.ITEM_DROP_FIXED, {'label': 'Fixed drops from stone'}),
             ('Drop_ID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of fixed drops from stone'}),
             ('Drop_ID', Lookup.ITEM_DROP_RANDOM, {'label': 'Random drops from stone'}),
             ('Drop_ID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random drops from stone'})]}