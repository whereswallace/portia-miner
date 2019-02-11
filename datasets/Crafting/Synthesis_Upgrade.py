{'name': 'Synthesis_Upgrade',
 'columns': [('Item_ID', Lookup.PROP, {'label': 'Name of crafting station'}),
             ('Level', None, {'label': 'Level of crafting station (0, 1, or 2)'}),
             ('Item_Cost', Lookup.PROP, {'split': ';',
                                         'quantity_post': ',',
                                         'label': 'Required materials to upgrade'}),
             ('Money_Cost', None, {'label': 'Required gols to upgrade'})]}