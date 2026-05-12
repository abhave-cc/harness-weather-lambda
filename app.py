import json
import os
import urllib.parse
import urllib.request


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    api_key = os.environ.get("METEOSOURCE_API_KEY")
    default_place = os.environ.get("DEFAULT_PLACE", "London")
    units = os.environ.get("UNITS", "metric")

    if not api_key:
        return _response(500, {
            "error": "METEOSOURCE_API_KEY is not configured"
        })

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
        temperature = current.get("temperature")
        summary = current.get("summary", "No summary available")
        wind = current.get("wind", {}).get("speed")

        return _response(200, {
            "place": place,
            "summary": f"{place}: {temperature}°C, {summary}, wind {wind} km/h.",
            "raw_current": current
        })

    except Exception as exc:
        return _response(500, {
            "place": place,
            "error": str(exc)
        })
