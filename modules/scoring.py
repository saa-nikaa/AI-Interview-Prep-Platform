MCQ_DIFFICULTY_WEIGHTS = {"Beginner": 1.0, "Intermediate": 1.3, "Advanced": 1.6}

def score_mcq(selected: int, correct: int, level: str, time_left: int) -> int:
    if selected is None or selected < 0:
        return -1
    base = 5 if selected == correct else -1
    bonus = int((time_left or 0) / 10)
    mult = MCQ_DIFFICULTY_WEIGHTS.get(level, 1.0)
    return int(base * mult + (bonus if selected == correct else 0))
