odoo.define('gio_obstgemuese_theme.panorama_view_config', function (require) {
"use strict";

var ajax = require("web.ajax");
var rpc = require('web.rpc');

      ajax.jsonRpc('/get/panorama/config', 'call', {}).then(function (result){
             if(result){
                var config = result[0]
                var hotspots = result[1]
                if(config.auto_rotate == true){
                    var rotate_value = config.auto_rotate_value
                }
                else{
                    var rotate_value = 0
                }
                var viewer = pannellum.viewer('load_panorama_360_view', {
                    "type": "equirectangular",
                    "panorama": "data:image/png;base64," + config.panorama_image,
                    "autoLoad": true,
                    "compass": false,
                    "showFullscreenCtrl": false,
                    "showZoomCtrl": false,
                    "autoRotate": rotate_value,
                })
                viewer.on('mousedown', function(event) {
                    var coords = viewer.mouseEventToCoords(event);
                    console.log(coords)
                     $('.selected_pitch').html(coords[0])
                     $('.selected_yaw').html(coords[1])
                });

             }
        });
        $('.js_action_done').click(function(events){
                    var pitch = $('.selected_pitch').html()
                    var yaw = $('.selected_yaw').html()
                    var rec_id = $(events.target).children().html()
                    rpc.query({
                        method: 'action_done',
                        model: 'panorama.hotspot.wizard',
                        args: [[],pitch,yaw,parseInt(rec_id)],
                    }).then(function(result){
                        if(result){
                            $(events.target).parents('.o_dialog').hide()
                            location.reload();
                        }
                    });
                });
        $('.close').click(function(){
            location.reload();
        });
});
