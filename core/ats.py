import re
from collections import Counter

#  ACTION VERBS 

ACTION_VERBS = [
    # Building / Engineering
    "developed", "built", "designed", "implemented", "created", "engineered",
    "architected", "programmed", "coded", "deployed", "launched", "shipped",
    "automated", "integrated", "migrated", "refactored", "debugged", "tested",

    # Improving
    "optimized", "improved", "enhanced", "upgraded", "streamlined", "accelerated",
    "reduced", "cut", "eliminated", "simplified", "restructured", "revamped",

    # Leading / Managing
    "led", "managed", "directed", "coordinated", "supervised", "mentored",
    "trained", "coached", "guided", "oversaw", "spearheaded", "championed",
    "established", "founded", "initiated", "drove",

    # Analyzing
    "analyzed", "evaluated", "researched", "investigated", "identified",
    "diagnosed", "assessed", "audited", "monitored", "tracked", "measured",

    # Delivering / Achieving
    "delivered", "achieved", "increased", "grew", "generated", "secured",
    "saved", "scaled", "expanded", "boosted", "maximized", "exceeded",

    # Collaborating
    "collaborated", "partnered", "worked", "contributed", "supported",
    "facilitated", "presented", "communicated", "negotiated",
]

#  HELPERS

def has_valid_verb_line(line):
    
    line_lower = line.strip().lower()

    cleaned = re.sub(r"^[\•\-\*\>\·\–\—\►\▶\○\●\□\■\✓\✔\d+\.\)]+\s*", "", line_lower).strip()

    if any(cleaned.startswith(v) for v in ACTION_VERBS):
        return True

    first_words = " ".join(cleaned.split()[:6])
    if any(re.search(rf"\b{v}\b", first_words) for v in ACTION_VERBS):
        return True

    return False


def has_real_metrics(line):
   
    patterns = [
        r"\d+\s*%",                             
        r"\$\s*\d+[\d,]*\s*(k|m|b|million|thousand)?", 
        r"\b\d+\s*x\b",                         
        r"\b\d[\d,]*\s*(users|clients|customers|projects|teams|engineers|members|employees)",
        r"\b(increased|reduced|improved|cut|saved|grew|boosted|decreased)\b.{0,30}\d+",
        r"\b\d+\s*(hours|days|weeks|months)\b",  
        r"\b(top|rank|ranked|#1|first|second|third)\b",
        r"\b\d+[\d,]+\b",                    
    ]
    return any(re.search(p, line, re.IGNORECASE) for p in patterns)


def line_quality_score(line):

    line = line.strip()
    if len(line) < 15:
        return 0

    has_verb = has_valid_verb_line(line)
    has_metric = has_real_metrics(line)
    is_long_enough = len(line) > 60 

    if has_verb and has_metric and is_long_enough:
        return 3
    elif has_verb and has_metric:
        return 2
    elif has_verb or has_metric:
        return 1
    else:
        return 0


