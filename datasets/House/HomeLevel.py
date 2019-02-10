{'name': 'HomeLevel',
 'columns': [('Level', None, {'label': 'Home Level'}),
             ('Item_ID', Lookup.PROP, {'label': 'Home ID'}),
             ('money_cost', None, {'label': 'Gol Cost'}),
             ('item_cost', Lookup.PROP, {'label': 'Supplies Needed'}),
             ('attr_max', None, {'label': 'Attribute Max',
                                 'split': ';'}),
             ('extra_des', Lookup.TRANSLATION, {'label': 'Additional Desc'})]}