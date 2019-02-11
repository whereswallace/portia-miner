{'name': 'ExchangeReq',
         'columns': [('npcId', Lookup.REPOSITORY, {'label': 'Name of NPC'}),
                     ('supplyPool', Lookup.PROP, {'split': ',',
                                                  'label': 'Relic pieces they offer on the exchange'}),
                     ('reqPool', Lookup.PROP, {'split': ',',
                                               'label': 'Relic pieces they request on the exchange'}),
                     ('exhibitPool', Lookup.PROP, {'split': ',',
                                                   'label': 'Favorite exhibits'})]}