{'name': 'TreeChop',
 'columns': [('TreeID', None, {'label': 'Name of tree'}),
             ('Tree_Prefab', None, {'label': 'Alt name of tree'}),
             ('Act_Type', None, {'label': '**Act_Type**'}),
             ('Tree_Radius', None, {'label': 'Radius'}),
             ('Defence', None, {'label': 'Defense'}),
             ('HP_Min', None, {'label': 'Minimum HP'}),
             ('HP_Max', None, {'label': 'Maximum HP'}),
             ('Chop_DropID', Lookup.ITEM_DROP_FIXED, {'label': 'Drops from chopping (fixed)'}),
             ('Chop_DropID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of drops from chopping (fixed)'}),
             ('Chop_DropID', Lookup.ITEM_DROP_RANDOM, {'label': 'Drops from chopping (random)'}),
             ('Chop_DropID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of drops from chopping (random)'}),
             ('Extra_ChopDropRate', None, {'label': 'Rate of extra chop drops',
                                           'ignore_if_equals': ['0']}),
             ('Extra_ChopDropID', Lookup.ITEM_DROP_FIXED, {'label': 'Extra chop drops (fixed)',
                                                           'ignore_if_equals': ['0']}),
             ('Extra_ChopDropID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of extra chop drops (fixed)'}),
             ('Extra_ChopDropID', Lookup.ITEM_DROP_RANDOM, {'label': 'Extra chop drops (random)'}),
             ('Extra_ChopDropID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of extra chop drops (random)'}),
             ('Stub_DropID', Lookup.ITEM_DROP_FIXED, {'label': 'Drops from stump (fixed)'}),
             ('Stub_DropID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of drops from stump (fixed)'}),
             ('Stub_DropID', Lookup.ITEM_DROP_RANDOM, {'label': 'Drops from stump (random)'}),
             ('Stub_DropID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of drops from stump (random)'}),
             ('Extra_StubDropRate', None, {'label': 'Rate of extra stump drops',
                                           'ignore_if_equals': ['0']}),
             ('Extra_StubDropID', Lookup.ITEM_DROP_FIXED, {'label': 'Extra stump drops (fixed)',
                                                           'ignore_if_equals': ['0']}),
             ('Extra_StubDropID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of extra stump drops (fixed)'}),
             ('Extra_StubDropID', Lookup.ITEM_DROP_RANDOM, {'label': 'Extra stump drops (random)'}),
             ('Extra_StubDropID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of extra stump drops (random)'}),
             ('Kick_DropID', Lookup.ITEM_DROP_FIXED, {'label': 'Drops from kicking trees (fixed)'}),
             ('Kick_DropID', Lookup.ITEM_DROP_FIXED_NUMBER, {'label': 'Number of drops from kicking trees (fixed)'}),
             ('Kick_DropID', Lookup.ITEM_DROP_RANDOM, {'label': 'Drops from kicking trees (random)'}),
             ('Kick_DropID', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of drops from kicking trees (random)'})]}