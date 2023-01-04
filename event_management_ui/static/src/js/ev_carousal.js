odoo.define('event_management_ui.ev_carousal', function(require){
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var ajax = require('web.ajax');
var rpc = require('web.rpc');
var _t = core._t;
var QWeb = core.qweb;
var publicWidget = require('web.public.widget');

publicWidget.registry.wrap = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {

    },
    start:function(){
        $('.enable_pickup').hide()
        $('.enable_delivery').hide()
        ajax.jsonRpc('/get/current/website', 'call', {})
            .then(function (result) {
            if(result){
                if(result.enable_pickup == true){
                    $('.enable_pickup').show()
                }
                if(result.enable_delivery == true){
                    $('.enable_delivery').show()
                }
            }
        });
    },

    });
});