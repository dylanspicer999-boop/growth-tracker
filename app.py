import json
from google import genai
from google.genai import types
from PIL import Image
import streamlit as st

# Page Config
st.set_page_config(
    page_title="5'11\" | 140 lb Growth & Debloat Tracker",
    page_icon="🎯",
    layout="wide",
)

# Red & Black Custom CSS Theme
st.markdown(
    """
<style>
    .stApp { background-color: #09090b; color: #f4f4f5; }
    h1, h2, h3 { color: #ef4444 !important; }
    .metric-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .badge-red { background: #7f1d1d; color: #fca5a5; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
    .badge-green { background: #14532d; color: #86efac; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)

# Daily Targets for 5'11" | 140 lbs | Age 14
TARGETS = {
    "Rest / School Day": {
        "calories": 2650,
        "protein": 140,
        "fats": 88,
        "carbs": 325,
        "cholesterol": 550,
        "potassium": 4200,
        "sodium": 2000,
        "sugar_cap": 25,
        "calcium": 1400,
        "zinc": 15,
        "magnesium": 410,
        "vitamin_d_iu": 2000,
        "vitamin_k2_mcg": 120,
    },
    "Practice / Training Day": {
        "calories": 3130,
        "protein": 150,
        "fats": 104,
        "carbs": 398,
        "cholesterol": 550,
        "potassium": 4500,
        "sodium": 2250,
        "sugar_cap": 25,
        "calcium": 1400,
        "zinc": 15,
        "magnesium": 410,
        "vitamin_d_iu": 2000,
        "vitamin_k2_mcg": 120,
    },
    "Full Match / Game Day": {
        "calories": 3438,
        "protein": 155,
        "fats": 110,
        "carbs": 460,
        "cholesterol": 550,
        "potassium": 4700,
        "sodium": 2500,
        "sugar_cap": 25,
        "calcium": 1400,
        "zinc": 15,
        "magnesium": 410,
        "vitamin_d_iu": 2000,
        "vitamin_k2_mcg": 120,
    },
}

# 1-Tap Quick-Add Meal Presets
PRESET_MEALS = {
    "🍳 3 Eggs + Sourdough + Butter + Banana": {
        "meal_name": "3 Whole Eggs, Sourdough w/ Grass-Fed Butter & Banana",
        "calories": 740,
        "protein": 36,
        "fats": 34,
        "carbs": 72,
        "cholesterol": 555,
        "potassium": 650,
        "sodium": 480,
        "added_sugar": 0,
        "calcium": 120,
        "zinc": 3,
        "magnesium": 65,
        "vitamin_d_iu": 150,
        "vitamin_k2_mcg": 45,
        "acne_risk": "Low",
        "acne_note": "Zero refined sugar and clean whole-food fats.",
        "growth_tip": "Hits 100% of your daily cholesterol target for hormone synthesis right at breakfast.",
    },
    "🥩 Steak + Baked Potato + Butter + Avocado": {
        "meal_name": "8oz Sirloin Steak, Large Baked Potato w/ Butter & Half Avocado",
        "calories": 920,
        "protein": 62,
        "fats": 44,
        "carbs": 70,
        "cholesterol": 165,
        "potassium": 1850,
        "sodium": 520,
        "added_sugar": 0,
        "calcium": 60,
        "zinc": 10,
        "magnesium": 115,
        "vitamin_d_iu": 20,
        "vitamin_k2_mcg": 35,
        "acne_risk": "Low",
        "acne_note": "High zinc actively lowers pore inflammation.",
        "growth_tip": "Massive 1,850mg potassium hit to flush facial water retention.",
    },
    "🧀 Greek Yogurt + Honey + Berries + Pumpkin Seeds": {
        "meal_name": "1.5 Cups Whole Greek Yogurt, Raw Honey, Berries & Pumpkin Seeds",
        "calories": 540,
        "protein": 38,
        "fats": 22,
        "carbs": 48,
        "cholesterol": 45,
        "potassium": 620,
        "sodium": 160,
        "added_sugar": 0,
        "calcium": 450,
        "zinc": 4,
        "magnesium": 160,
        "vitamin_d_iu": 100,
        "vitamin_k2_mcg": 15,
        "acne_risk": "Low",
        "acne_note": "Fermented Greek yogurt has lower IGF-1 impact than skim milk.",
        "growth_tip": "High calcium + 160mg magnesium for bone density and deep sleep.",
    },
}

STAT_KEYS = [
    "calories",
    "protein",
    "fats",
    "carbs",
    "cholesterol",
    "potassium",
    "sodium",
    "added_sugar",
    "calcium",
    "zinc",
    "magnesium",
    "vitamin_d_iu",
    "vitamin_k2_mcg",
]

if "meals" not in st.session_state:
    st.session_state.meals = []
if "totals" not in st.session_state:
    st.session_state.totals = {k: 0.0 for k in STAT_KEYS}
if "latest" not in st.session_state:
    st.session_state.latest = None


def log_meal_data(data):
    st.session_state.meals.append(data)
    for k in STAT_KEYS:
        st.session_state.totals[k] += float(data.get(k, 0) or 0)
    st.session_state.latest = data


# Sidebar Controls
st.sidebar.markdown("### ⚙️ Tracker Controls")
api_key_input = st.sidebar.text_input(
    "Gemini API Key (from aistudio.google.com)", type="password"
)
day_type = st.sidebar.selectbox(
    "Select Today's Schedule", list(TARGETS.keys()), index=1
)
t = TARGETS[day_type]

if st.sidebar.button("🔄 Reset Today's Log", use_container_width=True):
    st.session_state.meals = []
    st.session_state.totals = {k: 0.0 for k in STAT_KEYS}
    st.session_state.latest = None
    st.rerun()

st.title("🎯 5'11\" • 140 LB GROWTH & DEBLOAT TRACKER")
st.caption(
    "Fueling height growth (HGH), bone width, and 2:1 potassium-to-sodium facial debloating"
)

col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown("### ⚡ 1-Tap Quick Meals")
    for label, preset in PRESET_MEALS.items():
        if st.button(label, use_container_width=True):
            log_meal_data(preset)
            st.rerun()

    st.markdown("---")
    st.markdown("### 📸 Scan & Log Custom Meal")
    uploaded_file = st.file_uploader(
        "Snap or Upload Food Photo (Optional)", type=["jpg", "jpeg", "png", "webp"]
    )
    meal_notes = st.text_area(
        "Extra Details (e.g., 'Cooked in 2 tbsp grass-fed butter, lightly salted')"
    )

    if st.button("🔥 Scan & Add Meal Stats", type="primary", use_container_width=True):
        key = api_key_input.strip()
        if not key:
            st.error("Please paste your free Gemini API key in the sidebar first.")
        elif uploaded_file is None and not meal_notes.strip():
            st.error("Upload a photo or type what you ate.")
        else:
            with st.spinner("Analyzing nutrients with Gemini..."):
                client = genai.Client(api_key=key)
                prompt = f"""
                You are an expert sports nutritionist analyzing a meal for a 14-year-old male athlete (5'11", 140 lbs).
                User's extra notes about the meal: {meal_notes}

                Carefully estimate the nutrition stats using USDA standards.
                Return ONLY a valid JSON object with these exact keys:
                {{
                  "meal_name": "Short descriptive title",
                  "calories": integer,
                  "protein": number,
                  "fats": number,
                  "carbs": number,
                  "cholesterol": number,
                  "potassium": number,
                  "sodium": number,
                  "added_sugar": number,
                  "calcium": number,
                  "zinc": number,
                  "magnesium": number,
                  "vitamin_d_iu": number,
                  "vitamin_k2_mcg": number,
                  "acne_risk": "Low" or "Moderate" or "High",
                  "acne_note": "1 short sentence explaining acne impact (sugar/skim dairy)",
                  "growth_tip": "1 short sentence on how this meal helps height, bone density, or debloating"
                }}
                """
                contents = [prompt]
                if uploaded_file is not None:
                    img = Image.open(uploaded_file)
                    contents.append(img)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                data = json.loads(response.text)
                log_meal_data(data)
                st.rerun()

    if st.session_state.latest:
        lat = st.session_state.latest
        badge = "badge-green" if lat.get("acne_risk") == "Low" else "badge-red"
        st.markdown(
            f"""
        <div class="metric-card">
            <div style="font-weight:700; font-size:16px; margin-bottom:6px;">Latest Logged: {lat.get('meal_name')}</div>
            <div style="font-size:13px; margin-bottom:6px;">
                Acne Trigger Risk: <span class="{badge}">{lat.get('acne_risk')}</span> — {lat.get('acne_note')}
            </div>
            <div style="font-size:13px; color:#a1a1aa;">💡 {lat.get('growth_tip')}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if st.session_state.meals:
        st.markdown("#### 📋 Today's Logged Meals")
        for i, m in enumerate(st.session_state.meals, 1):
            st.markdown(
                f"**{i}. {m['meal_name']}** — `{int(m['calories'])} kcal | {int(m['protein'])}g P | {int(m['potassium'])}mg K | {int(m['sodium'])}mg Na`"
            )

with col2:
    tot = st.session_state.totals
    k_val = tot["potassium"]
    na_val = max(tot["sodium"], 1.0)
    ratio = round(k_val / na_val, 2) if tot["sodium"] > 0 else 0.0
    ratio_badge = "badge-green" if ratio >= 1.8 else "badge-red"

    st.markdown("### 📊 Live Stat Dashboard")
    st.markdown(
        f"""
    <div class="metric-card" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:12px; color:#a1a1aa;">LIVE POTASSIUM : SODIUM DEBLOAT RATIO</div>
            <div style="font-size:20px; font-weight:700;">{ratio} : 1 <span style="font-size:13px; font-weight:400; color:#a1a1aa;">(Goal is 2.0 : 1)</span></div>
        </div>
        <span class="{ratio_badge}">{'DEBLOATING ZONE' if ratio >= 1.8 else 'NEEDS MORE POTASSIUM'}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    def render_progress(label, val, goal, unit="", warn_over=False):
        pct = min(1.0, float(val) / float(goal)) if goal > 0 else 0.0
        status = " ⚠️ OVER CAP!" if (warn_over and val > goal) else ""
        st.markdown(f"**{label}** — `{round(val, 1)} / {goal} {unit}`{status}")
        st.progress(pct)

    st.markdown("#### 1. Core Growth & Hormone Macros")
    render_progress("Total Calories", tot["calories"], t["calories"], "kcal")
    render_progress("Protein (Bone/Muscle Matrix)", tot["protein"], t["protein"], "g")
    render_progress("Healthy Fats (T Synthesis)", tot["fats"], t["fats"], "g")
    render_progress("Clean Carbs (Cortisol Shield)", tot["carbs"], t["carbs"], "g")
    render_progress("Cholesterol (T Precursor)", tot["cholesterol"], t["cholesterol"], "mg")

    st.markdown("#### 2. Debloat & Clear Skin Guardrails")
    render_progress("Potassium (Flushes Face Water)", tot["potassium"], t["potassium"], "mg")
    render_progress("Sodium Cap (Water Control)", tot["sodium"], t["sodium"], "mg", warn_over=True)
    render_progress("Added Refined Sugar (Acne Cap)", tot["added_sugar"], t["sugar_cap"], "g", warn_over=True)

    st.markdown("#### 3. Height & Bone Density Micronutrients")
    render_progress("Calcium (Bone Width)", tot["calcium"], t["calcium"], "mg")
    render_progress("Vitamin D3", tot["vitamin_d_iu"], t["vitamin_d_iu"], "IU")
    render_progress("Vitamin K2 (Jaw/Bone Calcium Director)", tot["vitamin_k2_mcg"], t["vitamin_k2_mcg"], "mcg")
    render_progress("Zinc (Free T & Pore Defense)", tot["zinc"], t["zinc"], "mg")
    render_progress("Magnesium (Deep Sleep HGH)", tot["magnesium"], t["magnesium"], "mg")
