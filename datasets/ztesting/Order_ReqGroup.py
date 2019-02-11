{'name': 'Order_ReqGroup',
 'columns': [('ID', None, {'label': '**ID (Requester?)**'}),
             ('type', Lookup.REQ_TYPE, {'label': '**Type**'}),
             ('req', Lookup.ORDER_REQ_ITEM, {'split': ',',
                                             'label': 'Possible order items'})]}