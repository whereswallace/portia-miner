{'name': 'HomeConstruction',
 'columns': [('Name', Lookup.TRANSLATION, {'label': 'Building name'}),
             ('Type', None, {'label': 'Alt building name'}),
             ('ItemId', Lookup.PROP, {'split': ',',
                                      'label': 'Alt building name'}),
             ('Level', None, {'label': 'Building level (O,1,2...)'}),
             ('costitemlist', Lookup.PROP, {'label': 'Materials required to build',
                                            'split': ';',
                                            'quantity_post': ','}),
             ('costgol', None, {'label': 'Gols required to build'}),
             ('ModifyCostItemList', Lookup.PROP, {'split': ';',
                                                  'quantity_post': ',',
                                                  'label': '**Modify_Cost_Item_List**'}),
             ('ModifyCostGol', None, {'label': '**Modify_Cost_Gol**'})]}