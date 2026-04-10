import streamlit as st
from core.builder import render_resume
from core.genai import generate_resume_content
from core.fallback import generate_fallback
import random
import os
import base64

TEMPLATES = {
    "Modern":  "templates/modern.html",
    "Minimal": "templates/minimal.html",
    "Classic": "templates/classic.html",
}


# ── HELPERS ──

def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def ensure_three_bullets(text):
    if not isinstance(text, str):
        return "Generated description unavailable."
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    extras = [
        "Improved system efficiency and reliability.",
        "Applied structured problem-solving techniques.",
        "Optimized performance and ensured scalability.",
        "Enhanced functionality and user experience.",
        "Demonstrated strong development and debugging skills.",
    ]
    if len(lines) >= 3:
        return "\n".join(lines[:3])
    if len(lines) == 1:
        picks = random.sample(extras, 2)
        return f"{lines[0]}\n{picks[0]}\n{picks[1]}"
    if len(lines) == 2:
        return f"{lines[0]}\n{lines[1]}\n{random.choice(extras)}"
    return "Generated description unavailable."

def format_score(score):
    score = score.strip()
    if not score:
        return ""
    if "%" in score:
        return score
    try:
        val = float(score.replace("cgpa", "").replace("gpa", "").strip())
        if val > 10:
            return f"{val}%"
        else:
            return str(val) 
    except:
        return score

# ── MAIN ──

