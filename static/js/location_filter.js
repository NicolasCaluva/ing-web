document.addEventListener("DOMContentLoaded", function () {
    const distanceSelect = document.getElementById("distance");
    const searchInput = document.getElementById("search");
    const turnoSelect = document.getElementById("turno");

    let userCoords = null;

    // Pedir ubicación por IP (fallback para PCs sin GPS)
    async function getLocationByIP() {
        try {
            // Usar ip-api.com que tiene mejor límite y no tiene problemas de CORS
            const response = await fetch('https://ip-api.com/json/?fields=status,lat,lon,city,country');
            const data = await response.json();
            
            if (data.status === 'success' && data.lat && data.lon) {
                document.cookie = `user_lat=${data.lat}; path=/`;
                document.cookie = `user_lon=${data.lon}; path=/`;
                userCoords = { lat: data.lat, lon: data.lon };
                console.log("Ubicación obtenida por IP:", data.city, data.country);
                console.log("Coordenadas:", data.lat, data.lon);
                return true;
            }
        } catch (error) {
            console.warn("Error obteniendo ubicación por IP:", error);
            return false;
        }
        return false;
    }

    // Pedir ubicación por GPS/navegador
    function askLocation(callback) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;

                    document.cookie = `user_lat=${lat}; path=/`;
                    document.cookie = `user_lon=${lon}; path=/`;

                    userCoords = { lat, lon };
                    console.log("Ubicación GPS obtenida:", lat, lon);
                    if (callback) callback(true);
                },
                async (error) => {
                    console.warn("GPS no disponible, usando ubicación por IP");
                    const success = await getLocationByIP();
                    if (callback) callback(success);
                }
            );
        } else {
            console.warn("Geolocalización no soportada, usando ubicación por IP...");
            getLocationByIP().then(success => {
                if (callback) callback(success);
            });
        }
    }

    // Pedir ubicación al cargar, solo para calcular distancias
    askLocation();

    // HTMX se encarga automáticamente del filtrado gracias a hx-trigger="change"
    distanceSelect.addEventListener("change", function () {
        const selectedValue = this.value;
        
        if (selectedValue && !userCoords) {
            // Si selecciona una distancia pero no hay ubicación, pedir nuevamente
            askLocation((ok) => {
                if (!ok) {
                    this.value = ""; // Resetear a "--Selecciona--"
                    alert("No se pudo obtener tu ubicación. Por favor, verifica los permisos del navegador");
                }
            });
        }
    });
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
