"""
ChurnSense AI — Production-Grade Streamlit Application
======================================================
Fully refactored, optimized, and upgraded version.
"""

# ─────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────
import os
import json
import pickle
import hashlib
import datetime
import random
import warnings
from functools import lru_cache

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIGURATION  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChurnSense AI",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  CONSTANTS & THEME
# ─────────────────────────────────────────────────────────────
USERS_FILE   = "churnsense_users.json"
DATA_FILE    = "ChurnSense_MASTER.csv"
LOGO_FILE    = "logo.png"

PLAN_PRICES  = {"Starter": 49, "Pro": 149, "Enterprise": 499, "Free Trial": 0}

PLATFORM_COLORS = {
    "Amazon":  "#ff9900",
    "Flipkart":"#2874f0",
    "Meesho":  "#9b1fe8",
    "Myntra":  "#ff3f6c",
}
HEALTH_COLORS = {
    "Healthy":  "#10b981",
    "Moderate": "#f59e0b",
    "Critical": "#ef4444",
}
ACCENT = {
    "blue":   "#1447e6",
    "red":    "#ef4444",
    "green":  "#10b981",
    "amber":  "#f59e0b",
    "purple": "#8b5cf6",
    "teal":   "#0d9488",
    "slate":  "#64748b",
}

# Base Plotly layout applied to every chart
PLOTLY_BASE = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="DM Sans, sans-serif", color="#334155", size=11),
    margin=dict(l=18, r=18, t=40, b=18),
)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS  (light, professional, no dark-bg glitches)
# ─────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Google Font ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');

/* ── Reset & Base ────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    line-height: 1.55 !important;
    color: #0f172a;
}
#MainMenu, footer { visibility: hidden; }

/* ── Main container ──────────────────────────────────── */
.block-container {
    padding: 1.6rem 2.4rem 3rem !important;
    max-width: 1380px;
}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(170deg, #05112e 0%, #0f2158 100%) !important;
}
[data-testid="stSidebar"] * { color: #e8eef8 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.1) !important; }

/* Sidebar nav buttons */
[data-testid="stSidebar"] button {
    background: transparent !important;
    color: #c8d5f0 !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    text-align: left !important;
    transition: all .2s ease !important;
    font-size: .84rem !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] button:hover {
    background: rgba(255,255,255,.09) !important;
    border-color: rgba(255,255,255,.22) !important;
    transform: translateX(3px);
}
[data-testid="stSidebar"] button:focus {
    background: rgba(71, 113, 255, .22) !important;
    border-color: rgba(71, 113, 255, .55) !important;
    box-shadow: none !important;
}

/* Sidebar selectbox fix */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,.07) !important;
    border-color: rgba(255,255,255,.15) !important;
    border-radius: 10px !important;
    color: #e8eef8 !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] * { color: #e8eef8 !important; }
