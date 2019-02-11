{'name': 'Wish',  # I need wishitemgroup to also list the needrelation and addfavor. Right now the number listed with it represents how much they like that item, ish. Might need "value" from wishitem too.
 'columns': [('npcid', Lookup.NPC_ID_TO_NAME),
             ('wishitemgroup', Lookup.WISH_ITEM_GROUP, {'label': 'Wish Items',
                                                        'split': ';',
                                                        'quantity_post': ','})]},
# I'd like to show the range in the quantity for
# ITEM_DROP... the thing where you said you need to count how many commas
# there are. See the very last cell in row 26 of Item_drop table
