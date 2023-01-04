odoo.define('event_management_ui.location_delivery', function(require){
'use strict';


var publicWidget = require('web.public.widget');
var core = require('web.core');
var ajax = require('web.ajax');
var rpc = require('web.rpc');
var _t = core._t;
var QWeb = core.qweb;
var publicWidget = require('web.public.widget');
let map;
let markers = [];
publicWidget.registry.location_delivery = publicWidget.Widget.extend({
    selector: '.location_delivery',
    events: {
        'change .ev_delivery_date_js': '_onChangeDeliveryDate',
        'change .ev_delivery_time_js': '_onChangeDeliveryTime',
        'click .ev_button_close_js': '_onClickCloseButton',
        'click .map_night_switch_check_js': '_onClickNightModeMap',
    },
    _get_company_location:function(){
        var r = []
        var self = this
        var result = ajax.jsonRpc('/company/location', 'call', {})
            .then(function (result) {
            if(result){
                return result
            }
        });
        return result
    },
    start:function(){
        this.initMap()
    },

    _onChangeDeliveryDate:function(events){
        var date = $(events.target).val()
        ajax.jsonRpc('/delivery/date/change', 'call', {'date':date})
            .then(function (result) {
            if(result){
                $('.time_from').html(result.time_from)
                $('.time_to').html(result.time_to)
            }
        });
        _.each($('.ev_company_location').val(),function(m){
            console.log('fuc',m)
        })

    },
    _onChangeDeliveryTime:function(events){
    var date = $('.ev_delivery_date_js').val()
    if(date){
        var time_from = $('.time_from').html()
        var time_to = $('.time_to').html()
        var input_time = $(events.target).val()
        var input_time_float = this.convert_time_float(input_time)
        var time_from_float = this.convert_time_float(time_from)
        var time_to_float = this.convert_time_float(time_to)
        if(input_time_float < time_from_float){
            var head = "Validation Error"
            var text = "Choose time from "+time_from+" to "+time_to
            this.ev_pop_up(head, text)
        }
        else if(input_time_float > time_to_float){
            var head = "Validation Error"
            var text = "Choose time from "+time_from+" to "+time_to
            this.ev_pop_up(head, text)
        }
       }
       else{
           var head = "Validation Error"
           var text = "choose date"
           this.ev_pop_up(head, text)
       }
    },
    convert_time_float:function(val){
        var val = parseInt(val.split(":")[0]) + parseInt(val.split(":")[1])/60;
        return val
    },
    ev_pop_up:function(head,text){
        $('.location_delivery').last().append("<div id='ev_pop_up' class='ev_pop_up'><div class='ev_pop_up-content text-center'><i class='fa fa-times-circle d-block' style='font-size:5vw;color:red;'></i><h1 class='text-dark'>"+head+"</h1><p class='text-dark'>"+text+"</p><button class='btn ev_button ev_button_close_js'>ok</button></div></div>");
    },
    _onClickCloseButton:function(){
        $('#ev_pop_up').remove()
    },
     initMap:function () {
        var self = this
        var comp_loc = this._get_company_location()
        map = new google.maps.Map(document.getElementById("map"), {
            center: { lat: comp_loc[0].latitude, lng: comp_loc[0].longitude },
            zoom: 8,
        });
        comp_loc.then(function(comp_loc){
            var citymap = []
            _.each(comp_loc, function(comp){
                var company_name = comp.name
                console.log(comp.delivery_radius)
                var vals = {
                    company_name:{center:{lat : comp.latitude, lng : comp.longitude},radius : comp.delivery_radius },
                }
                citymap.push(vals)

                });


        for (const city in citymap) {
//              const marker = new google.maps.Marker({
             /* console.log('kkkkkk',citymap[city].company_name.center)
                    position: citymap[city].company_name.center,
                    map: map,
              });*/
              const cityCircle = new google.maps.Circle({
              strokeColor: "#FF0000",
              strokeOpacity: 0.8,
              strokeWeight: 2,
              fillColor: "#FF0000",
              fillOpacity: 0.25,
              map,
              center: citymap[city].company_name.center,
              radius: (citymap[city].company_name.radius) * 1000,
            });
        }
        self.click_add_marker_lat_lng()
        });

    },

    addMarker:function (location = google.maps.LatLngLiteral, map=google.maps.Map) {
          // Add the marker at the clicked location, and add the next-available label
          // from the array of alphabetical characters.
          const marker = new google.maps.Marker({
            position: location,
            map: map,
          });
          markers.push(marker);
    },
    deleteMarkers:function(){
       this.setMapOnAll(null);
       markers = [];
    },
    setMapOnAll:function(map = google.maps.Map | null) {
      for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
      }
    },

    _onClickNightModeMap:function(){
        if ($('.map_night_switch_check_js').is(":checked")==true){
            this.mapNightMode()
        }
        else{
             this.initMap()
        }
    },
     mapNightMode:function(){
     var self = this
        var comp_loc = this._get_company_location()
        comp_loc.then(function(comp){
        const map = new google.maps.Map(document.getElementById("map"), {
          center: { lat: comp[0].latitude, lng: comp[0].longitude },
          zoom: 8,
          styles: [{ elementType: "geometry", stylers: [{ color: "#242f3e" }] },
                { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
                { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
                {
                  featureType: "administrative.locality",
                  elementType: "labels.text.fill",
                  stylers: [{ color: "#d59563" }],
                },
                {
                  featureType: "poi",
                  elementType: "labels.text.fill",
                  stylers: [{ color: "#d59563" }],
                },
                {
                  featureType: "poi.park",
                  elementType: "geometry",
                  stylers: [{ color: "#263c3f" }],
                },
                {
                  featureType: "poi.park",
                  elementType: "labels.text.fill",
                  stylers: [{ color: "#6b9a76" }],
                },
                {
                  featureType: "road",
                  elementType: "geometry",
                  stylers: [{ color: "#38414e" }],
                },
                {
                  featureType: "road",
                  elementType: "geometry.stroke",
                  stylers: [{ color: "#212a37" }],
                },
                {
                  featureType: "road",
                  elementType: "labels.text.fill",
                  stylers: [{ color: "#9ca5b3" }],
                },
                {
                  featureType: "road.highway",
                  elementType: "geometry",
                  stylers: [{ color: "#746855" }],
                },
                {
                  featureType: "road.highway",
                  elementType: "geometry.stroke",
                  stylers: [{ color: "#1f2835" }],
                },
                {
                  featureType: "road.highway",
                  elementType: "labels.text.fill",
                  stylers: [{ color: "#f3d19c" }],
                },
                {
                  featureType: "transit",
                  elementType: "geometry",
                  stylers: [{ color: "#2f3948" }],
                },
                {
                  featureType: "transit.station",
                  elementType: "labels.text.fill",
                  stylers: [{ color: "#d59563" }],
                },
                {
                  featureType: "water",
                  elementType: "geometry",
                  stylers: [{ color: "#17263c" }],
                },
                {
                  featureType: "water",
                  elementType: "labels.text.fill",
                  stylers: [{ color: "#515c6d" }],
                },
                {
                  featureType: "water",
                  elementType: "labels.text.stroke",
                  stylers: [{ color: "#17263c" }],
                },
              ],
        });
        });
        google.maps.event.addDomListener(map, "click", (mapsMouseEvent) => {
            var location = JSON.stringify(mapsMouseEvent.latLng.toJSON(), null, 2)
            this.deleteMarkers()
            this.addMarker(mapsMouseEvent.latLng,map)
        });
     },
     click_add_marker_lat_lng:function(){
        google.maps.event.addDomListener(map, "click", (mapsMouseEvent) => {
            var location = JSON.stringify(mapsMouseEvent.latLng.toJSON(), null, 2)
            this.deleteMarkers()
            this.addMarker(mapsMouseEvent.latLng,map)
        });
     },

    });

});