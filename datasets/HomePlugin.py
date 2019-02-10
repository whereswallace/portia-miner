{'name': 'HomePlugin',
 'columns': [('Name', Lookup.TRANSLATION, {'label': 'Special building name'}),
             ('Desc', Lookup.TRANSLATION, {'label': 'Description'}),
             ('Unlock_Level', None, {'label': 'House level required*'}),
             ('Item_Need', Lookup.PROP, {'split': ';',
                                         'quantity_post': ',',
                                         'label': 'Items required'}),
             ('Item_Recycle', Lookup.PROP, {'split': ';',
                                            'quantity_post': ',',
                                            'label': 'Recycled products*'}),
             ('Gold_Need', None, {'label': 'Gol cost'})]}