odoo.define('guest_checkout.checkout_country_code', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const {_t, qweb} = require('web.core');
    const ajax = require('web.ajax');
    const session = require('web.session');

    publicWidget.registry.add_country_code = publicWidget.Widget.extend({
        selector: '.checkout_autoformat',
        events: {

        },
        start:function(){
            ajax.jsonRpc('/get/country/phone_code', 'call', {})
                    .then(function (result) {
                        if(result){
                            $('.phone_code_number').val("+"+result)
                        }
                    });
        },
    });
    publicWidget.registry.add_country_code = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        events: {
            'scroll': 'onscroll',
        },
        onscroll:function(event){
            var scroll = $('#wrapwrap').prop('scrollTop')
            if(scroll >=100){
                $('.te_header_before_overlay').hide()
            }
            else{
                $('.te_header_before_overlay').show()
            }
        },
    });
});