{'name': 'Props_total_table',
 'columns': [('Item_Type', None, {'label': 'Item type'}),
             ('Intend_Type', [Lookup.PLAYER_INTEND_NO_TARGET,
                              Lookup.PLAYER_INTEND_HOME_REGION], {'label': 'Used for'}),
             ('Props_Id', Lookup.PROP, {'label': 'Item'}),
             ('Props_Explain_One', Lookup.TRANSLATION, {'label': 'Description'}),
             ('Effect', Lookup.TRANSLATION, {'label': 'Additional description'}),
             ('User_Level', None, {'label': 'Armor level'}),
             ('Buy_Price', None, {'label': 'Purchase price'}),
             ('Sell_Price', None, {'label': 'Sell price'}),
             ('SourceDes', Lookup.ITEM_FROM, {'split': ',',
                                              'label': 'Obtained from'}),
             ('InVersion', None, {'label': 'Version it appeared in'}),
             ('IsGift', Transform.BOOL, {'label': 'Is a gift?'}),
             ('Skill_List', Lookup.ABILITY_TREE_NEW, {'split': ',',
                                                      'label': 'Related skill'}),
             ('Props_Id', Lookup.RECYCLE_TABLE_DROP_ID, {'split': ';',
                                                         'quantity_post': ',',
                                                         'label': 'Recycle drops'}),
             ('gift_tagid', Transform.GIFT_TAGID, {'label': '**gift_tagid**'}),
             ('Energy', None, {'label': '**Energy**'}),
             ('HotValue', None, {'label': '**HotValue**'}),
             ('Rare_Lv', None, {'label': '**Rare_Lv**'}),
             ('Tag_List', None, {'split': ',',
                                 'label': '**Tag_List**'})]}