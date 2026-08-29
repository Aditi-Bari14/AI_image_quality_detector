import os
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import cv2, numpy as np, os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib


# --------------------------------------------------
# IMAGE QUALITY FEATURE EXTRACTION
# --------------------------------------------------

def extract_features(image):
    """
    Extract image-quality features from an image.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 1. Brightness
    brightness = np.mean(gray)

    # 2. Contrast
    contrast = np.std(gray)

    # 3. Sharpness
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 4. Noise estimation
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    noise = np.std(gray.astype(np.float32) - blur.astype(np.float32))

    # 5. Saturation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = np.mean(hsv[:, :, 1])

    # 6. Highlight percentage
    overexposed_pixels = np.mean(gray > 245) * 100

    # 7. Shadow percentage
    underexposed_pixels = np.mean(gray < 20) * 100

    return [
        brightness,
        contrast,
        sharpness,
        noise,
        saturation,
        overexposed_pixels,
        underexposed_pixels
    ]


# --------------------------------------------------
# GENERATE A PHOTO-LIKE BASE IMAGE
# --------------------------------------------------

def generate_base_image():
    """
    Generate a random but photo-like "clean" base image.

    Pure per-pixel random noise (np.random.randint over the full
    128x128 grid) has no spatial correlation, so it doesn't resemble
    a real photograph and makes the GOOD class look artificially
    noisy/sharp. Instead, we generate a small low-frequency random
    image and upscale it with smoothing, which mimics the kind of
    smooth gradients and soft structure found in real photos.
    """

    small = np.random.randint(
        0, 256,
        (16, 16, 3),
        dtype=np.uint8
    )

    image = cv2.resize(
        small,
        (128, 128),
        interpolation=cv2.INTER_CUBIC
    )

    image = cv2.GaussianBlur(image, (5, 5), 0)

    return image


# --------------------------------------------------
# GENERATE SYNTHETIC TRAINING DATA
# --------------------------------------------------

def generate_dataset(num_images=3000):

    X = []
    y = []

    print("Generating synthetic training data...")

    for _ in range(num_images):

        # Generate a photo-like "clean" base image
        image = generate_base_image()

        condition = np.random.choice([
            "GOOD",
            "BLUR",
            "UNDEREXPOSED",
            "OVEREXPOSED",
            "NOISY"
        ])

        # ------------------------------------------
        # Apply degradation
        # ------------------------------------------

        if condition == "BLUR":

            kernel_size = np.random.choice([7, 11, 15])

            image = cv2.GaussianBlur(
                image,
                (kernel_size, kernel_size),
                0
            )

        elif condition == "UNDEREXPOSED":

            factor = np.random.uniform(0.2, 0.5)

            image = np.clip(
                image * factor,
                0,
                255
            ).astype(np.uint8)

        elif condition == "OVEREXPOSED":

            factor = np.random.uniform(1.5, 2.5)

            image = np.clip(
                image * factor,
                0,
                255
            ).astype(np.uint8)

        elif condition == "NOISY":

            noise = np.random.normal(
                0,
                np.random.uniform(25, 60),
                image.shape
            )

            image = np.clip(
                image.astype(np.float32) + noise,
                0,
                255
            ).astype(np.uint8)

        features = extract_features(image)

        X.append(features)
        y.append(condition)

    return np.array(X), np.array(y)


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

X, y = generate_dataset()

print("\nDataset shape:", X.shape)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    class_weight="balanced"
)

print("\nTraining model...")

model.fit(X_train, y_train)

# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

report_text = classification_report(y_test, predictions)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(report_text)

# --------------------------------------------------
# CONFUSION MATRIX + EVALUATION REPORT
# --------------------------------------------------

eval_dir = "../evaluation"
os.makedirs(eval_dir, exist_ok=True)

cm = confusion_matrix(y_test, predictions, labels=model.classes_)

plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    xticklabels=model.classes_,
    yticklabels=model.classes_,
    cmap="Blues"
)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.savefig(os.path.join(eval_dir, "confusion_matrix.png"))
plt.close()

with open(os.path.join(eval_dir, "report.txt"), "w") as f:

    f.write(f"Accuracy: {accuracy * 100:.2f}%\n\n")
    f.write(report_text)

    f.write("\n\nDataset Generation:\n")
    f.write(
        "- Base 'clean' images are generated as a small 16x16 random "
        "grid, upscaled to 128x128 with cubic interpolation, then "
        "lightly Gaussian-blurred. This produces smooth, low-frequency "
        "structure resembling real photo content, rather than pure "
        "per-pixel random noise.\n"
    )
    f.write(
        "- Degradations (blur, underexposure, overexposure, noise) are "
        "applied on top of the clean base image with randomized "
        "severity, and features are extracted from the degraded image.\n"
    )
    f.write(
        "- Train/test split is 80/20, stratified by class, with "
        "evaluation performed only on the held-out 20% (unseen during "
        "training).\n"
    )

    f.write("\nLimitations:\n")
    f.write(
        "- Trained on synthetic degradations applied to procedurally "
        "generated base images, not real photographs, so texture and "
        "content statistics differ from natural images.\n"
    )
    f.write(
        "- May not generalize well to compound real-world defects "
        "(e.g. motion blur combined with low light).\n"
    )
    f.write(
        "- Confidence scores reflect model certainty on the synthetic "
        "distribution and are not guaranteed to be calibrated on real "
        "images.\n"
    )

print("\nEvaluation report saved to:", os.path.join(eval_dir, "report.txt"))
print("Confusion matrix saved to:", os.path.join(eval_dir, "confusion_matrix.png"))



from sklearn.metrics import confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

cm = confusion_matrix(y_test, predictions, labels=model.classes_)
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=model.classes_, yticklabels=model.classes_, cmap="Blues")
plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.title("Confusion Matrix")
plt.tight_layout()
plt.savefig("../evaluation/confusion_matrix.png")

with open("../evaluation/report.txt", "w") as f:
    f.write(f"Accuracy: {accuracy*100:.2f}%\n\n")
    f.write(classification_report(y_test, predictions))
    f.write("\n\nLimitations:\n")
    f.write("- Trained on synthetic degradations applied to procedurally generated base images, not real photographs.\n")
    f.write("- May not generalize well to compound real-world defects (e.g. motion blur + low light together).\n")
    f.write("- Confidence scores reflect model certainty on synthetic distribution, not guaranteed calibration on real images.\n")

os.makedirs("sample_images", exist_ok=True)
img = cv2.imread("sample_images/test.jpg")  # use your existing one as the clean base
cv2.imwrite("sample_images/good.jpg", img)
cv2.imwrite("sample_images/blurry.jpg", cv2.GaussianBlur(img, (15,15), 0))
cv2.imwrite("sample_images/dark.jpg", np.clip(img*0.3,0,255).astype(np.uint8))
cv2.imwrite("sample_images/overexposed.jpg", np.clip(img*2.0,0,255).astype(np.uint8))
noisy = np.clip(img.astype(np.float32) + np.random.normal(0,40,img.shape),0,255).astype(np.uint8)
cv2.imwrite("sample_images/noisy.jpg", noisy)

# SAVE MODEL
os.makedirs("../backend/model", exist_ok=True)

model_path = "../backend/model/quality_model.pkl"

joblib.dump(model, model_path)

print("\nModel saved to:")
print(model_path)