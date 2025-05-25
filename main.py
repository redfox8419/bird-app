from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile, os
from datetime import datetime

# birdnetlib wraps both BirdNET-Lite & Analyzer
from birdnetlib.analyzer import Analyzer
from birdnetlib import Recording

app = Flask(__name__)
+CORS(app)

# Load the Analyzer once at startup
analyzer = Analyzer()
print("🚀 BirdNET Analyzer initialized")

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Expects multipart/form-data with:
      - 'audio': a WAV or MP3 file (~3s long)
      - optional form fields: lat, lon, date (YYYY-MM-DD), min_conf (0–1)
    Returns JSON list of detections.
    """
    # 1) save uploaded file to a temp path
    f = request.files.get("audio")
    if not f:
        return jsonify({"error": "no audio file provided"}), 400

    suffix = os.path.splitext(f.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        f.save(tmp.name)

    # 2) run BirdNET on it
    rec = Recording(
        analyzer,
        tmp.name,
        lat=request.form.get("lat"),
        lon=request.form.get("lon"),
        date=datetime.fromisoformat(request.form.get("date")) if request.form.get("date") else datetime.utcnow(),
        min_conf=float(request.form.get("min_conf", 0.25)),
    )
    rec.analyze()
    detections = rec.detections

    # 3) cleanup & respond
    os.unlink(tmp.name)
    return jsonify(detections)

if __name__ == "__main__":
    # for local dev
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