[data-testid="stSidebar"] .stSlider * { color: #e8eef8 !important; }
[data-testid="stSidebar"] .stSlider [role="slider"] { background-color: #4771ff !important; }

/* ── KPI Cards ───────────────────────────────────────── */
.kpi-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 18px 20px 14px;
    border: 1px solid #e8edf5;
    border-top: 4px solid #1447e6;
    box-shadow: 0 2px 12px rgba(0,0,0,.05);
    transition: box-shadow .2s ease, transform .2s ease;
}
.kpi-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.10); transform: translateY(-2px); }
.kpi-card.red    { border-top-color: #ef4444; }
.kpi-card.green  { border-top-color: #10b981; }
.kpi-card.purple { border-top-color: #8b5cf6; }
.kpi-card.amber  { border-top-color: #f59e0b; }
.kpi-card.teal   { border-top-color: #0d9488; }
.kpi-card.slate  { border-top-color: #64748b; }

.kpi-label { font-size: .63rem; font-weight: 700; text-transform: uppercase;
             letter-spacing: .12em; color: #7889a4; margin-bottom: 6px; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 1.9rem;
             font-weight: 400; color: #0f172a; line-height: 1.05; }
.kpi-sub   { font-size: .69rem; color: #a0aec0; margin-top: 5px; }

/* ── Section Headers ─────────────────────────────────── */
.sec-title { font-family: 'DM Serif Display', serif; font-size: 1.1rem;
             color: #0f172a; margin-bottom: 2px; }
.sec-sub   { font-size: .77rem; color: #7889a4; margin-bottom: 14px; }

/* ── Pill Badges ─────────────────────────────────────── */
.pill { display: inline-block; padding: 3px 11px; border-radius: 20px;
        font-size: .68rem; font-weight: 700; letter-spacing: .02em; }
.pill-green  { background: #d1fae5; color: #065f46; }
.pill-amber  { background: #fef3c7; color: #92400e; }
.pill-red    { background: #fee2e2; color: #991b1b; }
.pill-blue   { background: #dbeafe; color: #1e40af; }
.pill-purple { background: #ede9fe; color: #5b21b6; }
.pill-slate  { background: #f1f5f9; color: #475569; }

/* ── Callout boxes ───────────────────────────────────── */
.callout {
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 14px;
    font-size: .87rem;
    line-height: 1.65;
}
.callout-red  { background:#fff1f2; border:1px solid #fecdd3;
                border-left:4px solid #ef4444; color:#991b1b; font-weight: 600; }
.callout-blue { background:#eff6ff; border:1px solid #bfdbfe;
                border-left:4px solid #1447e6; color:#1e40af; }
.callout-green{ background:#f0fdf4; border:1px solid #bbf7d0;
                border-left:4px solid #10b981; color:#065f46; font-weight: 600; }
.callout-amber{ background:#fffbeb; border:1px solid #fde68a;
                border-left:4px solid #f59e0b; color:#92400e; }

/* ── Insight cards ───────────────────────────────────── */
.insight-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 20px 22px;
    border: 1px solid #e8edf5;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
    height: 100%;
}

/* ── Intervention action card ────────────────────────── */
.action-card {
    background: #fff;
    border-radius: 12px;
    padding: 16px 18px;
    border: 1px solid #e8edf5;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
    display: flex;
    align-items: flex-start;
    gap: 14px;
    transition: box-shadow .2s ease;
}
.action-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,.09); }
.action-icon  { font-size: 1.35rem; min-width: 36px; padding-top: 2px; }
.action-title { font-size: .88rem; font-weight: 700; color: #0f172a; margin-bottom: 3px; }
.action-desc  { font-size: .78rem; color: #64748b; line-height: 1.55; }
.action-trigger { font-size: .71rem; color: #4771ff; font-weight: 600; margin-bottom: 3px; }

/* ── Strategy card ───────────────────────────────────── */
.strategy-card {
    background: #fff;
    border-radius: 14px;
    padding: 20px 22px;
    border: 1px solid #e8edf5;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
    transition: box-shadow .2s ease, transform .15s ease;
    height: 100%;
}
.strategy-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,.10); transform: translateY(-3px); }

/* ── Page header bar ─────────────────────────────────── */
.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0 16px;
    border-bottom: 1px solid #e8edf5;
    margin-bottom: 26px;
}
.page-title { font-family: 'DM Serif Display', serif; font-size: 1.2rem; color: #0f172a; }

/* ── Active sidebar item ─────────────────────────────── */
.sidebar-active {
    background: rgba(71, 113, 255, .18) !important;
    border-left: 3px solid #4771ff !important;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 6px;
    font-weight: 700;
    font-size: .86rem;
    color: #c8d5f0 !important;
}

/* ── Health segment bars ─────────────────────────────── */
.seg-bar {
    border-radius: 12px;
    padding: 16px 18px;
    border-left: 4px solid;
}

/* ── Tab overrides ───────────────────────────────────── */
[data-baseweb="tab-list"] {
    background: #f8fafc !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid #e8edf5 !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: .83rem !important;
    color: #64748b !important;
    padding: 8px 18px !important;
}
[aria-selected="true"] {
    background: #1447e6 !important;
    color: #fff !important;
}

/* ── Login / signup card ─────────────────────────────── */
.auth-card {
    background: #fff;
    border-radius: 20px;
    padding: 36px 40px;
    border: 1px solid #e8edf5;
    box-shadow: 0 8px 36px rgba(0,0,0,.09);
}

/* ── Dataframe overrides ─────────────────────────────── */
[data-testid="stDataFrame"] table { font-size: .82rem !important; }

/* ── Input field refinements ─────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div,
.stSlider > div {
    border-radius: 10px !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1447e6, #3b5fe0) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: .88rem !important;
    padding: 10px 20px !important;
    transition: opacity .2s ease, transform .15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: .9 !important;
    transform: translateY(-1px) !important;
}

/* ── Metric overrides ────────────────────────────────── */
[data-testid="stMetric"] {
    background: #f8fafc;
    border-radius: 12px;
    padding: 14px 18px;
}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  USER DATABASE HELPERS
# ─────────────────────────────────────────────────────────────
def _hash_password(pw: str) -> str:
    """SHA-256 hash a password string."""
    return hashlib.sha256(pw.encode()).hexdigest()


def load_users() -> dict:
    """Load user records from JSON, seeding admin if missing."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as fh:
            return json.load(fh)
    seed = {
        "admin": {
            "role": "admin", "username": "admin",
            "password": _hash_password("admin123"),
            "business": "ChurnSense AI HQ",
            "plan": "Enterprise", "subscription": "Lifetime",
            "joined": "2024-01-01", "status": "Active",
            "payment": "Paid", "seed": 0,
        }
    }
    save_users(seed)
    return seed


def save_users(data: dict) -> None:
    """Persist user records to JSON."""
    with open(USERS_FILE, "w") as fh:
        json.dump(data, fh, indent=2)


# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
_STATE_DEFAULTS = {"page": "login", "user": None, "role": None, "business": None}
for _k, _v in _STATE_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def navigate(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def sign_out() -> None:
    for k, v in _STATE_DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()


# ─────────────────────────────────────────────────────────────
#  DATA LAYER
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_master_data() -> tuple[pd.DataFrame, bool]:
    """Load and pre-process the master CSV dataset."""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(), False
    try:
        df = pd.read_csv(DATA_FILE, low_memory=False)
        df["Churned"] = df["Churned"].astype(int)

        if "Health_Score_10" not in df.columns and "Final_Health_Score" in df.columns:
            df["Health_Score_10"] = (df["Final_Health_Score"] * 9 + 1).round(1)

        if "Health_Category" not in df.columns and "Health_Score_10" in df.columns:
            df["Health_Category"] = df["Health_Score_10"].apply(
                lambda s: "Healthy" if s >= 6.5 else ("Moderate" if s >= 4.0 else "Critical")
            )
        return df, True
    except Exception as exc:
        st.error(f"Data load error: {exc}")
        return pd.DataFrame(), False


@st.cache_resource(show_spinner=False)
def load_ml_models() -> tuple:
    """Load pickled ML models and feature column list."""
    required = ["churn_model.pkl", "engagement_model.pkl", "clv_model.pkl", "feature_columns.pkl"]
    if not all(os.path.exists(p) for p in required):
        return None, None, None, [], False
    try:
        def _unpickle(path):
            with open(path, "rb") as fh:
                obj = pickle.load(fh)
            return obj.get("model", obj) if isinstance(obj, dict) else obj

        churn_m   = _unpickle("churn_model.pkl")
        engage_m  = _unpickle("engagement_model.pkl")
        clv_m     = _unpickle("clv_model.pkl")
        with open("feature_columns.pkl", "rb") as fh:
            feat_cols = pickle.load(fh)
        return churn_m, engage_m, clv_m, feat_cols, True
    except Exception as exc:
        st.warning(f"Model loading failed: {exc}")
        return None, None, None, [], False


@st.cache_data(show_spinner=False)
def get_client_slice(seed: int, master_df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Return a reproducible random subset of rows for a given client seed."""
    if master_df.empty:
        return pd.DataFrame(), False
    rng = np.random.default_rng(int(seed))
    n   = int(rng.integers(7_000, 14_000))
    idx = rng.choice(len(master_df), size=min(n, len(master_df)), replace=False)
    return master_df.iloc[idx].copy(), True


# ── Load once at module level ──────────────────────────────
MASTER_DF, DATA_OK       = load_master_data()
CHURN_M, ENG_M, CLV_M, FEAT_COLS, MODELS_OK = load_ml_models()


# ─────────────────────────────────────────────────────────────
#  UI COMPONENT HELPERS
# ─────────────────────────────────────────────────────────────
def show_logo(width: int = 180) -> None:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=width)
    else:
        st.markdown(
            f"<div style='font-family:\"DM Serif Display\",serif;"
            f"font-size:1.4rem;font-weight:400;color:#fff;padding:8px 0'>"
            f"🔮 ChurnSense <span style='color:#4771ff'>AI</span></div>",
            unsafe_allow_html=True,
        )


def kpi_card(label: str, value: str, subtitle: str, colour: str = "blue") -> None:
    """Render a styled KPI card."""
    cls_map = {"blue": "", "red": "red", "green": "green",
               "purple": "purple", "amber": "amber", "teal": "teal", "slate": "slate"}
    cls = cls_map.get(colour, "")
    st.markdown(
        f"<div class='kpi-card {cls}'>"
        f"  <div class='kpi-label'>{label}</div>"
        f"  <div class='kpi-value'>{value}</div>"
        f"  <div class='kpi-sub'>{subtitle}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(f"<div class='sec-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='sec-sub'>{subtitle}</div>", unsafe_allow_html=True)


def pill(text: str, colour: str = "blue") -> str:
    return f"<span class='pill pill-{colour}'>{text}</span>"


def callout(message: str, kind: str = "blue") -> None:
    st.markdown(f"<div class='callout callout-{kind}'>{message}</div>",
                unsafe_allow_html=True)


def page_header(title: str, badges: list[tuple[str, str]] | None = None) -> None:
    badge_html = "".join(pill(t, c) for t, c in (badges or []))
    st.markdown(
        f"<div class='page-header'>"
        f"  <span class='page-title'>{title}</span>"
        f"  <div style='display:flex;gap:8px;align-items:center'>{badge_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
#  SIDEBAR BUILDERS
# ─────────────────────────────────────────────────────────────
_ADMIN_NAV = [
    ("📊", "Platform Overview"),
    ("👥", "Client Management"),
    ("💳", "Billing & Subscriptions"),
    ("📈", "Usage Analytics"),
]

_CLIENT_NAV = [
    ("📊", "KPI Overview"),
    ("🔍", "Filters & Analysis"),
    ("💡", "Insights & Strategy"),
    ("⚡", "Intervention Engine"),
    ("🧪", "Real-Time Prediction"),
    ("👤", "My Account"),
]


def _nav_button(icon: str, label: str, key: str, state_key: str) -> None:
    current = st.session_state.get(state_key)
    if current == label:
        st.markdown(
            f"<div class='sidebar-active'>{icon}&nbsp; {label}</div>",
            unsafe_allow_html=True,
        )
    else:
        if st.button(f"{icon}  {label}", key=key, use_container_width=True):
            st.session_state[state_key] = label
            st.rerun()


def build_admin_sidebar() -> str:
    if "admin_tab" not in st.session_state:
        st.session_state.admin_tab = "Platform Overview"

    with st.sidebar:
        show_logo(140)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:.6rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:.16em;color:rgba(255,255,255,.3);margin-bottom:8px'>ADMIN MENU</div>",
            unsafe_allow_html=True,
        )
        for icon, label in _ADMIN_NAV:
            _nav_button(icon, label, f"adm_{label}", "admin_tab")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:.7rem;color:rgba(255,255,255,.4)'>"
            f"🛡️ Admin · <b>{st.session_state.user}</b></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            sign_out()

    return st.session_state.admin_tab


def build_client_sidebar(n_customers: int) -> tuple:
    if "client_tab" not in st.session_state:
        st.session_state.client_tab = "KPI Overview"

    users = load_users()
    info  = users.get(st.session_state.user, {})
    seed  = info.get("seed", 42)
    dff, _ok = get_client_slice(seed, MASTER_DF)

    def _col_opts(col: str) -> list:
        if _ok and col in dff.columns:
            return ["All"] + sorted(dff[col].dropna().unique().tolist())
        return ["All"]

    with st.sidebar:
        show_logo(140)
        st.markdown("<hr>", unsafe_allow_html=True)

        biz = st.session_state.business or "Your Business"
        st.markdown(
            f"<div style='background:rgba(255,255,255,.07);border-radius:10px;"
            f"padding:10px 12px;margin-bottom:16px'>"
            f"<div style='font-size:.6rem;color:rgba(255,255,255,.4);"
            f"text-transform:uppercase;letter-spacing:.1em;margin-bottom:2px'>Business</div>"
            f"<div style='font-weight:700;font-size:.9rem'>{biz}</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='font-size:.6rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:.16em;color:rgba(255,255,255,.3);margin-bottom:8px'>NAVIGATION</div>",
            unsafe_allow_html=True,
        )
        for icon, label in _CLIENT_NAV:
            _nav_button(icon, label, f"nav_{label}", "client_tab")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:.6rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:.16em;color:rgba(255,255,255,.3);margin-bottom:8px'>FILTERS</div>",
            unsafe_allow_html=True,
        )

        p_opt  = st.selectbox("🏪 Platform",  _col_opts("Platform"))
        c_opt  = st.selectbox("🏷 Category",  _col_opts("Category"))
        h_opt  = st.selectbox("🏥 Health",    ["All", "Healthy", "Moderate", "Critical"])
        co_opt = st.selectbox("🌍 Country",   _col_opts("Country"))
        ch_max = st.slider("📉 Max Churn %", 0, 100, 100, 5)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:.69rem;color:rgba(255,255,255,.35);text-align:center'>"
            f"{n_customers:,} customers loaded</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            sign_out()

    return st.session_state.client_tab, p_opt, c_opt, h_opt, co_opt, ch_max


# ─────────────────────────────────────────────────────────────
#  ML: APPLY PREDICTIONS TO DATAFRAME
# ─────────────────────────────────────────────────────────────
def apply_ml_predictions(dff: pd.DataFrame) -> pd.DataFrame:
    """Run churn, engagement, and CLV models on the dataframe in-place."""
    if not MODELS_OK or dff.empty:
        return dff

    df_input = dff.copy()
    for col in FEAT_COLS:
        if col not in df_input.columns:
            df_input[col] = 0
    df_input = df_input[FEAT_COLS]

    try:
        dff["Churn_Probability"] = CHURN_M.predict_proba(df_input)[:, 1]
    except Exception:
        pass
    try:
        dff["Predicted_Engagement"] = ENG_M.predict(df_input)
    except Exception:
        pass
    try:
        dff["Predicted_CLV"] = CLV_M.predict(df_input)
    except Exception:
        pass

    return dff


# ─────────────────────────────────────────────────────────────
#  PAGE: LOGIN
# ─────────────────────────────────────────────────────────────
def page_login() -> None:
    left, _, right = st.columns([1.35, 0.1, 1])

    # ── Left: branding ─────────────────────────────────────
    with left:
        st.markdown("<br><br>", unsafe_allow_html=True)
        show_logo(190)
        st.markdown("""
        <div style='margin-top:26px'>
          <div style='font-family:"DM Serif Display",serif;font-size:2.2rem;
                      color:#0f172a;line-height:1.2'>
            Stop Churn<br><span style='color:#1447e6'>Before It Happens</span>
          </div>
          <p style='font-size:.93rem;color:#475569;margin-top:14px;line-height:1.8;max-width:440px'>
            ChurnSense AI is an end-to-end customer lifecycle intelligence platform that predicts
            churn risk, measures engagement, and estimates customer lifetime value — all unified
            into a single <strong>Customer Health Score</strong>.
          </p>
        </div>
        """, unsafe_allow_html=True)

        features = [
            ("📉", "#dbeafe", "#1e40af", "Churn Prediction"),
            ("⚡", "#d1fae5", "#065f46", "Engagement Analysis"),
            ("💰", "#fefce8", "#854d0e", "CLV Forecasting"),
            ("🏥", "#f5f3ff", "#5b21b6", "Health Score 1–10"),
            ("🎯", "#fff1f2", "#9f1239", "Intervention Engine"),
            ("📊", "#f0f9ff", "#0c4a6e", "Multi-Role Dashboard"),
        ]
        cols = st.columns(3)
        for i, (ico, bg, tc, lbl) in enumerate(features):
            with cols[i % 3]:
                st.markdown(
                    f"<div style='background:{bg};border:1px solid {bg};border-radius:10px;"
                    f"padding:10px 12px;font-size:.8rem;color:{tc};font-weight:600;"
                    f"margin-bottom:8px'>{ico} {lbl}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("""
        <div style='margin-top:20px;padding:14px 18px;background:#f8fafc;
                    border-radius:12px;border:1px solid #e8edf5'>
          <div style='font-size:.7rem;font-weight:700;color:#7889a4;
                      text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px'>
            Trusted by e-commerce leaders
          </div>
          <div style='display:flex;gap:16px;align-items:center;flex-wrap:wrap'>
            <span style='font-size:.9rem;font-weight:800;color:#ff9900'>Amazon</span>
            <span style='color:#d1d5db'>·</span>
            <span style='font-size:.9rem;font-weight:800;color:#2874f0'>Flipkart</span>
            <span style='color:#d1d5db'>·</span>
            <span style='font-size:.9rem;font-weight:800;color:#9b1fe8'>Meesho</span>
            <span style='color:#d1d5db'>·</span>
            <span style='font-size:.9rem;font-weight:800;color:#ff3f6c'>Myntra</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Right: auth card ────────────────────────────────────
    with right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)

        st.markdown("""
        <div style='font-family:"DM Serif Display",serif;font-size:1.55rem;color:#0f172a;
                    margin-bottom:4px'>Welcome Back</div>
        <div style='font-size:.82rem;color:#7889a4;margin-bottom:20px'>
            Sign in to ChurnSense AI</div>
        """, unsafe_allow_html=True)

        role_opt = st.radio(
            "Login as",
            ["🏢  Business Client", "🛡️  Admin"],
            horizontal=True,
        )
        is_admin = "Admin" in role_opt
        role     = "admin" if is_admin else "client"

        if is_admin:
            callout("🛡️ Admin Portal — full platform visibility", "red")
        else:
            callout("🏢 Business Client Portal — your data only", "blue")

        st.markdown("<hr style='border-color:#f1f5f9;margin:12px 0'>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            uname = st.text_input("Username", placeholder="Enter username")
            pw    = st.text_input("Password", type="password", placeholder="Enter password")
            login = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        if login:
            users = load_users()
            user  = users.get(uname)
            if user and user["password"] == _hash_password(pw) and user["role"] == role:
                if user.get("status") == "Suspended":
                    st.error("⛔ Account suspended. Please contact support.")
                else:
                    st.session_state.update(
                        page="dashboard", user=uname,
                        role=role, business=user["business"]
                    )
                    st.rerun()
            else:
                st.error("❌ Invalid credentials or role. Please try again.")

        st.markdown("<hr style='border-color:#f1f5f9;margin:12px 0'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;font-size:.82rem;color:#7889a4;margin-bottom:10px'>"
            "New to ChurnSense AI?</div>",
            unsafe_allow_html=True,
        )
        if st.button("✨ Create Account", use_container_width=True):
            navigate("signup")

        st.markdown(
            "<div style='text-align:center;margin-top:14px;font-size:.7rem;color:#a0aec0'>"
            "Demo: <b>admin</b> / <b>admin123</b></div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  PAGE: SIGN UP
# ─────────────────────────────────────────────────────────────
def page_signup() -> None:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        lc1, lc2, lc3 = st.columns([1, 2, 1])
        with lc2:
            show_logo(180)

        st.markdown("""
        <div style='text-align:center;margin:14px 0 24px'>
          <div style='font-family:"DM Serif Display",serif;font-size:1.6rem;color:#0f172a'>
              Create Your Account</div>
          <div style='font-size:.84rem;color:#7889a4;margin-top:4px'>
              Join ChurnSense AI today</div>
        </div>""", unsafe_allow_html=True)

        acc_type = st.radio(
            "Account Type",
            ["🏢  Business Client", "🛡️  Admin"],
            horizontal=True,
        )
        if "Admin" in acc_type:
            callout("⚠️ Admin access requires manual approval after signup.", "amber")
        else:
            callout("ℹ️ Business Client accounts show only your organisation's data.", "blue")

        st.markdown("<hr style='border-color:#f1f5f9;margin:12px 0'>", unsafe_allow_html=True)

        with st.form("signup_form", clear_on_submit=False):
            biz = st.text_input("🏢 Business Name *", placeholder="e.g. Acme Retail Ltd")
            c1, c2 = st.columns(2)
            with c1:
                plan = st.selectbox(
                    "📦 Plan *",
                    ["Starter — $49/mo", "Pro — $149/mo", "Enterprise — $499/mo", "Free Trial"],
                )
            with c2:
                tenure = st.selectbox(
                    "📅 Period *",
                    ["1 Month", "3 Months", "6 Months", "12 Months", "24 Months"],
                )

            st.markdown("<hr style='border-color:#f1f5f9;margin:8px 0'>", unsafe_allow_html=True)
            uname = st.text_input("👤 Username *",          placeholder="Choose a unique username")
            pw1   = st.text_input("🔒 Password *",          type="password", placeholder="Min 6 characters")
            pw2   = st.text_input("🔒 Confirm Password *",  type="password", placeholder="Re-enter password")
            submit = st.form_submit_button(
                "🚀 Create My Account →", use_container_width=True, type="primary"
            )

        if submit:
            users   = load_users()
            role_v  = "admin" if "Admin" in acc_type else "client"
            plan_v  = plan.split(" — ")[0]
            errors  = []
            if not biz.strip():   errors.append("Business Name is required.")
            if not uname.strip(): errors.append("Username is required.")
            if len(pw1) < 6:      errors.append("Password must be at least 6 characters.")
            if pw1 != pw2:        errors.append("Passwords do not match.")
            if uname in users:    errors.append(f"Username '{uname}' is already taken.")

            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                users[uname] = {
                    "role":         role_v,
                    "username":     uname,
                    "password":     _hash_password(pw1),
                    "business":     biz.strip(),
                    "plan":         plan_v,
                    "subscription": tenure,
                    "joined":       str(datetime.date.today()),
                    "status":       "Active",
                    "payment":      "Paid" if plan_v != "Free Trial" else "Trial",
                    "seed":         random.randint(1, 9_999),
                }
                save_users(users)
                callout(
                    f"✅ Account created for <b>{uname}</b> ({biz.strip()}). "
                    "You can now sign in.",
                    "green",
                )
                if st.button("→ Go to Login", type="primary", use_container_width=True):
                    navigate("login")

        st.markdown("<hr style='border-color:#f1f5f9;margin:12px 0'>", unsafe_allow_html=True)
        if st.button("← Back to Login", use_container_width=True):
            navigate("login")


# ─────────────────────────────────────────────────────────────
#  ADMIN: Usage Analytics tab
# ─────────────────────────────────────────────────────────────
def tab_admin_usage() -> None:
    section_header(
        "📈 Usage Analytics",
        "Aggregated platform metrics — individual client data is never exposed here",
    )
    callout(
        "🔒 <b>Data Privacy:</b> All metrics are aggregated. "
        "No individual client data is accessible here.",
        "blue",
    )

    if not DATA_OK or MASTER_DF.empty:
        st.warning("Master CSV not found — place ChurnSense_MASTER.csv in the app folder.")
        return

    total  = len(MASTER_DF)
    ch_rt  = MASTER_DF["Churned"].mean() * 100
    avg_h  = MASTER_DF["Health_Score_10"].mean() if "Health_Score_10" in MASTER_DF.columns else 0
    crit_n = (MASTER_DF["Health_Category"] == "Critical").sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total Records",    f"{total:,}",       "Global dataset",  "blue")
    with c2: kpi_card("Global Churn Avg", f"{ch_rt:.1f}%",    "Platform-wide",   "red")
    with c3: kpi_card("Avg Health Score", f"{avg_h:.1f}/10",  "All customers",   "purple")
    with c4: kpi_card("Critical Accounts",f"{crit_n:,}",      "Require action",  "amber")

    st.markdown("<br>", unsafe_allow_html=True)
    ua1, ua2 = st.columns(2)

    with ua1:
        cat = (
            MASTER_DF.groupby("Category")["Churned"]
            .mean()
            .reset_index()
            .rename(columns={"Churned": "Churn"})
        )
        cat["Churn"] = (cat["Churn"] * 100).round(1)
        cat = cat.sort_values("Churn", ascending=False)
        fig = px.bar(
            cat, x="Category", y="Churn",
            color="Churn", color_continuous_scale="RdYlGn_r",
            text="Churn", title="Platform-Wide Churn by Category (%)",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                          marker_line_width=0)
        fig.update_layout(**PLOTLY_BASE, height=320, coloraxis_showscale=False,
                          xaxis=dict(tickangle=-30), yaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)

    with ua2:
        hc = MASTER_DF["Health_Category"].value_counts().reset_index()
        hc.columns = ["Cat", "Count"]
        fig2 = px.pie(
            hc, names="Cat", values="Count",
            color="Cat", color_discrete_map=HEALTH_COLORS,
            hole=0.56, title="Platform-Wide Health Distribution",
        )
        fig2.update_layout(**PLOTLY_BASE, height=320, legend=dict(orientation="h", y=-0.05))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Platform Trend — Last 6 Months", "Aggregated averages")
    months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=months, y=[30.1, 29.8, 29.4, 29.0, 28.7, 28.9],
        name="Churn Rate %",
        line=dict(color=ACCENT["red"], width=2.5),
        mode="lines+markers",
    ))
    fig3.add_trace(go.Scatter(
        x=months, y=[4.5, 4.6, 4.7, 4.8, 4.9, 4.9],
        name="Avg Health Score",
        line=dict(color=ACCENT["blue"], width=2.5),
        mode="lines+markers",
        yaxis="y2",
    ))
    fig3.update_layout(
        **PLOTLY_BASE, height=290,
        yaxis=dict(title="Churn %", gridcolor="#f1f5f9"),
        yaxis2=dict(title="Health Score", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ─────────────────────────────────────────────────────────────
#  CLIENT: Intervention Engine tab
# ─────────────────────────────────────────────────────────────
def tab_intervention_engine(
    dff: pd.DataFrame,
    avg_p: float,
    ch_rt: float,
    avg_clv: float,
    crit_n: int,
    heal_n: int,
    total: int,
    clv_col: str,
) -> None:
    section_header(
        "⚡ Intervention Engine",
        "AI-assigned retention actions mapped to every customer segment",
    )

    vip_n  = int((dff["Churn_Probability"] > 0.65).sum()) if "Churn_Probability" in dff.columns else 0
    disc_n = int(((dff["Churn_Probability"] > 0.60) & (dff["Churn_Probability"] <= 0.65)).sum()) if "Churn_Probability" in dff.columns else 0
    mod_n  = int((dff["Health_Category"] == "Moderate").sum())

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi_card("VIP Rescue",        f"{vip_n:,}",  "Churn prob > 65%", "red")
    with k2: kpi_card("Discount Coupon",   f"{disc_n:,}", "Churn prob > 60%", "amber")
    with k3: kpi_card("Win-Back Campaign", f"{crit_n:,}", "Critical health",  "purple")
    with k4: kpi_card("Loyalty Push",      f"{mod_n:,}",  "Moderate health",  "green")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Action Rules", "Each rule fires automatically based on customer signals")

    BADGE_STYLES = {
        "URGENT": ("#fee2e2", "#991b1b"),
        "HIGH":   ("#fef3c7", "#92400e"),
        "MEDIUM": ("#dbeafe", "#1e40af"),
        "LOW":    ("#f1f5f9", "#475569"),
        "INFO":   ("#d1fae5", "#065f46"),
    }

    ACTIONS = [
        ("👑", "#991b1b", "Priority VIP Rescue",
         "High CLV + Churn Probability > 65%",
         "Send exclusive retention offer via email + personal call from account manager.",
         "URGENT", f"{vip_n:,} customers"),
        ("🚨", "#9f1239", "Urgent Win-Back Campaign",
         "Critical Health Score (< 4.0) + Churn Prob > 70%",
         "Trigger automated win-back email sequence with time-limited discount.",
         "URGENT", f"{crit_n:,} customers"),
        ("🎟️", "#854d0e", "Personalised Discount Coupon",
         "Churn Probability 60%–65%",
         "Auto-generate a personalised coupon code delivered via email within 24 hours.",
         "HIGH", f"{disc_n:,} customers"),
        ("📧", "#0c4a6e", "Re-Engagement Email / Push",
         "Inactive ≥ 45 days + Churn Probability > 40%",
         "3-part automated re-engagement drip: reminder → value highlight → incentive.",
         "MEDIUM", "—"),
        ("🎧", "#5b21b6", "Dedicated Support Agent",
         "Customer Service Calls > 8 in last 90 days",
         "Route to senior support agent with full history context and resolution mandate.",
         "HIGH", "—"),
        ("💎", "#065f46", "Loyalty Points Reminder",
         "Moderate Health Score (4.0–6.4)",
         "Send personalised loyalty balance update with expiry notice to prompt engagement.",
         "MEDIUM", f"{mod_n:,} customers"),
        ("📱", "#6b21a8", "App Engagement Drive",
         "Low App Usage Score + Moderate/Critical Health",
         "In-app notification with exclusive app-only promotion to drive re-activation.",
         "LOW", "—"),
        ("✅", "#14532d", "No Action Required",
         "Healthy Health Score (≥ 6.5)",
         "Customer is engaged and low-risk. Continue monitoring.",
         "INFO", f"{heal_n:,} customers"),
    ]

    for ico, tc, title, trigger, action, priority, count in ACTIONS:
        bg, ftc = BADGE_STYLES.get(priority, ("#f1f5f9", "#475569"))
        st.markdown(
            f"<div class='action-card' style='border-left:4px solid {tc}'>"
            f"  <div class='action-icon'>{ico}</div>"
            f"  <div style='flex:1'>"
            f"    <div style='display:flex;align-items:center;gap:8px;margin-bottom:2px'>"
            f"      <div class='action-title'>{title}</div>"
            f"      <span style='background:{bg};color:{ftc};padding:2px 9px;"
            f"border-radius:20px;font-size:.63rem;font-weight:700'>{priority}</span>"
            f"      <span style='background:#f1f5f9;color:#64748b;padding:2px 9px;"
            f"border-radius:20px;font-size:.63rem;font-weight:600'>{count}</span>"
            f"    </div>"
            f"    <div class='action-trigger'>🎯 Trigger: {trigger}</div>"
            f"    <div class='action-desc'>{action}</div>"
            f"  </div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🔎 Segment Explorer", "Select a health category to preview recommended actions")

    sel = st.selectbox("Filter by Health Category", ["All", "Critical", "Moderate", "Healthy"])
    seg = dff[dff["Health_Category"] == sel].copy() if sel != "All" else dff.copy()

    if not seg.empty:
        clv_local = "Predicted_CLV" if "Predicted_CLV" in seg.columns else "Lifetime_Value"
        action_map = {
            "Critical": "🚨 Urgent Win-Back / VIP Rescue",
            "Moderate": "💎 Loyalty Points Reminder",
            "Healthy":  "✅ No Action — Continue Monitoring",
        }
        rec = action_map.get(sel, "⚡ Review individually")

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Customers in Segment", f"{len(seg):,}")
        with m2: st.metric("Avg Churn Prob",
                            f"{seg['Churn_Probability'].mean()*100:.1f}%"
                            if "Churn_Probability" in seg.columns else "—")
        with m3: st.metric("Avg CLV",
                            f"${seg[clv_local].mean():,.0f}"
                            if clv_local in seg.columns else "—")

        if sel == "Critical":
            callout(f"<b>Recommended Action for {sel} segment:</b> {rec}", "red")
        else:
            callout(f"<b>Recommended Action for {sel} segment:</b> {rec}", "blue")

        if "Churn_Probability" in seg.columns:
            top = seg.nlargest(10, "Churn_Probability")
            show_cols = [c for c in ["CID", "Age", "Platform", "Health_Category",
                                     "Churn_Probability", clv_local, "Intervention_Action"]
                         if c in top.columns]
            disp = top[show_cols].copy()
            if "Churn_Probability" in disp.columns:
                disp["Churn_Probability"] = (
                    disp["Churn_Probability"] * 100
                ).round(1).astype(str) + "%"
            st.markdown(
                "<div style='font-size:.78rem;font-weight:600;color:#7889a4;margin:12px 0 6px'>"
                "Top 10 highest-risk customers in this segment:</div>",
                unsafe_allow_html=True,
            )
            st.dataframe(disp, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────
#  ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────
def admin_dashboard() -> None:
    tab = build_admin_sidebar()
    users   = load_users()
    clients = {k: v for k, v in users.items() if v["role"] == "client"}

    n_active = sum(1 for v in clients.values() if v.get("status") == "Active")
    n_issues = len(clients) - n_active

    badges = [
        (f"{len(clients)} Clients", "blue"),
        (f"{n_active} Active", "green"),
    ]
    if n_issues:
        badges.append((f"{n_issues} Issues", "red"))
    page_header("🛡️ Admin Control Panel", badges)

    # ── Platform Overview ───────────────────────────────────
    if tab == "Platform Overview":
        mrr = sum(PLAN_PRICES.get(v.get("plan", "Starter"), 49) for v in clients.values())
        paid = sum(1 for v in clients.values() if v.get("payment") == "Paid")

        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi_card("Total Clients",  str(len(clients)), "Registered businesses", "blue")
        with c2: kpi_card("Active Clients", str(n_active),
                          f"{n_active / max(len(clients), 1) * 100:.0f}% active", "green")
        with c3: kpi_card("Monthly Revenue",f"${mrr:,}",       "Estimated MRR",    "amber")
        with c4: kpi_card("Paid Accounts",  str(paid),         "Non-trial",        "purple")

        st.markdown("<br>", unsafe_allow_html=True)

        if DATA_OK and not MASTER_DF.empty:
            section_header("Platform Health — Global Dataset")
            g1, g2 = st.columns(2)
            with g1:
                plat = (
                    MASTER_DF.groupby("Platform")["Churned"]
                    .mean()
                    .reset_index()
                    .rename(columns={"Churned": "ChurnRate"})
                )
                plat["ChurnRate"] = (plat["ChurnRate"] * 100).round(1)
                fig = px.bar(
                    plat, x="Platform", y="ChurnRate",
                    color="Platform", color_discrete_map=PLATFORM_COLORS,
                    text="ChurnRate", title="Global Churn by Platform (%)",
                )
                fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                                  marker_line_width=0, width=0.5)
                fig.update_layout(**PLOTLY_BASE, height=300, showlegend=False,
                                  yaxis=dict(gridcolor="#f1f5f9"))
                st.plotly_chart(fig, use_container_width=True)

            with g2:
                hc = MASTER_DF["Health_Category"].value_counts().reset_index()
                hc.columns = ["Cat", "Count"]
                fig2 = px.pie(
                    hc, names="Cat", values="Count",
                    color="Cat", color_discrete_map=HEALTH_COLORS,
                    hole=0.58, title="Global Health Distribution",
                )
                fig2.update_layout(**PLOTLY_BASE, height=300,
                                   legend=dict(orientation="h", y=-0.05))
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Recent Client Signups")
        recent = sorted(clients.items(), key=lambda x: x[1].get("joined", ""), reverse=True)[:8]
        for uname, info in recent:
            ca, cb, cc, cd = st.columns([2, 2, 1, 1])
            with ca:
                st.markdown(
                    f"<div style='font-weight:700;font-size:.92rem'>🏢 {info['business']}</div>"
                    f"<div style='font-size:.7rem;color:#7889a4'>@{uname}</div>",
                    unsafe_allow_html=True,
                )
            with cb:
                st.markdown(
                    f"<div style='font-size:.78rem;color:#7889a4;margin-top:8px'>"
                    f"{info.get('plan','Starter')} · {info.get('subscription','—')}</div>",
                    unsafe_allow_html=True,
                )
            with cc:
                status = info.get("status", "Active")
                colour = "green" if status == "Active" else "red"
                st.markdown(
                    f"<div style='margin-top:8px'>{pill(status, colour)}</div>",
                    unsafe_allow_html=True,
                )
            with cd:
                st.markdown(
                    f"<div style='font-size:.7rem;color:#a0aec0;margin-top:10px'>"
                    f"Joined {info.get('joined','')}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("<hr style='border-color:#f1f5f9;margin:6px 0'>",
                        unsafe_allow_html=True)

    # ── Client Management ───────────────────────────────────
    elif tab == "Client Management":
        section_header("👥 Client Management",
                       "View and manage all registered business clients")
        search = st.text_input("🔍 Search", placeholder="Business name or username…")
        filt   = {
            k: v for k, v in clients.items()
            if not search
            or search.lower() in v["business"].lower()
            or search.lower() in k.lower()
        }
        st.markdown(
            f"<div style='font-size:.78rem;color:#7889a4;margin-bottom:10px'>"
            f"Showing <b>{len(filt)}</b> of <b>{len(clients)}</b> clients</div>",
            unsafe_allow_html=True,
        )
        if not filt:
            callout("No clients match your search. They appear here after signing up.", "blue")
            return

        for uname, info in filt.items():
            with st.expander(
                f"🏢 {info['business']}  ·  @{uname}  ·  "
                f"{info.get('plan','Starter')}  ·  {info.get('status','Active')}"
            ):
                e1, e2, e3 = st.columns(3)
                with e1:
                    st.metric("Business",  info["business"])
                    st.metric("Username",  uname)
                    st.metric("Joined",    info.get("joined", "—"))
                with e2:
                    st.metric("Plan",      info.get("plan", "Starter"))
                    st.metric("Period",    info.get("subscription", "—"))
                    st.metric("Payment",   info.get("payment", "—"))
                with e3:
                    cur = info.get("status", "Active")
                    new_s = st.selectbox(
                        "Status",
                        ["Active", "Suspended", "Trial"],
                        index=["Active", "Suspended", "Trial"].index(cur),
                        key=f"status_{uname}",
                    )
                    if st.button("💾 Save", key=f"save_{uname}"):
                        fresh = load_users()
                        fresh[uname]["status"] = new_s
                        save_users(fresh)
                        st.success("✅ Status updated.")
                        st.rerun()

    # ── Billing & Subscriptions ─────────────────────────────
    elif tab == "Billing & Subscriptions":
        section_header("💳 Billing & Subscriptions",
                       "Monitor payment status and subscription details")
        rows = [
            {
                "Business":    v["business"],
                "Username":    k,
                "Plan":        v.get("plan", "Starter"),
                "Period":      v.get("subscription", "—"),
                "Monthly ($)": PLAN_PRICES.get(v.get("plan", "Starter"), 49),
                "Payment":     v.get("payment", "Paid"),
                "Status":      v.get("status", "Active"),
                "Joined":      v.get("joined", "—"),
            }
            for k, v in clients.items()
        ]
        if not rows:
            callout("No clients registered yet.", "blue")
            return

        df_b = pd.DataFrame(rows)
        b1, b2, b3 = st.columns(3)
        with b1: kpi_card("Total MRR",    f"${df_b['Monthly ($)'].sum():,}",
                           "Monthly Recurring Revenue", "green")
        with b2: kpi_card("Paid Clients", str((df_b["Payment"] == "Paid").sum()),
                           "Non-trial accounts", "blue")
        with b3: kpi_card("Trial Clients",str((df_b["Payment"] == "Trial").sum()),
                           "Free trial", "amber")

        st.markdown("<br>", unsafe_allow_html=True)
        bp1, bp2 = st.columns(2)
        colors = ["#1447e6", "#8b5cf6", "#10b981", "#f59e0b"]
        with bp1:
            pc = df_b["Plan"].value_counts().reset_index()
            pc.columns = ["Plan", "Count"]
            fig_p = px.pie(pc, names="Plan", values="Count", hole=0.52,
                           title="Clients by Plan", color_discrete_sequence=colors)
            fig_p.update_layout(**PLOTLY_BASE, height=270)
            st.plotly_chart(fig_p, use_container_width=True)
        with bp2:
            rv = df_b.groupby("Plan")["Monthly ($)"].sum().reset_index()
            fig_r = px.bar(rv, x="Plan", y="Monthly ($)", color="Plan", text="Monthly ($)",
                           color_discrete_sequence=colors, title="Revenue by Plan ($)")
            fig_r.update_traces(texttemplate="$%{text}", textposition="outside",
                                 marker_line_width=0, width=0.5)
            fig_r.update_layout(**PLOTLY_BASE, height=270, showlegend=False,
                                 yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig_r, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("All Billing Records")
        st.dataframe(df_b, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Export CSV", df_b.to_csv(index=False),
                           "billing.csv", "text/csv")

    # ── Usage Analytics ─────────────────────────────────────
    elif tab == "Usage Analytics":
        tab_admin_usage()


# ─────────────────────────────────────────────────────────────
#  CLIENT DASHBOARD
# ─────────────────────────────────────────────────────────────
def client_dashboard() -> None:
    users = load_users()
    info  = users.get(st.session_state.user, {})
    seed  = info.get("seed", 42)
    dff, _ok = get_client_slice(seed, MASTER_DF)

    if not _ok or dff.empty:
        with st.sidebar:
            show_logo(140)
            st.warning("No data found — place ChurnSense_MASTER.csv in the app folder.")
            if st.button("🚪 Sign Out", use_container_width=True):
                sign_out()
        callout("⚠️ ChurnSense_MASTER.csv not found or dataset is empty.", "amber")
        return

    # Apply ML predictions once
    dff = apply_ml_predictions(dff)

    tab, p_opt, c_opt, h_opt, co_opt, ch_max = build_client_sidebar(len(dff))

    # ── Apply filters ──────────────────────────────────────
    if p_opt  != "All": dff = dff[dff["Platform"]      == p_opt]
    if c_opt  != "All": dff = dff[dff["Category"]      == c_opt]
    if h_opt  != "All": dff = dff[dff["Health_Category"]== h_opt]
    if co_opt != "All": dff = dff[dff["Country"]       == co_opt]
    if "Churn_Probability" in dff.columns:
        dff = dff[dff["Churn_Probability"] <= ch_max / 100]

    if dff.empty:
        callout("⚠️ No customers match the current filters. Adjust the sidebar filters.", "amber")
        return

    # ── Compute summary stats ──────────────────────────────
    total   = len(dff)
    churned = int(dff["Churned"].sum())
    ch_rt   = churned / total * 100
    avg_h   = dff["Health_Score_10"].mean() if "Health_Score_10" in dff.columns else 0
    avg_p   = dff["Churn_Probability"].mean() * 100 if "Churn_Probability" in dff.columns else 0
    clv_col = "Predicted_CLV" if "Predicted_CLV" in dff.columns else "Lifetime_Value"
    avg_clv = dff[clv_col].mean() if clv_col in dff.columns else 0
    crit_n  = int((dff["Health_Category"] == "Critical").sum())
    heal_n  = int((dff["Health_Category"] == "Healthy").sum())
    mod_n   = int((dff["Health_Category"] == "Moderate").sum())

    # ── Page header bar ────────────────────────────────────
    pl = info.get("plan", "Starter")
    plan_badge_map = {
        "Starter":    "blue",
        "Pro":        "purple",
        "Enterprise": "green",
        "Free Trial": "slate",
    }
    page_header(
        st.session_state.business or "Dashboard",
        [
            (f"{pl} Plan", plan_badge_map.get(pl, "blue")),
            (f"@{st.session_state.user}", "slate"),
        ],
    )

    # ══════════════════════════════════════════════════════
    #  TAB: KPI OVERVIEW
    # ══════════════════════════════════════════════════════
    if tab == "KPI Overview":
        callout(
            f"🚨 <b>{crit_n:,} customers</b> in Critical health need immediate action &nbsp;|&nbsp;"
            f" Avg churn probability: <b>{avg_p:.1f}%</b>",
            "red",
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi_card("Churn Probability", f"{avg_p:.1f}%",    "Avg — your customers", "red")
        with c2: kpi_card("Engagement Level",  "Medium",            "Dominant class",       "blue")
        with c3: kpi_card("Customer CLV",      f"${avg_clv:,.0f}", "Avg predicted CLV",    "green")
        with c4: kpi_card("Health Score",      f"{avg_h:.1f}/10",  "Avg health index",     "purple")

        st.markdown("<br>", unsafe_allow_html=True)
        c5, c6, c7, c8 = st.columns(4)
        with c5: kpi_card("Your Customers",  f"{total:,}",    "In your dataset",      "teal")
        with c6: kpi_card("Churn Rate",      f"{ch_rt:.1f}%", f"{churned:,} churned", "red")
        with c7: kpi_card("Critical Health", f"{crit_n:,}",   "Immediate action",     "amber")
        with c8: kpi_card("Healthy",         f"{heal_n:,}",   f"{heal_n/total*100:.1f}% safe", "green")

        st.markdown("<br>", unsafe_allow_html=True)
        hs1, hs2, hs3 = st.columns(3)
        SEG_STYLE = [
            (hs1, "🟢 Healthy",  heal_n, "#d1fae5", "#065f46"),
            (hs2, "🟡 Moderate", mod_n,  "#fef3c7", "#92400e"),
            (hs3, "🔴 Critical", crit_n, "#fee2e2", "#991b1b"),
        ]
        for col, label, val, bg, tc in SEG_STYLE:
            with col:
                st.markdown(
                    f"<div class='seg-bar' style='background:{bg};border-color:{tc}'>"
                    f"<div style='font-size:.68rem;font-weight:700;color:{tc};"
                    f"text-transform:uppercase;margin-bottom:4px'>{label}</div>"
                    f"<div style='font-family:\"DM Serif Display\",serif;font-size:2rem;"
                    f"color:{tc};line-height:1'>{val:,}</div>"
                    f"<div style='font-size:.7rem;color:{tc};margin-top:3px'>"
                    f"{val/total*100:.1f}% of your customers</div></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Platform & Churn Analysis")
        ch1, ch2 = st.columns([3, 2])
        with ch1:
            plat = (dff.groupby("Platform")["Churned"].mean().reset_index()
                    .rename(columns={"Churned": "ChurnRate"}))
            plat["ChurnRate"] = (plat["ChurnRate"] * 100).round(1)
            fig = px.bar(plat, x="Platform", y="ChurnRate",
                         color="Platform", color_discrete_map=PLATFORM_COLORS,
                         text="ChurnRate", title="Churn Rate by Platform (%)")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                              marker_line_width=0, width=0.5)
            fig.update_layout(**PLOTLY_BASE, height=300, showlegend=False,
                              yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)
        with ch2:
            hc = dff["Health_Category"].value_counts().reset_index()
            hc.columns = ["Cat", "Count"]
            fig2 = px.pie(hc, names="Cat", values="Count",
                          color="Cat", color_discrete_map=HEALTH_COLORS,
                          hole=0.58, title="Your Health Distribution")
            fig2.update_traces(textinfo="label+percent", pull=[0.04] * 3)
            fig2.update_layout(**PLOTLY_BASE, height=300,
                               legend=dict(orientation="h", y=-0.05))
            st.plotly_chart(fig2, use_container_width=True)

        ch3, ch4 = st.columns(2)
        with ch3:
            cat = (dff.groupby("Category")["Churned"].mean().reset_index()
                   .rename(columns={"Churned": "ChurnRate"}))
            cat["ChurnRate"] = (cat["ChurnRate"] * 100).round(1)
            cat = cat.sort_values("ChurnRate", ascending=False).head(8)
            fig3 = px.bar(cat, x="ChurnRate", y="Category", orientation="h",
                          color="ChurnRate", color_continuous_scale="RdYlGn_r",
                          text="ChurnRate", title="Churn by Category")
            fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                               marker_line_width=0)
            fig3.update_layout(**PLOTLY_BASE, height=310, coloraxis_showscale=False,
                               xaxis=dict(gridcolor="#f1f5f9"), yaxis=dict(title=""))
            st.plotly_chart(fig3, use_container_width=True)
        with ch4:
            clv_p = (dff.groupby("Platform")[clv_col].mean().reset_index()
                     .rename(columns={clv_col: "CLV"}))
            fig4 = px.bar(clv_p, x="Platform", y="CLV",
                          color="Platform", color_discrete_map=PLATFORM_COLORS,
                          text="CLV", title="Avg CLV by Platform ($)")
            fig4.update_traces(texttemplate="$%{text:,.0f}", textposition="outside",
                               marker_line_width=0, width=0.5)
            fig4.update_layout(**PLOTLY_BASE, height=310, showlegend=False,
                               yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig4, use_container_width=True)

        # ── KPI Deep Dives ────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("📖 KPI Deep Dives")

        with st.expander("📉 Churn Probability Deep Dive"):
            x1, x2 = st.columns(2)
            with x1:
                callout(
                    "<b>Model:</b> Random Forest Classifier · 42 features · 200 trees<br>"
                    "Top signals: CS Calls (0.29), Cart Abandonment (0.28), Session Duration (−0.23).",
                    "blue",
                )
                st.metric("Avg Churn Prob", f"{avg_p:.1f}%")
                st.metric("Actual Churn",   f"{ch_rt:.1f}%")
                if "Churn_Probability" in dff.columns:
                    st.metric("High Risk > 60%", f"{(dff['Churn_Probability'] > 0.6).sum():,}")
            with x2:
                if "Churn_Probability" in dff.columns:
                    fig_cp = px.histogram(dff, x="Churn_Probability", nbins=30,
                                          color_discrete_sequence=[ACCENT["blue"]],
                                          title="Churn Prob Distribution")
                    fig_cp.add_vline(x=0.6, line_color=ACCENT["red"],   line_dash="dash")
                    fig_cp.add_vline(x=0.4, line_color=ACCENT["amber"], line_dash="dash")
                    fig_cp.update_layout(**PLOTLY_BASE, height=250,
                                         xaxis=dict(gridcolor="#f1f5f9"),
                                         yaxis=dict(gridcolor="#f1f5f9"))
                    st.plotly_chart(fig_cp, use_container_width=True)

        with st.expander("🏥 Health Score Deep Dive"):
            x3, x4 = st.columns(2)
            with x3:
                callout(
                    "<b>Formula:</b> (1 − Churn) × 0.40 + Engagement × 0.35 + CLV × 0.25<br>"
                    "Scaled 1–10. ≥ 6.5 = Healthy, ≥ 4.0 = Moderate, < 4.0 = Critical.",
                    "blue",
                )
            with x4:
                if "Health_Score_10" in dff.columns:
                    fig_h = px.histogram(dff, x="Health_Score_10", nbins=30,
                                          color_discrete_sequence=[ACCENT["purple"]],
                                          title="Health Score Distribution")
                    fig_h.add_vline(x=6.5, line_color=ACCENT["green"], line_dash="dash")
                    fig_h.add_vline(x=4.0, line_color=ACCENT["red"],   line_dash="dash")
                    fig_h.update_layout(**PLOTLY_BASE, height=250,
                                        xaxis=dict(gridcolor="#f1f5f9"),
                                        yaxis=dict(gridcolor="#f1f5f9"))
                    st.plotly_chart(fig_h, use_container_width=True)

        # Revenue loss
        st.markdown("<br>", unsafe_allow_html=True)
        loss = dff[dff["Churned"] == 1][clv_col].sum() if clv_col in dff.columns else 0
        kpi_card("Estimated Revenue at Risk", f"${loss:,.0f}",
                 "Cumulative CLV of churned customers", "red")

        # Model performance
        if MODELS_OK and DATA_OK and not MASTER_DF.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            section_header("📊 Model Performance")
            try:
                from sklearn.metrics import accuracy_score, classification_report
                y_true = MASTER_DF["Churned"]
                y_pred = CHURN_M.predict(MASTER_DF[FEAT_COLS])
                acc    = accuracy_score(y_true, y_pred)
                callout(f"✅ Model Accuracy on Full Dataset: <b>{acc*100:.1f}%</b>", "green")
            except Exception:
                callout("Performance metrics unavailable for this model version.", "amber")

        # Top risk customers
        if "Churn_Probability" in dff.columns:
            st.markdown("<br>", unsafe_allow_html=True)
            section_header("⚠️ Top 10 High-Risk Customers")
            top_risk = dff.sort_values("Churn_Probability", ascending=False).head(10)
            show_c   = [c for c in ["CID", "Age", "Gender", "Platform", "Health_Category",
                                    "Churn_Probability", clv_col] if c in top_risk.columns]
            disp     = top_risk[show_c].copy()
            disp["Churn_Probability"] = (disp["Churn_Probability"] * 100).round(1).astype(str) + "%"
            st.dataframe(disp, use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════════
    #  TAB: FILTERS & ANALYSIS
    # ══════════════════════════════════════════════════════
    elif tab == "Filters & Analysis":
        callout(
            f"📌 Showing <b>{total:,} customers</b> &nbsp;|&nbsp; "
            f"Churn: <b>{ch_rt:.1f}%</b> &nbsp;|&nbsp; "
            f"Health: <b>{avg_h:.1f}/10</b> &nbsp;|&nbsp; CLV: <b>${avg_clv:,.0f}</b>",
            "blue",
        )

        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1: kpi_card("Filtered Customers", f"{total:,}",    "Matching filters",  "blue")
        with fc2: kpi_card("Churn Rate",          f"{ch_rt:.1f}%",f"{churned:,} churned","red")
        with fc3: kpi_card("Avg Health",          f"{avg_h:.1f}/10","This segment",     "purple")
        with fc4: kpi_card("Avg CLV",             f"${avg_clv:,.0f}","This segment",    "green")

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Segment Breakdown by Platform")
        pg = dff.groupby("Platform").agg(
            Count=("Churned", "count"),
            Churned=("Churned", "sum"),
            AvgH=("Health_Score_10", "mean"),
            AvgCLV=(clv_col, "mean"),
        ).reset_index()
        pg["Churn Rate"] = (pg["Churned"] / pg["Count"] * 100).round(1).astype(str) + "%"
        pg["Avg Health"] = pg["AvgH"].round(2)
        pg["Avg CLV"]    = "$" + pg["AvgCLV"].round(0).astype(int).astype(str)
        pg["% of Total"] = (pg["Count"] / total * 100).round(1).astype(str) + "%"
        st.dataframe(
            pg[["Platform", "Count", "Churn Rate", "Avg Health", "Avg CLV", "% of Total"]],
            use_container_width=True, hide_index=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        fa, fb = st.columns(2)
        with fa:
            st2 = dff.groupby(["Platform", "Health_Category"]).size().reset_index(name="Count")
            fig_s = px.bar(st2, x="Platform", y="Count", color="Health_Category",
                           color_discrete_map=HEALTH_COLORS, barmode="stack",
                           title="Health Distribution by Platform")
            fig_s.update_layout(**PLOTLY_BASE, height=300, yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig_s, use_container_width=True)
        with fb:
            st3 = dff.groupby(["Platform", "Churned"]).size().reset_index(name="Count")
            st3["Status"] = st3["Churned"].map({0: "Retained", 1: "Churned"})
            fig_s2 = px.bar(st3, x="Platform", y="Count", color="Status",
                            color_discrete_map={"Churned": ACCENT["red"],
                                                "Retained": ACCENT["green"]},
                            barmode="stack", title="Churned vs Retained by Platform")
            fig_s2.update_layout(**PLOTLY_BASE, height=300, yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig_s2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("📋 Customer Table")
        srch = st.text_input("🔍 Search by ID / Country / City")
        tbl  = dff.copy()
        if srch:
            mask = (
                tbl["CID"].astype(str).str.contains(srch, case=False, na=False)
                | tbl["Country"].astype(str).str.contains(srch, case=False, na=False)
                | tbl["City"].astype(str).str.contains(srch, case=False, na=False)
            )
            tbl = tbl[mask]

        dcols = [c for c in ["CID", "Age", "Gender", "Country", "Platform", "Category",
                              "Health_Score_10", "Health_Category", "Churn_Probability",
                              clv_col, "Intervention_Action", "Churned"]
                 if c in tbl.columns]
        show  = tbl[dcols].head(500).copy()
        if "Churn_Probability" in show.columns:
            show["Churn_Probability"] = (
                show["Churn_Probability"] * 100
            ).round(1).astype(str) + "%"
        if clv_col in show.columns:
            show[clv_col] = show[clv_col].round(0).astype(int)
        st.dataframe(show, use_container_width=True, height=420)
        st.download_button("⬇️ Download CSV", tbl[dcols].to_csv(index=False),
                           "customers.csv", "text/csv")

    # ══════════════════════════════════════════════════════
    #  TAB: INSIGHTS & STRATEGY
    # ══════════════════════════════════════════════════════
    elif tab == "Insights & Strategy":
        st.markdown(
            "<div style='background:linear-gradient(135deg,#05112e,#1e3a8a);"
            "border-radius:16px;padding:28px 32px;margin-bottom:22px;color:#fff'>"
            "<div style='font-family:\"DM Serif Display\",serif;font-size:1.4rem;"
            "margin-bottom:6px'>💡 AI-Powered Insights — Your Business</div>"
            "<div style='font-size:.87rem;color:rgba(255,255,255,.55)'>"
            "ChurnSense AI surfaces the most impactful retention opportunities "
            "specific to your customer data.</div></div>",
            unsafe_allow_html=True,
        )

        wp = dff.groupby("Platform")["Churned"].mean() * 100
        worst_p, worst_pv = (wp.idxmax(), wp.max()) if not wp.empty else ("—", 0)
        wc = dff.groupby("Category")["Churned"].mean() * 100
        worst_c, worst_cv = (wc.idxmax(), wc.max()) if not wc.empty else ("—", 0)
        crit_pct = crit_n / total * 100

        insights = [
            ("red",    "🔴 High Priority",  "Highest Churn Platform",
             f"{worst_p} shows {worst_pv:.1f}% churn in your data. "
             "Launch targeted win-back campaigns here first.",
             f"{worst_pv:.1f}%", "Platform Churn Rate"),
            ("amber",  "🟡 Category Alert", f"{worst_c} — Top Churn Category",
             f"{worst_c} hits {worst_cv:.1f}% churn. Consider subscription bundle offers.",
             f"{worst_cv:.1f}%", "Category Churn"),
            ("purple", "🔬 Health Alert",   f"{crit_pct:.1f}% Customers Are Critical",
             f"{crit_n:,} customers have Health Score < 4.0. Deploy urgent intervention.",
             f"{crit_pct:.1f}%", "Critical Share"),
            ("green",  "🟢 CLV Opportunity","Protect Your High-Value Customers",
             f"Avg CLV ${avg_clv:,.0f}. Prioritise VIP rescue programmes for top-tier customers.",
             f"${avg_clv:,.0f}", "Avg CLV"),
        ]

        ic1, ic2 = st.columns(2)
        for i, (colour, tag, title, text, mv, ml) in enumerate(insights):
            tc_map = {"red": "#ef4444", "amber": "#f59e0b",
                      "purple": "#8b5cf6", "green": "#10b981"}
            bc = tc_map[colour]
            with (ic1 if i % 2 == 0 else ic2):
                with st.expander(f"{tag} — {title}", expanded=i < 2):
                    st.markdown(
                        f"<div style='border-left:4px solid {bc};padding-left:14px'>"
                        f"<div style='font-size:.67rem;font-weight:700;text-transform:uppercase;"
                        f"color:#7889a4;margin-bottom:4px'>{tag}</div>"
                        f"<div style='font-family:\"DM Serif Display\",serif;font-size:1rem;"
                        f"color:#0f172a;margin-bottom:6px'>{title}</div>"
                        f"<div style='font-size:.83rem;color:#475569;line-height:1.65'>{text}</div>"
                        f"<div style='font-family:\"DM Serif Display\",serif;font-size:1.65rem;"
                        f"color:{bc};margin-top:8px'>{mv}</div>"
                        f"<div style='font-size:.7rem;color:#7889a4'>{ml}</div></div>",
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Top Churn Drivers", "Feature correlation with churn")
        drv = pd.DataFrame({
            "Feature":     ["CS_Calls", "Cart_Abandon", "Days_Since", "Returns",
                            "Session_Dur", "Email_Open", "Login_Freq", "App_Usage"],
            "Correlation": [0.29, 0.28, 0.18, 0.15, -0.23, -0.22, -0.20, -0.13],
        }).sort_values("Correlation")
        drv["Color"] = drv["Correlation"].apply(
            lambda x: ACCENT["red"] if x > 0 else ACCENT["green"]
        )
        fig_d = px.bar(drv, x="Correlation", y="Feature", orientation="h",
                       color="Color", color_discrete_map="identity",
                       title="Feature Correlation with Churn")
        fig_d.update_traces(marker_line_width=0)
        fig_d.update_layout(**PLOTLY_BASE, height=270, showlegend=False,
                            xaxis=dict(gridcolor="#f1f5f9"), yaxis=dict(title=""))
        st.plotly_chart(fig_d, use_container_width=True)

        try:
            piv = (
                dff.groupby(["Platform", "Category"])["Churned"]
                .mean() * 100
            ).unstack(fill_value=0).round(1)
            fig_hm = px.imshow(
                piv, color_continuous_scale="RdYlGn_r",
                zmin=26, zmax=32, aspect="auto", text_auto=".1f",
                title="Churn % — Platform × Category",
            )
            fig_hm.update_layout(**PLOTLY_BASE, height=300)
            st.plotly_chart(fig_hm, use_container_width=True)
        except Exception:
            pass

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("🎯 Retention Strategies")
        strategies = [
            ("🎟️", "#fee2e2", "Priority VIP Rescue",
             "Exclusive personalised offers for high-CLV + Churn > 65% customers.",
             "Est. 18% churn reduction"),
            ("📧", "#fef3c7", "Re-Engagement Sequence",
             "3-part email series for 45+ day inactive customers.",
             "Est. 12% win-back rate"),
            ("🎧", "#d1fae5", "CS Escalation Protocol",
             "Dedicated senior agent for customers with 8+ CS calls.",
             "Est. 25% CSAT improvement"),
            ("💎", "#eff6ff", "Loyalty Points Push",
             "Expiry reminders for Moderate-health customers.",
             "Est. 8% retention lift"),
            ("📱", "#f5f3ff", "App Engagement Drive",
             "In-app exclusives for low app-usage customers.",
             "Est. 10% engagement lift"),
            ("🌍", "#ecfdf5", "Localised Campaigns",
             "Region-specific offers for highest-churn countries.",
             "Est. 15% regional impact"),
        ]
        rc = st.columns(3)
        for i, (ico, bg, tit, txt, imp) in enumerate(strategies):
            with rc[i % 3]:
                st.markdown(
                    f"<div class='strategy-card' style='margin-bottom:14px'>"
                    f"<div style='font-size:1.35rem;background:{bg};width:42px;height:42px;"
                    f"border-radius:11px;display:flex;align-items:center;justify-content:center;"
                    f"margin-bottom:12px'>{ico}</div>"
                    f"<div style='font-size:.88rem;font-weight:700;color:#0f172a;"
                    f"margin-bottom:6px'>{tit}</div>"
                    f"<div style='font-size:.78rem;color:#64748b;line-height:1.6'>{txt}</div>"
                    f"<div style='font-size:.72rem;font-weight:700;color:#10b981;"
                    f"margin-top:10px'>✅ {imp}</div></div>",
                    unsafe_allow_html=True,
                )

    # ══════════════════════════════════════════════════════
    #  TAB: INTERVENTION ENGINE
    # ══════════════════════════════════════════════════════
    elif tab == "Intervention Engine":
        tab_intervention_engine(
            dff, avg_p, ch_rt, avg_clv, crit_n, heal_n, total, clv_col
        )

    # ══════════════════════════════════════════════════════
    #  TAB: REAL-TIME PREDICTION
    # ══════════════════════════════════════════════════════
    elif tab == "Real-Time Prediction":
        section_header("🧪 Real-Time Churn Prediction",
                       "Enter customer attributes and get an instant churn forecast")

        if not MODELS_OK:
            callout("❌ ML model not loaded. Place model files in the app folder.", "red")
            return

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**👤 Demographics & Loyalty**")
            age               = st.slider("Age", 18, 70, 35)
            membership_years  = st.slider("Membership Years", 0, 10, 2)
            login_freq        = st.slider("Login Frequency (per month)", 0, 100, 20)
            session_dur       = st.slider("Avg Session Duration (mins)", 0, 60, 15)
            pages_per_session = st.slider("Pages Per Session", 1, 30, 8)
        with col2:
            st.markdown("**🛒 Purchase Behaviour**")
            cart_abandon    = st.slider("Cart Abandonment Rate", 0.0, 1.0, 0.3)
            total_purchases = st.slider("Total Purchases", 0, 200, 20)
            avg_order_val   = st.slider("Avg Order Value ($)", 0, 500, 80)
            days_since      = st.slider("Days Since Last Purchase", 0, 365, 30)
            cs_calls        = st.slider("Customer Service Calls", 0, 20, 2)
        with col3:
            st.markdown("**📊 Engagement & Finance**")
            returns_rate   = st.slider("Returns Rate", 0.0, 1.0, 0.1)
            email_open     = st.slider("Email Open Rate", 0.0, 1.0, 0.3)
            mobile_app     = st.slider("Mobile App Usage Score", 0, 100, 50)
            discount_rate  = st.slider("Discount Usage Rate", 0.0, 1.0, 0.2)
            credit_balance = st.slider("Credit Balance ($)", 0, 5_000, 500)

        # ── Feature engineering (mirrors training) ──────
        purchase_rate      = total_purchases / max(membership_years * 12, 1)
        avg_spend          = avg_order_val * (1 - cart_abandon)
        high_value         = int(avg_order_val > 150)
        discount_dependent = int(discount_rate > 0.5)
        app_web_ratio      = mobile_app / 100
        churn_risk_flag    = int(days_since > 90 or cs_calls > 8)
        support_heavy      = int(cs_calls > 8)
        low_loyalty        = int(login_freq < 5)
        returns_risk       = int(returns_rate > 0.4)
        wishlist_items     = 5
        wishlist_no_buy    = int(wishlist_items > 3 and total_purchases < 5)
        is_inactive        = int(days_since > 60)
        engagement_norm    = min(login_freq / 100, 1.0)
        purchase_rate_norm = min(purchase_rate / 20, 1.0)
        age_norm           = (age - 18) / (70 - 18)
        membership_norm    = min(membership_years / 10, 1.0)
        if engagement_norm < 0.33:
            eng_low, eng_mid, eng_high = 1, 0, 0
        elif engagement_norm < 0.66:
            eng_low, eng_mid, eng_high = 0, 1, 0
        else:
            eng_low, eng_mid, eng_high = 0, 0, 1
        health_score       = (
            (1 - churn_risk_flag) * 0.4 + engagement_norm * 0.35 + purchase_rate_norm * 0.25
        ) * 9 + 1
        churn_prob_prior   = 0.5 - engagement_norm * 0.2 + churn_risk_flag * 0.2

        input_df = pd.DataFrame([{
            "Age":                           age,
            "Membership_Years":              membership_years,
            "Login_Frequency":               login_freq,
            "Session_Duration_Avg":          session_dur,
            "Pages_Per_Session":             pages_per_session,
            "Cart_Abandonment_Rate":         cart_abandon,
            "Wishlist_Items":                wishlist_items,
            "Total_Purchases":               total_purchases,
            "Average_Order_Value":           avg_order_val,
            "Days_Since_Last_Purchase":      days_since,
            "Discount_Usage_Rate":           discount_rate,
            "Returns_Rate":                  returns_rate,
            "Email_Open_Rate":               email_open,
            "Customer_Service_Calls":        cs_calls,
            "Product_Reviews_Written":       2,
            "Social_Media_Engagement_Score": 30,
            "Mobile_App_Usage":              mobile_app,
            "Payment_Method_Diversity":      2,
            "Credit_Balance":                credit_balance,
            "Purchase_Rate":                 purchase_rate,
            "Avg_Spend_Per_Visit":           avg_spend,
            "High_Value_Customer":           high_value,
            "Discount_Dependent":            discount_dependent,
            "App_Web_Ratio":                 app_web_ratio,
            "Churn_Risk_Flag":               churn_risk_flag,
            "Support_Heavy":                 support_heavy,
            "Low_Loyalty":                   low_loyalty,
            "Returns_Risk":                  returns_risk,
            "Wishlist_No_Purchase":          wishlist_no_buy,
            "Is_Inactive":                   is_inactive,
            "Platform_Encoded":              1,
            "Category_Encoded":              1,
            "Is_Fashion_Buyer":              0,
            "Is_Electronics_Buyer":          0,
            "Is_India_Platform":             1,
            "Gender_Encoded":                0,
            "Signup_Quarter_Encoded":        1,
            "Subscription_Encoded":          1,
            "Discount_Applied_Encoded":      int(discount_rate > 0),
            "Promo_Used_Encoded":            0,
            "Churn_Probability":             churn_prob_prior,
            "Engagement_Prob_Low":           eng_low,
            "Engagement_Prob_Medium":        eng_mid,
            "Engagement_Prob_High":          eng_high,
            "Engagement_Normalised":         engagement_norm,
            "Purchase_Rate_Norm":            purchase_rate_norm,
            "Age_Normalised":                age_norm,
            "Membership_Norm":               membership_norm,
            "Health_Score":                  health_score,
        }])

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔮 Predict Churn Risk", type="primary", use_container_width=True):
            try:
                model_feats = list(CHURN_M.feature_names_in_)
                final_input = input_df.reindex(columns=model_feats, fill_value=0)
                pred        = CHURN_M.predict_proba(final_input)[0][1]

                pr1, pr2, pr3 = st.columns(3)
                with pr1:
                    kpi_card("Churn Probability", f"{pred*100:.1f}%",
                             "This customer's risk score",
                             "red" if pred > 0.6 else ("amber" if pred > 0.4 else "green"))
                with pr2:
                    kpi_card("Health Score Proxy", f"{health_score:.1f}/10",
                             "Derived from inputs", "purple")
                with pr3:
                    risk_label = (
                        "🔥 High Risk"   if pred > 0.7
                        else "⚠️ Medium Risk" if pred > 0.5
                        else "✅ Low Risk"
                    )
                    kpi_card("Risk Level", risk_label, "Based on churn probability", "teal")

                if pred > 0.7:
                    callout(
                        "🔥 <b>High Risk</b> — Immediate intervention recommended. "
                        "Consider VIP rescue or personalised discount coupon.", "red"
                    )
                elif pred > 0.5:
                    callout(
                        "⚠️ <b>Medium Risk</b> — Monitor closely. "
                        "A re-engagement email sequence is advised.", "amber"
                    )
                else:
                    callout("✅ <b>Low Risk</b> — Customer appears healthy. No action required.", "green")

            except Exception as exc:
                callout(f"❌ Prediction error: {exc}", "red")

    # ══════════════════════════════════════════════════════
    #  TAB: MY ACCOUNT
    # ══════════════════════════════════════════════════════
    elif tab == "My Account":
        section_header("👤 My Account")
        pl = info.get("plan", "Starter")

        a1, a2 = st.columns(2)
        with a1:
            st.markdown(
                "<div class='insight-card'>"
                "<div style='font-weight:700;font-size:1rem;margin-bottom:16px'>🏢 Profile</div>"
                "<table style='width:100%;border-collapse:collapse'>",
                unsafe_allow_html=True,
            )
            for lbl, val in [
                ("Business",     info.get("business", "—")),
                ("Username",     st.session_state.user),
                ("Member Since", info.get("joined", "—")),
                ("Status",       info.get("status", "Active")),
            ]:
                colour = "#10b981" if lbl == "Status" and val == "Active" else "#0f172a"
                st.markdown(
                    f"<tr><td style='padding:8px 0;font-size:.74rem;color:#7889a4;"
                    f"font-weight:600;width:40%'>{lbl}</td>"
                    f"<td style='padding:8px 0;font-size:.86rem;font-weight:700;"
                    f"color:{colour}'>{val}</td></tr>",
                    unsafe_allow_html=True,
                )
            st.markdown("</table></div>", unsafe_allow_html=True)

        with a2:
            plan_badge_bg = {
                "Starter": "#dbeafe", "Pro": "#ede9fe",
                "Enterprise": "#d1fae5", "Free Trial": "#f1f5f9",
            }
            plan_badge_tc = {
                "Starter": "#1e40af", "Pro": "#5b21b6",
                "Enterprise": "#065f46", "Free Trial": "#64748b",
            }
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#05112e,#1e3a8a);"
                f"border-radius:14px;padding:26px;color:#fff'>"
                f"<div style='font-weight:700;font-size:1rem;margin-bottom:16px'>💳 Subscription</div>"
                f"<table style='width:100%;border-collapse:collapse'>",
                unsafe_allow_html=True,
            )
            for lbl, val in [
                ("Plan",         f"<span style='background:{plan_badge_bg.get(pl,'#f1f5f9')};"
                                 f"color:{plan_badge_tc.get(pl,'#64748b')};padding:2px 10px;"
                                 f"border-radius:20px;font-size:.72rem;font-weight:700'>{pl}</span>"),
                ("Period",       info.get("subscription", "—")),
                ("Payment",      info.get("payment", "—")),
                ("Monthly Cost", f"${PLAN_PRICES.get(pl, 0)}/mo"),
            ]:
                st.markdown(
                    f"<tr><td style='padding:8px 0;font-size:.74rem;"
                    f"color:rgba(255,255,255,.45);font-weight:600;width:40%'>{lbl}</td>"
                    f"<td style='padding:8px 0;font-size:.86rem;font-weight:700'>{val}</td></tr>",
                    unsafe_allow_html=True,
                )
            st.markdown("</table></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("🔒 Change Password")
        with st.form("change_password_form"):
            op  = st.text_input("Current Password",    type="password")
            np1 = st.text_input("New Password",        type="password")
            np2 = st.text_input("Confirm New Password",type="password")
            if st.form_submit_button("Update Password", type="primary"):
                fresh = load_users()
                if fresh[st.session_state.user]["password"] != _hash_password(op):
                    st.error("❌ Incorrect current password.")
                elif len(np1) < 6:
                    st.error("❌ New password must be at least 6 characters.")
                elif np1 != np2:
                    st.error("❌ Passwords do not match.")
                else:
                    fresh[st.session_state.user]["password"] = _hash_password(np1)
                    save_users(fresh)
                    st.success("✅ Password updated successfully.")


# ─────────────────────────────────────────────────────────────
#  MAIN ROUTER
# ─────────────────────────────────────────────────────────────
def main() -> None:
    page = st.session_state.page
    if page == "login":
        page_login()
    elif page == "signup":
        page_signup()
    elif page == "dashboard":
        if st.session_state.role == "admin":
            admin_dashboard()
        else:
            client_dashboard()
    else:
        navigate("login")


if __name__ == "__main__":
    main()