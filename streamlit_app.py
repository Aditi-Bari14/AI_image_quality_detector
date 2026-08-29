import streamlit as st
import requests
from PIL import Image
import io
import math
import os

# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")
st.set_page_config(
    page_title="VisionIQ | Image Quality Intelligence",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HTML RENDERER
# ============================================================

def html(content):
    """
    Render HTML using Streamlit's native HTML renderer.
    This prevents HTML tags from appearing as plain text.
    """

    try:
        st.html(content)
    except AttributeError:
        st.markdown(
            content,
            unsafe_allow_html=True
        )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   GLOBAL
   ========================================================= */

@import url(
    'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap'
);

html,
body,
[class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #f5f7fb;
    color: #172033;
}

.block-container {
    max-width: 1450px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}


/* =========================================================
   STREAMLIT HEADER
   ========================================================= */

header[data-testid="stHeader"] {
    background: rgba(245,247,251,.85);
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e9f0;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.8rem;
}


/* =========================================================
   BRAND
   ========================================================= */

.brand-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 26px;
}

.brand-logo {
    width: 43px;
    height: 43px;

    border-radius: 12px;

    background: linear-gradient(
        135deg,
        #2563eb,
        #14b8a6
    );

    display: flex;
    align-items: center;
    justify-content: center;

    color: white;

    font-family: 'Space Grotesk', sans-serif;

    font-size: 20px;
    font-weight: 700;

    box-shadow:
        0 7px 18px rgba(37,99,235,.20);
}

.brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 19px;
    font-weight: 700;
    color: #111827;
}

.brand-subtitle {
    color: #8993a4;
    font-size: 10px;
    margin-top: 2px;
}


/* =========================================================
   SIDEBAR STATUS
   ========================================================= */

.sidebar-status {
    display: flex;
    align-items: center;
    gap: 8px;

    padding: 10px 12px;

    border-radius: 9px;

    background: #f0fdf8;

    border: 1px solid #d1fae5;

    color: #047857;

    font-size: 10px;
    font-weight: 600;

    margin-bottom: 25px;
}

.sidebar-status-dot {
    width: 7px;
    height: 7px;

    background: #10b981;

    border-radius: 50%;

    box-shadow: 0 0 0 4px rgba(16,185,129,.10);
}


/* =========================================================
   SIDEBAR TEXT
   ========================================================= */

.sidebar-section-title {
    color: #9aa3b2;

    font-size: 9px;

    letter-spacing: 1.4px;

    font-weight: 700;

    text-transform: uppercase;

    margin: 22px 0 10px;
}

.sidebar-info {
    color: #667085;

    font-size: 10px;

    line-height: 1.9;
}

.sidebar-info strong {
    color: #253047;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {
    margin-bottom: 32px;
}

.hero-eyebrow {
    color: #2563eb;

    font-size: 10px;

    letter-spacing: 1.7px;

    font-weight: 700;

    margin-bottom: 8px;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;

    color: #101828;

    font-size: 42px;

    font-weight: 700;

    letter-spacing: -1.8px;

    line-height: 1.1;

    margin-bottom: 10px;
}

.hero-description {
    max-width: 760px;

    color: #667085;

    font-size: 13px;

    line-height: 1.7;
}


/* =========================================================
   SYSTEM BADGE
   ========================================================= */

.system-badge {
    display: inline-flex;

    align-items: center;

    gap: 8px;

    padding: 8px 13px;

    background: #ffffff;

    border: 1px solid #e3e8ef;

    border-radius: 30px;

    color: #667085;

    font-size: 10px;

    box-shadow:
        0 3px 12px rgba(15,23,42,.04);
}

.system-dot {
    width: 6px;
    height: 6px;

    border-radius: 50%;

    background: #10b981;
}


/* =========================================================
   SECTION
   ========================================================= */

.section-header {
    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    margin-bottom: 14px;
}

.section-eyebrow {
    color: #2563eb;

    font-size: 9px;

    letter-spacing: 1.5px;

    font-weight: 700;
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;

    color: #172033;

    font-size: 19px;

    font-weight: 600;

    margin-top: 4px;
}


/* =========================================================
   CARD
   ========================================================= */

.card {
    background: #ffffff;

    border: 1px solid #e5e9f0;

    border-radius: 15px;

    padding: 22px;

    box-shadow:
        0 5px 22px rgba(15,23,42,.045);

    margin-bottom: 16px;
}


