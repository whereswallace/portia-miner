{'name': 'HomeMaterial',
 'columns': [('Id', Lookup.PROP, {'label': 'Name of interior design item'}),
             ('Type', None, {'label': 'Type of item'}),
             ('Level', None, {'label': 'House level required'}),
             ('Item_Cost', Lookup.PROP, {'split': ';',
                                         'quantity_post': ',',
                                         'label': 'Materials required to build'}),
             ('Money', None, {'label': 'Gols required to build'})]}