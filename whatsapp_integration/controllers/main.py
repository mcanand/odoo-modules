from odoo.http import request
from odoo import http, _

class WhatsappCallBack(http.Controller):

    @http.route(['/call/back'],type='json', auth='public', methods=['GET', 'POST'], csrf=False   )
    def wa_recive_back(self,**kwargs):
        print(kwargs)
        print("{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{kwargs}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}")