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

    // Función para activar un tab específico
    function activateTab(tabId) {
        const navLinks = document.querySelectorAll('.nav-borders .nav-link');
        navLinks.forEach(l => l.classList.remove('active'));
        const tab = document.getElementById(tabId);
        if (tab) {
            tab.classList.add('active');
        }
    }

    // Función para determinar qué tab debe estar activo
    function detectAndActivateTab() {
        // Verificar si hay contenido de carreras cargado
        const careersContent = document.querySelector('#section .card-header');
        if (careersContent && careersContent.textContent.trim().includes('Carreras')) {
            activateTab('careers-tab');
            return;
        }

        // Si hay un mapa, es el tab de editar perfil
        const mapElement = document.getElementById('map');
        if (mapElement) {
            activateTab('edit-profile-tab');
            return;
        }

        // Si hay un formulario con fotos
        const photoSection = document.querySelector('#section form[enctype="multipart/form-data"]');
        if (photoSection) {
            const photosInput = photoSection.querySelector('input[type="file"][name="photos"]');
            if (photosInput) {
                activateTab('photos-tab');
                return;
            }
        }

        // Por defecto, activar el primer tab
        activateTab('edit-profile-tab');
    }

    // Detectar el tab activo al cargar la página
    detectAndActivateTab();

    // Inicializar Select2 después de detectar el tab
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

    // Manejar clics en los tabs de navegación
    const navLinks = document.querySelectorAll('.nav-borders .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remover 'active' de todos los links
            navLinks.forEach(l => l.classList.remove('active'));
            // Agregar 'active' al link clickeado
            this.classList.add('active');
        });
    });

    // Escuchar eventos de HTMX cuando se carga nuevo contenido
    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Re-inicializar Select2 si es necesario
        if (typeof $ !== 'undefined' && typeof $.fn.select2 !== 'undefined') {
            const selectElement = $('.select2-shifts');
            if (selectElement.length > 0 && !selectElement.hasClass('select2-hidden-accessible')) {
                selectElement.select2({
                    allowClear: true,
                    width: '100%'
                });
            }
        }
    });
});

// initMap se mantiene global para que Google Maps API pueda llamarla
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
