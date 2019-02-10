{'name': 'CreationFactory_Upgrade',
 'columns': [('item_id', Lookup.PROP, {'label': 'Assembly Station'}),
             ('Level', None, {'label': 'Assembly Station level'}),
             ('money_cost', None, {'label': 'Gols'}),
             ('item_cost', Lookup.PROP, {'label': 'Materials',
                                         'quantity_post': ',',
                                         'split': ";"}),
             ('farm_level_need', None, {'label': 'Farm Level Required'}),
             ('des', Lookup.TRANSLATION, {'label': 'Description'})]}