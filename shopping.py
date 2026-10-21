"""Shopping helper: builds search links for Indian fashion sites and estimates price ranges."""
from urllib.parse import quote_plus

import pandas as pd

# site -> (emoji, url builder, typical price multiplier range vs. a mid-market baseline)
SITES = {
    "Amazon": ("🛒", lambda q: f"https://www.amazon.in/s?k={quote_plus(q)}", (0.85, 1.20)),
    "Flipkart": ("🛍️", lambda q: f"https://www.flipkart.com/search?q={quote_plus(q)}", (0.80, 1.15)),
    "Myntra": ("👗", lambda q: "https://www.myntra.com/" + "-".join(q.lower().split()) + f"?rawQuery={quote_plus(q)}",
               (1.00, 1.60)),
    "Meesho": ("🏷️", lambda q: f"https://www.meesho.com/search?q={quote_plus(q)}", (0.50, 0.90)),
    "Ajio": ("🧵", lambda q: f"https://www.ajio.com/search/?text={quote_plus(q)}", (0.95, 1.50)),
}

# baseline (low, high) price in INR for a mid-market item, picked by keyword (first match wins)
PRICE_TIERS = [
    (("lehenga", "sherwani", "gown", "suit", "overcoat", "bandhgala"), (3500, 9000)),
    (("saree", "anarkali", "sharara", "gharara", "chaniya", "salwar", "nehru", "kasavu", "pattu", "veshti",
      "mundu", "pathani", "kedia"), (1500, 4500)),
    (("blazer", "jacket", "coat", "puffer", "bomber", "leather"), (1800, 4500)),
    (("dress", "jumpsuit", "co-ord", "set"), (900, 2800)),
    (("sweater", "hoodie", "sweatshirt", "cardigan", "shawl", "turtleneck"), (700, 2200)),
    (("shirt", "kurta", "kurti", "polo", "trousers", "chinos", "jeans", "palazzo", "skirt", "joggers",
      "track", "leggings"), (500, 1800)),
    (("tee", "top", "shorts", "tank"), (300, 1100)),
]
BUDGET_MULT = {"Budget (under ₹1,000 / item)": 0.55, "Mid-range": 1.0, "Premium": 1.9}


def split_pieces(outfit):
    """'Blazer + Trousers' -> ['Blazer', 'Trousers']; strips bracket notes."""
    out = []
    for p in outfit.replace("/", " or ").split("+"):
        p = p.split("(")[0].strip()
        if p:
            out.append(p)
    return out


def base_price(piece):
    low = piece.lower()
    for keys, rng in PRICE_TIERS:
        if any(k in low for k in keys):
            return rng
    return (600, 2000)


def build_query(piece, gender, color):
    colour = "" if color in ("", None) else color.lower() + " "
    return f"{colour}{piece.lower()} for {gender.lower()}"


def compare_table(piece, budget):
    """Estimated price range per site for one piece."""
    lo, hi = base_price(piece)
    m = BUDGET_MULT[budget]
    rows = []
    for site, (_, _, (a, b)) in SITES.items():
        low, high = int(round(lo * m * a, -1)), int(round(hi * m * b, -1))
        rows.append({"Website": site, "Min (₹)": low, "Max (₹)": high, "Avg (₹)": (low + high) // 2})
    return pd.DataFrame(rows)


def links(piece, gender, color):
    q = build_query(piece, gender, color)
    return {site: fn(q) for site, (_, fn, _) in SITES.items()}
