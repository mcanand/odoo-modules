odoo.define('gio_obstgemuese_theme.shop', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');

publicWidget.registry.shop = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events:{
        'change form.js_attributes input, form.js_attributes select': '_onChangeAttribute',
        'change .filter_select_category':'_onChangeFilterSelectCategory',
        'click .obst_mob_dots':'_onClickOpenFilter',
        'click .filter_use':'_onClickFilterUse',
    },
    start:function(){
        var path_name = window.location.pathname
        if(path_name.includes('category')){
            var select_val = parseInt((path_name.split('/')[3]).split('-')[1])
            $('.filter_select_category').val(select_val)
        }
    },
    _onChangeAttribute:function(ev){
        if (!ev.isDefaultPrevented()) {
            ev.preventDefault();
            $(ev.currentTarget).closest("form").submit();
        }
    },
    _onChangeFilterSelectCategory:function(ev){
        var id = $(ev.target).val()
        var name =$( ".filter_select_category option:selected" ).text();
        var cat = name+'-'+id

        let host = location.host;
        var url = location.href
        if(url.includes('/shop')){
                location.href = 'http://'+host+"/shop/category/"+cat
        }
        if(name == 'All Products'){
            location.href = 'http://'+host+'/shop'
        }
    },
    _onClickOpenFilter:function(){
        $('.obst_product_filter').addClass('toggle_active')
        $('.obst_product_filter').css({'display':'flex'})
        $('.obst_product_filter').animate({width: '100%'},500);
    },
    _onClickFilterUse:function(){
        $('.obst_product_filter').animate({width: '0%'},500);
        $('.obst_product_filter').css({'display':'none'})
        $('.obst_product_filter').removeClass('toggle_active')
    },
    });
});