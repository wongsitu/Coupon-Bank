$(document).ready(function() {
console.log("Let's get coding!");

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
                title: 'Hello World!'
            });
            return mapHere;
        })
    };
}

displayMap();

});