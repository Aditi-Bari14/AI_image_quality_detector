import os
import uuid
import sqlite3
from datetime import datetime

import cv2
import joblib
import numpy as np

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "..",
    "frontend"
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "model", "quality_model.pkl")
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

# Load trained ML model
model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def init_database():

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            quality_score REAL NOT NULL,
            quality_label TEXT NOT NULL,
            issues TEXT,
            statistics TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# FILE VALIDATION
# --------------------------------------------------

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# --------------------------------------------------
# FEATURE EXTRACTION
# --------------------------------------------------

def extract_features(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Brightness
    brightness = float(np.mean(gray))

    # Contrast
    contrast = float(np.std(gray))

    # Sharpness
    sharpness = float(
        cv2.Laplacian(gray, cv2.CV_64F).var()
    )

    # Noise estimation
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    noise = float(
        np.std(
            gray.astype(np.float32)
            - blur.astype(np.float32)
        )
    )

    # Saturation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    saturation = float(
        np.mean(hsv[:, :, 1])
    )

    # Exposure statistics
    overexposed_pixels = float(
        np.mean(gray > 245) * 100
    )

    underexposed_pixels = float(
        np.mean(gray < 20) * 100
    )

    features = [
        brightness,
        contrast,
        sharpness,
        noise,
        saturation,
        overexposed_pixels,
        underexposed_pixels
    ]

    statistics = {
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "sharpness": round(sharpness, 2),
        "noise": round(noise, 2),
        "saturation": round(saturation, 2),
        "overexposed_pixels": round(
            overexposed_pixels, 2
        ),
        "underexposed_pixels": round(
            underexposed_pixels, 2
        )
    }

    return np.array(features).reshape(1, -1), statistics


# --------------------------------------------------
# QUALITY SCORE
# --------------------------------------------------

def calculate_quality_score(prediction, confidence, statistics):

    score = 100.0

    # Blur
    if prediction == "BLUR":
        score -= 35

    # Underexposure
    elif prediction == "UNDEREXPOSED":
        score -= 30

    # Overexposure
    elif prediction == "OVEREXPOSED":
        score -= 30

    # Noise
    elif prediction == "NOISY":
        score -= 25

    # Confidence adjustment
    score = score * (0.75 + 0.25 * confidence)

    # Additional image-quality penalties

    if statistics["sharpness"] < 50:
        score -= 10

    if statistics["noise"] > 30:
        score -= 10

    score = max(0, min(100, score))

    return round(score, 2)


# --------------------------------------------------
# ISSUE GENERATION
# --------------------------------------------------

def generate_issue(prediction, confidence, statistics):

    issues = []

    if prediction == "BLUR":

        issues.append({
            "type": "blur",
            "severity": "high" if confidence > 0.8 else "medium",
            "confidence": round(confidence, 2)
        })

    elif prediction == "UNDEREXPOSED":

        issues.append({
            "type": "underexposure",
            "severity": "high" if confidence > 0.8 else "medium",
            "confidence": round(confidence, 2)
        })

    elif prediction == "OVEREXPOSED":

        issues.append({
            "type": "overexposure",
            "severity": "high" if confidence > 0.8 else "medium",
            "confidence": round(confidence, 2)
        })

    elif prediction == "NOISY":

        issues.append({
            "type": "noise",
            "severity": "high" if confidence > 0.8 else "medium",
            "confidence": round(confidence, 2)
        })

    return issues


# --------------------------------------------------
# HEALTH ENDPOINT
# --------------------------------------------------
# @app.route("/", methods=["GET"])
# def home():
#     return send_from_directory(
#         FRONTEND_DIR,
#         "index.html"
#     )

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    })


# --------------------------------------------------
# ANALYZE IMAGE
# --------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    # Check if image exists
    if "image" not in request.files:

        return jsonify({
            "error": "No image file provided."
        }), 400

    file = request.files["image"]

    # Check filename
    if file.filename == "":

        return jsonify({
            "error": "No file selected."
        }), 400

    # Check extension
    if not allowed_file(file.filename):

        return jsonify({
            "error": "Unsupported file type. "
                     "Use JPG, JPEG, PNG or WEBP."
        }), 400

    # Generate safe unique filename
    original_filename = secure_filename(
        file.filename
    )

    filename = (
        str(uuid.uuid4())
        + "_"
        + original_filename
    )

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    try:

        file.save(filepath)

        # Read image
        image = cv2.imread(filepath)

        if image is None:

            os.remove(filepath)

            return jsonify({
                "error": "Unable to read image."
            }), 400

        # Extract features
        features, statistics = extract_features(
            image
        )

        # ML prediction
        prediction = model.predict(features)[0]

        # Confidence
        probabilities = model.predict_proba(features)[0]

        confidence = float(
            np.max(probabilities)
        )

        # Calculate score
        quality_score = calculate_quality_score(
            prediction,
            confidence,
            statistics
        )

        # Quality label
        if quality_score >= 75:

            quality_label = "ACCEPTABLE"

        elif quality_score >= 45:

            quality_label = "DEGRADED"

        else:

            quality_label = "DEFECTIVE"

        # Issues
        issues = generate_issue(
            prediction,
            confidence,
            statistics
        )

        # Save to database
        conn = sqlite3.connect(
            DATABASE_PATH
        )

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO analyses
            (
                filename,
                quality_score,
                quality_label,
                issues,
                statistics,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            original_filename,
            quality_score,
            quality_label,
            str(issues),
            str(statistics),
            datetime.now().isoformat()
        ))

        analysis_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return jsonify({

            "id": analysis_id,

            "filename": original_filename,

            "quality_score": quality_score,

            "quality_label": quality_label,

            "predicted_condition": prediction,

            "issues": issues,

            "statistics": statistics,

            "confidence": round(
                confidence,
                2
            )

        }), 200

    except Exception as e:

        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({
            "error": "Image analysis failed.",
            "details": str(e)
        }), 500


# --------------------------------------------------
# ANALYSIS HISTORY
# --------------------------------------------------

@app.route("/history", methods=["GET"])
def history():

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM analyses
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    results = []

    for row in rows:

        results.append({
            "id": row["id"],
            "filename": row["filename"],
            "quality_score": row["quality_score"],
            "quality_label": row["quality_label"],
            "issues": row["issues"],
            "statistics": row["statistics"],
            "created_at": row["created_at"]
        })

    return jsonify(results)


# --------------------------------------------------
# SINGLE ANALYSIS
# --------------------------------------------------

@app.route("/analysis/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id):

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM analyses
        WHERE id = ?
        """,
        (analysis_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:

        return jsonify({
            "error": "Analysis not found."
        }), 404

    return jsonify({
        "id": row["id"],
        "filename": row["filename"],
        "quality_score": row["quality_score"],
        "quality_label": row["quality_label"],
        "issues": row["issues"],
        "statistics": row["statistics"],
        "created_at": row["created_at"]
    })


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":

    init_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )