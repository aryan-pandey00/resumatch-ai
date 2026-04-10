import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# SKILL SYNONYMS  – lightweight, no extra deps

SKILL_SYNONYMS = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8s": "kubernetes",
    "tf": "tensorflow",
    "node": "node js",
    "nodejs": "node js",
    "reactjs": "react",
    "vuejs": "vue",
    "postgresql": "postgres",
    "mongo": "mongodb",
    "aws": "amazon web services",
    "gcp": "google cloud",
    "ci/cd": "cicd",
    "rest api": "rest",
    "restful": "rest",
    "oop": "object oriented programming",
    "dsa": "data structures",
}

# SECTION WEIGHTS  – skills in EXPERIENCE / PROJECTS

SECTION_BOOST_PATTERNS = re.compile(
    r"(experience|projects?|work|internship|employment)", re.IGNORECASE
)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[-_/]', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _expand_synonyms(text):
  
    for abbr, full in SKILL_SYNONYMS.items():
        text = re.sub(rf'\b{re.escape(abbr)}\b', full, text)
    return text


def _extract_section_text(text, section_pattern=SECTION_BOOST_PATTERNS):
    
    lines = text.split('\n')
    in_section = False
    section_lines = []
    for line in lines:
        if section_pattern.search(line):
            in_section = True
        elif re.match(r'^[A-Z][A-Z\s]{3,}$', line.strip()):
            
            in_section = False
        if in_section:
            section_lines.append(line)
    return ' '.join(section_lines)

# SKILL EXTRACTION  

def extract_skills(text, skills_list):
    
    text = _expand_synonyms(text)
    found_skills = []
    for skill in skills_list:
        skill_lower = skill.lower()
        skill_expanded = _expand_synonyms(skill_lower)
       
        pattern = r'\b' + re.escape(skill_expanded) + r'\b'
        if re.search(pattern, text):
            found_skills.append(skill_lower)
    return list(set(found_skills))


# SECTION-BOOSTED SKILL SCORE

def _section_boosted_skill_score(resume_clean, jd_skills, matched_skills):
    
    if not jd_skills:
        return 0.0

    section_text = _extract_section_text(resume_clean)
    section_text = _expand_synonyms(section_text)

    score = 0.0
    for skill in jd_skills:
        if skill in matched_skills:
            skill_expanded = _expand_synonyms(skill)
            pattern = r'\b' + re.escape(skill_expanded) + r'\b'
            # Boost if found in key section, normal credit otherwise
            if re.search(pattern, section_text):
                score += 1.2
            else:
                score += 1.0

    raw = (score / len(jd_skills)) * 100
    return min(raw, 100.0)

# KEYWORD DENSITY BONUS 

def _keyword_density_bonus(resume_clean, jd_clean):
    """
    Count how many JD content-words appear in the resume.
    Returns a small 0–10 bonus to reward general JD language alignment
    beyond skills (e.g. domain words, role titles, tools not in skills.json).
    Uses only stdlib – no extra packages.
    """
    STOPWORDS = {
        'the','and','for','with','our','you','are','that','this','have',
        'will','from','your','not','but','they','all','can','its','been',
        'has','was','were','also','into','their','more','than','when',
        'which','who','what','there','out','one','we','be','to','of',
        'a','in','is','it','as','at','by','an','or','on','do','if',
        'up','so','no','he','she','me','my','us','am','go','get','use'
    }
    jd_words = set(w for w in jd_clean.split() if len(w) > 3 and w not in STOPWORDS)
    if not jd_words:
        return 0.0
    resume_words = set(resume_clean.split())
    overlap = len(jd_words & resume_words) / len(jd_words)
    return overlap * 10  


# MAIN SCORING FUNCTION 

def calculate_match_score(resume_text, jd_text, skills_list):
    resume_clean = clean_text(_expand_synonyms(resume_text))
    jd_clean     = clean_text(_expand_synonyms(jd_text))

    # ── Skill extraction ──────────────────────
    resume_skills  = extract_skills(resume_clean, skills_list)
    jd_skills      = extract_skills(jd_clean, skills_list)
    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))

    # ── Skill score (section-boosted) ─────────
    skill_score = _section_boosted_skill_score(resume_clean, jd_skills, matched_skills)

    # ── TF-IDF semantic similarity ────────────
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),     
        sublinear_tf=True,       
        min_df=1,
        stop_words='english'
    )
    tfidf      = vectorizer.fit_transform([resume_clean, jd_clean])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100

    # ── Keyword density bonus ──────
    density_bonus = _keyword_density_bonus(resume_clean, jd_clean)

    # ── Final weighted score ──────────────────

    final_score = (0.65 * skill_score) + (0.25 * similarity) + density_bonus
    final_score = min(final_score, 100.0)

    return round(final_score, 2), matched_skills, missing_skills, resume_skills, jd_skills