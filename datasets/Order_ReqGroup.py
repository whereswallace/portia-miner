{'name': 'Order_ReqGroup',
 'columns': [('type', Lookup.REQ_TYPE, {'label': 'Order type*'}),
             ('ID', None, {'label': 'ID'}),
             ('req', Lookup.ORDER_REQ_ITEM, {'split': '_',
                                             'label': 'Possible order items'})]}