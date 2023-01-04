//Set up some of our variables.
var map; //Will contain map object.
var marker = false; ////Has the user plotted their location marker?

//Function called to initialize / create the map.
//This is called when the page has loaded.
function initMap() {

//    The center location of our map.
console.log("infoasasasas");
    $.ajax({
              type: "POST",
              url: window.location.origin+'/calculate/company/location',
              data: {'lat':lat,'long':long},
              success: function(data){
                console.log("info",data)
              if (data){
                    if (data[0]){
                            var centerOfMap = new google.maps.LatLng(data[0].latitude, data[0].longitude);

                            //Map options.
                            var options = {
                              center: centerOfMap, //Set center.
                              zoom: 12 //The zoom value.
                            };
                            map = new google.maps.Map(document.getElementById('map'), options);
                            map.setOptions({ minZoom: 12});
                    }
                    _.each(data, function (positions) {
                    console.log("sssss",positions)
                         var RestaurantCoordinate = { lat: positions.latitude, lng: positions.longitude };
                            var RestaurantImage = positions.logo;
                            var CustomerImage = "/website_delivery_type/static/src/js/Wooshfood_Customer_marker.png";
                            new google.maps.Marker({
                                position: RestaurantCoordinate,
                                map,
                                icon: RestaurantImage,
                                title: positions.company,
                              });
                    });
              }

              },
    });
//    var centerOfMap = new google.maps.LatLng(-27.50888, 152.94746);
//
//    //Map options.
//    var options = {
//      center: centerOfMap, //Set center.
//      zoom: 12 //The zoom value.
//    };

//    var RestaurantCoordinate = { lat: -27.50888, lng: 152.94746 };
//    var RestaurantImage = "/website_delivery_type/static/src/js/WooshFood_map_marker.png";
//    var CustomerImage = "/website_delivery_type/static/src/js/Wooshfood_Customer_marker.png";
    //Create the map object.
//    map = new google.maps.Map(document.getElementById('map'), options);
//      new google.maps.Marker({
//        position: RestaurantCoordinate,
//        map,
//        icon: RestaurantImage,
//        title: "Onit Burgers!",
//      });

//    map.setOptions({ minZoom: 12});


    //Listen for any clicks on the map.
    google.maps.event.addListener(map, 'click', function(event) {
        //Get the location that the user clicked.
        var clickedLocation = event.latLng;
        //If the marker hasn't been added.
        if(marker === false){
            //Create the marker.
            marker = new google.maps.Marker({
                position: clickedLocation,
                map: map,
                icon: CustomerImage,
                draggable: true //make it draggable
            });
            //Listen for drag events!
            google.maps.event.addListener(marker, 'dragend', function(event){
                markerLocation();
            });
        } else{
            //Marker has already been added, so just change its location.
            marker.setPosition(clickedLocation);
        }
        //Get the marker's location.
        markerLocation();
    });
}

//This function will get the marker's current location and then add the lat/long
//values to our textfields so that we can save the location.
function markerLocation(){
    //Get location.
    var currentLocation = marker.getPosition();
    //Add lat and lng values to a field that we can save.
    document.getElementById('user_lat').value = currentLocation.lat();
    document.getElementById('user_long').value = currentLocation.lng();
    var lat = currentLocation.lat();
    var long = currentLocation.lng();

            $.ajax({
              type: "POST",
              url: window.location.origin+'/calculate/distance',
              data: {'lat':lat,'long':long},
              success: function(data){
                console.log("fgfgf",data)

                var result = JSON.parse(data);
                if (result['status'] == 'success'){
                    if (result['house_no'] && result['road']){
                        var street1 = result['house_no']+", "+result['road'];
                        $("#street1").val(street1);
                    }
                    else if(result['house_no']){
                        $("#street1").val(result['house_no']);
                    }
                    else if(result['road']){

                        $("#street1").val(result['road']);
                    }
                    if(result['suburb']){
                        var street2 = result['suburb']
                        $("#street2").val(street2)
                    }
                    if(result['city']){
                        $("#city").val(result['city'])
                    }
                    if(result['postcode']){
                        $("#zip").val(result['postcode'])
                    }
                }
                else{
                    alert("We are not currently delivering to this address. Please try another one..")
                }
                },
                error: function(e) {
                }
            })




//    ajax.rpc('/calculate/distance', 'call', {"lat": lat, "long":long}).then(function(res) {
//        if(res['status'] === 'failed'){
//            alert("No delivery for the selected location.")
//        }
//        else{
//        document.getElementById('user_lat').value = currentLocation.lat();
//        document.getElementById('user_long').value = currentLocation.lng();
//        }
//    });

}


//Load the map when the page has finished loading.
if (window.location.pathname == "/shop/delivery/type"){
    google.maps.event.addDomListener(window, 'load', initMap);
}