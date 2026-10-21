"""Core module for the AI Outfit Recommender (weather + occasion + body profile).

Contains: knowledge base, synthetic dataset generator, ML training/prediction, weather API helper.
"""
import os
import random

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, "outfit_dataset.csv")
MODEL_PATH = os.path.join(BASE, "outfit_model.joblib")

# ----------------------------------------------------------------- options
GENDERS = ["Women", "Men"]
BODY_TYPES = {
    "Women": ["Hourglass", "Pear", "Apple", "Rectangle", "Inverted Triangle"],
    "Men": ["Rectangle", "Triangle", "Inverted Triangle", "Oval", "Trapezoid"],
}
HEIGHTS = ["Short", "Average", "Tall"]  # Women: <155/155-168/>168 cm ; Men: <165/165-178/>178
SKIN_TONES = ["Fair", "Light", "Wheatish", "Olive", "Tan", "Deep"]
OCCASIONS = ["Casual Outing", "College", "Office", "Interview", "Formal Event", "Wedding",
             "Party / Night Out", "Date", "Travel", "Gym / Sports",
             "Diwali", "Eid", "Christmas", "Holi", "Navratri / Durga Puja", "Pongal / Onam"]
SEASONS = ["Summer", "Monsoon", "Autumn", "Winter", "Spring"]
PERSONALITIES = ["Classic", "Trendy", "Sporty", "Bohemian", "Minimalist", "Bold"]

BODY_TYPE_HELP = {
    "Women": {
        "Hourglass": "Shoulders and hips about equal, clearly defined waist.",
        "Pear": "Hips wider than shoulders.",
        "Apple": "Fuller midsection, slimmer legs, broader shoulders/bust.",
        "Rectangle": "Shoulders, waist and hips roughly the same width.",
        "Inverted Triangle": "Shoulders broader than hips.",
    },
    "Men": {
        "Rectangle": "Shoulders and waist roughly the same width.",
        "Triangle": "Waist/hips wider than shoulders.",
        "Inverted Triangle": "Broad shoulders and chest, narrow waist.",
        "Oval": "Rounder midsection, narrower shoulders.",
        "Trapezoid": "Broad shoulders, moderate waist, athletic build.",
    },
}

