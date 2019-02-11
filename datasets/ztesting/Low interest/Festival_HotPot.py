{'name': 'Festival_HotPot',
 'columns': [('HotPot_ID', None, {'label': '**HotPot_ID** (NPC name?)'}),
             ('ItemGroup', Lookup.PROP, {'split': ';',
                                         'quantity_post': ',',
                                         'label': 'Wanted hotpot ingredients'}),
             ('MaxHotValue', None, {'label': '**Max_Hot_Value**'})]}