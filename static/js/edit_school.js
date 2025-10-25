document.addEventListener('DOMContentLoaded', function() {
    // Event listener para imagen de perfil
    const imageUpload = document.getElementById('imageUpload');
    if (imageUpload) {
        imageUpload.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    document.getElementById('profileImage').src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Event listener para logo
    const imageUploadLogo = document.getElementById('imageUploadLogo');
    if (imageUploadLogo) {
        imageUploadLogo.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    document.getElementById('logoImage').src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Cargar Google Maps en la carga inicial si el mapa existe
    loadGoogleMapsIfNeeded();

    // Cuando se hace clic en un tab, HTMX maneja la carga del contenido
    // El tab ya se activa con el clic, no necesitamos detectar nada después
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.id === 'section') {
            // Cargar Google Maps si el nuevo contenido tiene un mapa
            setTimeout(() => {
                loadGoogleMapsIfNeeded();

                // Re-inicializar Select2 si existe
                if (typeof $ !== 'undefined' && typeof $.fn.select2 !== 'undefined') {
                    const selectElement = $('.select2-shifts');
                    if (selectElement.length > 0 && !selectElement.hasClass('select2-hidden-accessible')) {
                        selectElement.select2({
                            allowClear: true,
                            width: '100%'
                        });
                    }
                }
            }, 50);
        }
    });

    // Inicializar Select2 si existe
    setTimeout(() => {
        if (typeof $ !== 'undefined' && typeof $.fn.select2 !== 'undefined') {
            const selectElement = $('.select2-shifts');
            if (selectElement.length > 0) {
                selectElement.select2({
                    allowClear: true,
                    width: '100%'
                });
            }
        }
    }, 100);
});

// Función para cargar Google Maps solo cuando sea necesario
function loadGoogleMapsIfNeeded() {
    const mapElement = document.getElementById('map');
    if (mapElement && !window.googleMapsScriptLoaded) {
        window.googleMapsScriptLoaded = true;
        const script = document.createElement('script');
        const apiKey = document.querySelector('meta[name="google-maps-api-key"]')?.content || '';
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initMap`;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
    } else if (mapElement && typeof google !== 'undefined' && google.maps) {
        // Si Google Maps ya está cargado y el mapa existe, inicializar directamente
        initMap();
    }
}

// initMap se mantiene global para que Google Maps API pueda llamarla
window.initMap = function() {
    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    const defaultLocation = { lat: -31.25033, lng: -61.4867 };

    const latInput = document.getElementById("id_latitude");
    const lngInput = document.getElementById("id_longitude");
    const addressInput = document.getElementById("id_address");

    const initialLocation = (latInput && lngInput && latInput.value && lngInput.value)
        ? { lat: parseFloat(latInput.value), lng: parseFloat(lngInput.value) }
        : defaultLocation;

    const map = new google.maps.Map(mapElement, {
        zoom: 13,
        center: initialLocation,
    });

    const marker = new google.maps.Marker({
        position: initialLocation,
        map: map,
        draggable: true,
    });

    if (addressInput) {
        const autocomplete = new google.maps.places.Autocomplete(addressInput);
        autocomplete.bindTo("bounds", map);

        autocomplete.addListener("place_changed", () => {
            const place = autocomplete.getPlace();
            if (!place.geometry) return;

            map.setCenter(place.geometry.location);
            marker.setPosition(place.geometry.location);

            latInput.value = place.geometry.location.lat();
            lngInput.value = place.geometry.location.lng();
        });
    }

    const geocoder = new google.maps.Geocoder();

    google.maps.event.addListener(marker, "dragend", () => {
        const pos = marker.getPosition();
        latInput.value = pos.lat();
        lngInput.value = pos.lng();

        geocoder.geocode({ location: pos }, (results, status) => {
            if (status === "OK" && results[0] && addressInput) {
                addressInput.value = results[0].formatted_address;
            }
        });
    });
}
