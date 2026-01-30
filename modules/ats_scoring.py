from typing import List, Tuple
from modules.llm import generate_text
from config.roles import ROLE_SKILLS

def get_ats_score(extracted: List[str], role: str) -> Tuple[int, List[str], List[str]]:
    req = ROLE_SKILLS.get(role, [])
    if not req:
        return 0, [], []
    matched = [s for s in req if s in extracted]
    missing = [s for s in req if s not in extracted]
    score = int((len(matched) / max(1, len(req))) * 100)
    return score, matched, missing

def resume_suggestions(extracted: List[str], missing: List[str], role: str) -> List[str]:
    prompt = (
        "You are an ATS expert. Based on extracted skills: "
        + ", ".join(extracted)
        + " and missing skills: "
        + ", ".join(missing)
        + f" create concise bullet-point resume improvements for role {role}. "
          "Keep bullets short; focus on measurable achievements, relevant tools, and keywords."
    )
    raw = generate_text(prompt, max_tokens=400, temperature=0.8)
    if raw:
        lines = [l.strip("- •\n ") for l in raw.split("\n") if l.strip()]
        return lines[:10]
    tips = []
    if missing:
        tips.append(f"Add concrete mentions of: {', '.join(missing)} (projects, tools, achievements).")
    tips += [
        "Quantify outcomes (e.g., reduced latency 30%, improved accuracy 4%).",
        "Use action verbs (designed, optimized, automated, deployed).",
        "Mirror job description keywords in skills and experience sections.",
        "Place most relevant projects above older experience.",
        "Include links: GitHub, portfolio, Kaggle (if applicable).",
    ]
    return tips
