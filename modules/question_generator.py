import random
from typing import List
from config.roles import ROLE_SKILLS
from config.prompts import HR_SUFFIX_BY_LEVEL, TECH_TEMPLATES
from modules.question_ai import generate_ai_hr_questions, generate_ai_tech_questions
from modules.dedup import deduplicate_text_list


def simple_hr_questions(role: str, level: str, n: int) -> List[str]:
    base = [
        f"Tell me about a challenge you faced while working as a {role} and how you resolved it.",
        "Describe a time you had to handle conflicting priorities.",
        "How do you approach learning a new technology under a deadline?",
        "Give an example of working with a difficult stakeholder.",
        "What motivates you during long-term projects?",
        "Describe a failure and what you learned.",
        "How do you handle feedback professionally?",
    ]
    suffix = HR_SUFFIX_BY_LEVEL[level]
    qs = [q + suffix for q in base]
    random.shuffle(qs)
    return deduplicate_text_list(qs[:n])


def simple_tech_questions(role: str, level: str, skills: List[str], n: int) -> List[str]:
    sel = skills or ROLE_SKILLS.get(role, []) or ["problem solving"]
    pool = []

    for s in sel:
        for t in TECH_TEMPLATES:
            pool.append(t.format(skill=s))

    random.shuffle(pool)
    tag = {"Beginner": "(Basics)", "Intermediate": "(Depth)", "Advanced": "(Systems/Scale)"}[level]
    final = [f"{q} {tag}" for q in pool[:n]]

    return deduplicate_text_list(final)


# AI versions
def ai_hr_questions(role: str, level: str, n: int) -> List[str]:
    qs = generate_ai_hr_questions(role, level, n)
    # Fallback to simple questions if AI generation returns empty results
    if not qs or len(qs) == 0:
        qs = simple_hr_questions(role, level, n)
    return deduplicate_text_list(qs)


def ai_tech_questions(role: str, level: str, n: int, skills: List[str]) -> List[str]:
    qs = generate_ai_tech_questions(role, level, n, skills)
    # Fallback to simple questions if AI generation returns empty results
    if not qs or len(qs) == 0:
        qs = simple_tech_questions(role, level, skills, n)
    return deduplicate_text_list(qs)
