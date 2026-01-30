from typing import List
from modules.llm import generate_text
from modules.ai_utils import parse_bulleted

HR_PROMPT = """Generate {n} {level} HR interview questions for a {role}.
Focus on behavioral and situational questions.
Return as a bullet list with one question per line.
"""

TECH_PROMPT = """Generate {n} {level} technical interview questions for a {role}.
Consider the candidate's skills: {skills}.
Include system design or practical troubleshooting when appropriate.
Return as a bullet list with one question per line.
"""

ANS_PROMPT = """Provide a high-quality {level} interview answer for a {role}.
Question: {q}
Answer holistically with context, approach, metrics, tradeoffs, and conclusion.
"""

def generate_ai_hr_questions(role: str, level: str, n: int) -> List[str]:
    txt = generate_text(HR_PROMPT.format(n=n, role=role, level=level), max_tokens=800, temperature=0.8)
    qs = parse_bulleted(txt)
    return qs[:n] if len(qs) >= n else qs

def generate_ai_tech_questions(role: str, level: str, n: int, skills: List[str]) -> List[str]:
    skills_txt = ", ".join(skills) if skills else "general fundamentals"
    txt = generate_text(TECH_PROMPT.format(n=n, role=role, level=level, skills=skills_txt), max_tokens=900, temperature=0.85)
    qs = parse_bulleted(txt)
    return qs[:n] if len(qs) >= n else qs

def generate_ai_answer(question: str, role: str, level: str) -> str:
    return generate_text(ANS_PROMPT.format(role=role, level=level, q=question), max_tokens=600, temperature=0.7)
