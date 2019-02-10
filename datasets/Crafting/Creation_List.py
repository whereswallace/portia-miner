{'name': 'Creation_List',
 'columns': [('Item_ID', Lookup.PROP, {'label': 'Assembled item'}),
             ('Level', None, {'label': 'Assembly level required (add +1)'}),
             ('Name', Lookup.TRANSLATION, {'label': 'Assembled item'}),
             ('Time', None, {'label': 'Crafting time'}),
             ('Exp', None, {'label': 'Experience reward'}),
             ('PartList', Lookup.PARTS_LIST, {'split': ',',
                                              'label': 'Parts required'})]}