import random
from typing import List, Dict
from config.roles import ROLE_SKILLS
from modules.dedup import deduplicate_mcq_list  # ✅ correct import only


QUESTION_BANK = {
    "python": {
        "easy": [
            ("Which keyword defines a function?", ["func", "def", "define", "lambda"], 1, "Use 'def' to define."),
            ("What is len([1,2,3])?", ["2", "3", "1", "Error"], 1, "List has 3 items."),
            ("How to write a comment?", ["# text", "// text", "/* */", "' text"], 0, "# is correct."),
        ],
        "intermediate": [
            ("What does *args allow?", ["Keywords", "Var positional", "Async", "Typing"], 1, "*args = variable positional."),
            ("What does enumerate() do?", ["Counts", "Index+item", "Sorts", "Maps"], 1, "Provides index + item."),
        ],
        "advanced": [
            ("Dict lookup complexity?", ["O(n)", "O(logn)", "O(1)", "O(nlogn)"], 2, "Hash table lookup = O(1)."),
            ("What is a closure?", ["Fn with retained scope", "Class", "Decorator", "Loop"], 0, "Inner fn retains scope."),
        ],
    }
}

QUESTION_BANK["sql"] = {
    "easy": [
        ("What does SELECT do?", ["Retrieve", "Delete", "Update", "Drop"], 0, "SELECT retrieves."),
    ],
    "intermediate": [
        ("GROUP BY groups?", ["Rows", "Columns", "NULLs", "Tables"], 0, "Groups rows."),
    ],
    "advanced": [
        ("Correlated subquery?", ["Independent", "Depends on outer", "Debug only", "Index"], 1, "Depends on outer query."),
    ],
}

QUESTION_BANK["default"] = QUESTION_BANK["python"]


def get_bank(skill: str):
    return QUESTION_BANK.get(skill.lower(), QUESTION_BANK["default"])


def pick_unique(bank, level_key, count):
    out = []
    used = set()
    items = bank[level_key]

    for _ in range(count * 2):  # oversample to reduce duplicates
        q, opts, idx, exp = random.choice(items)
        if q not in used:
            out.append({
                "question": q,
                "options": list(opts),
                "answer_index": idx,
                "explanation": exp,
                "difficulty": level_key,
            })
            used.add(q)
        if len(out) >= count:
            break

    return out


def generate_mcqs(role: str, skills: List[str], n: int, level: str) -> List[Dict]:
    skill = (skills[0] if skills else None) or ROLE_SKILLS.get(role, ["python"])[0]
    bank = get_bank(skill)

    n_easy = max(1, int(n * 0.30))
    n_mid = max(1, int(n * 0.50))
    n_adv = max(1, n - n_easy - n_mid)

    mcqs = (
        pick_unique(bank, "easy", n_easy)
        + pick_unique(bank, "intermediate", n_mid)
        + pick_unique(bank, "advanced", n_adv)
    )

    mcqs = deduplicate_mcq_list(mcqs)
    random.shuffle(mcqs)

    return mcqs[:n]