/* =========================================================
   UPLOAD CARD
   ========================================================= */

.upload-card {
    background:
        linear-gradient(
            135deg,
            #ffffff,
            #f8fbff
        );

    border: 1px solid #dfe7f3;

    border-radius: 17px;

    padding: 25px;

    margin-bottom: 20px;

    box-shadow:
        0 8px 30px rgba(37,99,235,.055);
}

.upload-title {
    color: #172033;

    font-family: 'Space Grotesk', sans-serif;

    font-size: 17px;

    font-weight: 600;

    margin-top: 5px;
}

.upload-description {
    color: #7b8494;

    font-size: 10px;

    margin-top: 5px;
}


/* =========================================================
   FILE UPLOADER
   ========================================================= */

[data-testid="stFileUploader"] {
    background: #f9fafc;

    border: 1px dashed #cdd6e3;

    border-radius: 13px;

    padding: 12px;

    transition: .2s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: #2563eb;

    background: #f7faff;
}


/* =========================================================
   BUTTON
   ========================================================= */

.stButton > button {
    width: 100%;

    min-height: 45px;

    border-radius: 9px;

    border: none;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #0ea5e9
        );

    color: white;

    font-size: 12px;

    font-weight: 700;

    box-shadow:
        0 6px 16px rgba(37,99,235,.18);

    transition: all .2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);

    box-shadow:
        0 9px 20px rgba(37,99,235,.24);

    color: white;
}


/* =========================================================
   IMAGE PREVIEW
   ========================================================= */

.preview-label {
    color: #8993a4;

    font-size: 9px;

    letter-spacing: 1.3px;

    font-weight: 700;

    margin-bottom: 8px;
}

[data-testid="stImage"] {
    border-radius: 12px;

    overflow: hidden;

    border: 1px solid #e3e8ef;

    background: #f8fafc;
}


/* =========================================================
   FILE INFO
   ========================================================= */

.info-label {
    color: #8993a4;

    font-size: 9px;

    letter-spacing: 1px;

    text-transform: uppercase;

    margin-bottom: 4px;
}

.info-value {
    color: #253047;

    font-size: 12px;

    font-weight: 600;

    margin-bottom: 16px;
}


/* =========================================================
   RESULT SCORE
   ========================================================= */

.score-card {
    background: #ffffff;

    border: 1px solid #e5e9f0;

    border-radius: 15px;

    padding: 28px;

    min-height: 315px;

    text-align: center;

    box-shadow:
        0 6px 25px rgba(15,23,42,.045);
}

.score-eyebrow {
    color: #8993a4;

    font-size: 9px;

    letter-spacing: 1.4px;

    font-weight: 700;
}

.score-number {
    font-family: 'Space Grotesk', sans-serif;

    color: #111827;

    font-size: 62px;

    font-weight: 700;

    letter-spacing: -4px;

    margin-top: 24px;
}

.score-number span {
    color: #98a2b3;

    font-size: 12px;

    letter-spacing: 0;
}

.score-status {
    display: inline-block;

    margin-top: 12px;

    padding: 7px 15px;

    border-radius: 30px;

    font-size: 10px;

    font-weight: 700;
}

.score-description {
    color: #8993a4;

    font-size: 10px;

    line-height: 1.6;

    max-width: 330px;

    margin: 17px auto 0;
}


/* =========================================================
   CONDITION
   ========================================================= */

.condition-card {
    background: #ffffff;

    border: 1px solid #e5e9f0;

    border-radius: 15px;

    padding: 28px;

    min-height: 315px;

    box-shadow:
        0 6px 25px rgba(15,23,42,.045);
}

.condition-eyebrow {
    color: #8993a4;

    font-size: 9px;

    letter-spacing: 1.4px;

    font-weight: 700;
}

.condition-icon {
    width: 55px;
    height: 55px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 14px;

    background: #f1f5ff;

    border: 1px solid #dce5ff;

    color: #2563eb;

    font-size: 24px;

    margin: 25px 0 15px;
}

.condition-name {
    font-family: 'Space Grotesk', sans-serif;

    color: #172033;

    font-size: 26px;

    font-weight: 700;
}

.confidence-row {
    display: flex;

    justify-content: space-between;

    margin-top: 32px;

    font-size: 10px;
}

.confidence-row span {
    color: #8993a4;
}