# --------------------------------------------------------- knowledge base
# outfit options per (gender, occasion): [hot (>=27C), mild (16-27C), cold (<16C)]
OUTFITS = {
    "Women": {
        "Casual Outing": ["Cotton Top + Shorts/Skirt", "Tee + Jeans", "Sweater + Jeans"],
        "College": ["Kurti + Palazzo", "Tee + Jeans", "Hoodie + Jeans"],
        "Office": ["Linen Shirt + Trousers", "Blazer + Trousers", "Blazer + Turtleneck + Trousers"],
        "Interview": ["Formal Shirt + Trousers", "Blazer + Trousers", "Blazer + Turtleneck + Trousers"],
        "Formal Event": ["Midi Dress", "Jumpsuit", "Gown + Shawl"],
        "Wedding": ["Lehenga (light fabric)", "Silk Saree", "Silk Saree + Shawl"],
        "Party / Night Out": ["Bodycon/Slip Dress", "Co-ord Set", "Dress + Leather Jacket"],
        "Date": ["Sundress", "Wrap Dress", "Sweater Dress + Boots"],
        "Travel": ["Linen Co-ord + Sneakers", "Tee + Joggers/Jeans", "Puffer Jacket + Joggers"],
        "Gym / Sports": ["Dri-fit Top + Shorts", "Tank + Leggings", "Zip Jacket + Leggings"],
        "Diwali": ["Cotton Anarkali Suit", "Silk Saree", "Silk Saree + Shawl"],
        "Eid": ["Light Sharara Set", "Anarkali/Gharara Set", "Velvet Salwar Suit + Shawl"],
        "Christmas": ["Red Skater Dress", "Midi Dress + Cardigan", "Sweater Dress + Coat"],
        "Holi": ["White Kurti + Palazzo", "White Kurta Set", "White Kurta Set + Light Jacket"],
        "Navratri / Durga Puja": ["Chaniya Choli (light)", "Chaniya Choli", "Red-White Saree + Shawl"],
        "Pongal / Onam": ["Kasavu/Pattu Saree (cotton)", "Kasavu/Pattu Saree", "Pattu Saree + Shawl"],
    },
    "Men": {
        "Casual Outing": ["Tee + Shorts", "Tee + Jeans", "Sweatshirt + Jeans"],
        "College": ["Polo + Chinos", "Tee + Jeans", "Hoodie + Jeans"],
        "Office": ["Half-sleeve Shirt + Trousers", "Shirt + Trousers", "Blazer + Shirt + Trousers"],
        "Interview": ["Formal Shirt + Trousers", "Blazer + Shirt + Trousers", "Suit + Overcoat"],
        "Formal Event": ["Linen Suit", "Three-piece Suit", "Suit + Overcoat"],
        "Wedding": ["Light Kurta + Bandhgala", "Sherwani", "Sherwani + Shawl"],
        "Party / Night Out": ["Printed Shirt + Chinos", "Shirt + Jacket + Jeans", "Bomber/Leather Jacket + Jeans"],
        "Date": ["Linen Shirt + Chinos", "Casual Blazer + Tee", "Sweater + Chinos"],
        "Travel": ["Tee + Cargo Shorts", "Tee + Joggers", "Puffer Jacket + Joggers"],
        "Gym / Sports": ["Dri-fit Tee + Shorts", "Tee + Track Pants", "Zip Jacket + Track Pants"],
        "Diwali": ["Cotton Kurta + Pyjama", "Silk Kurta + Nehru Jacket", "Kurta + Nehru Jacket + Shawl"],
        "Eid": ["Pathani Suit (cotton)", "Kurta + Waistcoat", "Sherwani + Shawl"],
        "Christmas": ["Red Tee + Chinos", "Knit Sweater + Chinos", "Sweater + Coat + Jeans"],
        "Holi": ["White Tee + Shorts", "White Kurta + Pyjama", "White Kurta + Light Jacket"],
        "Navratri / Durga Puja": ["Kedia/Kurta (light)", "Kedia + Dhoti/Churidar", "Kurta + Dhoti + Shawl"],
        "Pongal / Onam": ["Cotton Mundu/Veshti + Shirt", "Veshti + Silk Shirt", "Veshti + Shirt + Angavastram"],
    },
}
# personality overrides for flexible (non-ethnic/formal) occasions
PERSONALITY_ALT = {
    "Sporty": {"Casual Outing": "Athleisure Set", "College": "Track Jacket + Joggers", "Travel": "Athleisure Set",
               "Date": "Smart Athleisure + Clean Sneakers"},
    "Bohemian": {"Casual Outing": "Boho Printed Set", "College": "Boho Printed Set", "Travel": "Flowy Boho Set",
                 "Date": "Boho Printed Set"},
    "Trendy": {"Casual Outing": "Streetwear Oversized Fit", "College": "Streetwear Oversized Fit",
               "Party / Night Out": "Statement Trend Look"},
}
FLEX = {"Casual Outing", "College", "Travel", "Date", "Party / Night Out"}

LAYERS = {  # by temperature band and rain
    "hot": "Breathable fabrics (cotton/linen), sunglasses, sunscreen",
    "warm": "No extra layer needed; light scarf optional",
    "mild": "Light jacket or shrug",
    "cold": "Warm jacket/coat, scarf",
    "freezing": "Heavy coat, thermals, gloves, beanie",
    "rain": "Carry umbrella/raincoat, quick-dry fabric, waterproof footwear",
}

