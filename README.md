# AI_image_quality_detector

# VisionIQ - AI Image Quality & Defect Detection

This is my submission for the IIIT Hyderabad internship technical assessment. It's a web app that takes an uploaded image and tells you whether it's blurry, too dark, too bright, noisy, or generally fine, using a mix of classic computer vision features and a trained ML model.

## How it's built

I went with a Flask backend + Streamlit frontend setup. Backend handles the actual image analysis and talks to a SQLite database to store past results. Frontend is just a dashboard that uploads images to the backend and displays whatever comes back.

Rough flow:

```
User uploads image on Streamlit
        -> sent to Flask /analyze endpoint
        -> OpenCV extracts features (brightness, sharpness, noise, etc.)
        -> features go into a Random Forest model
        -> model predicts a condition + confidence
        -> score gets calculated, saved to SQLite
        -> result sent back and shown on screen
```

No external AI APIs, no API keys, everything runs locally.

## Why this approach

The assessment specifically says a pure computer-vision solution (just thresholding brightness/sharpness manually) isn't enough for full marks - you need an actual learned model in there. So I did a hybrid: extract meaningful CV features first, then let a Random Forest classifier make the actual decision instead of hardcoding rules like "if brightness < 50 then dark." This also gives me confidence scores for free via `predict_proba`, which I use both for the quality score and to show "how sure" the model is on the frontend.

I picked Random Forest over a deep learning model mainly because of time - training a CNN properly (getting a real dataset, GPU time, tuning) wasn't realistic in a few hours, and RF works well with small engineered feature vectors without needing normalization or huge amounts of data.

## Where the training data comes from

I didn't use an external dataset (the assessment allows generating your own controlled degradations, which is what I did). Here's the process, in `training/train_model.py`:

1. Generate a "clean" base image - I actually changed this partway through. Originally I was just doing `np.random.randint` for a full 128x128 image, which is basically static, not anything resembling a photo. Fixed it to generate a small 16x16 random grid, resize it up with cubic interpolation, then blur it slightly. That gives smoother, more photo-like structure.
2. Randomly pick one of 5 labels: GOOD, BLUR, UNDEREXPOSED, OVEREXPOSED, NOISY.
3. Apply the corresponding degradation with some randomness in severity (e.g. blur uses a random kernel size, exposure changes use a random multiplier).
4. Extract features from the degraded image, save the feature vector + label.

Did this for 3000 images, split 80/20 for train/test, trained the RF only on the 80%.

## Features I'm extracting

Nothing fancy, just the classic image-quality signals:

- **Brightness** - mean grayscale pixel value
- **Contrast** - std dev of grayscale pixels
- **Sharpness** - variance of the Laplacian (this is the standard blur-detection trick)
- **Noise** - difference between the image and a blurred version of itself
- **Saturation** - mean of the HSV saturation channel
- **Overexposed %** - fraction of pixels above 245
- **Underexposed %** - fraction of pixels below 20

These 7 numbers are what actually go into the model.

## Evaluation results

Full numbers are in `evaluation/report.txt` and the confusion matrix image is in the same folder. Quick summary: I got 99.83% accuracy on the held-out test set (600 images the model never saw during training).

I know that number looks suspiciously high, and I want to be upfront about why instead of pretending it's not a little weird. It's because my degradation severities don't overlap much - e.g. blur always uses a kernel of 7-15, there's no "in-between" case where it's ambiguous whether something counts as blurry or not. So the classes end up pretty cleanly separated in feature space, which makes it an easy problem for the classifier. This is NOT the same as saying the model would get 99.83% on real, messy photos where defects might be subtle or mixed together (like slightly blurry AND a bit dark at the same time). I think it's more honest to say: the model correctly learned the boundaries of the distribution I gave it, and that distribution happens to be an easy one.

Other limitations worth mentioning:
- It's trained on synthetic images, not real camera photos, so texture/noise patterns are different from what a real phone or DSLR photo would look like.
- It only predicts one dominant condition per image right now - if a photo is both dark and blurry, it'll pick whichever one is stronger rather than flagging both.
- Confidence scores are calibrated to this synthetic distribution, not necessarily meaningful in an absolute sense on real photos.

**A real example of this limitation showing up:** I ran my original base photo (`test.jpg` in `sample_images/` — this is the real, unmodified phone photo I used as the source for generating all the synthetic variations, including `good.jpg`, `blurry.jpg`, `dark.jpg`, `overexposed.jpg`, and `noisy.jpg`) through the app, and got:
- Brightness: 146.80, Overexposed pixels: 4.32%, Sharpness: 1068.35
- Predicted: Overexposed, but only 29% confidence, quality score 57.6 (DEGRADED)

