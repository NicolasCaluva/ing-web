document.addEventListener('DOMContentLoaded', function() {
    const photoInput = document.getElementById('photoInput');
    const photoPreviewContainer = document.getElementById('photoPreviewContainer');
    const photoPreview = document.getElementById('photoPreview');
    const uploadButton = document.getElementById('uploadButton');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    const deletePhotosForm = document.getElementById('deletePhotosForm');

    let selectedFiles = [];

    // Manejar la selección de archivos y mostrar previsualización
    if (photoInput) {
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
    }

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
        deleteSelectedBtn.addEventListener('click', function() {
            const checkedBoxes = document.querySelectorAll('.photo-checkbox:checked');
            const count = checkedBoxes.length;

            if (count === 0) {
                return;
            }

            const confirmMessage = count === 1
                ? '¿Estás seguro de que deseas eliminar esta foto?'
                : `¿Estás seguro de que deseas eliminar ${count} fotos?`;

            if (confirm(confirmMessage)) {
                deletePhotosForm.submit();
            }
        });
    }

    // Re-inicializar después de HTMX swap
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.id === 'section') {
            // Re-ejecutar la inicialización si se carga el contenido de fotos vía HTMX
            const newPhotoInput = document.getElementById('photoInput');
            if (newPhotoInput) {
                location.reload(); // Recargar para reinicializar todo el JavaScript
            }
        }
    });
});

