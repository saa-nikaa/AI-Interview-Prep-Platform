from modules.question_ai import generate_ai_answer

def generate_answer(question: str, role: str, level: str) -> str:
    ans = (generate_ai_answer(question, role, level) or "").strip()
    if ans:
        return ans
    return (
        f"Answer outline: 1) Context 2) Approach 3) Key decisions 4) Result (metrics) 5) Learnings. "
        f"Tailor to {role}, keep it {level.lower()} depth, quantify impact."
    )
