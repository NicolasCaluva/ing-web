document.getElementById('imageUpload').addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('profileImage').src = e.target.result;
        }
        reader.readAsDataURL(file);
    }
});

document.getElementById('imageUploadLogo').addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('logoImage').src = e.target.result;
        }
        reader.readAsDataURL(file);
    }
});

$(document).ready(function () {
    $('.select2-shifts').select2({
        allowClear: true,
        width: '100%'
    });
});

window.initMap = function() {
    const defaultLocation = { lat: -31.25033, lng: -61.4867 };

    const latInput = document.getElementById("id_latitude");
    const lngInput = document.getElementById("id_longitude");
    const addressInput = document.getElementById("id_address");

    const initialLocation = (latInput.value && lngInput.value)
        ? { lat: parseFloat(latInput.value), lng: parseFloat(lngInput.value) }
        : defaultLocation;

    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: initialLocation,
    });

    const marker = new google.maps.Marker({
        position: initialLocation,
        map: map,
        draggable: true,
    });

    const autocomplete = new google.maps.places.Autocomplete(addressInput);
    autocomplete.bindTo("bounds", map);

    const geocoder = new google.maps.Geocoder();

    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place.geometry) return;

        map.setCenter(place.geometry.location);
        marker.setPosition(place.geometry.location);

        latInput.value = place.geometry.location.lat();
        lngInput.value = place.geometry.location.lng();
    });

    google.maps.event.addListener(marker, "dragend", () => {
        const pos = marker.getPosition();
        latInput.value = pos.lat();
        lngInput.value = pos.lng();

        geocoder.geocode({ location: pos }, (results, status) => {
            if (status === "OK" && results[0]) {
                addressInput.value = results[0].formatted_address;
            }
        });
    });
}