Looking at the actual numbers, this photo isn't really overexposed - brightness is roughly mid-range and only 4.32% of pixels are anywhere near the highlight threshold. The low confidence (barely above the 20% you'd expect from guessing across 5 classes) is the model basically telling you it's unsure. This happens because the synthetic training data used pretty extreme, clearly-separated degradation levels (e.g. brightness multiplied by 1.5-2.5x for the OVEREXPOSED class), so a real photo with more natural, subtle lighting doesn't cleanly match any of the patterns it learned. This is a direct real-world example of the synthetic-to-real generalization gap mentioned above, and honestly a decent argument for why surfacing the confidence score matters - a human looking at this result can see 29% confidence and reasonably decide not to trust the label at face value.

## Explainability

For each result I show:
- the raw feature values (so you can literally see "sharpness = 236" and understand why it got flagged as blur)
- the model's confidence
- a plain-language sentence explaining the decision, generated based on which condition was predicted and its relevant stat (this logic is in `generate_explanation()` inside `streamlit_app.py`)

I didn't do Grad-CAM or saliency maps since those are really meant for CNNs looking at pixel regions - doesn't apply the same way to a Random Forest working on 7 scalar features. Interpretable stats + confidence felt like the right fit here.

## API

Backend runs on `http://127.0.0.1:5000` locally.

**GET /health** - just returns whether the server + model are up.
```json
{ "status": "healthy", "model_loaded": true }
```

**POST /analyze** - upload an image (`multipart/form-data`, field name `image`), get back the analysis.

Example:
```bash
curl -X POST http://127.0.0.1:5000/analyze -F "image=@sample_images/blurry.jpg"
```

Response looks like:
```json
{
  "id": 1,
  "filename": "blurry.jpg",
  "quality_score": 56.44,
  "quality_label": "DEGRADED",
  "predicted_condition": "BLUR",
  "issues": [{"type": "blur", "severity": "medium", "confidence": 0.47}],
  "statistics": {
    "brightness": 165.71,
    "contrast": 65.32,
    "sharpness": 236.3,
    "noise": 3.37,
    "saturation": 56.75,
    "overexposed_pixels": 0.11,
    "underexposed_pixels": 0.05
  },
  "confidence": 0.47
}
```

Returns 400 if the file's missing/invalid/unreadable, 500 if something breaks unexpectedly on the server side.

**GET /history** - all past analyses, newest first.

**GET /analysis/<id>** - one specific analysis by ID, 404 if it doesn't exist.

## Database

Just SQLite, nothing to set up manually - `backend/database.db` gets created automatically the first time you run `app.py`, along with the `analyses` table. Schema:

```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    quality_score REAL NOT NULL,
    quality_label TEXT NOT NULL,
    issues TEXT,
    statistics TEXT,
    created_at TEXT NOT NULL
);
```

## Running it locally

You need Python 3.10+ installed. Two terminals:

**Terminal 1 - backend**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Runs on port 5000, sets up the DB and uploads folder automatically on first run.

**Terminal 2 - frontend**
```bash
pip install -r frontend_requirements.txt
streamlit run streamlit_app.py
```
Opens at `http://localhost:8501`. It talks to the backend at `127.0.0.1:5000` by default, or you can override that with an `API_URL` env variable.

**If you want to retrain the model:**
```bash
cd training
pip install -r ../backend/requirements.txt matplotlib seaborn
python train_model.py
```
This overwrites `backend/model/quality_model.pkl` and regenerates the evaluation report + confusion matrix.

## About Docker

I did write a `docker-compose.yml` and Dockerfiles for both the backend and frontend (they're in the repo). Honestly though, I ran into a disk space issue on my machine trying to install Docker Desktop and couldn't get it fully set up and tested before the deadline. The compose file follows the normal pattern for a Flask + Streamlit two-container setup, with the frontend pointed at the backend via an `API_URL` env var so they can talk to each other inside Docker's network - it should work with `docker compose build && docker compose up`, I just wasn't able to verify it end-to-end myself. Everything was fully tested and works fine running directly with Python, which is the setup described above.

Didn't do a cloud deployment either since that's listed as optional.

## Environment variables

- `API_URL` - used by the Streamlit app to know where the backend is. Defaults to `http://127.0.0.1:5000`, gets set to `http://backend:5000` inside docker-compose.
- `FLASK_ENV` - set to `production` in the Docker setup.

## Sample images

In `sample_images/`:
- `test.jpg` - the original, unmodified real phone photo. This is the actual source image everything else below was generated from.
- `good.jpg` - a direct copy of `test.jpg`, representing the "clean/acceptable" condition (no degradation applied).
- `blurry.jpg`, `dark.jpg`, `overexposed.jpg`, `noisy.jpg` - synthetic degraded variations, each generated by applying one specific degradation (Gaussian blur, reduced brightness, increased brightness, added noise) to `test.jpg`.

You can throw any of these at `/analyze` to see it work. Worth noting: running `test.jpg` itself (the real, unmodified photo) through `/analyze` is what produced the low-confidence "Overexposed" result discussed in the Evaluation section above - so that exact result is reproducible using this same file.

## Tech stack

Streamlit for the frontend, Flask + Flask-CORS for the backend, OpenCV/NumPy for the CV feature extraction, scikit-learn for the Random Forest, SQLite for storage, Docker/Compose files included but not locally verified. 

