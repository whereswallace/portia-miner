{'name': 'Item_seed',
 'columns': [('ID', Lookup.PROP, {'label': 'Seed name'}),
             ('Plant_Name', Lookup.TRANSLATION, {'label': 'Crop or tree name'}),
             ('Food_Point', None, {'label': 'Food Points*'}),
             ('Food_Happy', None, {'label': 'Fertilizer required to be happy*'}),
             ('Drop_Happy', Lookup.ITEM_DROP_RANDOM, {'label': 'Crops dropped when well fertilized'}),
             ('Drop_Happy', Lookup.ITEM_DROP_RANDOM_NUMBER, {'label': 'Number of well fertilized drops'})]}