FIT_ADVICE = {
    "Women": {
        "Hourglass": "Wrap and fitted silhouettes that follow your natural waist; belts work great.",
        "Pear": "A-line skirts, flared/wide-leg bottoms; draw eyes upward with detailed or bright tops.",
        "Apple": "Empire waists, V-necks, flowy tops; avoid clingy fabric at the midsection.",
        "Rectangle": "Create curves: peplum, ruffles, belted waists, layered textures.",
        "Inverted Triangle": "Wide-leg pants, A-line/full skirts; soft necklines, avoid shoulder pads.",
    },
    "Men": {
        "Rectangle": "Layer (jackets, overshirts) and pick structured shoulders to add dimension.",
        "Triangle": "Structured shoulders, darker bottoms, lighter/patterned tops; avoid tight waistlines.",
        "Inverted Triangle": "Straight/relaxed trousers, plain tops; avoid padded shoulders.",
        "Oval": "Vertical lines, dark solid colours, V-necks; untucked longer cuts that skim the body.",
        "Trapezoid": "You suit most cuts: slim/tailored fits show off your proportions.",
    },
}
HEIGHT_ADVICE = {
    "Short": "Monochrome looks, high-waisted/ankle-length bottoms, vertical stripes; avoid oversized, long layers.",
    "Average": "Most proportions work; play with layers and contrast freely.",
    "Tall": "Longer lengths, wide belts, horizontal stripes and layered looks suit you.",
}
# colour palettes: skin tone -> style
PALETTES = {
    "Fair": {"Classic": "Navy, Burgundy, Emerald, Charcoal", "Bold": "Royal Blue, Ruby Red, Fuchsia, Teal",
             "Soft": "Powder Blue, Lavender, Rose Pink, Mint"},
    "Light": {"Classic": "Maroon, Forest Green, Slate Blue, Taupe", "Bold": "Cobalt, Coral Red, Purple, Turquoise",
              "Soft": "Peach, Sky Blue, Sage Green, Blush"},
    "Wheatish": {"Classic": "Mustard, Olive, Maroon, Teal", "Bold": "Emerald, Magenta, Orange, Cobalt",
                 "Soft": "Coral, Mint, Dusty Rose, Cream"},
    "Olive": {"Classic": "Earthy Brown, Rust, Cream, Deep Green", "Bold": "Crimson, Gold, Burnt Orange, Royal Blue",
              "Soft": "Peach, Lilac, Beige, Warm White"},
    "Tan": {"Classic": "White, Beige, Olive, Navy", "Bold": "Bright Yellow, Fuchsia, Turquoise, Red",
            "Soft": "Pastel Pink, Light Blue, Mint, Ivory"},
    "Deep": {"Classic": "White, Cream, Camel, Deep Purple", "Bold": "Hot Pink, Gold, Electric Blue, Orange",
             "Soft": "Pastel Yellow, Baby Pink, Powder Blue, Lilac"},
}
AVOID_COLORS = {
    "Fair": "Very pale pastels/neon that wash you out",
    "Light": "Beige/nude shades close to your skin tone",
    "Wheatish": "Muddy browns close to your skin tone",
    "Olive": "Olive-green near face, dull yellow-greens",
    "Tan": "Mustard-brown and khaki shades that dull you",
    "Deep": "Very dark, dull browns/black without contrast",
}

NUM_COLS = ["temp_c", "rain"]
CAT_COLS = ["gender", "body_type", "height", "skin_tone", "occasion", "season", "personality"]
TARGETS = ["outfit", "fit", "height_tip", "palette"]


# --------------------------------------------------------------- labelling
def temp_band(t):
    return "hot" if t >= 31 else "warm" if t >= 24 else "mild" if t >= 16 else "cold" if t >= 8 else "freezing"


def warmth_idx(t):
    return 0 if t >= 27 else 1 if t >= 16 else 2


def palette_style(personality, occasion, season):
    if personality in ("Bold", "Trendy") and occasion not in ("Interview", "Office"):
        return "Bold"
    if personality in ("Classic", "Minimalist") or occasion in ("Interview", "Office", "Formal Event"):
        return "Classic"
    return "Soft" if season in ("Spring", "Summer", "Monsoon") else "Classic"


def label_row(r):
    outfit = OUTFITS[r["gender"]][r["occasion"]][warmth_idx(r["temp_c"])]
    alt = PERSONALITY_ALT.get(r["personality"], {})
    if r["occasion"] in FLEX and r["occasion"] in alt and r["temp_c"] >= 16:
        outfit = alt[r["occasion"]]
    return {
        "outfit": outfit,
        "fit": r["body_type"],
        "height_tip": r["height"],
        "palette": f"{r['skin_tone']}|{palette_style(r['personality'], r['occasion'], r['season'])}",
    }


