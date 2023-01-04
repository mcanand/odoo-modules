odoo.define('event_user_creation.event_selection.js', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
const Dialog = require('web.Dialog');
const {_t, qweb} = require('web.core');
const ajax = require('web.ajax');
const session = require('web.session');

publicWidget.registry.tickect_selction = publicWidget.Widget.extend({
    selector: '#o_wevent_tickets_collapse',
    events: {
        'click .custom-select':'_onChange_custom_select'
    },
    start:function(){
        console.log('sssssssss',$('custom-select').length)
    },
    _onChange_custom_select:function(event){
        var select = $('.custom-select')
        var arr = []
        $('.custom_option_select').remove()
        _.each(select,function(select){
            if($(select).val() > 0){
                arr.push($(select).val())
            }
            if(arr.length > 3){
                $(event.target).val(0)
                $(event.target).parents('.row').append("<div class='col custom_option_select' style='color:#9d7500;'>You can only select 3 options</div>")
            }
        });

    },
   })
});