.confidence-row strong {
    color: #172033;
}

.confidence-track {
    height: 7px;

    background: #edf1f6;

    border-radius: 20px;

    overflow: hidden;

    margin-top: 9px;
}

.confidence-fill {
    height: 100%;

    border-radius: 20px;

    background:
        linear-gradient(
            90deg,
            #2563eb,
            #14b8a6
        );
}


/* =========================================================
   ISSUE
   ========================================================= */

.issue-card {
    background: #ffffff;

    border: 1px solid #e5e9f0;

    border-radius: 12px;

    padding: 17px;

    min-height: 130px;

    box-shadow:
        0 4px 15px rgba(15,23,42,.035);
}

.issue-name {
    color: #172033;

    font-family: 'Space Grotesk', sans-serif;

    font-size: 13px;

    font-weight: 600;
}

.issue-description {
    color: #7b8494;

    font-size: 10px;

    line-height: 1.5;

    margin-top: 6px;
}

.issue-meta {
    display: flex;

    justify-content: space-between;

    margin-top: 15px;

    font-size: 9px;
}


/* =========================================================
   METRICS
   ========================================================= */

.metric-card {
    background: #ffffff;

    border: 1px solid #e5e9f0;

    border-radius: 12px;

    padding: 16px;

    min-height: 120px;

    margin-bottom: 10px;

    box-shadow:
        0 4px 15px rgba(15,23,42,.03);
}

.metric-top {
    display: flex;

    justify-content: space-between;

    align-items: center;
}

.metric-name {
    color: #7b8494;

    font-size: 10px;
}

.metric-value {
    color: #172033;

    font-family: 'Space Grotesk', sans-serif;

    font-size: 20px;

    font-weight: 600;

    margin-top: 6px;
}

.metric-track {
    height: 5px;

    background: #edf1f6;

    border-radius: 10px;

    overflow: hidden;

    margin-top: 12px;
}

.metric-fill {
    height: 100%;

    background:
        linear-gradient(
            90deg,
            #2563eb,
            #14b8a6
        );

    border-radius: 10px;
}

.metric-description {
    color: #a0a8b6;

    font-size: 8px;

    margin-top: 7px;
}


/* =========================================================
   EXPLANATION
   ========================================================= */

.explanation-card {
    background:
        linear-gradient(
            135deg,
            #f5f9ff,
            #f2fbfa
        );

    border: 1px solid #dbe7f5;

    border-radius: 14px;

    padding: 22px;

    margin-top: 16px;
}

.explanation-eyebrow {
    color: #2563eb;

    font-size: 9px;

    letter-spacing: 1.4px;

    font-weight: 700;
}

.explanation-title {
    color: #172033;

    font-family: 'Space Grotesk', sans-serif;

    font-size: 15px;

    font-weight: 600;

    margin-top: 5px;
}

.explanation-text {
    color: #667085;

    font-size: 11px;

    line-height: 1.7;

    margin-top: 8px;
}


/* =========================================================
   HISTORY
   ========================================================= */

.history-row {
    display: grid;

    grid-template-columns:
        2fr
        1fr
        1fr
        1.4fr;

    gap: 15px;

    align-items: center;

    background: #ffffff;

    border: 1px solid #e5e9f0;

    border-radius: 10px;

    padding: 14px 17px;

    margin-bottom: 8px;

    box-shadow:
        0 3px 12px rgba(15,23,42,.025);
}

.history-header {
    background: #f8fafc;

    color: #8993a4;

    font-size: 9px;

    font-weight: 700;

    letter-spacing: .7px;
}

.history-file {
    color: #253047;

    font-size: 11px;

    font-weight: 600;
}

.history-result {
    color: #667085;

    font-size: 10px;
}

.history-score {
    color: #2563eb;

    font-size: 11px;

    font-weight: 700;
}