def detect_garbage(text):

    penalty = 0
    feedback = []
    lines = text.split("\n")

    # Random numeric sequences like 1,2,3 or 12,34,56
    if re.search(r"\b\d+(,\s*\d+){2,}\b", text):
        penalty += 8  
        feedback.append("Your resume contains random numeric sequences that may confuse ATS parsers. Please remove them.")

    # Short lines: only penalize if they look like noise (no alpha content)
    noise_lines = [l for l in lines if 0 < len(l.strip()) < 8 and not re.search(r"[a-zA-Z]{2,}", l)]
    if len(noise_lines) > 8:
        penalty += 5
        feedback.append("Several lines appear to contain formatting noise. Consider using a simpler, ATS-friendly resume template.")
    elif len(noise_lines) > 4:
        penalty += 2

    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    word_freq = Counter(words)
    stopwords = {"with", "have", "that", "this", "from", "they", "were", "been",
                 "will", "also", "more", "than", "when", "your", "which", "their",
                 "using", "work", "team", "data", "project", "experience", "skill",
                 "resume", "company", "role", "time", "year", "month"}
    repeated = [(w, c) for w, c in word_freq.items() if c > 8 and w not in stopwords]
    if len(repeated) > 5:
        penalty += 6
        feedback.append("Some words appear too frequently throughout your resume. Varying your language will make it more compelling.")

    if re.search(r"lorem\s+ipsum|placeholder|sample\s+text|your\s+name\s+here", text, re.IGNORECASE):
        penalty += 25
        feedback.append("Placeholder or sample text was detected. Please replace all template content with your actual information.")

    gibberish_count = 0
    for line in lines:
        stripped = re.sub(r"[\s\d\W]+", "", line.strip().lower())
        if len(stripped) > 8:
            vowel_ratio = sum(1 for c in stripped if c in "aeiou") / len(stripped)
            if vowel_ratio < 0.08:
                gibberish_count += 1
    if gibberish_count >= 2:
        penalty += 5
        feedback.append("Some lines contain unreadable characters, likely from complex formatting. A clean single-column layout works best.")

    section_matches = list(re.finditer(
        r"(experience|education|skills|projects|certifications?|summary|objective)\s*\n",
        text, re.IGNORECASE
    ))
    empty_count = 0
    for m in section_matches:
        body_start = m.end()
        body_snippet = text[body_start:body_start + 80].strip()
        if len(body_snippet) < 8:
            empty_count += 1
    if empty_count >= 2:
        penalty += 8 * empty_count
        feedback.append("One or more sections appear to have no content. Make sure each section heading is followed by relevant details.")

    return penalty, feedback

#  CONTACT

def check_contact(text):

    score = 5
    feedback = []

    if not re.search(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text):
        score -= 3
        feedback.append("Please include a professional email address so recruiters can reach you.")

    # Covers: 9876543210, +91-9876543210, +1 (555) 123-4567, etc.
    if not re.search(r"(\+?\d[\d\s\-\(\)]{8,}\d)", text):
        score -= 2
        feedback.append("Adding a phone number makes it easier for recruiters to contact you quickly.")

    return max(score, 0), feedback

#  SECTIONS

def check_sections(text):
  
    score = 0
    feedback = []
    missing = []

    section_aliases = {
        "experience": ["experience", "work experience", "professional experience", "employment", "work history"],
        "education":  ["education", "academic", "qualification", "degree"],
        "skills":     ["skills", "technical skills", "core skills", "competencies", "technologies"],
        "projects":   ["projects", "project work", "personal projects", "academic projects", "key projects"],
    }

    for sec, aliases in section_aliases.items():
        found = any(re.search(rf"\b{alias}\b", text, re.IGNORECASE) for alias in aliases)
        if found:
            score += 2
        else:
            missing.append(sec)
            feedback.append(f"Consider adding a '{sec}' section to give your resume a complete, professional structure.")

    if len(missing) == 0:
        score += 2

    return score, missing, feedback

#  EXPERIENCE 

def check_experience(text):

    score = 0
    feedback = []

    lines = text.split("\n")

    # Section header words to skip
    header_words = re.compile(
        r"^(experience|education|skills|projects|summary|objective|profile|"
        r"certifications?|awards?|achievements?|contact|references?|languages?|"
        r"interests?|hobbies|declaration)\s*$",
        re.IGNORECASE
    )

    content_lines = []
    for l in lines:
        stripped = l.strip()
        if len(stripped) < 20:
            continue
        if header_words.match(stripped):
            continue
        
        if re.match(r"^[\w\s]+$", stripped) and len(stripped.split()) <= 3:
            continue
        content_lines.append(stripped)

    if not content_lines:
        feedback.append("Your resume seems to have very little content. Try adding detailed descriptions of your experience and projects.")
        return 0, feedback

    quality_scores = [line_quality_score(l) for l in content_lines]

    strong  = quality_scores.count(3)
    decent  = quality_scores.count(2)
    weak    = quality_scores.count(1)
    garbage = quality_scores.count(0)

    total_lines = len(quality_scores)
    quality_ratio = (strong * 3 + decent * 2 + weak * 1) / (total_lines * 3) if total_lines else 0

    # Thresholds tuned for real PDF-extracted resumes
    if quality_ratio >= 0.35:
        score += 20
    elif quality_ratio >= 0.20:
        score += 14
    elif quality_ratio >= 0.10:
        score += 8
    elif quality_ratio >= 0.05:
        score += 4
    else:
        score += 1

    # Bonus for strong lines count
    if strong >= 4:
        score += 10
    elif strong >= 2:
        score += 6
    elif strong >= 1:
        score += 3

    # Penalty for garbage-heavy content
    garbage_ratio = garbage / total_lines if total_lines else 0
    if garbage_ratio > 0.75:
        score -= 10
        feedback.append("Most of your bullet points read as descriptions rather than achievements. Starting each with a strong verb and including a result will significantly improve your score.")
    elif garbage_ratio > 0.55:
        score -= 5
        feedback.append("Several bullet points could be stronger. Try leading with an action verb and including a measurable outcome where possible.")

    verb_count   = sum(1 for l in content_lines if has_valid_verb_line(l))
    metric_count = sum(1 for l in content_lines if has_real_metrics(l))

    if verb_count < 3:
        feedback.append("Starting your bullet points with strong action verbs such as Developed, Built, Led or Optimized makes your experience much more impactful.")

    if metric_count == 0:
        feedback.append("Adding even one measurable outcome, such as an accuracy score, a speed improvement or a percentage gain, will make your experience stand out.")
    elif metric_count < 2 and total_lines > 8:
   
        feedback.append("You have some good metrics already. Adding one or two more quantified results will further strengthen the impact of your experience.")

    return max(min(score, 30), 0), feedback

