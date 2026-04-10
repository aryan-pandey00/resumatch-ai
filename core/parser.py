import pdfplumber
import re
import streamlit as st

def extract_text_from_pdf(uploaded_file):

    try:
        full_text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = _extract_page_smart(page)
                full_text += page_text + "\n"
        merged = _merge_continuation_lines(full_text)
        return merged.strip()
    except Exception as e:
        st.error(f"Could not read PDF. Please make sure it's a valid resume file.")
        print(f"Error reading PDF: {e}")
        return ""


def _extract_page_smart(page):
    words = page.extract_words(x_tolerance=3, y_tolerance=3)
    if not words:
        return ""
    if _is_two_column(words, page.width):
        return _extract_two_column(words, page.width)
    else:
        text = page.extract_text(x_tolerance=2, y_tolerance=3)
        return text or ""


def _is_two_column(words, page_width):
    mid_start = page_width * 0.20
    mid_end = page_width * 0.65
    bucket_count = 20
    bucket_size = (mid_end - mid_start) / bucket_count
    buckets = [0] * bucket_count

    for w in words:
        x_center = (w["x0"] + w["x1"]) / 2
        if mid_start <= x_center < mid_end:
            idx = min(int((x_center - mid_start) / bucket_size), bucket_count - 1)
            buckets[idx] += 1

    if not any(buckets):
        return False
    max_density = max(buckets)
    if max_density == 0:
        return False
    for i in range(3, bucket_count - 3):
        if buckets[i] < max_density * 0.15:
            return True
    return False


def _find_column_boundary(words, page_width):
    mid_start = page_width * 0.20
    mid_end = page_width * 0.65
    resolution = 2
    num_buckets = int((mid_end - mid_start) / resolution)
    buckets = [0] * num_buckets

    for w in words:
        x_center = (w["x0"] + w["x1"]) / 2
        if mid_start <= x_center < mid_end:
            idx = min(int((x_center - mid_start) / resolution), num_buckets - 1)
            buckets[idx] += 1

    min_val  = min(buckets)
    min_idxs = [i for i, v in enumerate(buckets) if v == min_val]
    gap_idx  = min_idxs[len(min_idxs) // 2]
    return mid_start + (gap_idx * resolution) + resolution / 2


def _extract_two_column(words, page_width):
    boundary = _find_column_boundary(words, page_width)
    left_words = [w for w in words if w["x1"] <= boundary + 5]
    right_words = [w for w in words if w["x0"] >= boundary - 5]
    left_text  = _words_to_text(left_words)
    right_text = _words_to_text(right_words)
    return left_text + "\n\n" + right_text


def _words_to_text(words):
    if not words:
        return ""
    words_sorted = sorted(words, key=lambda w: (round(w["top"] / 4) * 4, w["x0"]))
    lines, cur_line, cur_top = [], [], None
    line_tol = 4

    for w in words_sorted:
        if cur_top is None or abs(w["top"] - cur_top) <= line_tol:
            cur_line.append(w["text"])
            cur_top = w["top"]
        else:
            lines.append(" ".join(cur_line))
            cur_line = [w["text"]]
            cur_top = w["top"]
    if cur_line:
        lines.append(" ".join(cur_line))
    return "\n".join(lines)


def _merge_continuation_lines(text):
   
    SECTION_HEADERS = re.compile(
        r"^(skills|experience|education|projects|certifications?|summary|"
        r"objective|profile|awards?|achievements?|contact|references?|"
        r"languages?|interests?|hobbies|declaration|work experience|"
        r"professional experience|technical skills|core skills)[\s:]*$",
        re.IGNORECASE
    )

    BULLET_START = re.compile(
        r"^[\•\-\*\►\▶\○\●\□\■\✓\✔\d+\.\)]\s+"
    )

    lines  = text.split("\n")
    merged = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Always keep blank lines and section headers as-is
        if not stripped or SECTION_HEADERS.match(stripped):
            merged.append(line)
            i += 1
            continue

        # Try to merge with following continuation lines
        combined = stripped
        while i + 1 < len(lines):
            next_line = lines[i + 1].strip()

            if not next_line:
                break
            if SECTION_HEADERS.match(next_line):
                break
            if BULLET_START.match(next_line):
                break
            # New bullet: starts with capital after a name-like pattern (job title)
            if re.match(r"^[A-Z][a-z]", next_line) and combined.endswith((".", "!", "?")):
                break
            # Continuation: starts lowercase OR starts mid-word (hyphenated wrap)
            if next_line[0].islower() or combined.endswith("-"):
                if combined.endswith("-"):
                    combined = combined[:-1] + next_line  # rejoin hyphen-split word
                else:
                    combined = combined + " " + next_line
                i += 1
            else:
                break

        merged.append(combined)
        i += 1

    return "\n".join(merged)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "resume.pdf"
    print(f"Extracting: {path}\n")
    result = extract_text_from_pdf(path)
    print(result)
    print(f"\n--- Total chars: {len(result)} ---")