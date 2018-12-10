function displayMap(){
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            }
            var mapHere = new google.maps.Map(document.getElementById('map'), {
                center: pos,
                zoom: 12.5,
            });

            var marker = new google.maps.Marker({
                position: pos,
                map: mapHere,
            });

            $('#options').on('click','.coordinates',function(e){
                e.preventDefault
                lat = parseFloat($(this).attr('lat'))
                lng = parseFloat($(this).attr('lng'))
                rest_pos = {lat,lng}
                var marker = new google.maps.Marker({
                    position: rest_pos,
                    map: mapHere,
                });
                mapHere.setCenter(marker.getPosition());
            })

            return mapHere;
        })
    };
}

displayMap()
