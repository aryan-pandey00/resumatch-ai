import re

FA_CDN = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>'

SKILL_CATEGORIES = [
    "Languages",
    "Frameworks & Libraries",
    "Tools & Platforms",
    "AI / ML",
    "Cloud & DevOps",
    "Core CS",
    "Soft Skills",
]

def get_link_label(url):
    if "github.com" in url.lower():
        return "GitHub"
    return "Live"


def render_personal_info(data):
    name     = (data.get("name",     "") or "").strip()
    email    = (data.get("email",    "") or "").strip()
    phone    = (data.get("phone",    "") or "").strip()
    linkedin = (data.get("linkedin", "") or "").strip()
    github   = (data.get("github",   "") or "").strip()
    leetcode = (data.get("leetcode", "") or "").strip()

    if not any([name, email, phone, linkedin, github, leetcode]):
        return ""

    line2_parts = []

    if email:
        line2_parts.append(f'<i class="fas fa-envelope"></i> {email}')

    if phone:
        raw_phone = re.sub(r"\D", "", phone.replace("+91", ""))
        if len(raw_phone) == 10:
            phone_clean = "+91 " + raw_phone
            line2_parts.append(f'<i class="fas fa-phone"></i> {phone_clean}')

    profile_parts = []

    if linkedin:
        username = linkedin.rstrip("/").split("/")[-1]
        url = linkedin if linkedin.startswith("http") else "https://" + linkedin
        profile_parts.append(
            f'<i class="fab fa-linkedin" style="color:#000000;"></i> '
            f'<a href="{url}" target="_blank">{username}</a>'
        )

    if github:
        gh = github.strip().rstrip("/")
        if not gh.startswith("http"):
            gh = "https://" + gh
        username = gh.rstrip("/").split("/")[-1]
        profile_parts.append(
            f'<i class="fab fa-github" style="color:#333;"></i> '
            f'<a href="{gh}" target="_blank">{username}</a>'
        )

    if leetcode:
        lc = leetcode.strip().rstrip("/")
        if not lc.startswith("http"):
            lc = "https://" + lc
        username = lc.rstrip("/").split("/")[-1]
        profile_parts.append(
            f'LeetCode: <a href="{lc}" target="_blank">{username}</a>'
        )

    if len(profile_parts) >= 2:
        line2_html = "".join([f"<span class='contact-item'>{p}</span>" for p in line2_parts])
        line3_html = "".join([f"<span class='contact-item'>{p}</span>" for p in profile_parts])
        contact_block = f"""
        <div class="contact personal-contact">{line2_html}</div>
        <div class="contact personal-contact" style="margin-top:2px;">{line3_html}</div>
        """
    else:
        all_parts = line2_parts + profile_parts
        line2_html = "".join([f"<span class='contact-item'>{p}</span>" for p in all_parts])
        contact_block = f'<div class="contact personal-contact">{line2_html}</div>'

    return f"""
    {FA_CDN}
    <div class="header">
        <div class="personal-name">{name}</div>
        {contact_block}
    </div>
    """


def render_summary(summary):
    if not summary.strip():
        return ""
    return f"""
    <div class="card">
        <h2>SUMMARY</h2>
        <p>{summary}</p>
    </div>
    """


def render_skills(skills_dict, template="Minimal"):
    if not skills_dict or not isinstance(skills_dict, dict):
        return ""
    filled = {k: v for k, v in skills_dict.items() if v and v.strip()}
    if not filled:
        return ""
    if template == "Modern":
        return _render_skills_modern(filled)
    else:
        return _render_skills_flat(filled)


def _render_skills_flat(filled):
    items = ""
    for cat, val in filled.items():
        skills = [s.strip() for s in re.split(r",|\n", val) if s.strip()]
        if skills:
            skills_str = ", ".join(skills)
            items += f'<li style="margin-bottom:4px;"><strong>{cat}:</strong> {skills_str}</li>'
    return f"""
    <div class="section">
        <h2>SKILLS</h2>
        <ul style="list-style:none;padding:0;margin:4px 0;">{items}</ul>
    </div>
    """


def _render_skills_modern(filled):
    html = '<div class="section"><h2>SKILLS</h2>'
    for cat, val in filled.items():
        skills = [s.strip() for s in re.split(r",|\n", val) if s.strip()]
        if not skills:
            continue
        html += f'<div style="margin-bottom:10px;"><div style="font-size:13px;font-weight:600;color:rgba(255,255,255,0.95);border-bottom:1px solid rgba(255,255,255,0.25);padding-bottom:3px;margin-bottom:5px;">{cat}</div>'
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 8px;">'
        for s in skills:
            html += f'<div style="font-size:12.5px;color:rgba(255,255,255,0.85);">• {s}</div>'
        html += '</div></div>'
    html += '</div>'
    return html


