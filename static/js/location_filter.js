document.addEventListener("DOMContentLoaded", function () {
    const distanceSelect = document.getElementById("distance");
    const searchInput = document.getElementById("search");
    const turnoSelect = document.getElementById("turno");

    let userCoords = null;

    // Pedir ubicación
    function askLocation(callback) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;

                    document.cookie = `user_lat=${lat}; path=/`;
                    document.cookie = `user_lon=${lon}; path=/`;

                    userCoords = { lat, lon };
                    if (callback) callback(true);
                },
                (error) => {
                    console.warn("No se pudo obtener ubicación:", error);
                    userCoords = null;
                    if (callback) callback(false);
                }
            );
        } else {
            console.warn("Geolocalización no soportada.");
            if (callback) callback(false);
        }
    }

    // Pedir ubicación al cargar, solo para calcular distancias
    askLocation();

    // Función para disparar HTMX sin recargar scroll
    function triggerHTMX() {
        htmx.trigger(searchInput, 'keyup');
    }

    // Cambios en distancia
    distanceSelect.addEventListener("change", function () {
        if (!userCoords) {
            askLocation((ok) => {
                if (ok) triggerHTMX();
                else distanceSelect.value = ""; // volver a "--Selecciona--"
            });
        } else {
            triggerHTMX();
        }
    });

    // Cambios en búsqueda y turno
});

function getCookie(name) {
    let value = "; " + document.cookie;
    let parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
}

document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("btn-directions");
    if (!btn) return;

    const lat = getCookie("user_lat");
    const lon = getCookie("user_lon");
    const destination = encodeURIComponent(btn.dataset.address);

    if (lat && lon) {
        const origin = `${lat},${lon}`;
        btn.href = `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}`;
    } else {
        btn.href = `https://www.google.com/maps/search/?api=1&query=${destination}`;
    }
});
