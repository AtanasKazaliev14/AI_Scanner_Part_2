import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import cv2

from ingredient_database import INGREDIENT_DATABASE
from harmful_ingredients import HARMFUL_INGREDIENTS

from detection_service import (
    detect_ingredients,
    detect_harmful,
    detect_allergens,
    detect_product_category
)

from services.scoring_service import (
    calculate_health_score,
    get_health_label,
    get_product_grade,
    generate_summary,
    risk_color
)
from styles.custom_css import CSS


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Food Scanner Pro",
    page_icon="🧪",
    layout="centered"
)

st.markdown(
    CSS,
    unsafe_allow_html=True
)

# ==========================================
# OCR
# ==========================================

@st.cache_resource
def load_reader():
    return easyocr.Reader(
        ['bg', 'en']
    )

reader = load_reader()

# ==========================================
# IMAGE PREPROCESSING
# ==========================================

def preprocess_image(image):

    img = np.array(image)

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_RGB2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    blur = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    return thresh


# ==========================================
# HEADER
# ==========================================

st.title("🧪 AI Food Scanner Pro")

st.markdown("""
Analyze food labels and detect:

- ⚠️ Food Additives
- 🚨 Harmful Ingredients
- 🥜 Allergens
- 🍭 Artificial Sweeteners
- 📊 Health Score
- 🤖 AI Summary
""")

# ==========================================
# UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "📤 Upload Food Label",
    type=["jpg", "jpeg", "png"]
)

# ==========================================
# PROCESS
# ==========================================

if uploaded_file:

    image = Image.open(
        uploaded_file
    )

    st.image(
        image,
        caption="Uploaded Product",
        use_container_width=True
    )

    with st.spinner(
        "🔍 Scanning ingredients..."
    ):

        processed = preprocess_image(
            image
        )

        results = reader.readtext(
            processed,
            detail=0,
            paragraph=True
        )

        extracted_text = " ".join(
            results
        )

    # ======================================
    # OCR TEXT
    # ======================================

    st.subheader(
        "📄 OCR Result"
    )

    st.text_area(
        "Detected Text",
        extracted_text,
        height=200
    )

    # ======================================
    # DETECTION
    # ======================================

    additives = detect_ingredients(
        extracted_text
    )

    harmful = detect_harmful(
        extracted_text
    )

    allergens = detect_allergens(
        extracted_text
    )

    category = detect_product_category(
        extracted_text
    )

    # ======================================
    # SCORE
    # ======================================

    score, details = calculate_health_score(
        additives,
        harmful,
        allergens
    )

    health = get_health_label(
        score
    )

    grade = get_product_grade(
        score
    )

    summary = generate_summary(
        score,
        additives,
        harmful,
        allergens
    )

    # ======================================
    # RESULTS
    # ======================================

    st.subheader(
        "🧪 Analysis"
    )

    st.markdown(
        f"## {health['emoji']} {health['label']}"
    )

    st.markdown(
        f"### Health Score: {score}/100"
    )

    st.markdown(
        f"### Grade: {grade}"
    )

    st.markdown(
        f"### Category: {category}"
    )

    st.info(
        summary
    )

    # ======================================
    # SCORE DETAILS
    # ======================================

    if details:

        with st.expander(
            "📊 Score Breakdown"
        ):

            for item in details:
                st.write(item)

    # ======================================
    # ADDITIVES
    # ======================================

    if additives:

        st.subheader(
            "⚠️ Detected Additives"
        )

        for additive in additives:

            data = INGREDIENT_DATABASE[
                additive
            ]

            color = risk_color(
                data["risk"]
            )

            st.markdown(f"""
{color} **{additive} - {data['en']}**

🇧🇬 {data['bg']}

Category: {data['category']}

Risk Level: {data['risk']}/3

ℹ️ {data['info']}
""")

    # ======================================
    # HARMFUL
    # ======================================

    if harmful:

        st.subheader(
            "🚨 Harmful Ingredients"
        )

        for ingredient in harmful:

            data = HARMFUL_INGREDIENTS[
                ingredient
            ]

            color = risk_color(
                data["risk"]
            )

            st.markdown(f"""
{color} **{ingredient.title()}**

Risk Level: {data['risk']}/3

ℹ️ {data['info']}
""")

    # ======================================
    # ALLERGENS
    # ======================================

    if allergens:

        st.subheader(
            "🥜 Allergens"
        )

        for allergen in allergens:

            st.warning(
                f"⚠️ {allergen}"
            )

    # ======================================
    # SAFE
    # ======================================

    if (
        not additives
        and not harmful
        and not allergens
    ):

        st.success(
            "✅ No risky ingredients detected."
        )

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "AI Food Scanner Pro • BG + EN OCR"
)