.history-time {
    color: #8993a4;

    font-size: 9px;
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    border-top: 1px solid #e4e8ee;

    margin-top: 55px;

    padding-top: 18px;

    color: #98a2b3;

    font-size: 9px;

    display: flex;

    justify-content: space-between;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media(max-width: 900px) {

    .hero-title {
        font-size: 32px;
    }

    .history-row {
        grid-template-columns: 1fr 1fr;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_condition(value):

    if not value:
        return "--"

    return (
        str(value)
        .replace("_", " ")
        .title()
    )


def condition_icon(condition):

    condition = str(
        condition
    ).upper()

    icons = {
        "GOOD": "✓",
        "BLUR": "◌",
        "NOISY": "≈",
        "UNDEREXPOSED": "☾",
        "OVEREXPOSED": "☀"
    }

    return icons.get(
        condition,
        "◈"
    )


def quality_color(label):

    label = str(
        label
    ).upper()

    if label == "ACCEPTABLE":
        return "#16a34a"

    if label == "DEGRADED":
        return "#d97706"

    if label == "DEFECTIVE":
        return "#dc2626"

    return "#2563eb"


def severity_color(severity):

    severity = str(
        severity
    ).lower()

    if severity == "high":
        return "#dc2626"

    if severity == "medium":
        return "#d97706"

    return "#0891b2"


def metric_percentage(
    value,
    maximum
):

    try:

        value = float(value)

        maximum = float(maximum)

        if maximum <= 0:
            return 0

        return max(
            0,
            min(
                100,
                (value / maximum) * 100
            )
        )

    except Exception:

        return 0


def safe_float(
    value,
    default=0
):

    try:
        return float(value)
    except Exception:
        return default


def generate_explanation(data):

    stats = data.get(
        "statistics",
        {}
    )

    condition = str(
        data.get(
            "predicted_condition",
            ""
        )
    ).upper()

    brightness = safe_float(
        stats.get("brightness")
    )

    sharpness = safe_float(
        stats.get("sharpness")
    )

    noise = safe_float(
        stats.get("noise")
    )

    messages = []

    if condition == "BLUR":

        messages.append(
            f"The model identified reduced image "
            f"sharpness. The measured Laplacian "
            f"variance is {sharpness:.2f}, indicating "
            f"loss of high-frequency detail."
        )

    elif condition == "UNDEREXPOSED":

        messages.append(
            f"The image has relatively low brightness "
            f"with a measured mean intensity of "
            f"{brightness:.2f}. This indicates "
            f"possible underexposure."
        )

    elif condition == "OVEREXPOSED":

        messages.append(
            f"The image contains elevated pixel "
            f"intensity levels. This suggests "
            f"possible overexposure and loss of "
            f"highlight detail."
        )

    elif condition == "NOISY":

        messages.append(
            f"The measured noise level is "
            f"{noise:.2f}, indicating increased "
            f"high-frequency variation across "
            f"the image."
        )

    else:

        messages.append(
            "The image was evaluated using multiple "
            "visual features including sharpness, "
            "brightness, contrast, saturation and "
            "noise."
        )

    return " ".join(messages)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    html(
        """
        <div class="brand-wrapper">

            <div class="brand-logo">
                V
            </div>

            <div>

                <div class="brand-title">
                    VisionIQ
                </div>

                <div class="brand-subtitle">
                    Image Quality Intelligence
                </div>

            </div>

        </div>
        """
    )


    html(
        """
        <div class="sidebar-status">

            <div class="sidebar-status-dot"></div>

            AI MODEL ONLINE

        </div>
        """
    )


    st.markdown(
        "### Navigation"
    )


    page = st.radio(
        "Navigation",
        [
            "Inspection",
            "Analysis History"
        ],
        label_visibility="collapsed"
    )


    st.markdown("---")


    html(
        """
        <div class="sidebar-section-title">
            Detection Engine
        </div>

        <div class="sidebar-info">

            Computer Vision +
            Machine Learning

        </div>


        <div class="sidebar-section-title">
            Quality Signals
        </div>

        <div class="sidebar-info">

            • Sharpness<br>
            • Brightness<br>
            • Contrast<br>
            • Noise<br>
            • Saturation<br>
            • Exposure

        </div>


        <div class="sidebar-section-title">
            Model
        </div>

        <div class="sidebar-info">

            <strong>
                Random Forest Classifier
            </strong>

        </div>


        <div class="sidebar-section-title">
            Backend
        </div>

        <div class="sidebar-info">

            Flask REST API

        </div>


        <div class="sidebar-section-title">
            Database
        </div>

        <div class="sidebar-info">

            SQLite

        </div>
        """
    )


# ============================================================
# HERO
# ============================================================

html(
    """
    <div class="hero">

        <div class="hero-eyebrow">
            COMPUTER VISION · AI QUALITY INSPECTION
        </div>

        <div class="hero-title">
            Image Quality Inspector
        </div>

        <div class="hero-description">

            Analyze image quality using measurable
            visual characteristics and a machine
            learning classifier. Detect blur, noise,
            exposure problems and other forms of
            visual degradation.

        </div>

    </div>
    """
)


# ============================================================
# INSPECTION PAGE
# ============================================================

if page == "Inspection":

    html(
        """
        <div class="section-header">

            <div>

                <div class="section-eyebrow">
                    STEP 01 · IMAGE INPUT
                </div>

                <div class="section-title">
                    Upload Image
                </div>

            </div>

            <div class="system-badge">

                <span class="system-dot"></span>

                Analysis engine ready

            </div>

        </div>
        """
    )


    html(
        """
        <div class="upload-card">

            <div class="upload-title">
                Upload an image for inspection
            </div>

            <div class="upload-description">

                Supported formats: JPG, JPEG, PNG and WEBP
                · Maximum file size: 200 MB

            </div>

        </div>
        """
    )


    uploaded_file = st.file_uploader(
        "Upload image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        label_visibility="collapsed"
    )


    if uploaded_file:

        image_bytes = uploaded_file.getvalue()


        try:

            image = Image.open(
                io.BytesIO(
                    image_bytes
                )
            )

        except Exception:

            st.error(
                "The uploaded file could not be read as an image."
            )

            st.stop()


        st.markdown("")


        preview_col, info_col = st.columns(
            [1.5, 1],
            gap="large"
        )


        # ====================================================
        # PREVIEW
        # ====================================================

        with preview_col:

            html(
                """
                <div class="preview-label">
                    IMAGE PREVIEW
                </div>
                """
            )


            st.image(
                image,
                use_container_width=True
            )


        # ====================================================
        # FILE INFORMATION
        # ====================================================

        with info_col:

            html(
                f"""
                <div class="card">

                    <div class="section-eyebrow">
                        FILE INFORMATION
                    </div>


                    <div style="
                        margin-top:20px;
                    ">

                        <div class="info-label">
                            Filename
                        </div>

                        <div class="info-value">
                            {uploaded_file.name}
                        </div>


                        <div class="info-label">
                            Format
                        </div>

                        <div class="info-value">
                            {image.format or "Unknown"}
                        </div>


                        <div class="info-label">
                            Dimensions
                        </div>

                        <div class="info-value">
                            {image.width} × {image.height} px
                        </div>


                        <div class="info-label">
                            File Size
                        </div>

                        <div class="info-value">
                            {len(image_bytes) / 1024:.1f} KB
                        </div>

                    </div>

                </div>
                """
            )


            analyze = st.button(
                "Run AI Inspection  →",
                use_container_width=True
            )


        # ====================================================
        # ANALYSIS
        # ====================================================

        if analyze:

            with st.spinner(
                "Running computer vision analysis..."
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/analyze",

                        files={
                            "image": (
                                uploaded_file.name,
                                image_bytes,
                                uploaded_file.type
                            )
                        },

                        timeout=30
                    )


                    if response.status_code != 200:

                        try:

                            error = response.json().get(
                                "error",
                                "Image analysis failed."
                            )

                        except Exception:

                            error = (
                                "Image analysis failed."
                            )

                        st.error(error)

                    else:

                        data = response.json()

                        st.session_state[
                            "analysis"
                        ] = data

                        st.success(
                            "Analysis completed successfully."
                        )


                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to the Flask backend. "
                        "Please make sure this is running in "
                        "another terminal:\n\n"
                        "python backend/app.py"
                    )


                except requests.exceptions.Timeout:

                    st.error(
                        "The backend took too long to respond."
                    )


                except Exception as e:

                    st.error(
                        f"Unexpected error: {str(e)}"
                    )


    # ========================================================
    # RESULTS
    # ========================================================

    if "analysis" in st.session_state:

        data = st.session_state[
            "analysis"
        ]


        score = safe_float(
            data.get(
                "quality_score",
                0
            )
        )


        label = data.get(
            "quality_label",
            "UNKNOWN"
        )


        condition = data.get(
            "predicted_condition",
            "UNKNOWN"
        )


        confidence = safe_float(
            data.get(
                "confidence",
                0
            )
        )


        color = quality_color(
            label
        )


        st.markdown("---")


        html(
            """
            <div class="section-header">

                <div>

                    <div class="section-eyebrow">
                        STEP 02 · AI INSPECTION
                    </div>

                    <div class="section-title">
                        Quality Assessment
                    </div>

                </div>

                <div class="system-badge">

                    <span class="system-dot"></span>

                    Analysis complete

                </div>

            </div>
            """
        )


        score_col, condition_col = st.columns(
            2,
            gap="large"
        )


        # ====================================================
        # SCORE
        # ====================================================

        with score_col:

            html(
                f"""
                <div class="score-card">

                    <div class="score-eyebrow">
                        OVERALL QUALITY SCORE
                    </div>

                    <div class="score-number">

                        {score:.1f}

                        <span>
                            / 100
                        </span>

                    </div>

                    <div
                        class="score-status"
                        style="
                            color:{color};
                            background:{color}12;
                            border:1px solid {color}35;
                        "
                    >

                        {format_condition(label)}

                    </div>

                    <div class="score-description">

                        Composite image-quality assessment
                        based on computer-vision features
                        and machine-learning classification.

                    </div>

                </div>
                """
            )


        # ====================================================
        # CONDITION
        # ====================================================

        with condition_col:

            html(
                f"""
                <div class="condition-card">

                    <div class="condition-eyebrow">
                        PRIMARY FINDING
                    </div>

                    <div class="condition-icon">

                        {condition_icon(condition)}

                    </div>

                    <div class="condition-name">

                        {format_condition(condition)}

                    </div>

                    <div class="confidence-row">

                        <span>
                            Model confidence
                        </span>

                        <strong>
                            {confidence * 100:.1f}%
                        </strong>

                    </div>

                    <div class="confidence-track">

                        <div
                            class="confidence-fill"
                            style="
                                width:
                                {max(0,min(100,confidence*100)):.1f}%;
                            "
                        ></div>

                    </div>

                </div>
                """
            )


        # ====================================================
        # ISSUES
        # ====================================================

        st.markdown("")


        issues = data.get(
            "issues",
            []
        )


        html(
            f"""
            <div class="card">

                <div class="section-eyebrow">
                    QUALITY SIGNALS
                </div>

                <div class="section-title">

                    Detected Issues

                    <span style="
                        color:#98a2b3;
                        font-family:'DM Sans';
                        font-size:10px;
                        margin-left:7px;
                        font-weight:400;
                    ">

                        {len(issues)} detected

                    </span>

                </div>

            </div>
            """
        )


        if issues:

            issue_cols = st.columns(
                min(
                    3,
                    len(issues)
                )
            )


            for index, issue in enumerate(
                issues
            ):

                with issue_cols[
                    index % len(issue_cols)
                ]:

                    issue_type = issue.get(
                        "type",
                        "unknown"
                    )


                    severity = issue.get(
                        "severity",
                        "low"
                    )


                    issue_confidence = safe_float(
                        issue.get(
                            "confidence",
                            0
                        )
                    )


                    html(
                        f"""
                        <div class="issue-card">

                            <div class="issue-name">

                                {format_condition(
                                    issue_type
                                )}

                            </div>

                            <div class="issue-description">

                                Potential visual quality
                                degradation identified
                                by the inspection model.

                            </div>

                            <div class="issue-meta">

                                <span
                                    style="
                                        color:
                                        {severity_color(
                                            severity
                                        )};
                                        font-weight:600;
                                    "
                                >

                                    Severity:
                                    {format_condition(
                                        severity
                                    )}

                                </span>

                                <span style="
                                    color:#2563eb;
                                    font-weight:600;
                                ">

                                    {issue_confidence*100:.1f}%

                                </span>

                            </div>

                        </div>
                        """
                    )

        else:

            st.success(
                "✓ No significant image-quality issues detected."
            )


        # ====================================================
        # STATISTICS
        # ====================================================

        stats = data.get(
            "statistics",
            {}
        )


        st.markdown("")


        html(
            """
            <div class="card">

                <div class="section-eyebrow">
                    COMPUTER VISION FEATURES
                </div>

                <div class="section-title">
                    Image Diagnostics
                </div>

            </div>
            """
        )


        metrics = [

            (
                "Brightness",
                stats.get("brightness"),
                255,
                "Mean pixel intensity"
            ),

            (
                "Contrast",
                stats.get("contrast"),
                128,
                "Pixel intensity variation"
            ),

            (
                "Sharpness",
                stats.get("sharpness"),
                5000,
                "Laplacian variance"
            ),

            (
                "Noise",
                stats.get("noise"),
                100,
                "High-frequency variation"
            ),

            (
                "Saturation",
                stats.get("saturation"),
                255,
                "Mean HSV saturation"
            ),

            (
                "Overexposed Pixels",
                stats.get(
                    "overexposed_pixels"
                ),
                100,
                "Pixels above exposure threshold"
            )

        ]


        metric_cols = st.columns(3)


        for index, (
            name,
            value,
            maximum,
            description
        ) in enumerate(metrics):

            with metric_cols[
                index % 3
            ]:

                if value is None:

                    value_display = "--"

                    percentage = 0

                else:

                    value_float = safe_float(
                        value
                    )

                    value_display = (
                        f"{value_float:.2f}"
                    )

                    percentage = metric_percentage(
                        value_float,
                        maximum
                    )


                html(
                    f"""
                    <div class="metric-card">

                        <div class="metric-top">

                            <div class="metric-name">
                                {name}
                            </div>

                            <div class="metric-value">
                                {value_display}
                            </div>

                        </div>

                        <div class="metric-track">

                            <div
                                class="metric-fill"
                                style="
                                    width:
                                    {percentage:.1f}%;
                                "
                            ></div>

                        </div>

                        <div class="metric-description">
                            {description}
                        </div>

                    </div>
                    """
                )


        # ====================================================
        # EXPLAINABILITY
        # ====================================================

        explanation = generate_explanation(
            data
        )


        st.markdown("")


        html(
            f"""
            <div class="explanation-card">

                <div class="explanation-eyebrow">
                    MODEL INTERPRETABILITY
                </div>

                <div class="explanation-title">

                    Why did the system make this decision?

                </div>

                <div class="explanation-text">

                    {explanation}

                </div>

            </div>
            """
        )


# ============================================================
# HISTORY PAGE
# ============================================================

else:

    html(
        """
        <div class="hero">

            <div class="hero-eyebrow">
                STEP 03 · HISTORICAL ANALYSIS
            </div>

            <div class="hero-title"
                 style="font-size:34px;">

                Analysis History

            </div>

            <div class="hero-description">

                Review previously processed images
                and their quality assessments stored
                by the backend service.

            </div>

        </div>
        """
    )


    try:

        response = requests.get(
            f"{API_URL}/history",
            timeout=10
        )


        if response.status_code == 200:

            history = response.json()


            if not history:

                html(
                    """
                    <div class="card">

                        <div style="
                            text-align:center;
                            color:#8993a4;
                            padding:25px;
                            font-size:11px;
                        ">

                            No previous analyses available.

                        </div>

                    </div>
                    """
                )

            else:

                html(
                    """
                    <div class="history-row history-header">

                        <span>
                            IMAGE
                        </span>

                        <span>
                            RESULT
                        </span>

                        <span>
                            SCORE
                        </span>

                        <span>
                            ANALYZED AT
                        </span>

                    </div>
                    """
                )


                for item in history:

                    filename = item.get(
                        "filename",
                        "Unknown"
                    )


                    item_label = item.get(
                        "quality_label",
                        "--"
                    )


                    item_score = item.get(
                        "quality_score",
                        "--"
                    )


                    created_at = item.get(
                        "created_at",
                        "--"
                    )


                    try:

                        score_display = (
                            f"{float(item_score):.1f}"
                        )

                    except Exception:

                        score_display = str(
                            item_score
                        )


                    html(
                        f"""
                        <div class="history-row">

                            <span class="history-file">

                                {filename}

                            </span>

                            <span class="history-result">

                                {format_condition(
                                    item_label
                                )}

                            </span>

                            <span class="history-score">

                                {score_display} / 100

                            </span>

                            <span class="history-time">

                                {created_at}

                            </span>

                        </div>
                        """
                    )


        else:

            st.error(
                "Unable to retrieve analysis history."
            )


    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to the Flask backend. "
            "Please make sure it is running."
        )


    except requests.exceptions.Timeout:

        st.error(
            "The history request timed out."
        )


    except Exception as e:

        st.error(
            f"Error loading history: {str(e)}"
        )


# ============================================================
# FOOTER
# ============================================================

html(
    """
    <div class="footer">

        <span>
            VisionIQ · AI-Powered Image Quality Intelligence
        </span>

        <span>
            OpenCV · Scikit-learn · Flask · SQLite
        </span>

    </div>
    """
)

