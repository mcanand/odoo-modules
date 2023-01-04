odoo.define('gio_obstgemuese_theme.checkout', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');

publicWidget.registry.step_container = publicWidget.Widget.extend({
    selector: '.step-container',
    events:{
        'click .shipping_select':'onClickSelect',
    },
    onClickSelect:function(events){
        var id = $(events.target).parents('.shipping_select').attr('value')
        $('.shipping_select').removeClass('shipping_selected')
        $(events.target).parents('.shipping_select').addClass('shipping_selected')
    },
    });
});
