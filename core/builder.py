import re
def render_personal_info(data):
    name = data.get("name", "") or ""
    email = data.get("email", "") or ""
    phone = data.get("phone", "") or ""
    linkedin = data.get("linkedin", "") or ""

    # Clean values
    name = name.strip()
    email = email.strip()
    phone = phone.strip()
    linkedin = linkedin.strip()

    if not any([name, email, phone, linkedin]):
        return ""

    contact_parts = []

    # Email
    if email:
        contact_parts.append(f"✉ {email}")

    if phone:
        raw_phone = re.sub(r"\D", "", phone.replace("+91", ""))

        # Only show if exactly 10 digits
        if len(raw_phone) == 10:
            phone_clean = "+91 " + raw_phone
            contact_parts.append(f"✆ {phone_clean}")
        
    #Linkedin
    if linkedin:
        username = linkedin.rstrip("/").split("/")[-1]
        contact_parts.append(
            f'LinkedIn : <a href="{linkedin}" target="_blank">{username}</a>'
        )
    

    contact_html = "".join([f"<span class='contact-item'>{c}</span>" for c in contact_parts])

    return f"""
    <div class="header">
        <div class="personal-name">{name}</div>
        <div class="contact personal-contact">{contact_html}</div>
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


def render_skills(skills):
    if not skills or not skills.strip():
        return ""

    skills_list = re.split(r",|\n", skills)
    skills_list = [s.strip() for s in skills_list if s.strip()]

    if not skills_list:
        return ""

    items = "".join([f"<li class='skill-item'>{s}</li>" for s in skills_list])

    return f"""
    <div class="section">
        <h2>SKILLS</h2>
        <ul class="skills-list">{items}</ul>
    </div>
    """


def render_experience(exp_list):
    valid = [e for e in exp_list if e["role"] or e["company"] or e["desc"]]

    if not valid:
        return ""

    html = '<div class="card experience-section"><h2>EXPERIENCE</h2>'

    for e in valid:
        title_parts = []

        if e["role"]:
            title_parts.append(e["role"])
        if e["company"]:
            title_parts.append(e["company"])

        title = " | ".join(title_parts)

        html += '<div class="entry">'

        # Header (NEW STRUCTURE)
        html += '<div class="entry-header">'
        html += f'<div class="entry-title">{title}</div>'

        if e["duration"]:
            html += f'<div class="entry-duration">{e["duration"]}</div>'

        html += '</div>'

        # Description bullets
        if e["desc"]:
            bullets = e["desc"].split("\n")
            html += "<ul>"
            for b in bullets:
                if b.strip():
                    html += f"<li>{b.strip()}</li>"
            html += "</ul>"

        html += '</div>'  # entry close

    html += "</div>"
    return html

def render_projects(project_list):
    valid = [p for p in project_list if p["title"] or p["desc"]]

    if not valid:
        return ""

    html = '<div class="card project-section"><h2>PROJECTS</h2>'

    for p in valid:

        # Title + Tech
        title = p["title"]

        if p["tech"]:
            title += f" ({p['tech']})"

        html += '<div class="entry">'

        # HEADER (structured)
        html += '<div class="entry-header">'

        html += f'<div class="entry-title">{title}</div>'

        # Link (right aligned)
        if p.get("link") and p["link"].strip():
            html += f'<a href="{p["link"]}" target="_blank" class="project-link">View</a>'

        html += '</div>'

        # Description bullets
        if p["desc"]:
            bullets = p["desc"].split("\n")
            html += "<ul>"
            for b in bullets:
                if b.strip():
                    html += f"<li>{b.strip()}</li>"
            html += "</ul>"

        html += '</div>'  # entry close

    html += "</div>"
    return html

def render_education(edu_list):
    valid = [e for e in edu_list if e["course"] or e["college"]]

    if not valid:
        return ""

    html = '<div class="section"><h2>EDUCATION</h2>'

    for i, e in enumerate(valid):

        html += '<div class="entry">'

        # ROW 1 → Course + Year
        html += '<div class="entry-header">'

        if e["course"]:
            html += f'<div class="entry-title">{e["course"]}</div>'

        if e["year"]:
            html += f'<div class="entry-duration">{e["year"]}</div>'

        html += '</div>'

        # ROW 2 → College + Score
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


def render_certifications(cert_text):
    if not cert_text.strip():
        return ""

    certs = [c.strip() for c in cert_text.split("\n") if c.strip()]

    if not certs:
        return ""

    items = "".join([f"<li class='cert-item'>{c}</li>" for c in certs])

    return f"""
    <div class="section">
        <h2>CERTIFICATIONS</h2>
        <ul class="cert-list">{items}</ul>
    </div>
    """


def render_resume(data, template_html):
    html = template_html

    html = html.replace("{{personal_section}}", render_personal_info(data))
    html = html.replace("{{summary_section}}", render_summary(data.get("summary", "")))
    html = html.replace("{{skills_section}}", render_skills(data.get("skills", "")))
    html = html.replace("{{experience_section}}", render_experience(data.get("experience", [])))
    html = html.replace("{{projects_section}}", render_projects(data.get("projects", [])))
    html = html.replace("{{education_section}}", render_education(data.get("education", [])))
    html = html.replace("{{certifications_section}}", render_certifications(data.get("certifications", "")))

    return html