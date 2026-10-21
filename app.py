import datetime
import os

import streamlit as st

import outfit_ai as ai
import shopping as shop

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

st.set_page_config(page_title="StyleSense AI", page_icon="👗", layout="wide")

# ------------------------------------------------------------------ styling
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#fff5f9 0%,#f3eaff 50%,#eaf4ff 100%);}
/* force readable dark text everywhere (works in Streamlit light & dark themes) */
.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"],
.stRadio label, .stCheckbox label, .stSelectbox label, .stSlider label {color:#1e1b2e !important;}
.hero, .hero h1, .hero p, .pill, div.stButton>button, div[data-testid="stFormSubmitButton"] button,
div[data-testid="stFormSubmitButton"] button p {color:#ffffff !important;}
.pill.alt {color:#5a1596 !important;}
.sw span {color:#222 !important;}
.big {color:transparent !important;}
.stAlert, .stAlert p, .stAlert div {color:#1e1b2e !important;}
div[data-baseweb="select"] > div, input, textarea {background:#ffffff !important;color:#1e1b2e !important;}
div[data-baseweb="select"] span, div[data-baseweb="select"] div {color:#1e1b2e !important;}
[data-baseweb="popover"] li, [data-baseweb="popover"] div {color:#1e1b2e !important;background:#ffffff;}
[data-testid="stForm"] {background:rgba(255,255,255,.75);border-radius:20px;border:1px solid #e3d3f5;}
.hero {border-radius:24px;padding:38px 40px;color:#fff;margin-bottom:18px;
  background:linear-gradient(120deg,#7b2cbf,#ff4b9b);
  box-shadow:0 10px 30px rgba(150,60,200,.35);}
.hero h1{font-size:3rem;margin:0;font-weight:800;letter-spacing:-1px;color:#fff;}
.hero p{font-size:1.15rem;margin:6px 0 0;opacity:.95;color:#fff;}
.card{background:#fff;border-radius:20px;padding:22px 24px;box-shadow:0 6px 22px rgba(0,0,0,.08);margin-bottom:16px;}
.pill{display:inline-block;padding:6px 14px;margin:3px 4px 3px 0;border-radius:999px;
  background:linear-gradient(90deg,#8e2de2,#ff4b9b);color:#fff;font-weight:600;font-size:.9rem;}
.pill.alt{background:#f0e6ff;color:#6a1bb1;}
.sw{display:inline-block;text-align:center;margin:6px 10px 6px 0;}
.sw div.c{width:78px;height:78px;border-radius:50%;border:3px solid #fff;box-shadow:0 4px 12px rgba(0,0,0,.25);}
.sw span{font-size:.8rem;font-weight:600;color:#444;display:block;margin-top:6px;}
.big{font-size:2rem;font-weight:800;background:linear-gradient(90deg,#8e2de2,#ff4b9b);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;}
.look{display:flex;gap:8px;align-items:center;margin:8px 0;font-weight:600;color:#444;}
.look .dot{width:34px;height:34px;border-radius:50%;border:2px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.3);}
.tip{background:#fff7e6;border-left:5px solid #ffb020;padding:10px 14px;border-radius:10px;margin:6px 0;color:#333;}
div.stButton>button, div[data-testid="stFormSubmitButton"] button{
  background:linear-gradient(90deg,#8e2de2,#ff4b9b);color:#fff;border:0;border-radius:999px;
  font-weight:700;padding:.7rem 2rem;font-size:1.1rem;}
</style>
""", unsafe_allow_html=True)

COLOR_HEX = {
    "Navy": "#1f2a56", "Burgundy": "#800020", "Emerald": "#0b8a5a", "Charcoal": "#36454f",
    "Powder Blue": "#b0d4f1", "Lavender": "#c8a8e9", "Rose Pink": "#f06292", "Mint": "#a8e6cf",
    "Royal Blue": "#2748c9", "Ruby Red": "#c2123a", "Fuchsia": "#e91e8c", "Teal": "#0e8c8c",
    "Maroon": "#6d0f2a", "Forest Green": "#1d5a34", "Slate Blue": "#5c6fa8", "Taupe": "#8b7d6b",
    "Cobalt": "#0047ab", "Coral Red": "#ee5a4f", "Purple": "#7b2cbf", "Turquoise": "#2ec4c9",
    "Peach": "#ffcba4", "Sky Blue": "#87ceeb", "Sage Green": "#9caf88", "Blush": "#f7c6c7",
    "Mustard": "#e1ad01", "Olive": "#708238", "Coral": "#ff7f6e", "Dusty Rose": "#d4a0a7",
    "Cream": "#fff3d6", "Magenta": "#d4147a", "Orange": "#ff8a1f", "Earthy Brown": "#7b4b2a",
    "Rust": "#b7410e", "Deep Green": "#0b4d2c", "Crimson": "#c4112f", "Gold": "#d4a017",
    "Burnt Orange": "#cc5500", "Warm White": "#fbf3e4", "Lilac": "#c9a0dc", "Beige": "#d9c3a0",
    "White": "#ffffff", "Bright Yellow": "#ffd400", "Pastel Pink": "#ffd1dc", "Light Blue": "#a6d1f2",
    "Ivory": "#fffff0", "Camel": "#c19a6b", "Deep Purple": "#4b1a73", "Hot Pink": "#ff3d9a",
    "Electric Blue": "#1e90ff", "Pastel Yellow": "#fff3a3", "Baby Pink": "#f8c8dc",
}

WARM_ETHNIC = {"Wedding", "Diwali", "Eid", "Holi", "Navratri / Durga Puja", "Pongal / Onam"}
CATEGORY = {"Office": "work", "Interview": "work", "Formal Event": "work", "Party / Night Out": "party",
            "Date": "party", "Gym / Sports": "active", "Travel": "active", "Casual Outing": "casual",
            "College": "casual", "Christmas": "party"}
CAT_LABEL = {"work": "Smart & Professional", "ethnic": "Festive & Traditional", "party": "Glam & Evening",
             "active": "Active & Comfy", "casual": "Everyday Casual", "winter": "Cosy Layers"}


def pick_image(gender, occasion, temp):
    cat = "ethnic" if occasion in WARM_ETHNIC else CATEGORY.get(occasion, "casual")
    if temp < 16 and cat in ("casual", "active", "party"):
        cat = "winter"
    pre = "women" if gender == "Women" else "men"
    return cat, os.path.join(ASSETS, f"{pre}_{cat}.jpg")


def swatches(colors_str):
    html = ""
    for name in [c.strip() for c in colors_str.split(",")]:
        html += f"<div class='sw'><div class='c' style='background:{COLOR_HEX.get(name, '#ccc')}'></div><span>{name}</span></div>"
    return html


@st.cache_resource
def get_models():
    return ai.load_models()


models = get_models()

# ------------------------------------------------------------------- header
st.markdown("""<div class='hero'><h1>✨ StyleSense AI</h1>
<p>Outfits picked for your body, skin tone, occasion, season &amp; today's weather.</p></div>""",
            unsafe_allow_html=True)

left, right = st.columns([1, 1.5], gap="large")

with left:
    st.markdown("### 📝 Tell us about you")
    gender = st.radio("Outfit category", ai.GENDERS, horizontal=True)
    with st.form("survey"):
        body = st.selectbox("Body type", ai.BODY_TYPES[gender],
                            help="; ".join(f"{k}: {v}" for k, v in ai.BODY_TYPE_HELP[gender].items()))
        height_cm = st.number_input("Height (cm)", 120, 220, 165)
        skin = st.select_slider("Skin tone", ai.SKIN_TONES, value="Wheatish")
        personality = st.selectbox("Personality / style", ai.PERSONALITIES)
        occasion = st.selectbox("Occasion / festival", ai.OCCASIONS)
        budget = st.selectbox("💰 Shopping budget", list(shop.BUDGET_MULT.keys()), index=1)
        city = st.text_input("📍 City (live weather) - or leave blank")
        season = st.selectbox("Season", ai.SEASONS,
                              index=ai.SEASONS.index(ai.season_from_month(datetime.date.today().month)))
        manual_temp = st.slider("🌡️ Temperature °C (if no city)", -5, 45, 28)
        manual_rain = st.checkbox("🌧️ It is raining")
        go = st.form_submit_button("✨ Recommend my outfit")

with right:
    if not go:
        st.image(os.path.join(ASSETS, "hero_banner.jpg"), use_container_width=True)
        st.info("Fill in the survey and hit **Recommend my outfit** to see your personalised looks 👈")
    else:
        temp, rain, place = manual_temp, int(manual_rain), None
        if city.strip():
            w = ai.get_weather(city.strip())
            if w:
                temp, rain, place = w[0], int(w[1]), w[2]
            else:
                st.warning("Could not fetch weather - using manual values.")
        lo, hi = (155, 168) if gender == "Women" else (165, 178)
        height = "Short" if height_cm < lo else "Average" if height_cm <= hi else "Tall"
        profile = dict(gender=gender, body_type=body, height=height, skin_tone=skin, occasion=occasion,
                       season=season, personality=personality, temp_c=float(temp), rain=rain)
        rec = ai.recommend(profile, models)
        cat, img = pick_image(gender, occasion, temp)
        names = [c.strip() for c in rec["colors"].split(",")]

        st.success(f"{'🌧️' if rain else '☀️'} {temp:.1f}°C" + (f" in {place}" if place else "")
                   + f"  •  {season}  •  {occasion}")

        c1, c2 = st.columns([1, 1.1], gap="medium")
        with c1:
            st.image(img, caption=f"Look inspiration: {CAT_LABEL[cat]}", use_container_width=True)
        with c2:
            st.markdown(f"<div class='card'><p style='margin:0;color:#888'>Your best outfit</p>"
                        f"<p class='big'>{rec['outfits'][0][0]}</p>"
                        f"<p style='color:#555'>AI confidence: <b>{rec['outfits'][0][1]:.0%}</b></p>"
                        + "".join(f"<span class='pill alt'>{o} · {p:.0%}</span>"
                                  for o, p in rec["outfits"][1:] if p > 0.01)
                        + "</div>", unsafe_allow_html=True)
            top, bottom, acc = names[0], names[1 % len(names)], names[2 % len(names)]
            st.markdown("<div class='card'><b>🧩 Suggested colour combo</b>"
                        f"<div class='look'><div class='dot' style='background:{COLOR_HEX.get(top)}'></div>Top / Main: {top}</div>"
                        f"<div class='look'><div class='dot' style='background:{COLOR_HEX.get(bottom)}'></div>Bottom / Layer: {bottom}</div>"
                        f"<div class='look'><div class='dot' style='background:{COLOR_HEX.get(acc)}'></div>Accessories: {acc}</div>"
                        "</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='card'><b>🎨 {rec['palette_style']} palette for your {skin} skin tone</b><br>"
                    f"{swatches(rec['colors'])}"
                    f"<p style='color:#a33;margin-top:8px'>🚫 Avoid: {rec['avoid']}</p></div>",
                    unsafe_allow_html=True)

        t1, t2 = st.columns(2)
        with t1:
            st.markdown(f"<div class='card'><b>📐 Fit for {body} body</b><p>{rec['fit_advice']}</p>"
                        f"<b>📏 Height ({height})</b><p>{rec['height_advice']}</p></div>",
                        unsafe_allow_html=True)
        with t2:
            st.markdown("<div class='card'><b>🌦️ Weather tips</b>"
                        + "".join(f"<div class='tip'>{t}</div>" for t in rec["weather_tips"]) + "</div>",
                        unsafe_allow_html=True)

        st.markdown("### 🖼️ More looks to explore")
        others = [c for c in ("casual", "work", "party", "ethnic", "active", "winter") if c != cat][:3]
        cols = st.columns(3)
        pre = "women" if gender == "Women" else "men"
        for col, c in zip(cols, others):
            col.image(os.path.join(ASSETS, f"{pre}_{c}.jpg"), caption=CAT_LABEL[c], use_container_width=True)

        # ------------------------------------------------------------- shopping
        st.markdown("---")
        st.markdown("## 🛍️ Shop this look & compare prices")
        st.caption(f"Budget: **{budget}**. Buttons open live search results on each store. "
                   "Prices below are *estimated typical ranges* — check the store for today's exact price.")
        shop_outfits = [o for o, p in rec["outfits"] if p > 0.01] or [rec["outfits"][0][0]]
        tabs = st.tabs([f"👗 {o}" for o in shop_outfits])
        for tab, outfit in zip(tabs, shop_outfits):
            with tab:
                pieces = shop.split_pieces(outfit)
                totals = {s: 0 for s in shop.SITES}
                for i, piece in enumerate(pieces):
                    colour = names[i % len(names)]
                    st.markdown(f"<div class='card'><b>{piece}</b> &nbsp;"
                                f"<span class='pill alt'>🎨 {colour}</span></div>", unsafe_allow_html=True)
                    lk = shop.links(piece, gender, colour)
                    bcols = st.columns(len(lk))
                    for bc, (site, url) in zip(bcols, lk.items()):
                        bc.link_button(f"{shop.SITES[site][0]} {site}", url, use_container_width=True)
                    df = shop.compare_table(piece, budget)
                    for _, r_ in df.iterrows():
                        totals[r_["Website"]] += int(r_["Avg (₹)"])
                    cc1, cc2 = st.columns([1.1, 1])
                    cc1.dataframe(df.set_index("Website"), use_container_width=True)
                    cc2.bar_chart(df.set_index("Website")["Avg (₹)"], color="#8e2de2")
                if len(pieces) > 1:
                    st.markdown("#### 💰 Whole-outfit estimate by site")
                    import pandas as pd
                    tdf = pd.DataFrame({"Website": list(totals), "Estimated total (₹)": list(totals.values())})
                    cheapest = tdf.loc[tdf["Estimated total (₹)"].idxmin()]
                    st.success(f"Typically cheapest: **{cheapest['Website']}** "
                               f"(≈ ₹{int(cheapest['Estimated total (₹)']):,} for the full outfit)")
                    st.bar_chart(tdf.set_index("Website"), color="#ff4b9b")
                else:
                    cheapest = df.loc[df["Avg (₹)"].idxmin()]
                    st.success(f"Typically cheapest: **{cheapest['Website']}** (≈ ₹{int(cheapest['Avg (₹)']):,})")
