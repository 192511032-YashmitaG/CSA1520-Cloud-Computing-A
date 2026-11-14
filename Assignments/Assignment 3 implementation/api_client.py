"""Small client that performs two GET requests against CampusConnect."""
import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def get_json(path):
    request = urllib.request.Request(
        BASE_URL + path,
        headers={"User-Agent": "CO3-API-Client"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
        print("Request:", path)
        print("HTTP status:", response.status)
        print(json.dumps(payload, indent=2))
        print("-" * 60)


if __name__ == "__main__":
    get_json("/api/health")
    get_json("/api/opportunities")
