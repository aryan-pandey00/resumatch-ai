import streamlit as st
import json

from core.parser import extract_text_from_pdf
from core.matcher import calculate_match_score
from core.genai import generate_suggestions


# ── HELPERS ──

def parse_ai_output(text):
    sections = {"improvements": [], "skills": [], "tips": []}
    current_section = None
    for line in text.split("\n"):
        line = line.strip()
        if "improvements" in line.lower():
            current_section = "improvements"
            continue
        elif "skills to add" in line.lower():
            current_section = "skills"
            continue
        elif "resume tips" in line.lower():
            current_section = "tips"
            continue
        if line.startswith("-") and current_section:
            sections[current_section].append(line[1:].strip())
    return sections

def fallback_suggestions(missing_skills):
    return {
        "improvements": [
            "Add a professional summary at the top",
            "Use consistent bullet points throughout",
            "Highlight achievements with measurable impact"
        ],
        "skills": missing_skills[:5] if missing_skills else ["Communication", "Teamwork"],
        "tips": [
            "Use strong action verbs",
            "Keep resume concise and focused",
            "Avoid complex formatting for ATS readability"
        ]
    }


# ── MAIN PAGE ──

def show_jd_page():

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Playfair+Display:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --card-bg: #f5f4ff;
        --card-border: rgba(99,102,241,0.18);
        --card-border-hover: rgba(99,102,241,0.45);
        --text-primary: #1e1b4b;
        --text-secondary: #4b5563;
        --text-muted: #9ca3af;
        --accent: #6366f1;
        --accent-2: #8b5cf6;
        --accent-soft: rgba(99,102,241,0.07);
        --accent-soft-border: rgba(99,102,241,0.18);
        --success-bg: rgba(34,197,94,0.08);
        --success-border: rgba(34,197,94,0.25);
        --success-color: #16a34a;
        --warn-bg: rgba(251,191,36,0.08);
        --warn-border: rgba(251,191,36,0.25);
        --warn-color: #d97706;
        --danger-bg: rgba(239,68,68,0.08);
        --danger-border: rgba(239,68,68,0.25);
        --danger-color: #dc2626;
        --role-bg: rgba(59,130,246,0.07);
        --role-border: rgba(59,130,246,0.2);
        --role-color: #3b82f6;
        --divider: rgba(99,102,241,0.12);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --card-bg: linear-gradient(145deg, #13131f, #1a1a2e);
            --card-border: rgba(99,102,241,0.2);
            --card-border-hover: rgba(99,102,241,0.5);
            --text-primary: #f1f0ff;
            --text-secondary: #94a3b8;
            --text-muted: #6b7280;
            --accent: #818cf8;
            --accent-2: #a78bfa;
            --accent-soft: rgba(99,102,241,0.08);
            --accent-soft-border: rgba(99,102,241,0.2);
            --success-bg: rgba(34,197,94,0.08);
            --success-border: rgba(34,197,94,0.2);
            --success-color: #4ade80;
            --warn-bg: rgba(251,191,36,0.08);
            --warn-border: rgba(251,191,36,0.2);
            --warn-color: #fbbf24;
            --danger-bg: rgba(239,68,68,0.08);
            --danger-border: rgba(239,68,68,0.2);
            --danger-color: #f87171;
            --role-bg: rgba(59,130,246,0.08);
            --role-border: rgba(59,130,246,0.2);
            --role-color: #93c5fd;
            --divider: rgba(99,102,241,0.15);
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

    .status-card {
        padding: 14px 18px;
        border-radius: 12px;
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .status-success {
        background: var(--success-bg);
        border: 1px solid var(--success-border);
        color: var(--success-color);
    }

    .status-info {
        background: var(--warn-bg);
        border: 1px solid var(--warn-border);
        color: var(--warn-color);
    }

    .status-warning {
        background: var(--danger-bg);
        border: 1px solid var(--danger-border);
        color: var(--danger-color);
    }

    /* ── SKILLS BOX ── */
    .skills-box {
        border-radius: 14px;
        padding: 18px 20px;
        font-family: 'DM Sans', sans-serif;
        font-size: 13.5px;
        line-height: 1.8;
        font-weight: 400;
        box-sizing: border-box;
        min-height: 80px;
    }

    .skills-box-match {
        background: var(--success-bg);
        border: 1px solid var(--success-border);
        color: var(--success-color);
    }

    .skills-box-missing {
        background: var(--danger-bg);
        border: 1px solid var(--danger-border);
        color: var(--danger-color);
    }

    .skills-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 10px;
        letter-spacing: -0.2px;
    }

    /* ── AI SUGGESTION CARDS ── */
    .suggestion-card {
        border-radius: 16px;
        padding: 20px 20px 16px;
        height: 100%;
        box-sizing: border-box;
    }

    .suggestion-card-red {
        background: var(--danger-bg);
        border: 1px solid var(--danger-border);
    }

    .suggestion-card-blue {
        background: var(--role-bg);
        border: 1px solid var(--role-border);
    }

    .suggestion-card-green {
        background: var(--success-bg);
        border: 1px solid var(--success-border);
    }

    .suggestion-card-title {
        font-family: 'Syne', sans-serif;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin: 0 0 14px;
    }

    .card-title-red   { color: var(--danger-color); }
    .card-title-blue  { color: var(--role-color); }
    .card-title-green { color: var(--success-color); }

    .suggestion-card ul {
        padding-left: 16px;
        margin: 0;
    }

    .suggestion-card li {
        font-family: 'DM Sans', sans-serif;
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 8px;
        line-height: 1.6;
    }

    .suggestion-card li:last-child { margin-bottom: 0; }

    [data-testid="stMarkdownContainer"] { overflow: visible !important; }

    iframe {
        background-color: transparent !important;
        color-scheme: dark light;
    }

    </style>
    """, unsafe_allow_html=True)

    # ── PAGE HEADER ──
    st.markdown("""
    <div class="page-header">
        <div class="page-tag">Job Matching</div>
        <h2 class="page-title">JD Matcher</h2>
        <p class="page-subtitle">Compare your resume against any job description and identify exactly what's missing.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── INPUTS ──
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    st.caption("Supports single and multi-column PDF layouts")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    jd_text = st.text_area(
        "Paste Job Description",
        height=180,
        placeholder="Paste the full job description here..."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Match Resume", use_container_width=True):

        if not uploaded_file:
            st.warning("Please upload your resume.")
            return

        if not jd_text.strip():
            st.warning("Please paste the job description.")
            return

        with st.spinner("Analyzing match..."):

            resume_text = extract_text_from_pdf(uploaded_file)

            if not resume_text:
                st.error("Could not extract text from this PDF. Please try a different file.")
                return

            with open("data/skills.json", "r") as f:
                skills_data = json.load(f)

            skills_list = list(set(
                skill.lower()
                for category in skills_data.values()
                for skill in category
            ))

            score, matched_skills, missing_skills, resume_skills, jd_skills = calculate_match_score(
                resume_text, jd_text, skills_list
            )

        # ── GAUGE ──
        import streamlit.components.v1 as components

        gauge_html = f"""
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=DM+Sans:wght@500;600&display=swap" rel="stylesheet">
        <style>
        html,body{{margin:0;padding:0;}}
        @media(prefers-color-scheme:dark){{html,body{{background:#0e1117!important;}}}}
        @media(prefers-color-scheme:light){{html,body{{background:transparent!important;}}}}
        </style>
        <canvas id="g" style="display:block;width:100%;max-width:460px;margin:0 auto;"></canvas>
        <script>
        function getLabel(s) {{
            if (s < 40) return 'Low Match';
            if (s < 70) return 'Fair Match';
            if (s < 85) return 'Good Match';
            return 'Strong Match';
        }}

        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        function draw(score) {{
            const canvas = document.getElementById('g');
            if (!canvas) return;

            const dpr = window.devicePixelRatio || 1;
            const LW = 460, LH = 400;
            canvas.width  = LW * dpr;
            canvas.height = LH * dpr;
            canvas.style.width  = LW + 'px';
            canvas.style.height = LH + 'px';

            const ctx = canvas.getContext('2d');
            ctx.scale(dpr, dpr);

            const W = LW, H = LH;
            const cx = W / 2, cy = H * 0.57;
            const R = W * 0.34, trackW = W * 0.068;

            ctx.clearRect(0, 0, W, H);
            if (isDark) {{
                ctx.fillStyle = '#0e1117';
                ctx.fillRect(0, 0, W, H);
            }}

            const startA = Math.PI * 0.78;
            const endA   = Math.PI * 2.22;
            const fillA  = startA + (endA - startA) * (score / 100);

            const trackBg    = isDark ? '#1e1c30' : '#ede9fe';
            const scoreColor = isDark ? '#e8e6ff' : '#1e1b4b';
            const labelColor = isDark ? '#818cf8' : '#6366f1';
            const titleColor = isDark ? '#94a3b8' : '#475569';

            // ── Track
            ctx.save();
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.arc(cx, cy, R, startA, endA);
            ctx.strokeStyle = trackBg;
            ctx.lineWidth = trackW;
            ctx.stroke();
            ctx.restore();

            // ── Filled arc
            if (score > 0) {{
                ctx.save();
                const grad = ctx.createLinearGradient(cx - R, cy, cx + R, cy);
                grad.addColorStop(0,   '#a5b4fc');
                grad.addColorStop(0.5, '#6366f1');
                grad.addColorStop(1,   '#4f46e5');
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.arc(cx, cy, R, startA, fillA);
                ctx.strokeStyle = grad;
                ctx.lineWidth = trackW;
                ctx.shadowColor = 'rgba(99,102,241,0.5)';
                ctx.shadowBlur = 26;
                ctx.stroke();
                ctx.shadowBlur = 0;

                const dx = cx + R * Math.cos(fillA);
                const dy = cy + R * Math.sin(fillA);
                ctx.beginPath();
                ctx.arc(dx, dy, trackW * 0.48, 0, Math.PI * 2);
                ctx.fillStyle = '#818cf8';
                ctx.shadowColor = 'rgba(99,102,241,0.7)';
                ctx.shadowBlur = 30;
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.restore();
            }}

            // ── Title
            const titleFontSize = Math.round(W * 0.036);
            ctx.save();
            ctx.font = `600 ${{titleFontSize}}px 'DM Sans', sans-serif`;
            ctx.fillStyle = titleColor;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            const arcTopY = cy - R - trackW * 0.5;
            const titleY  = arcTopY * 0.38;
            ctx.fillText('JD Match Score', cx, titleY);
            ctx.restore();

            // ── Score number
            const scoreFontSize = Math.round(W * 0.19);
            ctx.save();
            ctx.font = `700 ${{scoreFontSize}}px 'Space Grotesk', sans-serif`;
            ctx.fillStyle = scoreColor;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(Math.round(score), cx, cy);
            ctx.restore();

            // ── Label
            const scoreBotY = cy + scoreFontSize * 0.36;
            ctx.save();
            ctx.font = `600 ${{Math.round(W * 0.042)}}px 'DM Sans', sans-serif`;
            ctx.fillStyle = labelColor;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillText(getLabel(score).toUpperCase(), cx, scoreBotY + 14);
            ctx.restore();
        }}

        function animate(target) {{
            const dur = 950, t0 = performance.now();
            function step(now) {{
                const p    = Math.min((now - t0) / dur, 1);
                const ease = 1 - Math.pow(1 - p, 3);
                draw(target * ease);
                if (p < 1) requestAnimationFrame(step);
            }}
            requestAnimationFrame(step);
        }}

        document.fonts.ready.then(() => animate({score}));
        </script>
        """

        components.html(gauge_html, height=410)

        # ── MATCH STATUS ──
        if score >= 80:
            st.markdown("""
            <div class="status-card status-success">
                Strong Match — Your resume aligns well with this role.
            </div>""", unsafe_allow_html=True)
        elif score >= 60:
            st.markdown("""
            <div class="status-card status-info">
                Moderate Match — Adding a few key skills can significantly improve your chances.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card status-warning">
                Low Match — Significant improvements needed to align with this role.
            </div>""", unsafe_allow_html=True)

        # ── SKILLS ANALYSIS ──
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.subheader("Skills Analysis")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.subheader("Matching Skills")
            if matched_skills:
                content = ", ".join([s.title() for s in matched_skills])
            else:
                content = "No matching skills found"
            st.markdown(f'<div class="skills-box skills-box-match">{content}</div>', unsafe_allow_html=True)

        with col2:
            st.subheader("Missing Skills")
            if missing_skills:
                content = ", ".join([s.title() for s in missing_skills])
            else:
                content = "No missing skills — great alignment"
            st.markdown(f'<div class="skills-box skills-box-missing">{content}</div>', unsafe_allow_html=True)

        # ── AI SUGGESTIONS ──
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.subheader("AI Suggestions")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        with st.spinner("Generating suggestions..."):
            try:
                raw = generate_suggestions(resume_text, missing_skills)
            except:
                raw = None

        if not raw or len(raw.strip()) < 20:
            sections = fallback_suggestions(missing_skills)
        else:
            try:
                sections = parse_ai_output(raw)
                if all(len(v) == 0 for v in sections.values()):
                    sections = fallback_suggestions(missing_skills)
            except:
                sections = fallback_suggestions(missing_skills)

        col1, col2, col3 = st.columns(3, gap="medium")

        def render_card(col, card_class, title_class, title, items):
            bullets = "".join(f"<li>{i}</li>" for i in items) if items else "<li>No suggestions available</li>"
            col.markdown(f"""
            <div class="suggestion-card {card_class}">
                <div class="suggestion-card-title {title_class}">{title}</div>
                <ul>{bullets}</ul>
            </div>
            """, unsafe_allow_html=True)

        render_card(col1, "suggestion-card-red",   "card-title-red",   "Improvements",  sections["improvements"])
        render_card(col2, "suggestion-card-blue",  "card-title-blue",  "Skills to Add", sections["skills"])
        render_card(col3, "suggestion-card-green", "card-title-green", "Resume Tips",   sections["tips"])

        # ── DEBUG ──
        with st.expander("View Detailed Data"):
            st.write("JD Skills detected:", ", ".join(jd_skills))
            st.write("Resume Skills detected:", ", ".join(resume_skills))