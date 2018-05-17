console.log("Hello");

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(getPosition);
} else {
}

function getPosition(position) {

    var data = {
    }
    $.ajax({
        url: "",
        type: "POST",
        data: {'lat': position.coords.latitude, 'long': position.coords.longitude},
        dataType: "json"
        });
}