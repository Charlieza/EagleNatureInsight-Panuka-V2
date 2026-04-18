"""
Lightweight authentication for EagleNatureInsight.

Design goals (from rubric and client context):
- Judges and SMEs can try the tool in under 10 seconds via demo accounts.
- Tiers (Free / Pro / Enterprise) demonstrate the commercial model.
- SSO stubs show the enterprise path (Google / Microsoft) without forcing setup.
- No external auth dependency — SQLite file, works offline, portable, no vendor lock-in.
- Password hashing uses PBKDF2-SHA256 (stdlib-only, no heavy crypto lib required).
- Session stored in Streamlit session_state; tokens are not persisted cross-session
  by default (this is a pilot tool; production would add refresh tokens).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

DB_PATH = Path(os.environ.get("ENI_AUTH_DB", "data/eni_users.sqlite3"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

PBKDF2_ITERATIONS = 150_000
SALT_BYTES = 16

TIERS = {
    "free": {
        "label": "Free",
        "monthly_usd": 0,
        "features": [
            "1 site screening per month",
            "Core nature indicators (vegetation, water, heat, rainfall)",
            "Plain-English summary",
            "PDF export with watermark",
        ],
        "limits": {"sites_per_month": 1, "pdf_watermark": True, "tnfd_matrix": False},
    },
    "pro": {
        "label": "Pro",
        "monthly_usd": 49,
        "features": [
            "Unlimited sites & portfolio view",
            "Full TNFD LEAP workflow + dependency matrix",
            "Nature Positive state-of-nature metrics",
            "Biodiversity, pollinator & species layers",
            "Branded PDF and Excel exports",
            "Email support",
        ],
        "limits": {"sites_per_month": -1, "pdf_watermark": False, "tnfd_matrix": True},
    },
    "enterprise": {
        "label": "Enterprise",
        "monthly_usd": 399,
        "features": [
            "Everything in Pro, plus:",
            "SSO (Google / Microsoft) and role-based access",
            "Portfolio-wide reporting & API access",
            "Custom biome/sector tuning + offline deployment",
            "Data-residency options (local hosting)",
            "Dedicated onboarding & SLA",
        ],
        "limits": {"sites_per_month": -1, "pdf_watermark": False, "tnfd_matrix": True},
    },
}


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
@contextmanager
def _db():
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    finally:
        conn.close()


def _init_schema() -> None:
    with _db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                email        TEXT PRIMARY KEY,
                name         TEXT NOT NULL,
                organisation TEXT,
                tier         TEXT NOT NULL DEFAULT 'free',
                pass_hash    TEXT NOT NULL,
                salt         TEXT NOT NULL,
                sso_provider TEXT,
                created_at   TEXT NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS usage (
                email  TEXT NOT NULL,
                ts     TEXT NOT NULL,
                action TEXT NOT NULL
            )"""
        )


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------
def _hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_bytes(SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return base64.b64encode(dk).decode(), base64.b64encode(salt).decode()


def _verify_password(password: str, stored_hash_b64: str, salt_b64: str) -> bool:
    salt = base64.b64decode(salt_b64)
    candidate, _ = _hash_password(password, salt)
    return hmac.compare_digest(candidate, stored_hash_b64)


# ---------------------------------------------------------------------------
# Demo account seeding (so judges / SMEs can try instantly)
# ---------------------------------------------------------------------------
DEMO_ACCOUNTS = [
    # (email, name, org, tier, password)
    ("demo@panuka.io",        "Panuka Demo User",      "Panuka AgriBiz Hub",   "pro",        "panuka123"),
    ("sme@spaceeagle.io",     "Demo SME",              "Space Eagle SMEs",     "free",       "demo1234"),
    ("judge@tnfd.org",        "TNFD Judge",            "TNFD Challenge Panel", "enterprise", "judge2026"),
    ("enterprise@demo.io",    "Enterprise Demo",       "Demo Corp",            "enterprise", "enterprise"),
]


def seed_demo_accounts():
    _init_schema()
    for email, name, org, tier, pw in DEMO_ACCOUNTS:
        if not get_user(email):
            register_user(email=email, name=name, organisation=org, password=pw, tier=tier)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
@dataclass
class User:
    email: str
    name: str
    organisation: str
    tier: str
    sso_provider: Optional[str] = None

    @property
    def tier_details(self) -> dict:
        return TIERS.get(self.tier, TIERS["free"])

    def can(self, capability: str) -> bool:
        return bool(self.tier_details.get("limits", {}).get(capability, False))


def get_user(email: str) -> Optional[User]:
    _init_schema()
    with _db() as conn:
        row = conn.execute(
            "SELECT email, name, organisation, tier, sso_provider FROM users WHERE email = ?",
            (email.lower().strip(),),
        ).fetchone()
    if not row:
        return None
    return User(**dict(row))


def register_user(
    email: str,
    name: str,
    organisation: str,
    password: str,
    tier: str = "free",
    sso_provider: Optional[str] = None,
) -> User:
    _init_schema()
    email = email.lower().strip()
    if not email or "@" not in email:
        raise ValueError("Please enter a valid email address.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")
    if tier not in TIERS:
        tier = "free"
    h, s = _hash_password(password)
    with _db() as conn:
        try:
            conn.execute(
                """INSERT INTO users (email, name, organisation, tier, pass_hash, salt,
                                      sso_provider, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (email, name.strip(), organisation.strip(), tier, h, s, sso_provider,
                 datetime.utcnow().isoformat()),
            )
        except sqlite3.IntegrityError as e:
            raise ValueError("An account with that email already exists.") from e
    return get_user(email)


def authenticate(email: str, password: str) -> Optional[User]:
    _init_schema()
    email = email.lower().strip()
    with _db() as conn:
        row = conn.execute(
            "SELECT pass_hash, salt FROM users WHERE email = ?", (email,)
        ).fetchone()
    if not row:
        return None
    if not _verify_password(password, row["pass_hash"], row["salt"]):
        return None
    return get_user(email)


def log_usage(email: str, action: str) -> None:
    with _db() as conn:
        conn.execute(
            "INSERT INTO usage (email, ts, action) VALUES (?, ?, ?)",
            (email, datetime.utcnow().isoformat(), action),
        )


# ---------------------------------------------------------------------------
# SSO stub (enterprise-ready; no external call made in pilot)
# ---------------------------------------------------------------------------
def sso_stub_login(provider: str) -> Optional[User]:
    """Enterprise SSO placeholder.

    In production this would redirect to OAuth via Authlib or streamlit-oauth.
    For the pilot we show a deterministic demo account so judges can see the
    enterprise experience without configuring credentials.
    """
    provider = provider.lower().strip()
    if provider not in {"google", "microsoft"}:
        return None
    demo_email = f"{provider}-sso@demo.io"
    if not get_user(demo_email):
        register_user(
            email=demo_email,
            name=f"{provider.title()} SSO Demo",
            organisation="Enterprise Demo",
            password=secrets.token_hex(10),
            tier="enterprise",
            sso_provider=provider,
        )
    return get_user(demo_email)


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
def _session_user() -> Optional[User]:
    u = st.session_state.get("auth_user")
    return u if isinstance(u, User) else None


def current_user() -> Optional[User]:
    return _session_user()


def logout():
    for k in ("auth_user",):
        if k in st.session_state:
            del st.session_state[k]


def login_gate(app_title: str = "EagleNatureInsight") -> User:
    """Render the login page until a user is authenticated, then return the User.

    Call at the top of app.py after the theme is injected. This function will
    call st.stop() itself until authentication succeeds, so callers only see
    return values for authenticated sessions.
    """
    from .theme import inject_theme

    _init_schema()
    seed_demo_accounts()
    inject_theme()

    user = _session_user()
    if user is not None:
        return user

    # Layout: hero on left, login on right.
    st.markdown(
        """
        <style>
            /* Hide Streamlit's default header on login for a cleaner feel */
            header[data-testid="stHeader"] { background: transparent; }
            .en-login-wrap {
                display: grid;
                grid-template-columns: 1.1fr 1fr;
                gap: 48px;
                align-items: center;
                margin-top: 24px;
            }
            .en-login-copy h1 { font-size: 44px; line-height: 1.1; margin-bottom: 14px;}
            .en-login-copy p  { color: #475569; font-size: 17px; line-height: 1.55; }
            .en-bullets li { margin: 6px 0; color: #1e293b; }
            @media (max-width: 980px) {
                .en-login-wrap { grid-template-columns: 1fr; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(
            f"""
            <div class="en-login-copy">
                <div class="en-chip">Nature Intelligence for Business · TNFD LEAP</div>
                <h1>Understand how nature affects your business — in plain English.</h1>
                <p>
                  {app_title} turns satellite and environmental data into a short,
                  clear nature story any SME can act on. Built on the TNFD LEAP framework
                  and Nature Positive state-of-nature metrics, measured in
                  <b>units of nature</b> and <b>units of currency</b>.
                </p>
                <ul class="en-bullets">
                  <li>✅ Locate your site in 30 seconds</li>
                  <li>✅ See which parts of nature your business depends on</li>
                  <li>✅ Get a banker-ready PDF report in one click</li>
                  <li>✅ Mobile-friendly and works in low-bandwidth settings</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="en-login">', unsafe_allow_html=True)
        st.markdown('<div class="en-login__brand">EagleNatureInsight</div>', unsafe_allow_html=True)
        st.markdown('<div class="en-login__title">Welcome back</div>', unsafe_allow_html=True)
        st.markdown('<div class="en-login__sub">Sign in to continue — or try a demo account below.</div>', unsafe_allow_html=True)

        tab_signin, tab_signup, tab_demo = st.tabs(["Sign in", "Create account", "Demo accounts"])

        with tab_signin:
            with st.form("signin_form", clear_on_submit=False):
                email = st.text_input("Email", placeholder="you@company.com")
                password = st.text_input("Password", type="password")
                col_a, col_b = st.columns(2)
                with col_a:
                    submitted = st.form_submit_button("Sign in", use_container_width=True)
                with col_b:
                    st.form_submit_button("Forgot password", use_container_width=True, disabled=True,
                                          help="Password reset will be enabled in the production release.")
                if submitted:
                    u = authenticate(email, password)
                    if u:
                        st.session_state["auth_user"] = u
                        log_usage(u.email, "login")
                        st.rerun()
                    else:
                        st.error("Those credentials didn't match. Try again or use a demo account.")

            st.markdown("---")
            st.markdown("**Enterprise SSO (preview)**")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Continue with Google", use_container_width=True, key="sso_g"):
                    u = sso_stub_login("google")
                    if u:
                        st.session_state["auth_user"] = u
                        st.rerun()
            with c2:
                if st.button("Continue with Microsoft", use_container_width=True, key="sso_ms"):
                    u = sso_stub_login("microsoft")
                    if u:
                        st.session_state["auth_user"] = u
                        st.rerun()
            st.caption("SSO shown here uses a demo Enterprise account. Production deployment supports Google, Microsoft, and OIDC-compliant providers.")

        with tab_signup:
            with st.form("signup_form"):
                s_name  = st.text_input("Your name")
                s_org   = st.text_input("Organisation")
                s_email = st.text_input("Work email")
                s_pw    = st.text_input("Choose a password (6+ characters)", type="password")
                s_tier  = st.selectbox(
                    "Plan", options=["free", "pro", "enterprise"],
                    format_func=lambda t: f"{TIERS[t]['label']} — ${TIERS[t]['monthly_usd']}/mo",
                )
                agree = st.checkbox("I agree to the pilot terms and data-use policy.")
                submit = st.form_submit_button("Create account", use_container_width=True)
                if submit:
                    if not agree:
                        st.warning("Please accept the pilot terms to create an account.")
                    else:
                        try:
                            u = register_user(
                                email=s_email, name=s_name, organisation=s_org,
                                password=s_pw, tier=s_tier,
                            )
                            st.session_state["auth_user"] = u
                            log_usage(u.email, "signup")
                            st.success("Account created — loading your dashboard…")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

        with tab_demo:
            st.caption("No setup needed — these accounts are pre-loaded for the Nature Intelligence Challenge reviewers.")
            rows = [
                ("🔬 TNFD Judge (Enterprise)", "judge@tnfd.org",       "judge2026"),
                ("🌾 Panuka Demo (Pro)",        "demo@panuka.io",       "panuka123"),
                ("🧑‍🌾 SME Demo (Free)",         "sme@spaceeagle.io",    "demo1234"),
            ]
            for label, email, pw in rows:
                cols = st.columns([3, 2])
                with cols[0]:
                    st.markdown(f"**{label}**  \n`{email}` / `{pw}`")
                with cols[1]:
                    if st.button(f"Sign in as {label.split(' ')[0]}", key=f"demo_{email}", use_container_width=True):
                        u = authenticate(email, pw)
                        if u:
                            st.session_state["auth_user"] = u
                            log_usage(u.email, "demo_login")
                            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()
    # Unreachable, but keeps type-checkers happy.
    raise RuntimeError("login_gate should have called st.stop().")
