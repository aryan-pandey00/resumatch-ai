import random

# -------- HELPER FUNCTION --------
def format_list_naturally(items):
    if not items:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return ", ".join(items[:-1]) + f", and {items[-1]}"


# -------- SUMMARY FALLBACK --------
def generate_summary_fallback(ai_input):

    skills = ai_input.get("skills", [])
    projects = ai_input.get("projects", [])

    # -------- SKILL SELECTION (PRIORITY + VARIATION) --------
    if len(skills) <= 4:
        selected_skills = skills
    else:
        base = skills[:2]  # priority skills
        extra = skills[2:]
        random.shuffle(extra)
        selected_skills = base + extra[:2]

    skill_text = format_list_naturally(selected_skills)

    # -------- PROJECT TITLES --------
    project_titles = [p["title"] for p in projects if p.get("title")]

    if len(project_titles) <= 2:
        selected_projects = project_titles
    else:
        random.shuffle(project_titles)
        selected_projects = project_titles[:2]

    project_text = format_list_naturally(selected_projects)

    # -------- VARIATIONS --------
    openings = [
        "Motivated and detail-oriented developer",
        "Enthusiastic and results-driven individual",
        "Passionate developer with strong problem-solving abilities",
        "Dedicated and adaptable individual with a strong technical foundation"
    ]

    middles = [
        f"with hands-on experience in {skill_text}",
        f"skilled in {skill_text} with practical exposure to real-world applications",
        f"experienced in working with {skill_text} across various projects"
    ]

    endings = [
        f"and has built projects such as {project_text}, demonstrating strong analytical and development skills.",
        f"with experience developing projects like {project_text}, showcasing the ability to solve real-world problems effectively.",
        f"and has applied these skills in projects like {project_text}, reflecting a strong interest in building scalable solutions."
    ]

    summary = f"{random.choice(openings)} {random.choice(middles)}, {random.choice(endings)}"

    return summary


# -------- PROJECT FALLBACK --------

def generate_project_fallback(ai_input):
    project_outputs = []

    # MULTIPLE FIRST-LINE PATTERNS (MAJOR FIX)
    def generate_line1(title, tech):
        templates = [
            f"Developed {title} using {tech} to solve real-world problems and improve system efficiency.",
            f"Built a {title} leveraging {tech} to enhance performance and deliver practical solutions.",
            f"Designed and implemented {title} with {tech}, focusing on scalability and real-world application.",
            f"Engineered a solution for {title} using {tech}, improving system functionality and user experience.",
            f"Created {title} utilizing {tech} to address key challenges and optimize overall system behavior."
        ]
        return random.choice(templates)

    second_lines_pool = [
        "Applied core concepts to optimize performance and ensure scalability of the solution.",
        "Focused on improving efficiency and maintaining reliability across different use cases.",
        "Utilized structured approaches to handle data processing and system design effectively.",
        "Integrated key functionalities to enhance usability and overall system behavior.",
        "Implemented efficient workflows to streamline processing and improve system responsiveness."
    ]

    third_lines_pool = [
        "Strengthened problem-solving abilities through practical implementation and testing.",
        "Gained hands-on experience in real-world application development and debugging.",
        "Improved analytical thinking through iterative development and refinement.",
        "Enhanced technical expertise by working on practical challenges and optimizing solutions.",
        "Developed a deeper understanding of system design and real-world constraints."
    ]

    projects = ai_input.get("projects", [])

    # SHUFFLE FOR UNIQUE ASSIGNMENT
    random.shuffle(second_lines_pool)
    random.shuffle(third_lines_pool)

    for i, p in enumerate(projects):
        title = p.get("title", "a project")
        tech = p.get("tech", "relevant technologies")

        # Line 1 (dynamic structure)
        line1 = generate_line1(title, tech)

        # Line 2 (unique)
        line2 = second_lines_pool[i % len(second_lines_pool)]

        # Line 3 (unique)
        line3 = third_lines_pool[i % len(third_lines_pool)]

        full_desc = f"{line1}\n{line2}\n{line3}"

        project_outputs.append(full_desc)

    return project_outputs
def generate_fallback(ai_input):
    return {
        "summary": generate_summary_fallback(ai_input),
        "projects": generate_project_fallback(ai_input)
    }