def generate_dataset(n=12000, seed=42):
    rng = random.Random(seed)
    ranges = {"Summer": (30, 44), "Monsoon": (22, 32), "Autumn": (16, 30), "Winter": (2, 18), "Spring": (20, 32)}
    rows = []
    for _ in range(n):
        g = rng.choice(GENDERS)
        season = rng.choice(SEASONS)
        lo, hi = ranges[season]
        r = {"gender": g, "body_type": rng.choice(BODY_TYPES[g]), "height": rng.choice(HEIGHTS),
             "skin_tone": rng.choice(SKIN_TONES), "occasion": rng.choice(OCCASIONS), "season": season,
             "personality": rng.choice(PERSONALITIES),
             "temp_c": round(rng.uniform(lo, hi) + rng.gauss(0, 1.5), 1),
             "rain": int(rng.random() < (0.7 if season == "Monsoon" else 0.12))}
        lab = label_row(r)
        # 4% label noise to mimic real-world subjectivity of fashion advice
        if rng.random() < 0.01:
            lab["outfit"] = rng.choice(OUTFITS[g][r["occasion"]])
        rows.append({**r, **lab})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- the ML
def _pipeline():
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS)],
                            remainder="passthrough")
    return Pipeline([("pre", pre), ("rf", RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1))])


def train(verbose=True):
    df = generate_dataset()
    df.to_csv(DATA_PATH, index=False)
    X = df[CAT_COLS + NUM_COLS]
    models, report = {}, {}
    for t in TARGETS:
        Xtr, Xte, ytr, yte = train_test_split(X, df[t], test_size=0.2, random_state=42)
        m = _pipeline().fit(Xtr, ytr)
        report[t] = accuracy_score(yte, m.predict(Xte))
        models[t] = _pipeline().fit(X, df[t])  # final model on all data
        if verbose:
            print(f"{t:<11} test accuracy: {report[t]:.3f}")
    joblib.dump(models, MODEL_PATH)
    return models, report


def load_models():
    if not os.path.exists(MODEL_PATH):
        train(verbose=False)
    return joblib.load(MODEL_PATH)


def recommend(profile, models=None, top_k=3):
    """profile keys: CAT_COLS + temp_c + rain. Returns dict with the recommendation."""
    models = models or load_models()
    X = pd.DataFrame([profile])[CAT_COLS + NUM_COLS]
    out = {}
    m = models["outfit"]
    proba = m.predict_proba(X)[0]
    idx = np.argsort(proba)[::-1][:top_k]
    out["outfits"] = [(m.classes_[i], float(proba[i])) for i in idx]
    fit = models["fit"].predict(X)[0]
    out["fit_advice"] = FIT_ADVICE[profile["gender"]][fit]
    out["height_advice"] = HEIGHT_ADVICE[models["height_tip"].predict(X)[0]]
    tone, style = models["palette"].predict(X)[0].split("|")
    out["palette_style"] = style
    out["colors"] = PALETTES[tone][style]
    out["avoid"] = AVOID_COLORS[tone]
    tips = [LAYERS[temp_band(profile["temp_c"])]]
    if profile["rain"]:
        tips.append(LAYERS["rain"])
    out["weather_tips"] = tips
    return out


# ----------------------------------------------------------------- weather
def get_weather(city):
    """Live weather via free Open-Meteo API (no key). Returns (temp_c, rain_bool, place) or None."""
    try:
        import requests
        g = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                         params={"name": city, "count": 1}, timeout=8).json()
        if not g.get("results"):
            return None
        loc = g["results"][0]
        w = requests.get("https://api.open-meteo.com/v1/forecast",
                         params={"latitude": loc["latitude"], "longitude": loc["longitude"],
                                 "current": "temperature_2m,precipitation"}, timeout=8).json()["current"]
        rain = w["precipitation"] > 0
        return w["temperature_2m"], rain, f"{loc['name']}, {loc.get('country', '')}"
    except Exception:
        return None


def season_from_month(month):
    return {3: "Spring", 4: "Summer", 5: "Summer", 6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
            10: "Autumn", 11: "Autumn", 12: "Winter", 1: "Winter", 2: "Winter"}[month]
