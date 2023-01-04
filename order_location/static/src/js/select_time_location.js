odoo.define('order_location.select_time_location', function (require) {
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


    publicWidget.registry.select_time_location = publicWidget.Widget.extend({
    selector: '#order_delivery_type',
    events: {
        'click #save_delivery_type': '_save_delivery_type',
    },

    init: function () {
        var self = this;
    },
    _save_delivery_type: function (ev){
        var self = this;
                var pickup_date = document.getElementById("pickup_date").value;
                var pickup_time = document.getElementById("pickup_time").value;
                var order_id = document.getElementById("sale_order_id_delivery_type").value;
                if (order_id) {
                    ajax.jsonRpc('/order/time/range/delivery/type', 'call', {
                                "pickup_date": pickup_date,
                                "pickup_time":pickup_time,
                                "order_id":order_id,
                    }).then(function(res) {
                            if (res) {
                                window.location.href = "/shop"
                            }else{
                                 swal(
                                      'Validation Error',
                                      'Sorry contact is not saved',
                                      'error'
                                    )
                            }
                    });

                }
    },
   });


   publicWidget.registry.order_delivery_type_kurb = publicWidget.Widget.extend({
    selector: '#order_delivery_type_kurb',
    events: {
        'click #save_delivery_type_kurb': '_save_delivery_type',
    },

    init: function () {
        var self = this;
    },
    _save_delivery_type: function (ev){
        var self = this;
                var pickup_date = document.getElementById("pickup_date").value;
                var pickup_time = document.getElementById("pickup_time").value;
                var order_id = document.getElementById("sale_order_id_delivery_type").value;
                var v_type = $('#vehicle_type_ids').find(":selected").text();
                var v_make = $('#vehicle_make_ids').find(":selected").text();
                var v_location = $('#vehicle_location_ids').find(":selected").text();

                var vehicle_color = document.getElementById("v_colour").value;
                var license_plate_no = document.getElementById("license_plate_no").value;
                var location_note = document.getElementById("location_note").value;

                if (order_id && pickup_date && pickup_time && v_type && v_make && v_location && vehicle_color && license_plate_no) {
                    ajax.jsonRpc('/order/time/range/delivery/type/kerb', 'call', {
                                "pickup_date": pickup_date,
                                "pickup_time":pickup_time,
                                "order_id":order_id,
                                "v_type":v_type,
                                "v_make":v_make,
                                "v_location":v_location,
                                "vehicle_color":vehicle_color,
                                "license_plate_no":license_plate_no,
                                "location_note":location_note,
                    }).then(function(res) {
                            if (res) {
                                window.location.href = "/shop"
                            }else{
                                 swal(
                                      'Validation Error',
                                      'Sorry contact is not saved',
                                      'error'
                                    )
                            }
                    });

                }else{
                    swal(
                                      'Validation Error',
                                      'Sorry please fill the fields',
                                      'error'
                                    )
                }
    },
   });
  publicWidget.registry.order_delivery_type_delivery = publicWidget.Widget.extend({
    selector: '#order_delivery_type_delivery',
    events: {
        'click #save_delivery_type_delivery': '_save_delivery_type',
        //'click #future_order': '_future_order',
    },

    init: function () {
        var self = this;
        ajax.jsonRpc('/calculate/company/location', 'call', {
                                        }).then(function(result){
                                        console.log("init map");
                                        self.initMap(result)
        });
    },

    initMap: function(result){
        var self = this;
            if (result){
                 if (result[0]){
                        self.centerOfMap = new google.maps.LatLng(result[0].latitude, result[0].longitude);

                        //Map options.
                        var options = {
                          center: self.centerOfMap, //Set center.
                          zoom: 12 //The zoom value.
                        };
                        self.map = new google.maps.Map(document.getElementById('map'), options);
                        self.map.setOptions({ minZoom: 12});
                        var map = self.map;
                }
            }
            for (var i=0;i<result.length;i++){
                var RestaurantCoordinate = { lat: result[i]['latitude'], lng: result[i]['longitude'] };
                                   const shape = {
                                        coords: [1, 1, 1, 20, 18, 20, 18, 1],
                                        type: "poly",
                                      };
                                    var RestaurantImage = "/order_location/static/src/images/crust_fa.png";
                                    var CustomerImage = "/order_location/static/src/images/maps1.png";
                                    new google.maps.Marker({
                                        position: RestaurantCoordinate,
                                        map,
                                        icon: RestaurantImage,
                                        shape: shape,
                                        title: result[i].company,
                                      });




                                   const cityCircle = new google.maps.Circle({
                                      strokeColor: "#FF0000",
                                      strokeOpacity: 0.1,
                                      strokeWeight: 2,
                                      fillColor: "#FF0000",
                                      fillOpacity: 0.1,
                                       clickable: false,
                                      map,
                                      center: RestaurantCoordinate,
                                      radius: Math.sqrt(result[i].delivery_radius*1.609) * 1000,
                                   });
            }

            google.maps.event.addListener(map, 'click', function(event) {
                var clickedLocation = event.latLng;
//                console.log(marker);
//                console.log(clickedLocation);
                if(self.marker === false || typeof self.marker === "undefined"){ console.log("kk");

                 self.marker = new google.maps.Marker({
                    position: clickedLocation,
                    map: map,
                    icon: CustomerImage,
                    draggable: true //make it draggable
                });
//                self.marker.setPosition(clickedLocation);
                //Listen for drag events!
                google.maps.event.addListener(self.marker, 'dragend', function(event){
                    self.markerLocation1(self.marker);
                    console.log("markeraa",self.marker);
                    $('#company_location_ids').empty();
                    $("#street1").empty();
                    $("#street2").empty();
                    $("#city").empty();
                    $("#zip").empty();
                });
                } else{
                 console.log("ccc");
                    //Marker has already been added, so just change its location.
                    self.marker.setPosition(clickedLocation);
                }
                self.markerLocation1(self.marker);

            });
    },
    markerLocation1: function(marker){
        var currentLocation = marker.getPosition();
        //Add lat and lng values to a field that we can save.
        document.getElementById('user_lat').value = currentLocation.lat();
        document.getElementById('user_long').value = currentLocation.lng();
//        ajax.jsonRpc('/calculate/distance/company', 'call', {
//                    'lat': document.getElementById('user_lat').value,
//                    'long': document.getElementById('user_long').value,
//        }).then(function(result){
//                    console.log("esilgtdtds",result);
//                    $('#company_location_ids').empty();
//                    _.each(result,function(item) {
//
//                        $('#company_location_ids').append('<option value='+item.company+'>'+item.company_name+'</option>');
//                    });
//        });
        ajax.jsonRpc('/calculate/distance/info', 'call', {
                    'lat': document.getElementById('user_lat').value,
                    'long': document.getElementById('user_long').value,
        }).then(function(data){

            var results21 = JSON.parse(data);
            var results = _.sortBy( results21, 'distance')
            console.log("wwwwww", results);
            $('#company_location_ids').empty().append(new Option('Select Nearest Stores', ''));
            _.each(results,function(item) {
                    $('#company_location_ids').append('<option value='+item.id+'>'+item.company_name+'  ('+item.distance+' Km)</option>');
            });
            if (results.length >=1){
                    $('#company_location_ids option:nth-child(2)').attr('selected', 'selected');
                    if (results[0]['status'] === 'success'){
                    try{
                        if (results[0]['house_no'] && results[0]['road']){
                            var street1 = results[0]['house_no']+", "+results[0]['road'];
                            $("#street1").val(street1);
                        }
                        else if(results[0]['house_no']){
                            $("#street1").val(results[0]['house_no']);
                        }
                        else if(result[0]['road']){

                            $("#street1").val(results[0]['road']);
                        }
                        if(results[0]['suburb']){
                            var street2 = results[0]['suburb']
                            $("#street2").val(street2)
                        }
                        if(results[0]['city']){
                            $("#city").val(results[0]['city'])
                        }
                        if(results[0]['postcode']){
                            $("#zip").val(results[0]['postcode'])
                        }

                    } catch (error) {
                        $("#street1").val("");
                        $("#street2").val("");
                        $("#city").val("");
                        $("#zip").val("");
                           swal(
                                      'Validation Error',
                                      'We are not currently delivering to this address. Please try another one..',
                                      'error'
                                    )
                        }


                }
                else{
                    $('#company_location_ids').val("");
                     $('#company_location_ids').empty();
                    $("#street1").val("");
                    $("#street2").val("");
                    $("#city").val("");
                    $("#zip").val("");
                     swal(
                                      'Validation Error',
                                      'We are not currently delivering to this address. Please try another one..',
                                      'error'
                                    )
//                        }
//                    alert("We are not currently delivering to this address. Please try another one..")
                }
            }else{
                 $('#company_location_ids').val("");
                     $('#company_location_ids').empty();
                $("#street1").val("");
                $("#street2").val("");
                $("#city").val("");
                $("#zip").val("");
                 swal(
                                      'Validation Error',
                                      'We are not currently delivering to this address. Please try another one..',
                                      'error'
                                    )
            }

        });

    },
    /*_future_order: function (ev){
        var is_checked = $(this).is(":checked")
        if ($('#future_order').is(":checked")){
            $('#order_delivery_type_delivery .advance_date').show();
            $('#order_delivery_type_delivery .advance_time').show();
        }
        else{
            $('#order_delivery_type_delivery .advance_date').hide();
            $('#order_delivery_type_delivery .advance_time').hide();
        }
    },*/
    _save_delivery_type: function (ev){
         var self = this;
         var company = $('#company_location_ids').find(":selected").val();
         var street1 = $('#street1').val();
         var street2 = $('#street2').val();
         var city = $('#city').val();
         var zip = $('#zip').val();
         var pickup_date = document.getElementById("pickup_date").value;
         var pickup_time = document.getElementById("pickup_time").value;
         var order_id = $('#sale_order_id_delivery_type').val();
             if (company && street1 && street2 && city && zip && pickup_date && pickup_time){
            ajax.jsonRpc('/order/location/company', 'call', {
                        'company': company,
                        'street1': street1,
                        'street2': street2,
                        'city': city,
                        'zip': zip,
                        'order_id': order_id,
            }).then(function(result){
                if (result){
                        if ($('#future_order').is(":checked")){

                            var order_id = document.getElementById("sale_order_id_delivery_type").value;
                            if (order_id) {
                                ajax.jsonRpc('/order/time/range/delivery/type', 'call', {
                                            "pickup_date": pickup_date,
                                            "pickup_time":pickup_time,
                                            "order_id":order_id,
                                }).then(function(res) {
                                        if (res) {
                                            console.log("Success")
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
                window.location.href = '/shop'
                }
                else{
                     swal(
                              'Validation Error',
                              'Sorry Location Not saved',
                              'error'
                            )
                }
            });
            }
            else{
                /*swal(
                              'Validation Error',
                              'Sorry Please fill the fields',
                              'error'
                            )*/
                            window.location.href = '/shop'
            }
    },
   });

   });