import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ResuMatch AI", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&family=Playfair+Display:wght@700;800&display=swap');

[data-testid="stSidebar"] { display: none; }
[data-testid="stToolbar"] { display: none; }

* { box-sizing: border-box; }

.block-container {
    padding-top: 3rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px;
}

/* Hide Streamlit image expand/fullscreen button */
[data-testid="StyledFullScreenButton"] { display: none !important; }
button[title="View fullscreen"] { display: none !important; }

/* ── ADAPTIVE VARIABLES ── */
:root {
    --card-bg: #f5f4ff;
    --card-border: rgba(99,102,241,0.18);
    --card-border-hover: rgba(99,102,241,0.5);
    --card-shadow-hover: 0 20px 40px rgba(99,102,241,0.13);
    --card-img-bg: #ede9fe;
    --tag-color: #6366f1;
    --title-color: #1e1b4b;
    --desc-color: #4b5563;
    --footer-color: #9ca3af;
}

@media (prefers-color-scheme: dark) {
    :root {
        --card-bg: linear-gradient(145deg, #13131f, #1a1a2e);
        --card-border: rgba(99,102,241,0.2);
        --card-border-hover: rgba(99,102,241,0.5);
        --card-shadow-hover: 0 20px 40px rgba(99,102,241,0.2);
        --card-img-bg: #0d0d1a;
        --tag-color: #818cf8;
        --title-color: #f1f0ff;
        --desc-color: #94a3b8;
        --footer-color: #475569;
    }
}

/* ── APP HEADING ── */
.app-heading {
    text-align: center;
    padding: 0.2rem 0 0.5rem;
    margin-bottom: 0.5rem;
}

.app-heading-name {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(2rem, 4vw, 3rem) !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 60%, #06b6d4 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    display: inline-block !important;
    margin: 0 !important;
    line-height: 1.1 !important;
}

/* ── HERO ── */
.hero-wrap {
    text-align: center;
    padding: 0.8rem 0 2.5rem;
}

.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15));
    border: 1px solid rgba(99,102,241,0.35);
    color: #818cf8;
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 16px;
    border-radius: 999px;
    margin-bottom: 14px;
}

.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    color: var(--desc-color);
    font-weight: 300;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.7;
    text-align: center;
}
/* ── CARDS ── */
.card-wrap {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    position: relative;
}

.card-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 1;
}

.card-wrap:hover {
    transform: translateY(-6px);
    box-shadow: var(--card-shadow-hover);
    border-color: var(--card-border-hover);
}

.card-wrap:hover::before {
    opacity: 1;
}

.card-img-wrap {
    width: 100%;
    overflow: hidden;
    background: var(--card-img-bg);
}

.card-body {
    padding: 18px 20px 20px;
}

.card-tag {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--tag-color);
    margin-bottom: 6px;
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--title-color);
    margin-bottom: 8px;
}

.card-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: var(--desc-color);
    line-height: 1.6;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.35) !important;
}

/* ── FOOTER ── */
.footer-text {
    text-align: center;
    font-family: 'DM Sans', sans-serif;
    color: var(--footer-color);
    font-size: 12px;
    padding-top: 2.5rem;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION NAVIGATION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- NAVIGATION FUNCTION ----------------
def go_to(page):
    st.session_state.page = page
    st.rerun()

# ---------------- HOME PAGE ----------------
def show_home():

    # ── APP HEADING ──

    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 0.8rem;">
    <span style="
        font-family: 'Playfair Display', serif;
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">ResuMatch AI</span>
    </div>
    """, unsafe_allow_html=True)

    # ── HERO ──
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-badge">AI-Powered Resume Platform</div>
        <p class="hero-sub" style="text-align:center; margin:0 auto;">Build, analyze and optimize your resume with intelligent insights that get you hired faster.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown('<div class="card-wrap"><div class="card-img-wrap">', unsafe_allow_html=True)
        st.image("assets/ats.png", use_column_width=True)
        st.markdown("""</div><div class="card-body">
        <div class="card-tag">Resume Analysis</div>
        <div class="card-title">ATS Checker</div>
        <div class="card-desc">Analyze your resume structure, formatting and ATS compatibility. Get instant feedback to pass automated filters.</div>
        </div></div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Analyze Resume", use_container_width=True, key="home_ats"):
            go_to("ats")

    with col2:
        st.markdown('<div class="card-wrap"><div class="card-img-wrap">', unsafe_allow_html=True)
        st.image("assets/jd.png", use_column_width=True)
        st.markdown("""</div><div class="card-body">
        <div class="card-tag">Job Matching</div>
        <div class="card-title">JD Matcher</div>
        <div class="card-desc">Compare your resume against any job description. Identify missing skills and get AI-powered suggestions.</div>
        </div></div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Match Resume", use_container_width=True, key="home_jd"):
            go_to("jd")

    with col3:
        st.markdown('<div class="card-wrap"><div class="card-img-wrap">', unsafe_allow_html=True)
        st.image("assets/builder.png", use_column_width=True)
        st.markdown("""</div><div class="card-body">
        <div class="card-tag">AI Builder</div>
        <div class="card-title">Resume Builder</div>
        <div class="card-desc">Create a professional ATS-friendly resume using AI. Choose templates, enhance with AI and download instantly.</div>
        </div></div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Build Resume", use_container_width=True, key="home_builder"):
            go_to("builder")

    st.markdown("""
    <div class="footer-text">ResuMatch AI &mdash; Smart Resume Platform</div>
    """, unsafe_allow_html=True)

# ---------------- ROUTING ----------------
if st.session_state.page == "home":
    show_home()

elif st.session_state.page == "ats":
    from page_views.ats_page import show_ats_page
    if st.button("← Back to Home", key="back_ats"):
        go_to("home")
    show_ats_page()

elif st.session_state.page == "jd":
    from page_views.jd_page import show_jd_page
    if st.button("← Back to Home", key="back_jd"):
        go_to("home")
    show_jd_page()

elif st.session_state.page == "builder":
    from page_views.builder_page import show_builder_page
    if st.button("← Back to Home", key="back_builder"):
        go_to("home")
    show_builder_page()