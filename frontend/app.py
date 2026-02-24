"""
WASTE IQ – Main Streamlit App Entry Point
Run locally: streamlit run app.py --server.port 8502
"""

import sys
from pathlib import Path
import streamlit as st

# ─────────────────────────────────────────────
# PAGE CONFIG (MUST BE FIRST)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="WASTE IQ",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Ensure frontend directory is importable
# ─────────────────────────────────────────────
HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# ─────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────
from utils import inject_css, init_session, check_backend
from languages import t, LANGUAGE_NAMES

# ─────────────────────────────────────────────
# Initialize
# ─────────────────────────────────────────────
init_session()
inject_css()

# ─────────────────────────────────────────────
# LOGIN GATE
# ─────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    from _pages.login import show_login
    show_login()
    st.stop()

# ═════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════
with st.sidebar:

    st.markdown("""
    <div class="wiq-sidebar-logo">
      <div class="logo-icon">♻️</div>
      <div class="logo-text">
        <h1>WASTE IQ</h1>
        <span>Smart Waste Management</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    role = st.session_state.role
    name = st.session_state.name

    st.markdown(
        f"""
        <div class="wiq-user-card">
          <div class="user-name">👤 {name}</div>
          <div class="user-role-badge role-{role}">{role.title()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### Navigation")

    def nav(label: str, page: str):
        if st.button(label, use_container_width=True):
            st.session_state.active_page = page
            st.rerun()

    nav(f"📊  {t('nav_dashboard')}", "dashboard")
    nav(f"🔍  {t('nav_classify')}", "classify")
    nav(f"📢  {t('nav_complaints')}", "complaints")
    nav(f"🏆  {t('nav_rewards')}", "rewards")
    nav(f"🔔  {t('nav_notifications')}", "notifications")
    nav(f"👤  {t('nav_profile')}", "profile")

    if role in ("driver", "admin"):
        st.markdown("---")
        nav(f"🗺️  {t('nav_route')}", "route")

    if role == "admin":
        nav(f"⚙️  {t('nav_admin')}", "admin")

    st.markdown("---")

    # Language
    langs = list(LANGUAGE_NAMES.keys())
    current = st.session_state.get("language", "en")
    idx = langs.index(current) if current in langs else 0

    selected = st.selectbox(
        f"🌐 {t('lbl_language')}",
        options=langs,
        format_func=lambda x: LANGUAGE_NAMES[x],
        index=idx,
    )

    if selected != current:
        st.session_state.language = selected
        st.rerun()

    # Dark mode
    dark = st.toggle(
        f"🌙 {t('lbl_dark_mode')}",
        value=st.session_state.get("dark_mode", False),
    )

    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.markdown("---")

    if st.button(f"🚪 {t('nav_logout')}", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    with st.expander("System Status"):
        if check_backend():
            st.success("Backend Online")
        else:
            st.warning("Backend Offline")

# ═════════════════════════════════════════════
# PAGE ROUTING
# ═════════════════════════════════════════════
page = st.session_state.get("active_page", "dashboard")
role = st.session_state.role

if page == "dashboard":
    if role == "household":
        from _pages.household_dashboard import show
    elif role == "municipal":
        from _pages.municipal_dashboard import show
    elif role == "driver":
        from _pages.driver_dashboard import show
    else:
        from _pages.admin_dashboard import show
    show()

elif page == "classify":
    from _pages.classifier import show
    show()

elif page == "complaints":
    from _pages.complaints import show
    show()

elif page == "rewards":
    from _pages.rewards import show
    show()

elif page == "notifications":
    from _pages.notifications import show
    show()

elif page == "profile":
    from _pages.profile import show
    show()

elif page == "route":
    from _pages.driver_route import show
    show()

elif page == "admin":
    from _pages.admin_dashboard import show
    show()

else:
    st.error(f"Unknown page: {page}")
