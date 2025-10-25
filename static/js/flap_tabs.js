// Funcionalidad para manejar las pestañas activas en school_detail
document.addEventListener('DOMContentLoaded', function() {
    initializeFlapTabs();
});

function initializeFlapTabs() {
    const flapButtons = document.querySelectorAll('.flap button');

    // Marcar el primer botón como activo por defecto
    if (flapButtons.length > 0) {
        flapButtons[0].classList.add('flap-active');
    }

    // Agregar event listener a cada botón
    flapButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remover la clase 'flap-active' de todos los botones
            flapButtons.forEach(btn => {
                btn.classList.remove('flap-active');
            });

            // Agregar la clase 'flap-active' al botón clickeado
            this.classList.add('flap-active');
        });
    });
}

