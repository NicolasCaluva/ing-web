$(document).ready(function () {
    $('#eye-icon').on('click', function () {
        var eyeIcon = $(this);
        var input = $('#password');

        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            eyeIcon.children().removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            input.attr('type', 'password');
            eyeIcon.children().removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });
})
