{'name': 'Synthesis_Upgrade',
 'columns': [('Item_ID', Lookup.PROP, {'label': 'Crafting station'}),
             ('Level', None, {'label': 'Worktable level (+1)'}),
             ('Item_Cost', Lookup.PROP, {'split': ';',
                                         'quantity_post': ',',
                                         'label': 'Required materials to upgrade'}),
             ('Money_Cost', None, {'label': 'Gol cost of upgrade'})]}