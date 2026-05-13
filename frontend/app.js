const API_URL = "https://sis7aflfqci5tepm5z7bakixuq0nelpj.lambda-url.eu-west-2.on.aws/";

async function getWeather(placeOverride=null) {

  const loading = document.getElementById("loading");
  const card = document.getElementById("weatherCard");

  loading.classList.remove("hidden");
  card.classList.add("hidden");

  const place = placeOverride || document.getElementById("placeInput").value;

  try {

    const response = await fetch(`${API_URL}?place=${place}`);

    const data = await response.json();

    document.getElementById("icon").innerText = data.icon;
    document.getElementById("temperature").innerText = `${data.temperature}°C`;
    document.getElementById("summary").innerText = data.summary;
    document.getElementById("wind").innerText = `Wind: ${data.wind_kmh} km/h`;

    document.getElementById("metadata").innerHTML = `
      Environment: ${data.environment}<br>
      Version: ${data.version}<br>
      API latency: ${data.latency_ms}ms<br>
      Powered by: ${data.powered_by}
    `;

    document.getElementById("versionBanner").innerText =
      `Version ${data.version}`;

    const envBadge = document.getElementById("envBadge");

    envBadge.innerText = data.environment.toUpperCase();

    if (data.environment === "prod") {
      envBadge.style.background = "#d32f2f";
    } else {
      envBadge.style.background = "#1976d2";
    }

    loading.classList.add("hidden");
    card.classList.remove("hidden");

  } catch (err) {

    loading.innerText = "Error loading weather";

  }
}

function quickPlace(place) {
  document.getElementById("placeInput").value = place;
  getWeather(place);
}
