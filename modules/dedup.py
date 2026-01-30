def deduplicate_text_list(items):
    """
    Deduplicate a list of strings (HR questions, Tech questions).
    Keeps the first occurrence of each question.
    """
    seen = set()
    unique = []
    for it in items:
        if not isinstance(it, str):
            continue
        q = it.strip().lower()
        if q not in seen:
            unique.append(it)
            seen.add(q)
    return unique


def deduplicate_mcq_list(mcqs):
    """
    Deduplicate MCQ dictionaries based on the 'question' key.
    """
    seen = set()
    unique = []
    for m in mcqs:
        if not isinstance(m, dict) or "question" not in m:
            continue
        q = m["question"].strip().lower()
        if q not in seen:
            unique.append(m)
            seen.add(q)
    return unique