def main():

    # ── SESSION STATE ──
    for key, default in [("exp_count", 1), ("proj_count", 1), ("edu_count", 1)]:
        if key not in st.session_state:
            st.session_state[key] = default
    if "template" not in st.session_state:
        st.session_state["template"] = "Modern"

    # ── STYLES ──
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Playfair+Display:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --text-primary: #1e1b4b;
        --text-secondary: #4b5563;
        --text-muted: #9ca3af;
        --accent: #6366f1;
        --accent-2: #8b5cf6;
        --accent-soft: rgba(99,102,241,0.07);
        --accent-soft-border: rgba(99,102,241,0.18);
        --card-bg: #ffffff;
        --card-border: rgba(99,102,241,0.18);
        --divider: rgba(99,102,241,0.12);
        --input-bg: #fafafa;
        --section-bg: #f9f8ff;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #f1f0ff;
            --text-secondary: #94a3b8;
            --text-muted: #6b7280;
            --accent: #818cf8;
            --accent-2: #a78bfa;
            --accent-soft: rgba(99,102,241,0.08);
            --accent-soft-border: rgba(99,102,241,0.2);
            --card-bg: #13131f;
            --card-border: rgba(99,102,241,0.2);
            --divider: rgba(99,102,241,0.15);
            --input-bg: #0e0e1a;
            --section-bg: #0f0f1e;
        }
    }

    .page-header { margin-bottom: 1.8rem; }

    .page-tag {
        display: inline-block;
        background: var(--accent-soft);
        border: 1px solid var(--accent-soft-border);
        color: var(--accent);
        font-family: 'DM Sans', sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 10px;
    }

    .page-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(1.6rem, 3vw, 2.2rem);
        font-weight: 800;
        color: var(--text-primary);
        margin: 0 0 6px;
        letter-spacing: -0.5px;
    }

    .page-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        color: var(--text-muted);
        font-weight: 300;
        margin: 0;
    }

    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--divider), transparent);
        margin: 1.8rem 0;
    }

    .form-section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 0 1rem;
    }

    .form-section-label {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.2px;
    }

    .form-section-pill {
        font-family: 'DM Sans', sans-serif;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--accent);
        background: var(--accent-soft);
        border: 1px solid var(--accent-soft-border);
        padding: 2px 10px;
        border-radius: 999px;
    }

    .template-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 1.2rem;
    }

    .template-card {
        border-radius: 18px;
        padding: 14px 14px 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        border: 1.5px solid var(--card-border);
        background: var(--card-bg);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: pointer;
    }

    .template-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(99,102,241,0.13);
    }

    .template-card-selected {
        border: 2px solid #6366f1;
        box-shadow: 0 0 0 4px rgba(99,102,241,0.1), 0 12px 32px rgba(99,102,241,0.15);
    }

    .template-img-wrap {
        width: 100%;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(0,0,0,0.18), 0 2px 8px rgba(0,0,0,0.1);
        line-height: 0;
    }

    .template-img-wrap img {
        width: 100%;
        display: block;
    }

    .template-card-name {
        font-family: 'Syne', sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: var(--text-primary);
    }

    .template-card-name-selected {
        color: #6366f1;
    }

    .selected-badge {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #ffffff;
        font-family: 'DM Sans', sans-serif;
        font-size: 11px;
        font-weight: 600;
        padding: 5px 18px;
        border-radius: 999px;
        letter-spacing: 0.3px;
    }

    .ai-notice {
        background: var(--accent-soft);
        border: 1px solid var(--accent-soft-border);
        border-radius: 12px;
        padding: 13px 18px;
        font-family: 'DM Sans', sans-serif;
        font-size: 13.5px;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 4px;
    }

    .ai-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent);
        flex-shrink: 0;
    }

    .entry-card {
        background: var(--section-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }

    .entry-card-title {
        font-family: 'Syne', sans-serif;
        font-size: 0.88rem;
        font-weight: 700;
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 20px rgba(99,102,241,0.35) !important;
    }

    .preview-wrap {
        border: 1px solid var(--card-border);
        border-radius: 16px;
        overflow: hidden;
        background: #ffffff;
    }

    [data-testid="stMarkdownContainer"] { overflow: visible !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── PAGE HEADER ──
    st.markdown("""
    <div class="page-header">
        <div class="page-tag">AI Builder</div>
        <h2 class="page-title">Resume Builder</h2>
        <p class="page-subtitle">Build a professional ATS-ready resume with AI-powered content suggestions.</p>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 1 — TEMPLATE SELECTION

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Choose Template</span>
        <span class="form-section-pill">Step 1</span>
    </div>
    """, unsafe_allow_html=True)

    templates = ["Modern", "Minimal", "Classic"]

    cards_html = '<div class="template-grid">'
    for t in templates:
        img_path = os.path.join("assets", f"{t.lower()}.png")
        is_selected = st.session_state["template"] == t
        card_class = "template-card template-card-selected" if is_selected else "template-card"
        name_class = "template-card-name template-card-name-selected" if is_selected else "template-card-name"
        badge = '<div class="selected-badge">Selected</div>' if is_selected else ''

        if os.path.exists(img_path):
            encoded = get_base64(img_path)
            img_html = f'<div class="template-img-wrap"><img src="data:image/png;base64,{encoded}" alt="{t} template"/></div>'
        else:
            img_html = f'<div style="width:100%;height:120px;background:var(--accent-soft);border-radius:10px;display:flex;align-items:center;justify-content:center;font-family:DM Sans,sans-serif;font-size:12px;color:var(--text-muted);">No preview</div>'

        cards_html += f'<div class="{card_class}">{img_html}<div class="{name_class}">{t}</div>{badge}</div>'
    cards_html += '</div>'

    st.markdown(cards_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")
    for col, t in zip([col1, col2, col3], templates):
        with col:
            if st.session_state["template"] != t:
                if st.button(f"Select {t}", key=f"btn_{t}", use_container_width=True):
                    st.session_state["template"] = t
                    st.rerun()

    st.markdown("""
    <div class="ai-notice">
        <div class="ai-dot"></div>
        <span><strong style="color:var(--text-primary);">AI Assist available</strong> — Generate your summary and project descriptions automatically from your inputs below.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 2 — PERSONAL INFO

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Personal Information</span>
        <span class="form-section-pill">Step 2</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        name = st.text_input("Full Name")
    with col2:
        phone = st.text_input("Phone", value="+91 ", key="phone_input")

    raw_phone = phone.replace("+91", "").strip()
    if raw_phone:
        if not raw_phone.isdigit():
            st.caption("Only digits are allowed in phone number")
        elif len(raw_phone) != 10:
            st.caption("Enter a valid 10-digit phone number")

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        email = st.text_input("Email", placeholder="you@example.com")
    with col2:
        linkedin = st.text_input("LinkedIn", placeholder="linkedin.com/in/username")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 3 — SUMMARY

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Professional Summary</span>
        <span class="form-section-pill">Step 3</span>
    </div>
    """, unsafe_allow_html=True)

    if "summary" not in st.session_state:
        st.session_state["summary"] = ""
    if "ai_summary" in st.session_state:
        st.session_state["summary"] = st.session_state.pop("ai_summary")

    summary = st.text_area(
        "Summary",
        key="summary",
        height=100,
        label_visibility="collapsed",
        placeholder="Write a concise 2–4 line summary about yourself, or use AI Enhancement below to generate one automatically..."
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 4 — SKILLS

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Skills</span>
        <span class="form-section-pill">Step 4</span>
    </div>
    """, unsafe_allow_html=True)

    skills = st.text_input(
        "Skills",
        label_visibility="collapsed",
        placeholder="Python, SQL, Excel..."
    )
    st.caption("Separate skills with commas")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 5 — EXPERIENCE

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Work Experience</span>
        <span class="form-section-pill">Step 5</span>
    </div>
    """, unsafe_allow_html=True)

    if "ai_projects" in st.session_state:
        for i, desc in enumerate(st.session_state["ai_projects"]):
            st.session_state[f"pdesc{i}"] = desc
        del st.session_state["ai_projects"]

    exp_list = []
    for i in range(st.session_state.exp_count):
        st.markdown(f'<div class="entry-card"><div class="entry-card-title">Experience {i + 1}</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 3, 2], gap="small")
        with col1:
            role = st.text_input("Role", key=f"role{i}", placeholder="Intern/Software Engineer")
        with col2:
            company = st.text_input("Company", key=f"company{i}")
        with col3:
            duration = st.text_input("Duration", key=f"duration{i}", placeholder="Jan 2023 – Dec 2023")

        desc = st.text_area(
            "Description",
            key=f"desc{i}",
            height=80,
            placeholder="Write each responsibility on a new line — each becomes a bullet point..."
        )
        st.markdown('</div>', unsafe_allow_html=True)
        exp_list.append({"role": role, "company": company, "duration": duration, "desc": desc})

    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("Add Experience", key="add_exp", use_container_width=True):
            st.session_state.exp_count += 1
            st.rerun()
    with col_remove:
        if st.session_state.exp_count > 1:
            if st.button("Remove Last", key="rem_exp", use_container_width=True):
                st.session_state.exp_count -= 1
                st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 6 — PROJECTS

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Projects</span>
        <span class="form-section-pill">Step 6</span>
    </div>
    """, unsafe_allow_html=True)

    project_list = []
    for i in range(st.session_state.proj_count):
        st.markdown(f'<div class="entry-card"><div class="entry-card-title">Project {i + 1}</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 3, 2], gap="small")
        with col1:
            title = st.text_input("Title", key=f"title{i}")
        with col2:
            tech = st.text_input("Tech Stack", key=f"tech{i}")
        with col3:
            link = st.text_input("Link", key=f"link{i}", placeholder="github.com/... (optional)")

        desc = st.text_area(
            "Description",
            key=f"pdesc{i}",
            height=80,
            placeholder="Describe the project or use AI Enhancement to generate a description..."
        )
        st.markdown('</div>', unsafe_allow_html=True)
        project_list.append({"title": title, "tech": tech, "desc": desc, "link": link})

    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("Add Project", key="add_proj", use_container_width=True):
            st.session_state.proj_count += 1
            st.rerun()
    with col_remove:
        if st.session_state.proj_count > 1:
            if st.button("Remove Last", key="rem_proj", use_container_width=True):
                st.session_state.proj_count -= 1
                st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 7 — EDUCATION

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Education</span>
        <span class="form-section-pill">Step 7</span>
    </div>
    """, unsafe_allow_html=True)

    edu_list = []
    for i in range(st.session_state.edu_count):
        st.markdown(f'<div class="entry-card"><div class="entry-card-title">Education {i + 1}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            course = st.text_input("Degree / Course", key=f"course{i}")
        with col2:
            year = st.text_input("Year", key=f"year{i}", placeholder="2021 – 2025")

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            college = st.text_input("College / University", key=f"college{i}")
        with col2:
            score = st.text_input("Score / GPA", key=f"score{i}", placeholder="8.5 or 85%")

        st.markdown('</div>', unsafe_allow_html=True)
        edu_list.append({"course": course, "college": college, "year": year, "score": score})

    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("Add Education", key="add_edu", use_container_width=True):
            st.session_state.edu_count += 1
            st.rerun()
    with col_remove:
        if st.session_state.edu_count > 1:
            if st.button("Remove Last", key="rem_edu", use_container_width=True):
                st.session_state.edu_count -= 1
                st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 8 — CERTIFICATIONS

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Certifications</span>
        <span class="form-section-pill">Step 8</span>
    </div>
    """, unsafe_allow_html=True)

    certifications = st.text_area(
        "Certifications",
        height=90,
        label_visibility="collapsed",
        placeholder="Google Data Analytics Certificate\nMeta Front-End Developer..."
    )
    st.caption("One certification per line")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 9 — AI ENHANCEMENT

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">AI Enhancement</span>
        <span class="form-section-pill">Optional</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ai-notice" style="margin-bottom:1rem;">
        <div class="ai-dot"></div>
        <span>Fills in your <strong style="color:var(--text-primary);">Summary</strong> and all <strong style="color:var(--text-primary);">Project descriptions</strong> automatically — based on your skills and project titles above.</span>
    </div>
    """, unsafe_allow_html=True)

    ai_clicked = st.button("✨Enhance Resume with AI", use_container_width=True)

    if "ai_applied" in st.session_state:
        if st.session_state.get("ai_mode") == "fallback":
            st.info("Smart suggestions applied — AI fallback mode active")
        else:
            st.success("AI suggestions applied. Feel free to edit them.")
        del st.session_state["ai_applied"]
        st.session_state.pop("ai_mode", None)

    if ai_clicked:
        with st.spinner("Generating AI content..."):
            skills_list = [s.strip() for s in skills.split(",") if s.strip()]
            if not skills_list:
                skills_list = ["problem solving", "team collaboration"]

            project_inputs = []
            for p in project_list:
                t = p.get("title", "").strip()
                tk = p.get("tech", "").strip()
                if t:
                    project_inputs.append({"title": t, "tech": tk if tk else "relevant technologies"})

            if not project_inputs:
                st.warning("Please add at least one project title before using AI enhancement.")
                st.stop()

            exp_inputs = []
            for e in exp_list:
                r = e.get("role", "").strip()
                c = e.get("company", "").strip()
                if r or c:
                    exp_inputs.append({"role": r or "Role", "company": c or "Organization"})

            ai_input = {"skills": skills_list, "projects": project_inputs, "experience": exp_inputs}
            ai_output = generate_resume_content(ai_input)

            if not ai_output:
                ai_output = generate_fallback(ai_input)
                st.session_state["ai_mode"] = "fallback"
            else:
                st.session_state["ai_mode"] = "ai"

        summary_text = ai_output.get("summary", "")
        if not isinstance(summary_text, str):
            summary_text = ""
        st.session_state["ai_summary"] = summary_text

        ai_projects = ai_output.get("projects", [])
        if not isinstance(ai_projects, list):
            ai_projects = []

        mapped = []
        for i in range(len(project_inputs)):
            if i < len(ai_projects):
                item = ai_projects[i]
                if isinstance(item, str):
                    mapped.append(ensure_three_bullets(item))
                elif isinstance(item, dict):
                    desc = item.get("description") or item.get("desc")
                    mapped.append(ensure_three_bullets(desc) if isinstance(desc, str) else "Generated description unavailable.")
                else:
                    mapped.append("Generated description unavailable.")
            else:
                mapped.append("Generated description unavailable.")

        st.session_state["ai_projects"] = mapped
        st.session_state["ai_applied"] = True
        st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # SECTION 10 — LIVE PREVIEW

    st.markdown("""
    <div class="form-section-header">
        <span class="form-section-label">Live Preview</span>
        <span class="form-section-pill">Preview</span>
    </div>
    """, unsafe_allow_html=True)

    data = {
        "name": name, "email": email, "phone": phone, "linkedin": linkedin,
        "summary": summary, "skills": skills,
        "experience": exp_list,
        "projects": project_list,
        "education": [
            {**edu, "score": format_score(edu["score"])}
            for edu in edu_list
        ],
        "certifications": certifications,
    }

    template_path = TEMPLATES[st.session_state.get("template", "Minimal")]
    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    final_html = render_resume(data, template_html)

    st.components.v1.html(
        f"""
        <div style="
            border:1px solid rgba(99,102,241,0.18);
            border-radius:16px;
            overflow:auto;
            height:640px;
            background:#ffffff;
            padding:10px;
        ">
            {final_html}
        </div>
        """,
        height=660,
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    download_clicked = st.download_button(
        label="Download Resume",
        data=final_html,
        file_name="resume.html",
        mime="text/html",
        use_container_width=True,
    )

    if download_clicked:
        st.caption("Open the downloaded file in your browser, then press Ctrl + P and save as PDF.")


def show_builder_page():
    main()