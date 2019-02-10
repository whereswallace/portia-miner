{'name': 'ExchangeReq',
         'columns': [('npcId', Lookup.REPOSITORY, {'label': 'NPC'}),
                     ('supplyPool', Lookup.PROP, {'split': ',',
                                                  'label': 'Offers'}),
                     ('reqPool', Lookup.PROP, {'split': ',',
                                               'label': 'Requests'}),
                     ('exhibitPool', Lookup.PROP, {'split': ',',
                                                   'label': 'Favorite donations'})]}