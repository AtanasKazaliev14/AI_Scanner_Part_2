import re

from rapidfuzz import fuzz

from databases.ingredient_database import INGREDIENT_DATABASE
from databases.harmful_ingredients import HARMFUL_INGREDIENTS
from databases.allergens import ALLERGENS


# ==========================================
# NORMALIZE TEXT
# ==========================================

def normalize_text(text):

    text = text.lower()

    replacements = {
        "|": "i"
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    return text


# ==========================================
# NORMALIZE E NUMBER
# ==========================================

def normalize_e_number(e):

    e = e.upper()

    e = e.replace(" ", "")
    e = e.replace("-", "")
    e = e.replace(".", "")
    e = e.replace(":", "")

    e = e.replace("O", "0")
    e = e.replace("I", "1")
    e = e.replace("Z", "2")
    e = e.replace("S", "5")

    return e


# ==========================================
# DETECT E NUMBERS
# ==========================================

def detect_e_numbers(text):

    found = []

    patterns = [

        r'[Ee][\s\-\.:]?\d{3}',

        r'[Ee][\s\-\.:]?\d{3}[a-zA-Z]?',

        r'E[\s\-]?\d{3}'
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text
        )

        for match in matches:

            e_clean = normalize_e_number(match)

            if e_clean in INGREDIENT_DATABASE:
                found.append(e_clean)

    return list(set(found))


# ==========================================
# FUZZY SEARCH
# ==========================================

def fuzzy_contains(term, words):

    term = term.lower()

    for word in words:

        word = word.strip().lower()

        if term in word:
            return True

        score = fuzz.ratio(
            term,
            word
        )

        if score >= 88:
            return True

    return False


# ==========================================
# DETECT ADDITIVES
# ==========================================

def detect_ingredients(text):

    text_normalized = normalize_text(text)

    found = []

    found.extend(
        detect_e_numbers(text)
    )

    words = re.split(
        r'[,;\n()\[\]]',
        text_normalized
    )

    for code, data in INGREDIENT_DATABASE.items():

        aliases = data.get(
            "aliases",
            []
        )

        for alias in aliases:

            if fuzzy_contains(
                alias,
                words
            ):
                found.append(code)
                break

    return list(set(found))


# ==========================================
# DETECT HARMFUL
# ==========================================

def detect_harmful(text):

    text = normalize_text(text)

    words = re.split(
        r'[,;\n()\[\]]',
        text
    )

    found = []

    for ingredient in HARMFUL_INGREDIENTS:

        if fuzzy_contains(
            ingredient,
            words
        ):
            found.append(
                ingredient
            )

    return list(set(found))


# ==========================================
# DETECT ALLERGENS
# ==========================================

def detect_allergens(text):

    text = normalize_text(text)

    words = re.split(
        r'[,;\n()\[\]]',
        text
    )

    found = []

    for allergen in ALLERGENS:

        if fuzzy_contains(
            allergen,
            words
        ):
            found.append(
                allergen
            )

    return list(set(found))


# ==========================================
# PRODUCT CATEGORY
# ==========================================

def detect_product_category(text):

    text = normalize_text(text)

    categories = {

        "Energy Drink": [
            "taurine",
            "гуарана",
            "guarana",
            "caffeine"
        ],

        "Soft Drink": [
            "carbonated",
            "газирана"
        ],

        "Chocolate": [
            "cocoa",
            "какао"
        ],

        "Snack": [
            "chips",
            "чипс"
        ],

        "Processed Meat": [
            "salami",
            "sausage",
            "колбас",
            "салам"
        ],

        "Dairy Product": [
            "milk",
            "мляко"
        ]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in text:
                return category

    return "Unknown Product"
