import streamlit as st
import json

from core.parser import extract_text_from_pdf
from core.ats import calculate_ats_score
from core.genai import generate_ats_ai_output, fallback_ats_output


def show_ats_page():

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
        --warn-bg: rgba(251,191,36,0.08);
        --warn-border: rgba(251,191,36,0.25);
        --danger-bg: rgba(239,68,68,0.08);
        --danger-border: rgba(239,68,68,0.25);
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
            --warn-bg: rgba(251,191,36,0.08);
            --warn-border: rgba(251,191,36,0.2);
            --danger-bg: rgba(239,68,68,0.08);
            --danger-border: rgba(239,68,68,0.2);
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

    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 12px;
        letter-spacing: -0.3px;
        line-height: 1.6;
        padding-bottom: 6px;
        overflow: visible;
        display: block;
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
        color: #16a34a;
    }

    .status-info {
        background: var(--warn-bg);
        border: 1px solid var(--warn-border);
        color: #d97706;
    }

    .status-warning {
        background: var(--danger-bg);
        border: 1px solid var(--danger-border);
        color: #dc2626;
    }

    .suggestions-box {
        background: var(--accent-soft);
        border: 1px solid var(--accent-soft-border);
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 8px;
        box-sizing: border-box;
        max-width: 100%;
        overflow: hidden;
    }

    .suggestions-box ul { padding-left: 18px; margin: 0; }

    .suggestions-box li {
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        color: var(--text-secondary);
        margin-bottom: 10px;
        line-height: 1.6;
    }

    .suggestions-box li:last-child { margin-bottom: 0; }

    .role-card {
        background: var(--role-bg);
        border: 1px solid var(--role-border);
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: var(--role-color);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .role-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(59,130,246,0.12);
    }

    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--divider), transparent);
        margin: 1.8rem 0;
    }

    h4 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.3px !important;
        margin-bottom: 12px !important;
    }
                
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
        <div class="page-tag">Resume Analysis</div>
        <h2 class="page-title">ATS Checker</h2>
        <p class="page-subtitle">Analyze your resume for ATS compatibility, formatting, and keyword optimization.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── UPLOAD ──
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    st.caption("Supports single and multi-column PDF layouts")

    if uploaded_file:

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Analyze Resume", use_container_width=True):

            with st.spinner("Analyzing your resume..."):

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

                result    = calculate_ats_score(resume_text, skills_list)
                score     = result["score"]
                ai_input  = result["ai_input"]
                ai_output = generate_ats_ai_output(ai_input)

                if ai_output:
                    suggestions = ai_output["suggestions"]
                    jobs        = ai_output["job_roles"]
                else:
                    fallback    = fallback_ats_output(ai_input)
                    suggestions = fallback["suggestions"]
                    jobs        = fallback["job_roles"]

            # ── GAUGE ──
            import streamlit.components.v1 as components

            gauge_html = f"""
            <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=DM+Sans:wght@500;600&display=swap" rel="stylesheet">
            <style>
                html,body{{margin:0;padding:0;}}
                @media(prefers-color-scheme:dark){{
                    html,body{{background:#0e1117!important;}}
                }}
                @media(prefers-color-scheme:light){{
                    html,body{{background:transparent!important;}}
                }}
            </style>
            <canvas id="g" style="display:block;width:100%;max-width:460px;margin:0 auto;"></canvas>
            <script>
            function getLabel(s) {{
                if (s < 40) return 'Poor';
                if (s < 70) return 'Fair';
                if (s < 85) return 'Good';
                return 'Excellent';
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

                // ── FIX: paint over white iframe background on Streamlit Cloud dark mode
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

                // ── Filled arc — purple gradient
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

                    // Glow dot at tip
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

                // ── "ATS Score Analysis" title
                const titleFontSize = Math.round(W * 0.036);
                ctx.save();
                ctx.font = `600 ${{titleFontSize}}px 'DM Sans', sans-serif`;
                ctx.fillStyle = titleColor;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                const arcTopY = cy - R - trackW * 0.5;
                const titleY  = arcTopY * 0.38;
                ctx.fillText('ATS Score Analysis', cx, titleY);
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

            # ── SCORE STATUS ──
            if score >= 85:
                st.markdown("""
                <div class="status-card status-success">
                    Excellent — Your resume is highly ATS optimized and ready to submit.
                </div>""", unsafe_allow_html=True)
            elif score >= 70:
                st.markdown("""
                <div class="status-card status-info">
                    Good — A few targeted improvements can significantly boost your chances.
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="status-card status-warning">
                    Needs Improvement — Your resume needs optimization to pass ATS filters.
                </div>""", unsafe_allow_html=True)

            # ── SUGGESTIONS ──
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("ATS Suggestions")

            unique_feedback = list(dict.fromkeys(suggestions))
            if not unique_feedback:
                unique_feedback = ["Your resume looks good — no major issues detected."]

            bullet_points = "".join(f"<li>{item}</li>" for item in unique_feedback)

            st.markdown(f"""
            <div style="overflow:hidden; padding-right:1px;">
                <div class="suggestions-box">
                    <ul>{bullet_points}</ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── JOB ROLES ──
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("Recommended Roles")

            if jobs:
                cols = st.columns(min(len(jobs), 3))
                for i, job in enumerate(jobs[:3]):
                    cols[i].markdown(f'<div class="role-card">{job}</div>', unsafe_allow_html=True)
            else:
                st.info("No roles detected. Try adding more skills to your resume.")