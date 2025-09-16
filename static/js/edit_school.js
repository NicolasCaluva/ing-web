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