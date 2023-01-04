odoo.define('gio_obstgemuese_theme.portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');
var newsletter = require('gio_obstgemuese_theme.newsletter');
console.log(publicWidget)

publicWidget.registry.portal = publicWidget.Widget.extend({
    selector: '.ob_portal_wrap',
    events:{
        'click .ob_portal_tab_links':'_onClickOpenTab',
        'click .js_overview_check_newsletter':'_onClickOverviewNewClick',
        'click .js_show_order_line':'_onClickShowOrderLine',
        'click .profile_image_ob_add':'_onClickAddImage',
        'click .save_first_last_name_picture_submit':'_onClickSaveFl_name_picture',
        'change .ob_add_image':'_onChange_image',
        'click .ob_portal_pop_up_close':'ob_portal_pop_up_close',
        'click .change_email':'change_email_toggle',
        'click .change_password':'change_password_toggle',
        'click .email_change_save':'_change_email_save',
        'click .password_change_save':'_change_password_save',
    },
    _onClickOverviewNewClick:function(events){
        if ($(events.target).is(":checked")){
            publicWidget.registry.newsletter_subscribe.prototype
            ._onSubscribeClick()
        }
    },
    _change_password_save:function(){
        var new_password = $('.new_password').val()
        var conf_password = $('.conf_new_password').val()
        var password = $('.curr_password_p').val()
        var html = $('#wrap').last()
        var head = "Validation Error"
        if(!new_password || !conf_password || !password){
            var text = "fill up the fields"
            this.portal_pop_up(html,head,text)
        }
        else if(new_password != conf_password){
            var text = "Password does not match"
            this.portal_pop_up(html,head,text)
        }
        else{
            ajax.jsonRpc('/change/password', 'call', {conf_password,password})
            .then((result) => {
                if(result == 'change'){
                    var head = "Successful change"
                    var text = "Password has successfully changed"
                    this.portal_pop_up(html,head,text)
                    window.location.href = "/web/login"
                }
                else if(result == 'nochange'){
                    var head = "Alert"
                    var text = "Password does not change please try again"
                    this.portal_pop_up(html,head,text)
                }
                else if(result == 'error'){
                    var head = "Alert"
                    var text = "Incorrect Password, Please enter right password"
                    this.portal_pop_up(html,head,text)
                }
            });
        }
    },
    _change_email_save:function(events){
        var new_email = $('.new_email').val()
        var conf_new_email = $('.conf_new_email').val()
        var password = $('.curr_password_e').val()
        var html = $('#wrap').last()
        var head = "Validation Error"
        if(this.email_validation(new_email) != true && this.email_validation(conf_new_email)!=true){
            var text = "Enter correct email address"
            this.portal_pop_up(html,head,text)
        }
        else if(!new_email || !conf_new_email || !password){
            var text = "fill up the fields"
            this.portal_pop_up(html,head,text)
        }
        else if(new_email != conf_new_email){
            var text = "E-mails does not match"
            this.portal_pop_up(html,head,text)
        }
        else{
            ajax.jsonRpc('/change/email', 'call', {conf_new_email,password}).then((result) => {
                if(result == 'exist'){
                    var head = "Alert"
                    var text = "E-mail already exists"
                    this.portal_pop_up(html,head,text)
                }
                else if(result == 'change'){
                    var head = "Successful change"
                    var text = "E-mail has successfully changed"
                    this.portal_pop_up(html,head,text)
                    window.location.href = "/web/login"
                }
                else if(result == 'nochange'){
                    var head = "Alert"
                    var text = "E-mail does not change please try again"
                    this.portal_pop_up(html,head,text)
                }
                else if(result == 'error'){
                    var head = "Alert"
                    var text = "Incorrect Password, Please enter right password"
                    this.portal_pop_up(html,head,text)
                }
            });
        }
    },
    email_validation:function(val){
        var pattern = new RegExp("^[_A-Za-z0-9-]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$");
        var result = pattern.test(val);
        return result
        console.log(result)
    },
    change_password_toggle:function(){
        $('.change_password_container').toggle('slow');
        $('.change_email_container').hide('slow')
    },
    change_email_toggle:function(){
        $('.change_email_container').toggle('slow');
        $('.change_password_container').hide('slow')
    },
    _onClickSaveFl_name_picture:function(){
        var first_name = $('#save_first_last_name_picture #first_name').val()
        var last_name = $('#save_first_last_name_picture #Surname').val()
        if($('.profile_image_ob_add img').hasClass('is_changed')){
            var image = $('.profile_image_ob_add img').attr('src')
            $('.profile_image_ob_add img').removeClass('is_changed')
        }
        else{
            var image = false;
        }
        ajax.jsonRpc('/account/save/Fl_name_picture', 'call', {first_name,
        last_name,image}).then
        ((result)
        => {
            var html = $('#wrap').last()
            var head = "Successful change"
            var text = "You have successfully changed your name and profile picture."
            this.portal_pop_up(html,head,text)
        });
    },
    ob_portal_pop_up_close:function(){
        $('#ob_portal_pop_up').remove()
    },
/*    custom pop up use anywhere*/
    portal_pop_up:function(html,head,text){
        html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
    },
    _onChange_image:function(events){
        var image = $(events.target)[0].files[0]
        var reader  = new FileReader();
        $('.profile_image_ob_add img').addClass('is_changed');
         reader.onload = function () {
            var preview = $('.profile_image_ob_add img')
            var read_image = reader.result;
            preview.attr("src",read_image);
        }
         reader.readAsDataURL(image)
    },
    get_image:function(image){
        var preview = $('.profile_image_ob_add img')
        var reader  = new FileReader();
        reader.onload = function () {
            var read_image = reader.result;
            preview.src = read_image;
            return read_image
        }
        reader.readAsDataURL(image)
    },
    _onClickAddImage:function(events){
        $('.ob_add_image').click()
    },
    _onClickShowOrderLine:function(events){
         var order_id = $(events.target).attr('id')

         if($('#orderid_'+order_id).is(':visible')){
            $('#orderid_'+order_id).hide('slide')
            $(events.target).html('to show')
            $(events.target).css({'color':'black'})
         }
         else{
            $('#orderid_'+order_id).toggle('slow')
            $(events.target).html('hide')
            $(events.target).css({'color':'#eeca00'})
         }
    },
    start:function(){
        $("#defaultOpen").click();
    },
    _onClickOpenTab:function(events){
        var tab_id = $(events.target).val()
        var i
        var tab_content = $(".tab_content");
        _.each(tab_content, function(tab_content) {
            tab_content.style.display = 'none'
        });
//        var tab_links = $(".ob_portal_tab_links");
//         _.each(tab_links, function(tab_links) {
//            tab_links.className = tab_links.className.replace(" active","");
//        });

        $(".ob_portal_tab_links").removeClass('active')
        $('#'+tab_id).show()
        $('#'+tab_id).load(window.location.href +' #'+tab_id);
        $(events.target).addClass('active')

//        events.currentTarget.className += "active";
    },
    });
});
