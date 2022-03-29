odoo.define('website_coupons.website_coupons', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    var session = require('web.session');
    var utils = require('web.utils');
    var timeout;
    var ajax = require('web.ajax');

    publicWidget.registry.show_coupon = publicWidget.Widget.extend({
        selector: '.show_coupon',
        events: {
        },
    //    /**
    //     * @constructor
    //     */
        init: function () {
            var self = this;
            var location =  window.location.pathname;
            console.log("XCHKL", location)
            if (window.location.pathname === '/shop/payment'){
                console.log("XCHKL")
                $(".show_coupon").show();
            }
            else{
                console.log("CVNME")
                $(".show_coupon").hide();
            }
            this._super.apply(this, arguments);

        },

    });
});