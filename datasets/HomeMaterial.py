{'name': 'HomeMaterial',
 'columns': [('Id', Lookup.PROP, {'label': 'Home design item name'}),
             ('Type', None, {'label': 'Type of item'}),
             ('Level', None, {'label': 'House level required'}),
             ('Item_Cost', Lookup.PROP, {'split': ';',
                                         'quantity_post': ',',
                                         'label': 'Item cost'}),
             ('Money', None, {'label': 'Gol cost'})]}