#  SKILLS

def check_skills(text, skills_list):

    found = []
    for s in skills_list:
        # whole-word match to avoid 'java' matching 'javascript' etc.
        if re.search(rf"\b{re.escape(s.lower())}\b", text):
            found.append(s)

    count = len(found)

    if count >= 8:
        score = 10
    elif count >= 5:
        score = 7
    elif count >= 3:
        score = 4
    elif count >= 1:
        score = 2
    else:
        score = 0

    feedback = []
    if count < 4:
        feedback.append("Your skills section could be more detailed. Listing the specific tools, languages and frameworks you know well will improve your visibility.")

    return score, feedback, found

#  LENGTH

def check_length(text):

    words = len(text.split())

    if words < 150:
        return 2, ["Your resume is quite brief. Expanding on your experience and projects, even with a few extra lines each, will give recruiters more to evaluate."]
    elif words < 250:
        return 8, ["Your resume is on the shorter side. Adding a summary section or a few more details to your projects can help it feel more complete."]
    elif words <= 750:
        return 15, []
    elif words <= 950:
        return 10, ["Your resume is slightly over the ideal length. Trimming it to one page will keep it focused and easier to scan."]
    else:
        return 5, ["Your resume is quite long. Keeping it to one page with the most relevant information tends to perform better with both ATS systems and recruiters."]


#  FORMATTING

def check_formatting(raw_text):
  
    score = 10
    feedback = []

    lines = raw_text.split("\n")

    # Table-like structures (pipes)
    pipe_lines = [l for l in lines if l.count("|") > 2]
    if len(pipe_lines) > 4:
        score -= 4
        feedback.append("Your resume appears to use tables. Most ATS systems cannot read tabular content correctly, so a clean linear layout is strongly recommended.")

    # Excessive ALL CAPS lines
    allcaps_lines = [l for l in lines if l.strip().isupper() and len(l.strip()) > 10]
    if len(allcaps_lines) > 5:
        score -= 2
        feedback.append("Using title case for section headings rather than all capitals looks more professional and is easier for parsers to process.")

    # Special character noise
    special_chars = re.findall(r"[★✓●▪▸◆✔✗✘☑]", raw_text)
    if len(special_chars) > 12:
        score -= 2
        feedback.append("Your resume contains many special characters. Keeping formatting minimal and clean ensures nothing gets lost during ATS parsing.")

    # Very long lines 
    very_long_lines = [l for l in lines if len(l.strip()) > 200]
    if len(very_long_lines) > 3:
        score -= 2
        feedback.append("Your resume appears to use a multi-column layout. While it may look great visually, ATS systems often misread columnar formats. A single-column layout is safer.")

    return max(score, 0), feedback

#  KEYWORDS  

