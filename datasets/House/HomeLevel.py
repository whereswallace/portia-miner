{'name': 'HomeLevel',
 'columns': [('Level', None, {'label': 'Home level (0,1,2...)'}),
             ('Item_ID', Lookup.PROP, {'label': 'Name of building'}),
             ('money_cost', None, {'label': 'Gols required to upgrade'}),
             ('item_cost', Lookup.PROP, {'label': 'Materials required to upgrade'}),
             ('attr_max', None, {'label': 'Attribute Max',
                                 'split': ';'}),
             ('extra_des', Lookup.TRANSLATION, {'label': 'Additional description'})]}