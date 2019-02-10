{'name': 'Festival_HotPot',
 'columns': [('HotPot_ID', None, {'label': 'NPC name'}),
             ('ItemGroup', Lookup.PROP, {'split': ';',
                                         'quantity_post': ',',
                                         'label': 'Wanted hotpot ingredients'}),
             ('MaxHotValue', None, {'label': 'Spicyness quota*'})]}