odoo.define('invoice.action_button', function (require) {
"use strict";
var core = require('web.core');
var ListController = require('web.ListController');
var rpc = require('web.rpc');
var session = require('web.session');
var _t = core._t;
var Dialog = require('web.Dialog');

ListController.include({
   renderButtons: function($node) {
       this._super.apply(this, arguments);
           if (this.$buttons) {
             this.$buttons.find('.oe_action_button').click(this.proxy('action_def')) ;
           }
   },
   action_def: function () {
            var self =this
            var user = session.uid;
            var message ='Contacts Added To Marketing'
            var options = ''

            rpc.query({
                model: 'res.partner',
                method: 'click_btn_contact',
                args: [{'id':user}],
                }).then(function (result){
                    if(result==true){
                        Dialog.alert(this, message, options);
                    }

                });
            },
   });
});