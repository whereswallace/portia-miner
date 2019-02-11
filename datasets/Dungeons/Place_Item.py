{'name': 'Place_Item',
 'columns': [('Prefab_Path', None, {'label': 'Dungeon feature'}),
             ('Defence', None, {'label': 'Defense of feature'}),
             ('HP_Max', None, {'label': 'Max HP of feature'}),
             ('Drop_ID', Lookup.ITEM_DROP_FIXED, {'label': 'Fixed items that drop'}),
             ('Drop_ID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of fixed drops'}),
             ('Drop_ID', Lookup.ITEM_DROP_RANDOM, {'label': 'Random items that can drop'}),
             ('Drop_ID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of random drops'}),
             ('Extra_ID', None, {'label': '**Extra items that can drop'}),
             ('Extra_Rate', None, {'label': '**Rate of extra items dropped'}),
             ('Extra_DropID', Lookup.ITEM_DROP_FIXED, {'label': '**Other extra item fixed drops'}),
             ('Extra_DropID', Lookup.ITEM_DROP_FIXED_NUMBER, {
                 'label': '**Number of other extra item fixed drops'}),
             ('Extra_DropID', Lookup.ITEM_DROP_RANDOM, {'label': '**Other extra item random drops'}),
             ('Extra_DropID', Lookup.ITEM_DROP_RANDOM_NUMBER, {
                 'label': '**Number of other extra item random drops'}),
             ('Extra_DropRate', None, {'label': '**Rate of other extra items dropped'})]}