"""Data Privacy Stack brand styling for the Presidio Streamlit demo.

Applies the Presidio / Data Privacy Stack look & feel — the violet/indigo palette,
Plus Jakarta Sans + Inter typography and the "Inky" octopus icon — so the demo
matches the project's documentation site.
"""

import base64
import os

import streamlit as st

_HERE = os.path.dirname(__file__)
BRAND_ICON = os.path.join(_HERE, "dps-icon.svg")

# ---- Brand tokens (mirrors docs/stylesheets/extra.css) ----------------------
NAVY = "#131d4a"
INDIGO = "#4f46e5"
VIOLET = "#7c3aed"
VIOLET_BRIGHT = "#8957e8"
CYAN = "#22d3ee"
INK = "#11131a"
BG = "#fbfbfd"
GRADIENT = f"linear-gradient(135deg, #7c8be8 0%, {VIOLET_BRIGHT} 100%)"
TEXT_GRADIENT = "linear-gradient(120deg, #7d4dcb 0%, #6366f1 55%, #81c0f1 100%)"


def _icon_data_uri() -> str:
    """Return the octopus icon as a base64 data URI for inline HTML/CSS."""
    with open(BRAND_ICON, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def _brand_css() -> str:
    return f"""
    <style>
    @import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap");

    html, body, [class*="css"], .stApp, [data-testid="stMarkdownContainer"] {{
        font-family: "Inter", "Segoe UI", sans-serif;
    }}
    .stApp {{ background-color: {BG}; }}

    h1, h2, h3, h4,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {{
        font-family: "Plus Jakarta Sans", "Inter", sans-serif;
        letter-spacing: -0.02em;
        color: {INK};
    }}

    /* Primary buttons / interactive accents */
    .stButton > button, .stDownloadButton > button {{
        background: {VIOLET};
        border: 1px solid {VIOLET};
        color: #fff;
        border-radius: 10px;
        font-weight: 600;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background: {INDIGO};
        border-color: {INDIGO};
    }}
    a {{ color: {INDIGO}; }}
    a:hover {{ color: {VIOLET}; }}

    /* Slider / accent widgets */
    [data-testid="stSlider"] [role="slider"] {{ background-color: {VIOLET} !important; }}

    /* Brand hero banner */
    .dps-hero {{
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.1rem 1.5rem;
        margin-bottom: 1.25rem;
        border-radius: 18px;
        background:
            radial-gradient(120% 140% at 100% 0%, rgba(137, 87, 232, 0.12) 0%, transparent 55%),
            radial-gradient(120% 140% at 0% 100%, rgba(34, 211, 238, 0.10) 0%, transparent 50%),
            #ffffff;
        border: 1px solid #e6e8ee;
        box-shadow: 0 1px 2px rgba(17,19,26,0.04), 0 14px 34px rgba(17,19,26,0.09);
    }}
    .dps-hero img {{ width: 56px; height: 56px; filter: drop-shadow(0 8px 16px rgba(79,70,229,0.26)); }}
    .dps-hero__title {{
        font-family: "Plus Jakarta Sans", "Inter", sans-serif;
        font-weight: 800;
        font-size: 2rem;
        line-height: 1;
        margin: 0;
        background: {TEXT_GRADIENT};
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .dps-hero__tagline {{
        margin: 0.25rem 0 0;
        color: #5b6472;
        font-size: 0.92rem;
    }}
    </style>
    """


def apply_branding() -> None:
    """Inject the brand CSS, logo and hero banner into the Streamlit app."""
    st.markdown(_brand_css(), unsafe_allow_html=True)

    # Logo in the top-left chrome (Streamlit >= 1.35).
    try:
        st.logo(BRAND_ICON, link="https://data-privacy-stack.github.io/presidio/")
    except Exception:  # pragma: no cover - older Streamlit without st.logo
        pass

    st.markdown(
        f"""
        <div class="dps-hero">
            <img src="{_icon_data_uri()}" alt="Presidio" />
            <div>
                <p class="dps-hero__title">Presidio</p>
                <p class="dps-hero__tagline">
                    PII detection &amp; de-identification &middot; an open source project by
                    <strong>Data Privacy Stack</strong>
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
