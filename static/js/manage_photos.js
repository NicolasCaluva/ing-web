document.addEventListener('DOMContentLoaded', function() {
    initializePhotoManagement();
    initializePhotoUploadForm();
});

// Función para manejar el formulario de subida de fotos con AJAX
function initializePhotoUploadForm() {
    const uploadForm = document.getElementById('uploadPhotosForm');
    if (!uploadForm) return;

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevenir el submit tradicional

        const formData = new FormData(uploadForm);
        const uploadButton = document.getElementById('uploadButton');

        // Deshabilitar el botón mientras se suben las fotos
        if (uploadButton) {
            uploadButton.disabled = true;
            uploadButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subiendo...';
        }

        fetch(uploadForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            if (response.redirected) {
                // Si hay redirect, recargar la sección con HTMX
                const photosUrl = response.url;
                fetch(photosUrl, {
                    headers: {
                        'HX-Request': 'true'
                    }
                })
                .then(res => res.text())
                .then(html => {
                    const section = document.getElementById('section');
                    if (section) {
                        section.innerHTML = html;
                        // Reinicializar después de cargar el nuevo contenido
                        setTimeout(() => {
                            initializePhotoManagement();
                            initializePhotoUploadForm();
                            showSuccessToast('¡Fotos subidas exitosamente!');
                        }, 100);
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorToast('Ocurrió un error al subir las fotos. Por favor, intenta de nuevo.');
            if (uploadButton) {
                uploadButton.disabled = false;
                uploadButton.innerHTML = '<i class="fas fa-upload"></i> Subir fotos';
            }
        });
    });
}

// Función para inicializar o reinicializar la gestión de fotos
function initializePhotoManagement() {
    const photoInput = document.getElementById('photoInput');
    const photoPreviewContainer = document.getElementById('photoPreviewContainer');
    const photoPreview = document.getElementById('photoPreview');
    const uploadButton = document.getElementById('uploadButton');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    const deletePhotosForm = document.getElementById('deletePhotosForm');

    // Si los elementos no existen, salir de la función
    if (!photoInput) return;

    let selectedFiles = [];

    // Manejar la selección de archivos y mostrar previsualización
    photoInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);

        if (files.length === 0) {
            photoPreviewContainer.style.display = 'none';
            uploadButton.disabled = true;
            selectedFiles = [];
            return;
        }

        selectedFiles = files;
        showPreview(files);
        uploadButton.disabled = false;
    });

    // Mostrar previsualización de las fotos seleccionadas
    function showPreview(files) {
        photoPreview.innerHTML = '';
        photoPreviewContainer.style.display = 'block';

        files.forEach((file, index) => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    const col = document.createElement('div');
                    col.className = 'col-md-3 col-sm-6';

                    const previewItem = document.createElement('div');
                    previewItem.className = 'preview-item';

                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'img-thumbnail';
                    img.style.width = '100%';
                    img.style.height = '150px';
                    img.style.objectFit = 'cover';

                    const removeBtn = document.createElement('button');
                    removeBtn.className = 'preview-remove';
                    removeBtn.innerHTML = '×';
                    removeBtn.type = 'button';
                    removeBtn.onclick = function() {
                        removePreviewImage(index);
                    };

                    previewItem.appendChild(img);
                    previewItem.appendChild(removeBtn);
                    col.appendChild(previewItem);
                    photoPreview.appendChild(col);
                };

                reader.readAsDataURL(file);
            }
        });
    }

    // Eliminar una imagen de la previsualización
    function removePreviewImage(index) {
        selectedFiles.splice(index, 1);

        if (selectedFiles.length === 0) {
            photoPreviewContainer.style.display = 'none';
            uploadButton.disabled = true;
            photoInput.value = '';
        } else {
            // Actualizar el input file con los archivos restantes
            const dataTransfer = new DataTransfer();
            selectedFiles.forEach(file => dataTransfer.items.add(file));
            photoInput.files = dataTransfer.files;
            showPreview(selectedFiles);
        }
    }

    // Manejar checkboxes de fotos existentes
    const photoCheckboxes = document.querySelectorAll('.photo-checkbox');

    function updateDeleteButton() {
        const checkedBoxes = document.querySelectorAll('.photo-checkbox:checked');
        if (deleteSelectedBtn) {
            deleteSelectedBtn.disabled = checkedBoxes.length === 0;
        }
    }

    photoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateDeleteButton);
    });

    // Botón seleccionar todas
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            photoCheckboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
            updateDeleteButton();
        });
    }

    // Botón deseleccionar todas
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function() {
            photoCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            updateDeleteButton();
        });
    }

    // Confirmar eliminación de fotos
    if (deleteSelectedBtn) {
        deleteSelectedBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevenir el submit por defecto

            const checkedBoxes = document.querySelectorAll('.photo-checkbox:checked');
            const count = checkedBoxes.length;

            if (count === 0) {
                return;
            }

            const confirmMessage = count === 1
                ? '¿Estás seguro de que deseas eliminar esta foto?'
                : `¿Estás seguro de que deseas eliminar ${count} fotos?`;

            if (confirm(confirmMessage)) {
                // Enviar petición AJAX
                const formData = new FormData(deletePhotosForm);

                fetch(deletePhotosForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Eliminar las fotos del DOM
                        data.deleted_ids.forEach(photoId => {
                            const photoCard = document.querySelector(`input[value="${photoId}"]`)?.closest('.col-md-3');
                            if (photoCard) {
                                photoCard.style.transition = 'opacity 0.3s ease';
                                photoCard.style.opacity = '0';
                                setTimeout(() => {
                                    photoCard.remove();

                                    // Verificar si ya no hay más fotos
                                    const remainingPhotos = document.querySelectorAll('.photo-checkbox');
                                    if (remainingPhotos.length === 0) {
                                        // Ocultar el formulario de eliminación
                                        const deletePhotosForm = document.getElementById('deletePhotosForm');
                                        if (deletePhotosForm) {
                                            deletePhotosForm.style.display = 'none';
                                        }

                                        // Mostrar la alerta de "no hay fotos" después del contador
                                        const photosCounter = document.getElementById('photosCounter');
                                        if (photosCounter) {
                                            // Verificar si ya existe la alerta
                                            let noPhotosAlert = document.getElementById('noPhotosAlert');
                                            if (!noPhotosAlert) {
                                                noPhotosAlert = document.createElement('div');
                                                noPhotosAlert.className = 'alert alert-info';
                                                noPhotosAlert.id = 'noPhotosAlert';
                                                noPhotosAlert.innerHTML = '<i class="fas fa-info-circle"></i> No hay fotos cargadas aún. ¡Sube algunas fotos para mostrar tu institución!';
                                                // Insertar después del contador de fotos
                                                photosCounter.parentNode.insertAdjacentElement('afterend', noPhotosAlert);
                                            }
                                        }
                                    }

                                    // Actualizar el contador de fotos
                                    updatePhotosCounter();
                                }, 300);
                            }
                        });

                        // Mostrar mensaje de éxito
                        showSuccessToast(data.message);

                        // Deshabilitar el botón de eliminar
                        deleteSelectedBtn.disabled = true;
                    } else {
                        // Mostrar mensaje de error
                        showErrorToast(data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showErrorToast('Ocurrió un error al eliminar las fotos. Por favor, intenta de nuevo.');
                });
            }
        });
    }

    // Función para actualizar el contador de fotos
    function updatePhotosCounter() {
        const remainingPhotos = document.querySelectorAll('.photo-checkbox');
        const photosCountElement = document.getElementById('photosCount');
        if (photosCountElement) {
            photosCountElement.textContent = remainingPhotos.length;
        }
    }
}

// Re-inicializar después de HTMX swap (SIN recargar la página)
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'section') {
        // Re-ejecutar la inicialización si se carga el contenido de fotos vía HTMX
        const newPhotoInput = document.getElementById('photoInput');
        if (newPhotoInput) {
            // Usar setTimeout para asegurar que el DOM esté completamente actualizado
            setTimeout(() => {
                initializePhotoManagement();
                initializePhotoUploadForm();
            }, 50);
        }
    }
});

// Función para mostrar toast de éxito
function showSuccessToast(message) {
    const toast = document.createElement('div');
    toast.className = 'success-toast';
    toast.innerHTML = `
        <div class="toast-content">
            <i class="bi bi-check-circle-fill"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);

    // Mostrar el toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Ocultar y eliminar después de 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// Función para mostrar toast de error
function showErrorToast(message) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.innerHTML = `
        <div class="toast-content">
            <i class="bi bi-exclamation-circle-fill"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);

    // Mostrar el toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Ocultar y eliminar después de 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}
