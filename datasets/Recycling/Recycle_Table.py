{'name': 'Recycle_Table',
 'columns': [('Item_Id', Lookup.PROP, {'label': 'Item that can be recycled'}),
             ('Drop_Id', Lookup.ITEM_DROP_FIXED, {'label': 'What drops from Recycling Machine'}),
             ('Drop_Id', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of drops'}),
             ('Time', None, {'label': 'Recycling time'})]}