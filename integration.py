import os, time, uuid, hmac, hashlib, json
import requests
from dotenv import load_dotenv

load_dotenv()  # loads .env if present

BASE = os.getenv("API_BASE_URL", "https://httpbin.org/anything")
TOKEN = os.getenv("API_TOKEN", "")
APP_ID = os.getenv("APP_ID", "")
SECRET = os.getenv("APP_SECRET", "")

def request_with_retry(path: str, body: dict, tries: int = 0) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "X-App-Id": APP_ID,
        "X-Scope": "contacts.write",
        "Idempotency-Key": str(uuid.uuid4()),  # new key per attempt (demo)
        "Content-Type": "application/json",
    }
    url = f"{BASE}{path}"
    resp = requests.post(url, json=body, headers=headers)

    if resp.status_code == 429 or (500 <= resp.status_code < 600):
        if tries >= 2:
            return resp
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                delay = float(retry_after)
            except ValueError:
                delay = [0.5, 1.0, 2.0][tries]
        else:
            delay = [0.5, 1.0, 2.0][tries]
        time.sleep(delay)
        return request_with_retry(path, body, tries + 1)

    return resp

def verify_webhook(raw_body: str, timestamp: str, signature_header: str, secret: str, max_skew_sec: int = 300) -> bool:
    # Optionally enforce replay window by checking timestamp; omitted for demo clarity.
    try:
        int(timestamp)  # basic sanity
    except Exception:
        return False
    mac = hmac.new(secret.encode(), f"{timestamp}.{raw_body}".encode(), hashlib.sha256).hexdigest()
    expected = f"sha256={mac}"
    return hmac.compare_digest(signature_header, expected)

if __name__ == "__main__":
    # Upsert example
    body = {
        "email": "camila.ramos@retail.pe",
        "country": "Peru",
        "budget_usd": 13500,
        "rfp_source": "AI-RFP"
    }
    r = request_with_retry("/v1/contacts:upsert", body)
    print("Status:", r.status_code)
    try:
        j = r.json()
        print(json.dumps({
            "url": j.get("url"),
            "headers_subset": {
                "Authorization": j.get("headers", {}).get("Authorization"),
                "X-App-Id": j.get("headers", {}).get("X-App-Id"),
                "X-Scope": j.get("headers", {}).get("X-Scope"),
                "Idempotency-Key": j.get("headers", {}).get("Idempotency-Key"),
                "Content-Type": j.get("headers", {}).get("Content-Type"),
            },
            "json": j.get("json"),
        }, indent=2))
    except Exception:
        print(r.text[:500])

    # Webhook verification test with the prompt’s sample
    sample_ts = "1732392000"
    sample_sig = "sha256=d482183916df45138cc2e9fd4f6e9f128091b402ea74e30565887628c665d5a7"
    sample_raw = '{"event":"contact.created","email":"camila.ramos@retail.pe","rfp_source":"AI-RFP"}'
    print("Webhook signature valid?", verify_webhook(sample_raw, sample_ts, sample_sig, SECRET))
