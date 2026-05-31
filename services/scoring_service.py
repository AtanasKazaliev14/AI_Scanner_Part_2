from ingredient_database import INGREDIENT_DATABASE
from harmful_ingredients import HARMFUL_INGREDIENTS


# ==========================================
# CALCULATE HEALTH SCORE
# ==========================================

def calculate_health_score(
        additives,
        harmful_ingredients,
        allergens
):

    score = 100

    details = []

    # ======================================
    # ADDITIVES
    # ======================================

    for additive in additives:

        if additive not in INGREDIENT_DATABASE:
            continue

        risk = INGREDIENT_DATABASE[additive]["risk"]

        if risk == 3:
            score -= 15
            details.append(
                f"{additive}: -15"
            )

        elif risk == 2:
            score -= 8
            details.append(
                f"{additive}: -8"
            )

        elif risk == 1:
            score -= 3
            details.append(
                f"{additive}: -3"
            )

    # ======================================
    # HARMFUL INGREDIENTS
    # ======================================

    for ingredient in harmful_ingredients:

        if ingredient not in HARMFUL_INGREDIENTS:
            continue

        risk = HARMFUL_INGREDIENTS[
            ingredient
        ]["risk"]

        if risk == 3:
            score -= 15
            details.append(
                f"{ingredient}: -15"
            )

        elif risk == 2:
            score -= 8
            details.append(
                f"{ingredient}: -8"
            )

        elif risk == 1:
            score -= 3
            details.append(
                f"{ingredient}: -3"
            )

    # ======================================
    # ALLERGENS
    # ======================================

    if len(allergens) > 0:

        penalty = min(
            len(allergens) * 5,
            20
        )

        score -= penalty

        details.append(
            f"Allergens: -{penalty}"
        )

    # ======================================
    # LIMITS
    # ======================================

    score = max(
        0,
        min(score, 100)
    )

    return score, details


# ==========================================
# HEALTH LABEL
# ==========================================

def get_health_label(score):

    if score >= 90:

        return {
            "emoji": "🟢",
            "label": "Excellent",
            "description": "Very healthy product"
        }

    elif score >= 70:

        return {
            "emoji": "🟢",
            "label": "Good",
            "description": "Generally safe product"
        }

    elif score >= 50:

        return {
            "emoji": "🟡",
            "label": "Moderate",
            "description": "Consume in moderation"
        }

    elif score >= 30:

        return {
            "emoji": "🟠",
            "label": "Poor",
            "description": "Contains several risky ingredients"
        }

    return {
        "emoji": "🔴",
        "label": "Very Poor",
        "description": "Highly processed product"
    }


# ==========================================
# RISK COLOR
# ==========================================

def risk_color(risk):

    if risk == 1:
        return "🟢"

    elif risk == 2:
        return "🟡"

    return "🔴"


# ==========================================
# PRODUCT GRADE
# ==========================================

def get_product_grade(score):

    if score >= 90:
        return "A"

    elif score >= 80:
        return "B"

    elif score >= 70:
        return "C"

    elif score >= 50:
        return "D"

    return "F"


# ==========================================
# AI SUMMARY
# ==========================================

def generate_summary(
        score,
        additives,
        harmful,
        allergens
):

    summary = []

    if score >= 80:

        summary.append(
            "This product appears relatively safe."
        )

    elif score >= 50:

        summary.append(
            "This product contains several ingredients that should be consumed in moderation."
        )

    else:

        summary.append(
            "This product is highly processed and contains multiple potentially harmful ingredients."
        )

    if additives:

        summary.append(
            f"Detected {len(additives)} food additives."
        )

    if harmful:

        summary.append(
            f"Detected {len(harmful)} potentially harmful ingredients."
        )

    if allergens:

        summary.append(
            f"Detected {len(allergens)} allergens."
        )

    return " ".join(summary)
