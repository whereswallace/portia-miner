{'name': 'Favor_Influence',
 'columns': [('npc_id', Lookup.REPOSITORY, {'label': 'Name'}),
             ('benefit', Lookup.FAVOR_RELATION, {'split': ";",
                                                 'quantity_post': '=',
                                                 'label': 'Perks'})]}
