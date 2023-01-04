                            odoo.define('event_management_ui.pickup', function(require){
'use strict';


var publicWidget = require('web.public.widget');
var core = require('web.core');
var ajax = require('web.ajax');
var rpc = require('web.rpc');
var _t = core._t;
var QWeb = core.qweb;
var publicWidget = require('web.public.widget');

publicWidget.registry.event_management_pickup = publicWidget.Widget.extend({
    selector: '.event_management_pickup',
    events: {
        'click .ev_pickup_button': '_onPickupBtn_click',
        'keyup .ev_pickup_input': '_onkeyUpPickupInput',
        'keydown .ev_pickup_input': '_onkeyDownPickupInput',
        'mouseover .pick_text': '_onMouseoverPickupInput',
        'click .location_js': '_onClickLocation',
    },

    _onPickupBtn_click:function(events){
        $(events.target).siblings('.ev_pickup_container').toggle('slow', function(){
            if($(this).is(':visible') == true) {
                $(events.target).children('span').children('.fa-angle-down').animate({ deg: 180 },{
                  duration: 200,
                  step: function(now) {
                    $(this).css({ transform: 'rotate(' + now + 'deg)' });
                  }
                });
            }
            if($(this).is(':visible') == false) {
                $(events.target).children('span').children('.fa-angle-down').animate({ deg: 0 },{
                  duration: 200,
                  step: function(now) {
                    $(this).css({ transform: 'rotate(' + now + 'deg)' });
                  }
                });
            }
        });
    },
    _onkeyUpPickupInput:function(events){
        var val = $(events.target).val()
        ajax.jsonRpc("/find/address", 'call', {'input': val}).then(function(data) {
        if (data){
            $('.pick_up_address').remove().hide('slow')
            _.each(data,function(x){
                 $('.ev_pick_up_address').append("<div style='display:none;' class='pick_up_address mt-1'><a href='#' class='pick_text'>"+x['name']+", "+x['street']+", "+x['street2']+", "+x['city']+", "+x['zip']+"</a></div>")
                 $('.pick_up_address').show('slow')
            })
        }
        });
    },
    _onkeyDownPickupInput:function(events){
        if(!$(events.target).val()){
            $('.pick_up_address').remove().hide('slow')
        }
    },
    _onMouseoverPickupInput:function(events){
        $('.ev_pickup_input').val($(events.target).html())
    },
    _onClickLocation:function(){
        window.location.href = '/delivery/location'
    },
    });
});