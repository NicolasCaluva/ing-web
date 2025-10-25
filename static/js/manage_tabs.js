document.addEventListener("DOMContentLoaded", () => {
    // Agregar función manageTabs al evento click de todas las etiquetas a que tengan la clase 'tab'
    document.querySelectorAll('a.tab').forEach(tab => {
        tab.addEventListener('click', manageTabs);
    });

    function manageTabs(event) {
        const clickedTab = event.currentTarget; // Obtener la pestaña que fue clickeada

        // Desactivar todas las pestañas y ocultar todas las secciones
        document.querySelectorAll('a.tab').forEach(tab => {
            if (tab.classList.contains('active')) {
                tab.classList.remove('active');
            }
        });

        // Activar la pestaña clickeada y mostrar la sección correspondiente
        clickedTab.classList.add('active');
    }
})