def check_keywords(text, skills_list):

    # Industry/role keywords beyond just skills
    general_keywords = [
        "team", "project", "product", "system", "solution", "platform",
        "process", "performance", "strategy", "development", "cross-functional",
        "stakeholder", "deadline", "agile", "scrum", "workflow", "pipeline",
        "architecture", "infrastructure", "database", "api", "frontend", "backend",
        "machine learning", "data", "cloud", "security", "testing", "ci/cd",
    ]

    all_keywords = list(set([s.lower() for s in skills_list] + general_keywords))
    matches = sum(1 for kw in all_keywords if re.search(rf"\b{re.escape(kw)}\b", text))

    if matches >= 15:
        score = 10
    elif matches >= 10:
        score = 8
    elif matches >= 6:
        score = 5
    elif matches >= 3:
        score = 3
    else:
        score = 0

    feedback = []
    if matches < 6:
        feedback.append("Including more industry-specific keywords throughout your resume will help it surface in recruiter searches and ATS filters.")

    return score, feedback

#  EDUCATION QUALITY 

def check_education(text):

    score = 0
    feedback = []

    degree_pattern = r"\b(b\.?tech|b\.?e|b\.?sc|m\.?tech|m\.?sc|mba|bachelor|master|phd|diploma|b\.?com|b\.?a\b)\b"
    year_pattern = r"\b(19|20)\d{2}\b"
    institution_words = ["university", "institute", "college", "iit", "nit", "bits", "school"]

    has_degree = bool(re.search(degree_pattern, text, re.IGNORECASE))
    has_year = bool(re.search(year_pattern, text))
    has_institution = any(w in text.lower() for w in institution_words)

    if has_degree:
        score += 2
    else:
        feedback.append("Please mention your degree title clearly. Writing it out explicitly, such as B.Tech or MBA, helps ATS systems categorise your qualification correctly.")

    if has_institution:
        # Check if institution name looks like a placeholder
        inst_match = re.search(
            r"(university|institute|college|iit|nit|bits|school)[^\n]{0,60}",
            text, re.IGNORECASE
        )
        if inst_match:
            # Check surrounding context: 40 chars before + 60 chars after the keyword
            start = max(0, inst_match.start() - 40)
            inst_context = text[start : inst_match.end() + 20].lower()
            if re.search(r"\b(abc|xyz|test|dummy|sample|college name|university name|your college|my college|institute name)\b", inst_context):
                score -= 1
                feedback.append("Your institution name appears to be a placeholder. Please replace it with your actual college or university name.")
        score += 2
    else:
        score -= 1  # small penalty — missing institution is a real gap
        feedback.append("Including your college or university name adds credibility and is expected by most ATS systems and recruiters.")

    if has_year:
        score += 1

    return score, feedback

#  CERTIFICATIONS 

def check_certifications(text):

    score = 0
    feedback = []

    has_cert_section = bool(re.search(r"\bcertifications?\b", text, re.IGNORECASE))

    if not has_cert_section:
        # Soft suggestion only — not everyone has certs
        feedback.append("A certifications section, even with just one or two entries, can meaningfully strengthen your profile and demonstrate initiative.")
        return 0, feedback

    # Find content in certifications section
    cert_match = re.search(
        r"certifications?\s*\n([\s\S]{0,400}?)(?=\n[A-Z]{3,}|\Z)",
        text, re.IGNORECASE
    )

    if not cert_match:
        # Section heading exists but content not found
        feedback.append("Your resume has a certifications heading but no content beneath it. Listing your actual certifications there will add real value.")
        return 1, feedback

    cert_body = cert_match.group(1).strip()
    cert_lines = [l.strip() for l in cert_body.split("\n")
                  if len(l.strip()) > 4
                  and not re.match(r"^(experience|education|skills|projects|summary|objective)$",
                                   l.strip(), re.IGNORECASE)]

    count = len(cert_lines)

    if count >= 3:
        score = 5
    elif count >= 2:
        score = 4
    elif count >= 1:
        score = 3
        feedback.append("You have a solid set of certifications. Ensuring all of them are clearly listed will give recruiters a fuller picture of your expertise.")
    else:
        score = 1
        feedback.append("Your certifications section appears incomplete. Adding the full names of your certifications will make this section count.")

    return score, feedback

#  SUMMARY 

