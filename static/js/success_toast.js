// Script para manejar el toast de éxito y redirección
function initSuccessToast(redirectUrl) {
    let seconds = 3;
    const countdownElement = document.getElementById('countdown');

    if (!countdownElement) return;

    const interval = setInterval(() => {
        seconds--;
        countdownElement.textContent = seconds;

        if (seconds <= 0) {
            clearInterval(interval);
            window.location.href = redirectUrl;
        }
    }, 1000);
}
