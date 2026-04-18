"""
Premium CSS theme for EagleNatureInsight.

Design intent (from TNFD consultation feedback):
- Narrative-first, low-jargon feel. Feels like a magazine story, not a data wall.
- Strong contrast and large typography for non-expert SME users.
- Loads even on low-bandwidth connections (no remote fonts, no animations).
- Works on mobile (phones are the primary device for many African SMEs).
"""
from __future__ import annotations
import streamlit as st


_PALETTE = {
    "brand":       "#1f8f5f",   # Eagle nature green
    "brand_deep":  "#0f5c3d",
    "accent":      "#f59e0b",   # warm attention
    "ink":         "#0f172a",
    "ink_soft":    "#334155",
    "mute":        "#64748b",
    "hairline":    "#e2e8f0",
    "canvas":      "#f6faf7",
    "panel":       "#ffffff",
    "good":        "#16a34a",
    "watch":       "#eab308",
    "warn":        "#f97316",
    "risk":        "#dc2626",
    "soft_blue":   "#e0f2fe",
}


def inject_theme():
    """Inject custom CSS once per session. Safe to call on every rerun."""
    st.markdown(
        f"""
        <style>
        :root {{
            --en-brand: {_PALETTE['brand']};
            --en-brand-deep: {_PALETTE['brand_deep']};
            --en-accent: {_PALETTE['accent']};
            --en-ink: {_PALETTE['ink']};
            --en-ink-soft: {_PALETTE['ink_soft']};
            --en-mute: {_PALETTE['mute']};
            --en-hairline: {_PALETTE['hairline']};
            --en-canvas: {_PALETTE['canvas']};
            --en-panel: {_PALETTE['panel']};
            --en-good: {_PALETTE['good']};
            --en-watch: {_PALETTE['watch']};
            --en-warn: {_PALETTE['warn']};
            --en-risk: {_PALETTE['risk']};
        }}

        .stApp {{
            background: var(--en-canvas);
        }}
        html, body, [class*="css"] {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                         "Helvetica Neue", Arial, sans-serif;
            color: var(--en-ink);
        }}
        h1, h2, h3, h4 {{
            color: var(--en-ink);
            letter-spacing: -0.01em;
        }}
        h1 {{ font-weight: 800; }}
        h2 {{ font-weight: 700; }}

        /* Hero block */
        .en-hero {{
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdfa 60%, #fef3c7 120%);
            border: 1px solid var(--en-hairline);
            border-radius: 22px;
            padding: 28px 32px;
            margin-bottom: 18px;
            box-shadow: 0 10px 35px rgba(15, 92, 61, 0.07);
        }}
        .en-hero__eyebrow {{
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 12px;
            color: var(--en-brand-deep);
            font-weight: 700;
        }}
        .en-hero__title {{
            font-size: 34px;
            font-weight: 800;
            margin-top: 6px;
            line-height: 1.18;
            color: var(--en-ink);
        }}
        .en-hero__sub {{
            color: var(--en-ink-soft);
            font-size: 17px;
            margin-top: 10px;
            max-width: 780px;
        }}
        .en-hero__meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 16px;
        }}
        .en-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(31, 143, 95, 0.10);
            color: var(--en-brand-deep);
            border: 1px solid rgba(31, 143, 95, 0.22);
            padding: 5px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
        }}

        /* Narrative block */
        .en-story {{
            background: var(--en-panel);
            border: 1px solid var(--en-hairline);
            border-left: 4px solid var(--en-brand);
            border-radius: 14px;
            padding: 18px 22px;
            margin: 12px 0 18px 0;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        }}
        .en-story__label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--en-brand-deep);
            font-weight: 700;
            margin-bottom: 6px;
        }}
        .en-story__body {{
            font-size: 16px;
            color: var(--en-ink);
            line-height: 1.55;
        }}

        /* KPI card */
        .en-kpi {{
            background: var(--en-panel);
            border: 1px solid var(--en-hairline);
            border-radius: 16px;
            padding: 16px 18px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
            height: 100%;
        }}
        .en-kpi__label {{
            font-size: 12px;
            color: var(--en-mute);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
        }}
        .en-kpi__value {{
            font-size: 28px;
            font-weight: 800;
            margin-top: 6px;
            color: var(--en-ink);
        }}
        .en-kpi__sub {{
            font-size: 12px;
            color: var(--en-mute);
            margin-top: 6px;
        }}
        .en-kpi--good  {{ border-left: 4px solid var(--en-good); }}
        .en-kpi--watch {{ border-left: 4px solid var(--en-watch); }}
        .en-kpi--warn  {{ border-left: 4px solid var(--en-warn); }}
        .en-kpi--risk  {{ border-left: 4px solid var(--en-risk); }}

        /* Status badges */
        .en-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
        }}
        .en-badge--good  {{ background: #dcfce7; color: #166534; }}
        .en-badge--watch {{ background: #fef9c3; color: #854d0e; }}
        .en-badge--warn  {{ background: #ffedd5; color: #9a3412; }}
        .en-badge--risk  {{ background: #fee2e2; color: #991b1b; }}
        .en-badge--info  {{ background: #e0f2fe; color: #075985; }}

        /* LEAP stepper */
        .en-leap {{
            display: flex;
            gap: 8px;
            margin: 10px 0 18px 0;
            flex-wrap: wrap;
        }}
        .en-leap__step {{
            flex: 1 1 160px;
            padding: 14px 16px;
            border: 1px solid var(--en-hairline);
            border-radius: 14px;
            background: #fff;
        }}
        .en-leap__step--on {{
            background: linear-gradient(135deg, #ecfdf5, #f0fdfa);
            border-color: var(--en-brand);
            box-shadow: 0 6px 20px rgba(31,143,95,0.15);
        }}
        .en-leap__letter {{
            display: inline-flex; width: 28px; height: 28px;
            border-radius: 50%; background: var(--en-brand); color: #fff;
            font-weight: 800; align-items: center; justify-content: center;
            margin-right: 8px;
        }}
        .en-leap__name {{ font-weight: 700; color: var(--en-ink); }}
        .en-leap__desc {{ font-size: 12px; color: var(--en-mute); margin-top: 4px;}}

        /* Section dividers */
        .en-section-title {{
            font-size: 22px;
            font-weight: 800;
            margin: 22px 0 4px 0;
            display: flex; align-items: center; gap: 10px;
        }}
        .en-section-sub {{
            color: var(--en-ink-soft);
            font-size: 14px;
            margin-bottom: 12px;
        }}

        /* Callout */
        .en-callout {{
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-radius: 12px;
            padding: 14px 16px;
            margin: 14px 0;
        }}
        .en-callout--info {{ background: #eff6ff; border-color: #bfdbfe; }}
        .en-callout--risk {{ background: #fef2f2; border-color: #fecaca; }}

        /* Matrix cells */
        .en-matrix-cell {{
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid var(--en-hairline);
            background: #fff;
            margin-bottom: 8px;
        }}

        /* Pricing */
        .en-price {{
            background: #fff;
            border: 1px solid var(--en-hairline);
            border-radius: 18px;
            padding: 22px;
            height: 100%;
        }}
        .en-price--featured {{
            border: 2px solid var(--en-brand);
            box-shadow: 0 10px 30px rgba(31,143,95,0.15);
        }}
        .en-price__tier {{ font-size: 13px; color: var(--en-mute); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; }}
        .en-price__amount {{ font-size: 30px; font-weight: 800; margin: 8px 0; }}
        .en-price__feat {{ font-size: 14px; color: var(--en-ink-soft); margin: 4px 0; }}

        /* Buttons */
        div.stButton > button {{
            border-radius: 10px;
            border: 1px solid var(--en-brand);
            background: var(--en-brand);
            color: #fff;
            font-weight: 600;
            padding: 6px 16px;
            transition: transform 0.04s ease-in-out, box-shadow 0.12s;
        }}
        div.stButton > button:hover {{
            background: var(--en-brand-deep);
            border-color: var(--en-brand-deep);
            color: #fff;
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(15,92,61,0.25);
        }}
        div.stButton > button:focus:not(:active) {{
            border-color: var(--en-brand-deep);
            color: #fff;
        }}

        /* Sidebar polish */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border-right: 1px solid var(--en-hairline);
        }}

        /* Login card */
        .en-login {{
            max-width: 460px;
            margin: 60px auto 0 auto;
            padding: 36px 34px;
            background: #fff;
            border-radius: 22px;
            border: 1px solid var(--en-hairline);
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
        }}
        .en-login__brand {{ color: var(--en-brand-deep); font-weight: 800; font-size: 14px; letter-spacing: 0.18em; text-transform: uppercase; }}
        .en-login__title {{ font-size: 26px; font-weight: 800; margin-top: 6px; }}
        .en-login__sub   {{ font-size: 14px; color: var(--en-mute); margin-top: 4px; margin-bottom: 14px; }}

        /* Responsive tweaks for mobile */
        @media (max-width: 720px) {{
            .en-hero__title {{ font-size: 26px; }}
            .en-hero {{ padding: 20px; }}
            .en-kpi__value {{ font-size: 22px; }}
        }}

        /* Accessibility: respect reduced motion */
        @media (prefers-reduced-motion: reduce) {{
            * {{ transition: none !important; animation: none !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def story(label: str, body: str) -> None:
    """Render a narrative "story" block with a labelled lede."""
    st.markdown(
        f"""
        <div class="en-story">
            <div class="en-story__label">{label}</div>
            <div class="en-story__body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def callout(text: str, kind: str = "info") -> None:
    cls = "en-callout"
    if kind == "info":
        cls += " en-callout--info"
    elif kind == "risk":
        cls += " en-callout--risk"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def badge(text: str, kind: str = "info") -> str:
    """Return the HTML for an inline status badge (caller controls placement)."""
    kind_map = {
        "Favourable": "good", "Good": "good",
        "Watch": "watch",
        "Warning": "warn", "Moderate": "watch",
        "High concern": "risk", "High": "risk",
        "Low": "good",
    }
    cls = kind_map.get(text, kind)
    return f'<span class="en-badge en-badge--{cls}">{text}</span>'


def kpi_card(label: str, value: str, sub: str = "", level: str = "") -> None:
    """Render a KPI card with optional severity colour strip."""
    mod = f" en-kpi--{level}" if level in {"good", "watch", "warn", "risk"} else ""
    st.markdown(
        f"""
        <div class="en-kpi{mod}">
            <div class="en-kpi__label">{label}</div>
            <div class="en-kpi__value">{value}</div>
            <div class="en-kpi__sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def leap_stepper(current: str) -> None:
    """Render the TNFD LEAP stepper with the active phase highlighted.

    current: one of 'L', 'E', 'A', 'P'.
    """
    phases = [
        ("L", "Locate",   "Find your site on the map and describe it."),
        ("E", "Evaluate", "See which parts of nature your business uses."),
        ("A", "Assess",   "Understand risk and opportunity in plain English."),
        ("P", "Prepare",  "Get a report you can share with banks and funders."),
    ]
    html = ['<div class="en-leap">']
    for letter, name, desc in phases:
        active = " en-leap__step--on" if letter == current else ""
        html.append(
            f'<div class="en-leap__step{active}">'
            f'<span class="en-leap__letter">{letter}</span>'
            f'<span class="en-leap__name">{name}</span>'
            f'<div class="en-leap__desc">{desc}</div>'
            "</div>"
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def section_title(title: str, sub: str = "", icon: str = "") -> None:
    st.markdown(
        f'<div class="en-section-title">{icon} {title}</div>'
        + (f'<div class="en-section-sub">{sub}</div>' if sub else ""),
        unsafe_allow_html=True,
    )
