import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }


def weather_icon(summary):
    summary = summary.lower()

    if "rain" in summary:
        return "🌧️"
    elif "cloud" in summary:
        return "☁️"
    elif "snow" in summary:
        return "❄️"
    elif "storm" in summary:
        return "⛈️"
    elif "sun" in summary or "clear" in summary:
        return "☀️"
    else:
        return "🌤️"


def lambda_handler(event, context):
    start = time.time()

    api_key = os.environ.get("METEOSOURCE_API_KEY")
    default_place = os.environ.get("DEFAULT_PLACE", "London")
    units = os.environ.get("UNITS", "metric")
    deploy_env = os.environ.get("DEPLOY_ENV", "dev")
    app_version = os.environ.get("APP_VERSION", "v1")

    query_params = event.get("queryStringParameters") or {}
    place = query_params.get("place", default_place)

    params = urllib.parse.urlencode({
        "place_id": place,
        "sections": "current",
        "timezone": "UTC",
        "language": "en",
        "units": units,
        "key": api_key
    })

    url = f"https://www.meteosource.com/api/v1/free/point?{params}"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        current = data.get("current", {})

        summary = current.get("summary", "Unknown")
        temperature = current.get("temperature")
        wind = current.get("wind", {}).get("speed")

        latency = round((time.time() - start) * 1000)

        return _response(200, {
            "place": place,
            "temperature": temperature,
            "summary": summary,
            "wind_kmh": wind,
            "icon": weather_icon(summary),
            "environment": deploy_env,
            "version": app_version,
            "latency_ms": latency,
            "powered_by": "Harness + AWS Lambda"
        })
    
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return _response(exc.code, {
            "place": place,
            "error": f"HTTP Error {exc.code}: {exc.reason}",
            "meteosource_response": error_body
        })    

    except Exception as exc:
        return _response(500, {
            "error": str(exc),
            "place": place
        })
