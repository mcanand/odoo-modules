odoo.define('create_pizza.custom_pizza', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
var core = require('web.core');
var ajax = require('web.ajax');
var QWeb = core.qweb;
var _t = core._t;

publicWidget.registry.cppage = publicWidget.Widget.extend({
selector: '.cppage',
    events: {
        'click .drop_down':'_drop_btn',
        'click .pluss':'_c_plus',
        'click .minuss':'_c_minus',
        'click .plus':'_cr_plus',
        'click .minus':'_cr_minus',


    },
    init:function(){
        var size_p_id = $('.size_dough').find(":selected").attr('data-size-id')
        var size_p_name = $('.size_dough').find(":selected").attr('data-size-p-name')
        var size_p_price = $('.size_dough').find(":selected").attr('data-size-p-price')
        $('.products_append').append("<div class='product_apnd row mt-4 font_popins size"+size_p_id+"'><div class='col-5'></div><div class='col p-0'><p>"+size_p_name+"</p></div><div class='col-2 p-0 p_price'><p class='float-right'>$&#160;<input type='hidden' class='t_price' value='"+parseFloat(size_p_price).toFixed(2)+"'></input>"+parseFloat(size_p_price).toFixed(2)+"</p></div></div>")
        var sauce_id = $('.sauce').find(":selected").attr('data-sauce-id')
        var sauce_name = $('.sauce').find(":selected").attr('data-sauce-p-name')
        var sauce_price = $('.sauce').find(":selected").attr('data-sauce-p-price')
        $('.products_append').append("<div class='product_apnd row mt-4 font_popins sauce"+sauce_id+"'><div class='col-5'></div><div class='col p-0'><p>"+sauce_name+"</p></div><div class='col-2 p-0 p_price'><p class='float-right'>$&#160;<input type='hidden' class='t_price' value='"+parseFloat(sauce_price).toFixed(2)+"'></input>"+parseFloat(sauce_price).toFixed(2)+"</p></div></div>")
//        console.log($('.products_append').children().children('.p_price').children('p').children('.t_price').html())
        var arr=[]
        $('.t_price').each(function(){
            arr.push($(this)[0].value)
        })
//        alert(arr)
    },

    _cr_plus:function(event){
        var input_value = $(event.target).siblings('.value').val()
        if(input_value<10){
            $(event.target).siblings('.value').val(parseInt(input_value)+1)
            var qty = $(event.target).siblings('.value').val()
            var array = []
            $('.t_price').each(function(){
            array.push($(this)[0].value)
            })
            var sum = eval(array.join("+"))
//            var sum = $('.total_price_input').val()
            var s = parseFloat(sum)*parseFloat(qty)
            $('.total_price').html('$&#160;'+parseFloat(s).toFixed(2))

        }
    },
    _cr_minus:function(){
        var input_value = $(event.target).siblings('.value').val()
        if(input_value>1){
            $(event.target).siblings('.value').val(parseInt(input_value)-1)
            var qty = $(event.target).siblings('.value').val()
//            var sum = $('.total_price_input').val()
//var qty = $(event.target).siblings('.value').val()
            var array = []
            $('.t_price').each(function(){
            array.push($(this)[0].value)
            })
            var sum = eval(array.join("+"))
            if(qty == 1){
                    $('.total_price').html('$&#160;'+parseFloat((sum)*1).toFixed(2))
            }
            else{
                var s = parseFloat(sum)*parseFloat(qty)
                $('.total_price').html('$&#160;'+parseFloat(s).toFixed(2))
            }

        }
    },
    _drop_btn:function(event){
        var target = $(event.target)
        target.siblings('.drop_content').toggle('slow')
    },
    _c_plus:function(event){
        var input_value = $(event.target).siblings('.value').val()
        if($('.selected').length < 6){
            if(input_value<2){
            $(event.target).siblings('.value').val(parseInt(input_value)+1)

            }
            var new_input_value = $(event.target).siblings('.value').val()
            if(new_input_value >=1){
                $(event.target).parents('.drop_content').addClass("selected")
                var product_id = $(event.target).siblings('.product').attr('data-product-id')
                var product_price = $(event.target).siblings('.product').attr('data-product-price')
                var product_name = $(event.target).siblings('.product').attr('data-product-name')
                var qty = $(event.target).siblings('.value').val()
                var len = $(event.target).parents('.drop_content').parents('.drop_down').children('.drop_btn').children('.selected').length
                if(len!=0){
                    $(event.target).parents('.drop_content').parents('.drop_down').children('.drop_btn').children('.dot_count').html(len)
                }

                if($('.product_apnd').hasClass(product_id)==true){
                    var p_total = parseFloat(product_price)*parseFloat(qty)
                     $('.'+product_id).children('.p_price').children('p').children('.t_price').val(parseFloat(p_total).toFixed(2))
                    console.log($('.'+product_id).children('.p_price').children('p').children('.replace').html('$&#160;'+p_total.toFixed(2)))
                    $('.p_qty'+product_id).val(qty)
                }
                else{
//                  $('.products_append').hide().slideDown();
                    var p_total = parseFloat(product_price)*parseFloat(qty)
                    $('.products_append').append("<div class='product_apnd row mt-4 font_popins "+product_id+"'><div class='col-5'></div><div class='col p-0'><p>"+product_name+"</p></div><div class='col-2 p-0 p_price'><p class='float-right'><input type='hidden' class='t_price' value='"+parseFloat(p_total).toFixed(2)+"'></input><span class='replace'>$&#160;"+parseFloat(product_price).toFixed(2)+"</span><input type='hidden' class='p_qty"+product_id+"' name='"+product_id+"' value='"+qty+"'></input></p></div></div>")
                    $('.'+product_id).hide(1, function(){ $(this).slideDown(200)});

                }
            }
            var t_selected = $('.extras').children('.drop_down').children('.drop_btn').children('.selected').length
            $('.choose').html(6-t_selected)
        }
        else if($(event.target).parents().hasClass('selected')){
            if(input_value<2){
            var product_price = $(event.target).siblings('.product').attr('data-product-price')
            var product_id = $(event.target).siblings('.product').attr('data-product-id')

            $(event.target).siblings('.value').val(parseInt(input_value)+1)

            var qty = $(event.target).siblings('.value').val()
            $('.p_qty'+product_id).val(qty)
            var p_total = parseFloat(product_price)*parseFloat(qty)
            $('.'+product_id).children('.p_price').children('p').children('.t_price').val(parseFloat(p_total).toFixed(2))
            $('.'+product_id).children('.p_price').children('p').children('.replace').html('$&#160;'+parseFloat(p_total).toFixed(2))

            }
        }

    },
    _c_minus:function(event){
       var input_value = $(event.target).siblings('.value').val()
       var product_id = $(event.target).siblings('.product').attr('data-product-id')
       var product_price = $(event.target).siblings('.product').attr('data-product-price')

       var qty = $(event.target).siblings('.value').val()
       if(input_value>0){
            $(event.target).siblings('.value').val(parseInt(input_value)-1)
            var qty_m = $(event.target).siblings('.value').val()
            var val = $(event.target).siblings('.value').val()
            var p_total = parseFloat(product_price) * parseFloat(val)
            $('.'+product_id).children('.p_price').children('p').children('.t_price').val(p_total.toFixed(2))
            $('.'+product_id).children('.p_price').children('p').children('.replace').html('$&#160;'+p_total.toFixed(2))
            $('.p_qty'+product_id).val(qty_m)
        }
        var new_input_value = $(event.target).siblings('.value').val()
       if(new_input_value == 0){
            $(event.target).parents('.drop_content').removeClass("selected")
            var len = $(event.target).parents('.drop_content').parents('.drop_down').children('.drop_btn').children('.selected').length
            var t_selected = $('.extras').children('.drop_down').children('.drop_btn').children('.selected').length
            $('.choose').html(6-t_selected)
            if(len!=0){
                $(event.target).parents('.drop_content').parents('.drop_down').children('.drop_btn').children('.dot_count').html(len)
            }
            else{
                $(event.target).parents('.drop_content').parents('.drop_down').children('.drop_btn').children('.dot_count').html("")
            }
            var product_id = $(event.target).siblings('.product').attr('data-product-id')
            var product_price = $(event.target).siblings('.product').attr('data-product-price')
            var qty = $(event.target).siblings('.value').val()
             if($('.product_apnd').hasClass(product_id)==true){
                $('.'+product_id).slideUp(200, function(){ $(this).remove();});
             }
       }
    }
    });
    $(".size_dough").on('focus', function (e) {
        var ddl = $(this);
        ddl.data('previous', ddl.find(":selected").attr('data-size-id'));
    }).on('change', function (e) {
        var ddl = $(this);
        var previous = ddl.data('previous');
//        alert(previous)
//        ddl.data('previous', ddl.val());
        if($('.product_apnd').hasClass('size'+previous)==true){
            $('.size'+previous).slideUp(20, function(){ $(this).remove()});
            var size_p_id = $('.size_dough').find(":selected").attr('data-size-id')
            var size_p_name = $('.size_dough').find(":selected").attr('data-size-p-name')
            var size_p_price = $('.size_dough').find(":selected").attr('data-size-p-price')
            $('.products_append').append("<div class='product_apnd row mt-4 font_popins size"+size_p_id+"'><div class='col-5'></div><div class='col p-0'><p>"+size_p_name+"</p></div><div class='col-2 p-0 p_price'><p class='float-right'>$&#160;<input type='hidden' class='t_price' value='"+parseFloat(size_p_price).toFixed(2)+"'></input>"+parseFloat(size_p_price).toFixed(2)+"</p></div></div>")
            $('.size'+size_p_id).hide(1, function(){ $(this).slideDown(200)});
            $(".col_pad").focus()
        }
    });
    $(".sauce").on('focus', function (e) {
        var ddl = $(this);
        ddl.data('previous', ddl.find(":selected").attr('data-sauce-id'));
    }).on('change', function (e) {
        var ddl = $(this);
        var previous = ddl.data('previous');
//        alert($('.product_apnd').hasClass('sauce'+previous))
//        ddl.data('previous', ddl.val());
        if($('.product_apnd').hasClass('sauce'+previous)==true){
            $('.sauce'+previous).slideUp(20, function(){ $(this).remove()});
            var sauce_p_id = $('.sauce').find(":selected").attr('data-sauce-id')
            var sauce_p_name = $('.sauce').find(":selected").attr('data-sauce-p-name')
            var sauce_p_price = $('.sauce').find(":selected").attr('data-sauce-p-price')
            $('.products_append').append("<div class='product_apnd row mt-4 font_popins sauce"+sauce_p_id+"'><div class='col-5'></div><div class='col p-0'><p>"+sauce_p_name+"</p></div><div class='col-2 p-0 p_price'><p class='float-right'>$&#160;<input type='hidden' class='t_price' value='"+parseFloat(sauce_p_price).toFixed(2)+"'></input>"+parseFloat(sauce_p_price).toFixed(2)+"</p></div></div>")
            $('.sauce'+sauce_p_id).hide(1, function(){ $(this).slideDown(200)});
            $(".col_pad").focus()
        }
    });
        $("body").on('DOMSubtreeModified', ".products_append", function() {
//        alert('changed');
        var array = []
        var qty = $('.input_txt_cart').val()
        $('.t_price').each(function(){
            array.push($(this)[0].value)
        })
        var sum = eval(array.join("+"))
        $('.total_price').html('$&#160;'+parseFloat(sum*qty).toFixed(2))
        $('.total_price_input').val(parseFloat(sum*qty).toFixed(2))
        console.log("sunm",sum)

    });
});