odoo.define('gio_obstgemuese_theme.login_register', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');

publicWidget.registry.login_register = publicWidget.Widget.extend({
    selector: '.oe_website_login_container',
    events:{
        'click .del_add_checkbox_js': '_onClickCheckboxShowShipping',
        'click .log_reg_btn': '_onClickLogin',
        'focusout .login_input':'_onFocusOutLoginInputs',
        'focusout .reg_input':'_onFocusOutRegisterInputs',
        'keyup .login_input':'_onKeyupInputValidation',
        'keyup .reg_input':'_onKeyupRegInputValidation',
        'click .privacy_policy_js':'_onClickPrivacyPolicy',
    },
    start:function(){
        $('.obst_sign_up_js').attr('disabled','disabled');
    },
    _onClickPrivacyPolicy:function(events){
        if($(events.target).is(':checked') == true){
            $('.obst_sign_up_js').removeAttr('disabled');
        }
        else{
            $('.obst_sign_up_js').attr('disabled','disabled');
        }
    },
    _onKeyupInputValidation:function(events){
        var input_id = $(events.target).attr('id')
        var value = $(events.target).val()
        if(input_id == 'login'){
            var pattern = new RegExp("^[_A-Za-z0-9-]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$");
            var result = pattern.test(value);
            if(result == false){
                $(events.target).parents().children('.validation_error_email').html("Please enter a valid email address.")
                $(events.target).css({'border':'1px solid #eeca00'})
                $(events.target).siblings('.input_close').css({'display':'block'})
                $(events.target).siblings('.input_tick').css({'display':'none'})
            }
            else{
                $(events.target).css({'border':'1px solid black'})
                $(events.target).parents().children('.validation_error_email').html("")
                $(events.target).siblings('.input_close').css({'display':'none'})
                $(events.target).siblings('.input_tick').css({'display':'block'})
            }

        }
         if(input_id == 'password'){
            if(value.length >= 8){
                $(events.target).css({'border':'1px solid black'})
                $(events.target).parents().children('.validation_error_password').html("")
                $(events.target).siblings('.input_close').css({'display':'none'})
                $(events.target).siblings('.input_tick').css({'display':'block'})
            }
            else{
                $(events.target).parents().children('.validation_error_password').html("password must contain 8 characters.")
                $(events.target).css({'border':'1px solid #eeca00'})
                $(events.target).siblings('.input_close').css({'display':'block'})
                $(events.target).siblings('.input_tick').css({'display':'none'})
            }
         }
    },
    _onKeyupRegInputValidation:function(events){
        var value = $(events.target).val()
        if(value.length >= 1){
            $(events.target).css({'border':'1px solid black'})
            $(events.target).parents().children('.validation_error').html("")
            $(events.target).siblings('.input_close').css({'display':'none'})
            $(events.target).siblings('.input_tick').css({'display':'block'})
        }
        else{
            $(events.target).parents().children('.validation_error').html("Please fill up the field.")
            $(events.target).css({'border':'1px solid #eeca00'})
            $(events.target).siblings('.input_close').css({'display':'block'})
            $(events.target).siblings('.input_tick').css({'display':'none'})
        }
    },
   _onClickCheckboxShowShipping:function(events){
        if($(events.target).is(':checked') == true){
            $('.shipping_address').toggle('slow')
        }
        else{
            $('.shipping_address').toggle('hide')
        }
   },
   _onClickLogin:function(){
        if($('.rem_me_checkbox').is(':checked')){

        }
   },
   _onFocusOutLoginInputs:function(events){
        if(!$('.login_input:first').val() && !$('.login_input:last').val()){
            $('.login_input').css({'border':'1px solid #eeca00'})
        }
//        if($(events.target).val()){
//            $(events.target).css({'border':'1px solid black'})
//        }
//        else{
//            $(events.target).css({'border':'1px solid #eeca00'})
//        }
   },
   _onFocusOutRegisterInputs:function(events){
        if(!$('.reg_input').val()){
            $('.reg_input').css({'border':'1px solid #eeca00'})
        }
        if($(events.target).val()){
            $(events.target).css({'border':'1px solid black'})
        }
        else{
            $(events.target).css({'border':'1px solid #eeca00'})
        }
   },
   });
});
