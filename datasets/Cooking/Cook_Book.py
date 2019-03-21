{'name': 'Cook_Book',
 'columns': [('Food', Lookup.PROP, {'label': 'Recipe'}),
             ('Material', [Lookup.PROP, Lookup.COOK_TAG_NAME], {'quantity_post': '_',
                                                                'split': ';',
                                                                'label': 'Ingredients'}),
             ('Quality', Lookup.COOK_BOOK_QUALITY_COST, {'label': '**Quality>Cost**'}),
             ('Quality', Lookup.COOK_BOOK_QUALITY_WEIGHT, {'label': '**Quality>Weight**'}),
             ('Weight', None, {'label': '**Weight**'})]}