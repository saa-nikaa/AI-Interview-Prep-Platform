from io import BytesIO
from typing import List, Dict, Tuple, Optional
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def export_pdf_bytes(
    questions: List[str],
    answers: List[str],
    mcqs: List[Dict],
    ats: Tuple[int, List[str], List[str]],
    suggestions: List[str],
    analytics_rows: Optional[List[Dict]] = None,
    practice_results: Optional[List[Dict]] = None,
    per_q_time: Optional[int] = None,
) -> bytes:
    styles = getSampleStyleSheet()
    story = []

    def h2(text):
        story.append(Paragraph(f"<b>{text}</b>", styles["Heading2"]))
        story.append(Spacer(1, 10))

    def p(text):
        story.append(Paragraph(text, styles["BodyText"]))
        story.append(Spacer(1, 6))

    h2("AI Interview Report")

    if questions:
        h2("Interview Questions & Answers")
        for q, a in zip(questions, answers or [""] * len(questions)):
            p(f"<b>Q:</b> {q}")
            p(f"<b>A:</b> {a}")

    if mcqs:
        h2("MCQs (with answers)")
        for i, m in enumerate(mcqs, 1):
            p(f"{i}. {m['question']}")
            for j, opt in enumerate(m["options"]):
                p(f"&nbsp;&nbsp;{chr(65+j)}. {opt}")
            p(f"Correct: {chr(65+m['answer_index'])}. {m.get('explanation','')}")
            if m.get("difficulty"):
                p(f"Difficulty: {m['difficulty']}")

    if ats:
        score, matched, missing = ats
        h2("ATS Score")
        p(f"Score: {score}%")
        p(f"Matched Skills: {', '.join(matched) if matched else '-'}")
        p(f"Missing Skills: {', '.join(missing) if missing else '-'}")

    if suggestions:
        h2("Resume Suggestions")
        for s in suggestions:
            p(f"• {s}")

    if analytics_rows:
        h2("MCQ Analytics (ad-hoc)")
        for r in analytics_rows:
            p(f"Q{r.get('q#','?')}: Selected={r.get('selected')}, Correct={r.get('correct')}, "
              f"Correct?={'Yes' if r.get('is_correct') else 'No'}, Score={r.get('score')}")

    if practice_results:
        h2("Practice Session Results")
        p(f"Per-question time: {per_q_time or '-'}s")
        for i, r in enumerate(practice_results, 1):
            p(f"Q{i}: Selected={r.get('selected')}, CorrectIndex={r.get('correct')}, "
              f"Score={r.get('score')}, Time Left={r.get('time_left')}s")

    buffer = BytesIO()
    SimpleDocTemplate(buffer, pagesize=A4).build(story)
    return buffer.getvalue()
