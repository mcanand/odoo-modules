odoo.define('order_location.checkout', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    var session = require('web.session');
    var utils = require('web.utils');
    var timeout;
    var ajax = require('web.ajax');
    var ServicesMixin = require('web.ServicesMixin');
    var rpc = require('web.rpc');


    publicWidget.registry.crust_checkout = publicWidget.Widget.extend({
    selector: '#crust_checkout',
    events: {
        'click #proceed_payment': '_proceed_payment',
        'change #cpart10_img input': '_check_value1',
        'change #cpart11_img input': '_check_value2',
        'change #cpart12_img input': '_check_value3',
        'change #cpart13_img input': '_check_value4',
        'change #cpart14_img input': '_check_value5',
        'change #cpart15_img input': '_check_value6',
        'change #cpart16_img input': '_check_value7',
        'change #cpart17_img input': '_check_value8',
        'change #cpart18_img input': '_check_value9',

    },

    init: function () {
        var self = this;
         console.log("proceed_payment")
        this._super.apply(this, arguments);
        $('.cpart10').hide();
        $('.cpart10').hide();
        $('.cpart10').hide();
//        delivery
        ajax.jsonRpc('/delivery/autofill/crust', 'call', {"ready": 1}).then(function(res) {
         console.log("proceed_payment",res)
            if(res === false){

            }
            else{
               if (res['name']) {
                    $("#cpart10_img input").val(res['name']);
                    $("#cpart11_img input").val(res['name']);
                    $("#partner_name").val(res['name']);
                    $("#partner_name_curb").val(res['name']);
                    $("#autofill_user_details").text(res['name']);
               }

                if (res['mobile']) {
                    $("#cpart12_img input").val(res['mobile']);
                    $("#partner_phone").val(res['mobile']);
                    $("#partner_phone_curb").val(res['mobile']);

               }

               if (res['email']) {
                    $("#cpart13_img input").val(res['email']);
                    $("#partner_email").val(res['email']);
                    $("#partner_email_curb").val(res['email']);

               }
               if (res['street']){
                    $("#cpart14_img input").val(res['street']);
               }
               if (res['street2']){
                    $("#cpart15_img input").val(res['street2']);
               }
               if (res['city']){
                    $("#cpart16_img input").val(res['city']);
               }
               if (res['country']){
                    $("#cpart17_img input").val(res['country']);
               }
               if (res['zip']){
                    $("#cpart18_img input").val(res['zip']);
               }
               }
               //var value = $('#cpart10_img input').val()
//               var validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
//               var validRegex1 = ("");
               /*if (value) {
                $('.cpart10_img').show();
                }else{
                $('.cpart10_img').hide();
                }*/
               //var value1 = $('#cpart11_img input').val()
               /*if (value) {
                $('.cpart11_img').show();
                }else{
                $('.cpart11_img').hide();
                }*/
                //var value1 = $('#cpart12_img input').val()
               /*if (value) {
                $('.cpart12_img').show();
                }else{
                $('.cpart12_img').hide();
                }*/
                //var value1 = $('#cpart13_img input').val()
               /*if (value) {
                $('.cpart13_img').show();
                }else{
                $('.cpart13_img').hide();
                }*/

        });

//        delivery ends

    },
    _check_value1: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
      /*if (value.length > 1){
              $('.cpart10_img').show();
        }
        else{
             $('.cpart10_img').hide();
        }*/
    },
    _check_value2: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
        /*if (value) {
            $('.cpart11_img').show();
        }else{
            $('.cpart11_img').hide();
        }*/
    },
     _check_value3: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
        var phoneno = /(\+\d{1,3}\s?)?((\(\d{3}\)\s?)|(\d{3})(\s|-?))(\d{3}(\s|-?))(\d{4})(\s?(([E|e]xt[:|.|]?)|x|X)(\s?\d+))?/g;
        console.log("phonee",phoneno);
        console.log("phonee",value.match(phoneno));
//        console.log("phonee",value.match(phoneno)[0].length);
        if (value.match(phoneno)){
            if (value.match(phoneno) !== null){
                console.log('yhgfkjhgfjhkgh')
                $('.cpart12_img').show();
            }
        }
        else{
             $('.cpart12_img').hide();
        }
        var regExp = /[a-zA-Z]/g;
        if(regExp.test(value)){
            $('.cpart12_img').hide();
        }
//        else{
//            $('.cpart12_img').show();
//        }
//        if (value) {
//             $('.cpart12_img').show();
//       }
    },
    _check_value4: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
        var validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;

      if (value.match(validRegex)) {
            $('.cpart13_img').show();
      }else{
        $target.val('');
         $('.cpart13_img').hide();
      }
    },
    _check_value5: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
        if (value) {
            $('.cpart14_img').show();
        }else{
            $('.cpart14_img').hide();
        }
    },
    _check_value6: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
        if (value) {
            $('.cpart15_img').show();
        }else{
            $('.cpart15_img').hide();
        }
    },
    _check_value7: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
        if (value) {
            $('.cpart16_img').show();
        }else{
            $('.cpart16_img').hide();
        }
    },
    _check_value8: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
        if (value) {
            $('.cpart17_img').show();
        }else{
            $('.cpart17_img').hide();
        }
    },
    _check_value9: function (ev){
        var $target = $(ev.currentTarget);
        var value = $target.val();
//        if (value) {
        if(value.match(/^-?\d+$/)){
            $('.cpart18_img').show();
        }else{
            $('.cpart18_img').hide();
        }
    },


    pass_function: function(){
    },
    _check_all_values: function (){
        var valid = true
        var first_name = $('#cpart10_img input').val();
        var last_name = $('#cpart11_img input').val();
        var phone = $('#cpart12_img input').val();
        var email = $('#cpart13_img input').val();

        if (first_name && last_name) {
           this.pass_function();
        }else{
            valid = false;
        }
        var phoneno = /(\+\d{1,3}\s?)?((\(\d{3}\)\s?)|(\d{3})(\s|-?))(\d{3}(\s|-?))(\d{4})(\s?(([E|e]xt[:|.|]?)|x|X)(\s?\d+))?/g;
        if (phone.match(phoneno)){
               this.pass_function();
        }else{
            valid = false;
        }

        var regExp = /[a-zA-Z]/g;
        if(regExp.test(phone)){
            valid = false;
        }
        else{
            this.pass_function();
            }

        var validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
        if (email.match(validRegex)) {
            this.pass_function();
        }else{
            valid = false;
        }

        return valid
    },

    _proceed_payment: function (ev){
        var self = this;
        var $target = $(ev.currentTarget);
        return $.when(this._check_all_values()).then(function (result) {
            console.log("resultsssss",result)
            if(!result){
                       swal(
                          'Validation Error',
                          'Please check the fields',
                          'error'
                        )
            }else{
                var first_name = $('#cpart10_img input').val();
                var last_name = $('#cpart11_img input').val();
                var phone = $('#cpart12_img input').val();
                var email = $('#cpart13_img input').val();
                var email_confirmation = $('#email_confirmation').val();
                var sms_confirmation = $('#sms_confirmation').val();
                var contactless_confirmation = $('#contactless_confirmation').val();
                var order_id = $('#order_id').val();
                var location =  window.location.href;
                var is_address = location.includes('shop/address');
                var is_checkout = location.includes('shop/checkout');
                var d_type = ""
                if (is_address === true){
                    d_type = "public"
                }
                if (is_checkout === true){
                    d_type = "user"
                }
                if (order_id) {
                    ajax.jsonRpc('/save/checkout', 'call', {
                                "order_id": order_id,
                                "partner_name":first_name + last_name,
                                "partner_phone":phone,
                                "partner_email":email,
                                "delivery_type":d_type,
                                "email_confirmation":email_confirmation,
                                "sms_confirmation":sms_confirmation,
                                "contactless_confirmation":contactless_confirmation,

                    }).then(function(res) {
                            if (res) {
                                window.location.href = "/shop/payment"
                            }else{
                                 swal(
                                      'Validation Error',
                                      'Sorry contact is not saved',
                                      'error'
                                    )
                            }
                    });

                }
            }
        });

    },



   });
   });