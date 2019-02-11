{'name': 'CreationFactory_Upgrade',
 'columns': [('item_id', Lookup.PROP, {'label': 'Crafting station'}),
             ('Level', None, {'label': 'Assembly Station level (0, 1, or 2)'}),
             ('des', Lookup.TRANSLATION, {'label': 'Description'}),
             ('money_cost', None, {'label': 'Gol cost to upgrade'}),
             ('item_cost', Lookup.PROP, {'label': 'Material cost to upgrade',
                                         'quantity_post': ',',
                                         'split': ";"}),
             ('farm_level_need', None, {'label': '**farm_level_need**'})]}