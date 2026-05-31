import re
from rapidfuzz import fuzz

from ingredient_database import INGREDIENT_DATABASE
from harmful_ingredients import HARMFUL_INGREDIENTS
from allergens import ALLERGENS


# ==========================================
# NORMALIZE TEXT
# ==========================================

def normalize_text(text):
    if not text:
        return ""
    
    text = text.lower()

    replacements = {
        "|": "i",
        "l": "i", # Честа OCR грешка
        "0": "o"  # Помага при разчитане на думи, но внимаваме за Е-номерата
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

    term = term.lower().strip()

    for word in words:
        word = word.strip().lower()
        if not word:
            continue

        # Първо: Директно съвпадение като подниз (напр. "соя" в "соев лецитин")
        if term in word:
            return True

        # Второ: Fuzzy съвпадение дума по дума
        # Разбиваме фразата на отделни чисти думи
        sub_words = re.findall(r'\b\w+\b', word)
        for sub_word in sub_words:
            score = fuzz.ratio(term, sub_word)
            if score >= 85: # Свалих го леко на 85 за по-добро хващане на OCR грешки
                return True

    return False


# ==========================================
# DETECT ADDITIVES
# ==========================================

def detect_ingredients(text):

    text_normalized = normalize_text(text)

    found = []

    # ПОПРАВКА: Подаваме нормализирания текст тук
    found.extend(
        detect_e_numbers(text_normalized)
    )

    # Разбиваме текста на смислени фрази/думи
    words = re.split(r'[,;\n()\[\]\.]', text_normalized)

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

    text_normalized = normalize_text(text)

    words = re.split(r'[,;\n()\[\]\.]', text_normalized)

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

    text_normalized = normalize_text(text)

    words = re.split(r'[,;\n()\[\]\.]', text_normalized)

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
            "caffeine",
            "кофеин"
        ],

        "Soft Drink": [
            "carbonated",
            "газирана",
            "напитка"
        ],

        "Chocolate": [
            "cocoa",
            "какао",
            "шоколад"
        ],

        "Snack": [
            "chips",
            "чипс",
            "снак"
        ],

        "Processed Meat": [
            "salami",
            "sausage",
            "колбас",
            "салам",
            "месо"
        ],

        "Dairy Product": [
            "milk",
            "мляко",
            "сирене",
            "кашкавал"
        ]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in text:
                return category

    return "Unknown Product"