def render_experience(exp_list):
    valid = [e for e in exp_list if e["role"] or e["company"] or e["desc"]]
    if not valid:
        return ""

    html = '<div class="card experience-section"><h2>EXPERIENCE</h2>'

    for e in valid:
        role     = e.get("role", "").strip()
        company  = e.get("company", "").strip()
        duration = e.get("duration", "").strip()
        desc     = e.get("desc", "").strip()
        link     = e.get("link", "").strip()

        html += '<div class="entry">'

        html += '<div class="entry-header">'
        if role:
            html += f'<div class="entry-title">{role}</div>'
        if duration:
            html += f'<div class="entry-duration">{duration}</div>'
        html += '</div>'

        if company or link:
            html += '<div class="entry-row">'
            if company:
                html += f'<div class="entry-sub"><em>{company}</em></div>'
            if link:
                url = link if link.startswith("http") else "https://" + link
                html += f'<div class="entry-meta"><a href="{url}" target="_blank" class="project-link">Certificate</a></div>'
            html += '</div>'

        if desc:
            bullets = [b.strip() for b in desc.split("\n") if b.strip()]
            if len(bullets) == 1:
                html += f"<p style='margin:2px 0;'>{bullets[0]}</p>"
            elif len(bullets) > 1:
                html += "<ul>"
                for b in bullets:
                    html += f"<li>{b}</li>"
                html += "</ul>"

        html += '</div>'

    html += "</div>"
    return html


def render_projects(project_list):
    valid = [p for p in project_list if p["title"] or p["desc"]]
    if not valid:
        return ""

    html = '<div class="card project-section"><h2>PROJECTS</h2>'

    for p in valid:
        title = p["title"]
        if p["tech"]:
            title += f" ({p['tech']})"

        html += '<div class="entry">'
        html += '<div class="entry-header">'
        html += f'<div class="entry-title">{title}</div>'

        if p.get("link") and p["link"].strip():
            link_url = p["link"].strip()
            if not link_url.startswith("http"):
                link_url = "https://" + link_url
            label = get_link_label(link_url)
            html += f'<a href="{link_url}" target="_blank" class="project-link">{label}</a>'

        html += '</div>'

        if p["desc"]:
            bullets = [b.strip() for b in p["desc"].split("\n") if b.strip()]
            if len(bullets) == 1:
                html += f"<p style='margin:2px 0;'>{bullets[0]}</p>"
            elif len(bullets) > 1:
                html += "<ul>"
                for b in bullets:
                    html += f"<li>{b}</li>"
                html += "</ul>"

        html += '</div>'

    html += "</div>"
    return html


def render_education(edu_list):
    valid = [e for e in edu_list if e["course"] or e["college"]]
    if not valid:
        return ""

    html = '<div class="section"><h2>EDUCATION</h2>'

    for e in valid:
        html += '<div class="entry">'

        html += '<div class="entry-header">'
        if e["course"]:
            html += f'<div class="entry-title">{e["course"]}</div>'
        if e["year"]:
            html += f'<div class="entry-duration">{e["year"]}</div>'
        html += '</div>'

        html += '<div class="entry-row">'
        if e["college"]:
            html += f'<div class="entry-sub">{e["college"]}</div>'
        if e["score"]:
            score = e["score"].strip()
            score_clean = score.replace(" ", "")
            if "%" in score_clean:
                html += f'<div class="entry-meta">{score}</div>'
            else:
                html += f'<div class="entry-meta">CGPA: {score}</div>'
        html += '</div>'

        html += '</div>'

    html += "</div>"
    return html


def render_certifications(cert_list):
    valid = [c for c in cert_list if isinstance(c, dict) and c.get("name", "").strip()]
    if not valid:
        return ""

    items = ""
    for c in valid:
        name = c.get("name", "").strip()
        link = c.get("link", "").strip()
        if link:
            url = link if link.startswith("http") else "https://" + link
            items += f'<li class="cert-item" style="display:flex;justify-content:space-between;align-items:center;"><span>{name}</span><a href="{url}" target="_blank" class="project-link">View</a></li>'
        else:
            items += f'<li class="cert-item">{name}</li>'

    return f"""
    <div class="section">
        <h2>CERTIFICATIONS</h2>
        <ul class="cert-list" style="list-style:none;padding:0;">{items}</ul>
    </div>
    """


def render_resume(data, template_html):
    template = data.get("template", "Minimal")
    html = template_html

    html = html.replace("{{personal_section}}",       render_personal_info(data))
    html = html.replace("{{summary_section}}",        render_summary(data.get("summary", "")))
    html = html.replace("{{skills_section}}",         render_skills(data.get("skills", {}), template))
    html = html.replace("{{experience_section}}",     render_experience(data.get("experience", [])))
    html = html.replace("{{projects_section}}",       render_projects(data.get("projects", [])))
    html = html.replace("{{education_section}}",      render_education(data.get("education", [])))
    html = html.replace("{{certifications_section}}", render_certifications(data.get("certifications", [])))

    return html