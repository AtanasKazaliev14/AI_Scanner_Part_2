import os
from openai import OpenAI
from dotenv import load_dotenv
from ingredient_database import INGREDIENT_DATABASE
from harmful_ingredients import HARMFUL_INGREDIENTS

load_dotenv()

# ==========================================
# CALCULATE HEALTH SCORE
# ==========================================

def calculate_health_score(additives, harmful_ingredients, allergens):
    score = 100
    details = []
    penalized_names = set() # Справя се с двойното наказване

    # ======================================
    # ADDITIVES
    # ======================================
    for additive in additives:
        if additive not in INGREDIENT_DATABASE:
            continue

        data = INGREDIENT_DATABASE[additive]
        risk = data["risk"]
        name_bg = data["bg"].lower()
        
        # Записваме името, за да не го наказваме пак в harmful
        penalized_names.add(name_bg)

        if risk == 3:
            score -= 15
            details.append(f"{additive} ({data['bg']}): -15")
        elif risk == 2:
            score -= 8
            details.append(f"{additive} ({data['bg']}): -8")
        elif risk == 1:
            score -= 3
            details.append(f"{additive} ({data['bg']}): -3")

    # ======================================
    # HARMFUL INGREDIENTS
    # ======================================
    for ingredient in harmful_ingredients:
        if ingredient not in HARMFUL_INGREDIENTS:
            continue
        
        # ПОПРАВКА: Ако вече е наказано като Е-номер, пропускаме
        if ingredient.lower() in penalized_names:
            continue

        risk = HARMFUL_INGREDIENTS[ingredient]["risk"]

        if risk == 3:
            score -= 15
            details.append(f"{ingredient.title()}: -15")
        elif risk == 2:
            score -= 8
            details.append(f"{ingredient.title()}: -8")
        elif risk == 1:
            score -= 3
            details.append(f"{ingredient.title()}: -3")

    # ======================================
    # ALLERGENS
    # ======================================
    if len(allergens) > 0:
        penalty = min(len(allergens) * 5, 20)
        score -= penalty
        details.append(f"Алергени: -{penalty}")

    # ======================================
    # LIMITS
    # ======================================
    score = max(0, min(score, 100))
    return score, details


# ==========================================
# HEALTH LABEL
# ==========================================

def get_health_label(score):
    if score >= 90:
        return {"emoji": "🟢", "label": "Отличен", "description": "Много здравословен продукт"}
    elif score >= 70:
        return {"emoji": "🟢", "label": "Добър", "description": "Като цяло безопасен продукт"}
    elif score >= 50:
        return {"emoji": "🟡", "label": "Среден", "description": "Консумирайте умерено"}
    elif score >= 30:
        return {"emoji": "🟠", "label": "Лош", "description": "Съдържа няколко рискови съставки"}
    return {"emoji": "🔴", "label": "Много лош", "description": "Силно преработен продукт"}


# ==========================================
# RISK COLOR
# ==========================================

def risk_color(risk):
    if risk == 1: return "🟢"
    elif risk == 2: return "🟡"
    return "🔴"


# ==========================================
# PRODUCT GRADE
# ==========================================

def get_product_grade(score):
    if score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 50: return "D"
    return "F"


# ==========================================
# REAL AI SUMMARY (Истински AI Анализ)
# ==========================================

def generate_summary(score, additives, harmful, allergens):
    # Взимаме ключа от .env
    api_key = os.getenv("OPENAI_API_KEY")
    
    # 1. СТРАТЕГИЯ ПРИ ЛИПСА НА КЛУЧ: Връщаме стандартно текстово съобщение
    if not api_key:
        summary = [f"Продуктът има здравен рейтинг {score}/100."]
        if additives: summary.append(f"Открити добавки: {len(additives)}.")
        if harmful: summary.append(f"Открити вредни съставки: {len(harmful)}.")
        if allergens: summary.append(f"Внимание: Има {len(allergens)} алергена.")
        return " ".join(summary)

    # 2. ИСТИНСКО ИЗВИКВАНЕ НА OPENAI
    try:
        client = OpenAI(api_key=api_key)
        
        # Подготвяме ясен промпт за модела на български
        prompt = f"""
        Направи кратко и ясно резюме (до 3 изречения) на български език за хранителен продукт със следните данни:
        - Здравен резултат: {score}/100
        - Е-номера (добавки): {", ".join(additives) if additives else "Няма"}
        - Вредни съставки: {", ".join(harmful) if harmful else "Няма"}
        - Алергени: {", ".join(allergens) if allergens else "Няма"}
        Кажи дали е безопасен за ежедневна консумация.
        """

        otgovor = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти си експерт по здравословно хранене."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return otgovor.choices[0].message.content.strip()

    except Exception as e:
        # Ако OpenAI се срине, връщаме базово съобщение без да чупим програмата
        return f"Продуктът е сканиран успешно (Рейтинг: {score}/100). Генерирането на AI анализ в момента е недостъпно."
