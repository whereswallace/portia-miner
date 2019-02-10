{'name': 'Research_Choice',
 'columns': [('ID', None, {'label': 'Research ID'}),
             ('CD_Count', None, {'label': 'Data Discs turned in'}),
             ('CD_Extra', None, {'label': 'CD extra*'}),
             ('Creation_List', Lookup.RESEARCH_LIST_ITEM_LIST, {'split': ',',
                                                                'quantity_post': '_',
                                                                'label': 'Items to research'}),
             ('Creation_List', Lookup.RESEARCH_LIST_RESEARCH_SPEED, {'split': ',',
                                                                     'quantity_post': '_',
                                                                     'label': 'Speed of research'})]}