def check_summary(text):

    score = 0
    feedback = []

    has_summary = bool(re.search(r"\b(summary|objective|profile|about)\b", text, re.IGNORECASE))

    if not has_summary:
        feedback.append("Adding a short professional summary at the top of your resume gives recruiters an immediate sense of who you are and what you bring.")
        return 0, feedback

    # Find content after summary heading
    match = re.search(
        r"(summary|objective|profile|about)[^\n]*\n(.{50,})",
        text, re.IGNORECASE | re.DOTALL
    )

    if match:
        summary_text = match.group(2)[:400]
        words = len(summary_text.split())
        if words >= 30:
            score = 5
        elif words >= 15:
            score = 3
        else:
            score = 1
            feedback.append("Your summary is quite brief. Two to three sentences covering your background, key skills and goals will make a much stronger first impression.")
    else:
        score = 1
        feedback.append("Your summary section has very little content. A couple of well-crafted sentences about your background and goals will set a strong tone for the rest of your resume.")

    return score, feedback

#  MAIN CALCULATOR

def calculate_ats_score(resume_text, skills_list):
    """
    SCORE BREAKDOWN (clamped to 100):
    - Experience quality:  30 pts  
    - Keywords:            10 pts
    - Skills match:        10 pts
    - Length:              15 pts
    - Formatting:          10 pts
    - Sections presence:   10 pts
    - Education:            5 pts
    - Summary:              5 pts
    - Contact:              5 pts
    - Certifications:       5 pts  
    TOTAL:               ~105 pts 

    PENALTIES (can reduce score):
    - Garbage detection:   up to -30
    """

    text = resume_text.lower()
    raw_text = resume_text

    total_score = 0
    feedback = []

    # ── 1. SECTIONS (max 10)
    sec_score, missing, sec_fb = check_sections(text)
    total_score += sec_score
    feedback.extend(sec_fb)

    # ── 2. SKILLS (max 10)
    skill_score, skill_fb, found_skills = check_skills(text, skills_list)
    total_score += skill_score
    feedback.extend(skill_fb)

    # ── 3. EXPERIENCE QUALITY (max 30)
    exp_score, exp_fb = check_experience(text)
    total_score += exp_score
    feedback.extend(exp_fb)

    # ── 4. KEYWORDS (max 10)
    key_score, key_fb = check_keywords(text, skills_list)
    total_score += key_score
    feedback.extend(key_fb)

    # ── 5. LENGTH (max 15)
    len_score, len_fb = check_length(text)
    total_score += len_score
    feedback.extend(len_fb)

    # ── 6. FORMATTING (max 10)
    fmt_score, fmt_fb = check_formatting(raw_text)
    total_score += fmt_score
    feedback.extend(fmt_fb)

    # ── 7. CONTACT (max 5)
    contact_score, contact_fb = check_contact(text)
    total_score += contact_score
    feedback.extend(contact_fb)

    # ── 8. EDUCATION (max 5)
    edu_score, edu_fb = check_education(text)
    total_score += edu_score
    feedback.extend(edu_fb)

    # ── 9. SUMMARY (max 5)
    sum_score, sum_fb = check_summary(text)
    total_score += sum_score
    feedback.extend(sum_fb)

    # ── 10. CERTIFICATIONS (max 5)
    cert_score, cert_fb = check_certifications(text)
    total_score += cert_score
    feedback.extend(cert_fb)

    # ── PENALTIES

    # Garbage detection (up to -30)
    garbage_penalty, garbage_fb = detect_garbage(text)
    total_score -= garbage_penalty
    feedback.extend(garbage_fb)

    # ── FINAL NORMALIZATION
    
    final_score = max(min(round(total_score, 1), 100), 0)

    seen = set()
    deduped_feedback = []
    for f in feedback:
        if f not in seen:
            seen.add(f)
            deduped_feedback.append(f)

    result = {
        "score": final_score,
        "feedback": deduped_feedback,
        "found_skills": found_skills,
        "missing_sections": missing
    }

    # add ai_input cleanly
    result["ai_input"] = prepare_ai_input(result)

    return result

def prepare_ai_input(ats_result):
    """
    Prepare clean, structured data for AI suggestions
    """

    return {
        "score": ats_result["score"],
        "skills": ats_result["found_skills"][:10],   
        "issues": ats_result["feedback"][:6],        
        "missing": ats_result["missing_sections"]
    }