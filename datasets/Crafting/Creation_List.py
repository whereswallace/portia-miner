{'name': 'Creation_List',
 'columns': [('Item_ID', Lookup.PROP, {'label': 'Name of assembled item'}),
             ('Name', Lookup.TRANSLATION, {'label': 'Alternate name'}),
             ('Level', None, {'label': 'Assembly Station required (0, 1, or 2)'}),
             ('Time', None, {'label': 'Crafting time (auto assembly)'}),
             ('Exp', None, {'label': 'Experience reward'}),
             ('PartList', Lookup.PARTS_LIST, {'split': ',',
                                              'label': 'Parts required'})]}