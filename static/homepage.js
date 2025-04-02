function refreshData() {
    location.reload();
}

function showPopup(temp, hum, time) {
    let status = getWeatherStatus(temp);
    let action = getActionStatus(temp);
    document.getElementById("popup-text").innerHTML = `
        <strong>Temperature:</strong> ${temp}°C 🌡️<br>
        <strong>Humidity:</strong> ${hum}% 💧<br>
        <strong>Timestamp:</strong> ${time}<br>
        <strong>Weather Status:</strong> ${status}<br>
        <strong>Recommended Action:</strong> ${action}
    `;
    document.getElementById("popup-overlay").style.display = "block";
    document.getElementById("popup").style.display = "block";
}

function closePopup() {
    document.getElementById("popup-overlay").style.display = "none";
    document.getElementById("popup").style.display = "none";
}

function getWeatherStatus(temp) {
    if (temp < 10) return "🧊🥶 freezing/cold";
    if (temp >= 10 && temp < 18) return "❄️🍃 Slightly chilly";
    if (temp >= 18 && temp < 26) return "⛅👍🏻 Moderate/Comfortable";
    if (temp >= 26 && temp < 32) return "☀️ Slightly warm";
    if (temp >= 32) return "🔥♨️ burning/hot";

}

function getActionStatus(temp) {
    if (temp < 10) return "Stay inside, keep warm!";
    if (temp >= 10 && temp < 18) return "Have some warm drinks!";
    if (temp >= 18 && temp < 26) return "Perfect time for outing!";
    if (temp >= 26 && temp < 32) return "stay hydrated, grab a soda!";
    if (temp >= 32) return "Cold showers and fan+ice bowl will do the trick!";
}
