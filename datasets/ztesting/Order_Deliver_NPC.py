{'name': 'Order_Deliver_NPC',
 'columns': [('Deliver_NPC', Lookup.NPC_ID_TO_NAME, {'label': '**ID (Requester?)**'}),
             ('Req_Des_Dial', Transform.ORDER_CAN_REQUEST, {'label': 'Can request'}),
             ('Req_Des_Dial', Transform.ORDER_MISSION_DIALOGUE, {'label': 'Mission Dialogue'}),
             ('Paper', None),
             ('extraDrop', Lookup.ITEM_DROP_RANDOM, {'split': '|',
                                                     'quantity_pre': '='}),
             ('extraDrop', Lookup.RANDOM_HERBS_ITEM_DROP_RANDOM_NUMBER, {'split': '|',
                                                                         'quantity_pre': '='})]}