{'name': 'Repair_Table',
 'columns': [('Item_Id', Lookup.PROP, {'label': 'Item to recover'}),
             ('Parts_List', Lookup.PROP, {'split': ',',
                                          'label': 'Required pieces'}),
             ('Time', None, {'label': 'Crafting time'}),
             ('CD_Cost', None, {'label': 'Data Disc cost for recovery'})]}