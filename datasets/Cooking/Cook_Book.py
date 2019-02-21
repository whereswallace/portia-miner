{'name': 'Cook_Book',
 'columns': [('Food', Lookup.PROP, {'label': 'Recipe'}),
             ('Material', [Lookup.PROP, Lookup.STORE_PRODUCT, Lookup.COOK_TAG_NAME], {'quantity_post': '_',
                                                                                      'split': ';',
                                                                                      'label': 'Ingredients'}),
             ('Weight', None, {'label': '**Weight**'}),
             ('Quality', None, {'label': '**Quality**'})]}