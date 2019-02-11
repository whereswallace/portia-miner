{'name': 'The_Chest',
 'columns': [('ID', None, {'label': 'Treasure chest ID'}),
             ('scene_name', None, {'label': 'General location in open world'}),
             ('Coordinate', None, {'label': 'Map coordinates'}),
             ('drop_group', Lookup.ITEM_DROP_FIXED, {'label': 'Items in the chest',
                                                     'quantity_post': ','}),
             ('drop_group', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of items in the chest'})]}