{'name': 'Cook_AckList',
 'columns': [('Food', Lookup.PROP, {'label': 'Recipe owned by Ack'}),
             ('Material', Lookup.PROP, {'split': ';',
                                        'quantity_post': '_',
                                        'label': 'Required ingredients'}),
             ('Unlocked', Transform.BOOL, {'label': 'Unlocked?'})]}