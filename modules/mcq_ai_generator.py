from typing import List, Dict
from modules.llm import generate_text
from modules.ai_utils import parse_ai_mcq_block
from modules.mcq_generator import generate_mcqs as fallback_mcqs
from modules.dedup import deduplicate_mcq_list

TEMPLATE = """
Generate {n} MCQs for the topic: {skill}.
Difficulty mix: 30% Easy, 50% Intermediate, 20% Advanced.
Format:

Q: <question>
A) <option>
B) <option>
C) <option>
D) <option>
Correct: <A|B|C|D>
Explanation: <why>

Separate questions using lines of ---.
"""


def generate_ai_mcqs(role: str, skills: List[str], n: int, level: str) -> List[Dict]:
    skill = (skills[0] if skills else None) or "python"

    txt = generate_text(TEMPLATE.format(n=n, skill=skill), max_tokens=2400, temperature=0.92)
    mcqs = parse_ai_mcq_block(txt)

    # ✅ Deduplicate AI output
    mcqs = deduplicate_mcq_list(mcqs)

    # ✅ Not enough? → Fill using fallback (also deduped)
    if len(mcqs) < n:
        extra = fallback_mcqs(role, skills, n - len(mcqs), level)
        extra = deduplicate_mcq_list(extra)
        combined = deduplicate_mcq_list(mcqs + extra)
        return combined[:n]

    return mcqs[:n]
