odoo.define('gio_obstgemuese_theme.cart', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');

publicWidget.registry.cart = publicWidget.Widget.extend({
    selector: '.cart_container',
    events:{
        'click .cart_close':'_onClickCloseCart',
        'click .cart_trash':'_onClickCartTrash',
    },
    _onClickCloseCart:function(){
        $('.cart_container').animate({left: '110%'},1000);
        $('.cart_container').removeClass('toggle_active');
        $('#wrapwrap').css('overflow-y','scroll')
    },
    _onClickCartTrash:function(ev){
        var line_id = $(ev.target).siblings('.line_id').val()
        var order_line = 'order_lines_'+line_id

         ajax.jsonRpc('/remove/order/line', 'call', {'line_id':line_id})
            .then(function (result) {
                  if(result == true){
                    $('.'+order_line).remove()
                    $('.item_count').html($('.order_lines').length+' items')
                  }
            });
    },
    });
});
odoo.define('gio_obstgemuese_theme.website_sale_inherit', function (require) {
'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var WebsiteSale = require('website_sale.website_sale');
    require('website_sale.website_sale');

    publicWidget.registry.WebsiteSale.include({
        async _onClickAdd(ev){
            return this._super.apply(this, arguments).then(function () {
                   publicWidget.registry.header.prototype._onClickOpenCart();
            });
        }
    });
});
