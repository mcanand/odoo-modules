odoo.define('gio_obstgemuese_theme.header', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');

publicWidget.registry.header = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events:{
        'click .close_icon':'_onClickClose',
        'click .navbar-toggler':'_onClickToggle',
        'click .ob_nav_search':'_onClickSearchPop',
        'click .ob_search_close':'_onClickSearchClose',
        'focusin .ob_search_input':'_onFocusInSearch',
        'focusout .ob_search_input':'_onFocusOutSearch',
        'keyup .ob_search_input':'_onKeyUpSearch',
        'keydown .ob_search_input':'_onKeyDownSearch',
        'click .scroll_to_top':'_onclickScrollToTop',
        'scroll': '_onScroll',
        'mousewheel': '_onMousewheel',
         'click .ob_cart':'async _onClickOpenCart',
        },
        _onClickOpenCart:function(){
            $('.cart_container').addClass('toggle_active');
            $('#wrapwrap').css('overflow-y','hidden')
            $('.navbar').fadeIn(1000)
            this.load_cart()
            if($(window).width() < 750){
                $('.cart_container').animate({left: '0%'},1000);
            }
            else{
                $('.cart_container').animate({left: '65%'},1000);
            }
        },
        load_cart:function(){
        ajax.jsonRpc('/get/cart/values', 'call', {})
            .then(function (result) {
                if(result){
                   $('.item_count').html(result.length+' items')
                   $('.order_lines').remove()
                   _.each(result,function(result){
                        $('.order_line').append("<div class='col-md-12 order_lines order_lines_"+result.line_id+" pb-5'><div class='row'><div class='col-4'><img src='data:image/png;base64,"+result.product_img+"' t-options='{'widget': 'image',}' width='100%'/></div><div class='col-6 p-0'><h4 class='GT_Pressura_Pro_Mono'>"+result.product_name+"</h4><h4 class='GT_Pressura_Pro_Mono'><span>"+result.symbol+"</span>"+result.price+"</h4><span>"+result.variant+"</span>, <span>"+result.qty+" qty</span></div><div class='col-2'><img src='/gio_obstgemuese_theme/static/src/svg/08-trash2.svg' class='cart_trash'/><input type='hidden' value='"+result.line_id+"' class='line_id'></input></div></div></div>")
                   });
                }
            });
    },
    start:function(){
        var url=location.href
        if(url.includes("/shop")){
            $('.navbar').css({'position':'relative'})
            $('.navbar').css({'background':'white'})
        }
    },
    _onClickClose:function(){
         $('.close_icon').animate({opacity: '0'},400);
         $('.overlay').animate({width: '0%'},1000);
         $('#top_menu_collapse').animate({width: '0%'},1000);
         $('.overlay').hide(10)
         $('.overlay').removeClass('toggle_active')
    },
    _onClickToggle:function(){
        $('.close_icon').animate({opacity: '1'},400);
        $('.overlay').show()
        $('.overlay').animate({width: '100%',display:'block'},1000);
        $('.overlay').addClass('toggle_active')
        $('#top_menu_collapse').animate({width: '50%',display:'block'},1000);
    },
    _onClickSearchPop:function(){
        $('.ob_search_overlay').show()
        $('.ob_search_overlay').animate({height: '100%',display:'block'},500);
        $('.ob_search_overlay').addClass('toggle_active')
    },
    _onClickSearchClose:function(){
        $('.ob_search_overlay').animate({height: '0%'},1000);
        $('.ob_search_overlay').hide(10)
        $('.ob_search_overlay').removeClass('toggle_active')

    },
    _onFocusInSearch:function(){
        $('.search_box_input').animate({marginTop:'0%'},1000);
    },
    _onFocusOutSearch:function(){
        $('.search_box_input').animate({marginTop:'16%'},500);
    },
    _onKeyUpSearch:function(events){
        var target = $(events.target)
        var search_key = target.val()
        $('.ob_product_card').remove()
        ajax.jsonRpc('/get/products', 'call', { 'search_key':search_key })
        .then(function(result){
            if(result){
                _.each(result,function(result){
                    console.log('anand',typeof(result.image))
                    var img = "data:image/png;base64,"+result.image+""
                    $('.search_product_show').append("<div class='ob_product_card col-md-3 pt-2 pb-2'><div class='row'><div class=' col-md-12'><img src='"+img+"' class='ob_product_image w-100'/></div><div class='product_name col-md-12 text-center'><h4>"+result.name+"</h4><h5>"+result.price+"</h5></div></div></div>")
                });
            }
        });

    },
    _onKeyDownSearch:function(){
        $('.ob_product_card').remove()
    },
    _onclickScrollToTop:function(){
      $('html,body').animate({ scrollTop: 0 }, 400);
      return false;
    },
    _onScroll:function(events){
        var url=location.href
        if(url.includes("/shop")){
            $('.navbar').css({'position':'relative'})
            $('.navbar').css({'background':'white'})
        }
        var height = $(events.target).scrollTop()
        if(height <= 50){
           $('.navbar').css({'background':'transparent'})
        }
        else{
            $('.navbar').css({'position':'fixed'})
            $('.navbar').css({'background-color':'white'})
        }
        if($(window).width() > 600){
             if(height <= 50){
               $('.obst_product_filter').css({'position':'relative','background':'white'})
            }
            else{
                 $('.obst_product_filter').css({'position':'fixed'})
            }

        }
    },
    _onMousewheel:function(events){
        if($('.toggle_active').length == 0){
            if (events.originalEvent.wheelDelta >= 0) {
    //        Scroll up
                $('.navbar').fadeIn(1000)
                $('.obst_product_filter').css({'z-index':9,'top':'8%','width':'100%'})
                $('.obst_product_filter').fadeIn(1000)
            }
            else {
    //        scroll down
                $('.navbar').fadeOut(100)
                $('.obst_product_filter').fadeOut(100)
            }
        }
    },
    });
});
