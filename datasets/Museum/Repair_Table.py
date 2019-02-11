{'name': 'Repair_Table',
 'columns': [('Item_Id', Lookup.PROP, {'label': 'Name of relic that can be recovered'}),
             ('Parts_List', Lookup.PROP, {'split': ',',
                                          'label': 'Required pieces for recovery'}),
             ('CD_Cost', None, {'label': 'Data Disc cost (for recovery at Research Center'}),
             ('Time', None, {'label': 'Crafting time (on personal Recovery Machine)'})]}