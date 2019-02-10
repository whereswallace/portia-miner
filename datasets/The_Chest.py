{'name': 'The_Chest',
 'columns': [('scene_name', None, {'label': 'Location'}),
             ('Coordinate', None, {'label': 'Map coordinates'}),
             ('drop_group', Lookup.ITEM_DROP_FIXED, {'label': 'Chest Items',
                                                     'quantity_post': ','}),
             ('drop_group', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Items inside chest'}),
             ('ID', None, {'label': 'Chest ID'}),
             ('Model_Path', None, {'label': 'Type of chest'})]}