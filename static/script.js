function startCountdown(targetTime) {
    const countdownElement = document.getElementById("countdown");

    setInterval(function() {
        const now = new Date().getTime();
        const distance = targetTime - now;

        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        countdownElement.innerHTML = `${hours}h ${minutes}m ${seconds}s`;

        if (distance < 0) {
            countdownElement.innerHTML = "Time's up!";
        }
    }, 1000);
}
