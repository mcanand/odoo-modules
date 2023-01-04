odoo.define('gio_obstgemuese_theme.home', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');

publicWidget.registry.home = publicWidget.Widget.extend({
    selector: '#wrap',
    events:{
        'click .panorama_popup_close':'_onClickClosePnoPopup',
    },
    start:function(){
      var self = this
      ajax.jsonRpc('/get/panorama/config', 'call', {}).then(function (result) {
             if(result){
                var config = result[0]
                var hotspots = result[1]
                if(config.auto_rotate == true){
                    var rotate_value = config.auto_rotate_value
                }
                else{
                    var rotate_value = 0
                }
                var hotspot_array = []
                _.each(hotspots,function(hotspots){
                    var val = { "pitch": hotspots.pitch,
                            "yaw": hotspots.yaw,
                            "cssClass": "custom-hotspot",
                            "createTooltipFunc": self.hotspot,
                            "createTooltipArgs": "product",
                            "clickHandlerArgs": {'product_id':hotspots.product_id},
                            "clickHandlerFunc": self.onclick_hotSpot,}
                    hotspot_array.push(val)
                })
                pannellum.viewer('panorama-360-view', {
                    "type": "equirectangular",
                    "panorama": "data:image/png;base64," + config.panorama_image,
                    "autoLoad": true,
                    "compass": false,
                    "showFullscreenCtrl": false,
                    "showZoomCtrl": false,
                    "mouseZoom":false,
                    "autoRotate": rotate_value,
                    "hotSpots": hotspot_array
             })
             }
        });
    },
    onclick_hotSpot:function(ev,clickHandlerArgs){
        var product_id = clickHandlerArgs.product_id
        ajax.jsonRpc('/get/product/details', 'call', {'product_id':product_id})
            .then(function (result) {
                if(result){
                    $('.panorama_popup').show()
                    $('.pano_val').remove()
                    $('.pano_vals').append("<div class='row pano_val'><div class='col-md-12 text-center mt-3'><img src='data:image/png;base64,"+result.image+"' class='pano_click_product_img'/></div><div class='col-md-12 text-center mt-2'><h2 class='GT_Pressura_Pro_Mono'>"+result.name+"</h2></div><div class='col-md-12 text-center mt-2'><h3 class='GT_Pressura_Pro_Mono'>"+result.price+"</h3></div><div class='col-md-12 text-center mt-2'><a href='#' class='buy_link GT_Pressura_Pro_Mono'>buy product</a></div><div class='col-md-12 text-center mt-2'><p class='GT_Pressura_Pro_Mono'>"+result.description+"</p></div><div class='col-md-12 text-center mt-2'><a href='/shop' class='GT_Pressura_Pro_Mono ob_in_the_cart pano_shop'>To The Shop</a></div></div>")
                }
            });
        },
    _onClickClosePnoPopup:function(){
        $('.panorama_popup').hide()
    },
    hotspot:function(hotSpotDiv, args){
        hotSpotDiv.classList.add('plus_border');
        var span = document.createElement('span');
        span.innerHTML = "<i class='fa fa-plus d-block text-white plus_icon'/>";
        hotSpotDiv.appendChild(span);
        span.style.width = span.scrollWidth - 20 + 'px';
        span.style.marginLeft = -(span.scrollWidth - hotSpotDiv.offsetWidth) / 2 + 'px';
        span.style.marginTop = -span.scrollHeight - 12 + 'px';
    },
    });

});
