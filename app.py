import time
import streamlit as st
import pandas as pd
from typing import List

# --- CONFIG ---
from config.roles import ROLE_SKILLS, DIFFICULTY_SETTINGS

# --- Resume + ATS ---
from modules.resume_parser import extract_text_from_pdf, extract_skills, load_spacy
from modules.ats_scoring import get_ats_score, resume_suggestions

# --- Question Generators ---
from modules.question_generator import (
    simple_hr_questions, simple_tech_questions,
    ai_hr_questions, ai_tech_questions
)
from modules.answers import generate_answer

# --- MCQs ---
from modules.mcq_generator import generate_mcqs
from modules.mcq_ai_generator import generate_ai_mcqs
from modules.scoring import MCQ_DIFFICULTY_WEIGHTS

# --- Practice Mode ---
from modules.timer import init_practice_state, render_practice_block

# --- Export ---
from modules.pdf_export import export_pdf_bytes

# --- Dedup ---
from modules.dedup import deduplicate_text_list, deduplicate_mcq_list

# --- Job Description Analyzer ---
from modules.jd_analyzer import (
    extract_jd_text, extract_jd_skills,
    compare_resume_vs_jd, jd_summary
)

# --- Voice Interview ---
from modules.voice_interview import render_voice_interview


# ✅ Load spaCy once
_ = load_spacy()


# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
def init_state():
    ss = st.session_state

    ss.setdefault("role", list(ROLE_SKILLS.keys())[0])
    ss.setdefault("level", "Beginner")

    ss.setdefault("resume_text", "")
    ss.setdefault("skills", [])
    ss.setdefault("ats", (0, [], []))
    ss.setdefault("suggestions", [])

    ss.setdefault("hr_questions", [])
    ss.setdefault("tech_questions", [])
    ss.setdefault("answers", [])

    ss.setdefault("mcqs", [])
    ss.setdefault("mcq_score", 0)
    ss.setdefault("use_ai", True)

    ss.setdefault("analytics", {"mcq_rows": []})

    # Voice interview
    ss.setdefault("vi_question", "")
    ss.setdefault("vi_last_feedback", {})
    ss.setdefault("vi_transcript", "")

    # Practice mode
    init_practice_state()


def difficulty_badge(d: str) -> str:
    d = (d or "").lower()
    if d.startswith("easy"):
        return "🟢 Easy"
    if d.startswith("inter"):
        return "🟡 Intermediate"
    if d.startswith("adv"):
        return "🔥 Advanced"
    return "⬜ Unknown"


# -----------------------------------------------------------------------------
# MAIN APPLICATION
# -----------------------------------------------------------------------------
def main():

    st.set_page_config(page_title="AI Interview + ATS Suite (AI++)", page_icon="🧠", layout="wide")
    init_state()
    ss = st.session_state

    # ===================== SIDEBAR =========================
    with st.sidebar:
        st.header("Settings ⚙️")

        ss.role = st.selectbox("Role", list(ROLE_SKILLS.keys()))
        ss.level = st.selectbox("Difficulty", list(DIFFICULTY_SETTINGS.keys()))
        ss.use_ai = st.toggle("Use AI generation (HR/Tech/MCQ)", value=ss.use_ai)

        st.markdown("---")

        uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        if uploaded:
            ss.resume_text = extract_text_from_pdf(uploaded)
            ss.skills = extract_skills(ss.resume_text)
            ss.ats = get_ats_score(ss.skills, ss.role)
            st.success(f"Extracted {len(ss.skills)} skills.")

        if ss.skills:
            st.caption("Detected:")
            st.write(", ".join(ss.skills))

    # ===================== TITLE =========================
    st.title("🧠 AI Interview Helper")

    # Tabs
    tab1, tab2, tab3, tab4, tabJD, tabVoice, tab5, tab6 = st.tabs([
        "ATS & Resume",
        "HR & Technical",
        "MCQ Practice",
        "Practice Mode (Timed)",
        "JD Analyzer",
        "Voice Interview",
        "Analytics",
        "Export"
    ])

    # =======================================================================
    # ✅ TAB 1 — ATS + Resume Suggestions
    # =======================================================================
    with tab1:
        st.subheader("✅ ATS Skill Matcher")

        score, matched, missing = ss.ats

        c1, c2, c3 = st.columns(3)
        c1.metric("ATS Score", f"{score}%")
        c2.metric("Matched Skills", len(matched))
        c3.metric("Missing Skills", len(missing))

        st.write("✅ **Matched:**", matched or "-")
        st.write("❌ **Missing:**", missing or "-")

        if st.button("Generate Resume Suggestions"):
            ss.suggestions = resume_suggestions(ss.skills, missing, ss.role)

        if ss.suggestions:
            st.success("\n".join([f"• {s}" for s in ss.suggestions]))

    # =======================================================================
    # ✅ TAB 2 — HR + Technical Questions
    # =======================================================================
    with tab2:
        st.subheader("🎤 HR & Technical Question Generator")

        n_q = st.slider("How many questions?", 3, 20, 8)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate HR Questions"):
                qs = ai_hr_questions(ss.role, ss.level, n_q) if ss.use_ai else simple_hr_questions(ss.role, ss.level, n_q)
                ss.hr_questions = deduplicate_text_list(qs)

        with col2:
            if st.button("Generate Technical Questions"):
                qs = ai_tech_questions(ss.role, ss.level, n_q, ss.skills) if ss.use_ai else simple_tech_questions(ss.role, ss.level, ss.skills, n_q)
                ss.tech_questions = deduplicate_text_list(qs)

        # Display HR
        if ss.hr_questions:
            st.markdown("### 👥 HR Questions")
            for i, q in enumerate(ss.hr_questions, start=1):
                with st.expander(f"{i}. {q}"):
                    if st.button(f"Answer HR {i}"):
                        ans = generate_answer(q, ss.role, ss.level)
                        if len(ss.answers) < i:
                            ss.answers += [""] * (i - len(ss.answers))
                        ss.answers[i - 1] = ans
                    st.write(ss.answers[i - 1] if len(ss.answers) >= i else "")

        # Display Technical
        if ss.tech_questions:
            st.markdown("### 💻 Technical Questions")
            base = len(ss.hr_questions)
            for i, q in enumerate(ss.tech_questions, start=1):
                idx = base + i
                with st.expander(f"{i}. {q}"):
                    if st.button(f"Answer Tech {i}"):
                        ans = generate_answer(q, ss.role, ss.level)
                        if len(ss.answers) < idx:
                            ss.answers += [""] * (idx - len(ss.answers))
                        ss.answers[idx - 1] = ans
                    st.write(ss.answers[idx - 1] if len(ss.answers) >= idx else "")

    # =======================================================================
    # ✅ TAB 3 — MCQ Generator
    # =======================================================================
    with tab3:
        st.subheader("📝 MCQ Generator + Checking")
        n_mcq = st.slider("MCQs count", 5, 60, 12)

        if st.button("Generate MCQs"):
            ss.mcqs = generate_ai_mcqs(ss.role, ss.skills, n_mcq, ss.level) if ss.use_ai else generate_mcqs(ss.role, ss.skills, n_mcq, ss.level)
            ss.mcqs = deduplicate_mcq_list(ss.mcqs)
            ss.mcq_score = 0
            ss.analytics["mcq_rows"] = []

        for i, m in enumerate(ss.mcqs):
            st.markdown(f"### Q{i+1}: {m['question']}")
            st.caption(difficulty_badge(m.get("difficulty", "")))

            choice = st.radio("Choose:", m["options"], key=f"mcq_{i}")
            correct = m["options"][m["answer_index"]]

            if st.button(f"Check {i+1}"):
                is_correct = (choice == correct)
                points = 5 if is_correct else -1

                if is_correct:
                    st.success(f"✅ Correct! {m['explanation']}")
                    ss.mcq_score += points
                else:
                    st.error(f"❌ Wrong. Correct: {correct}")

                ss.analytics["mcq_rows"].append({
                    "q#": i + 1, "difficulty": m.get("difficulty", ""),
                    "selected": choice, "correct": correct,
                    "is_correct": is_correct, "score": points
                })

        if ss.mcqs:
            st.info(f"Score: {ss.mcq_score} / {len(ss.mcqs) * 5}")

    # =======================================================================
    # ✅ TAB 4 — Timed Practice Mode
    # =======================================================================
    with tab4:
        from modules.scoring import score_mcq
        render_practice_block(ss, DIFFICULTY_SETTINGS, score_mcq, use_ai=ss.use_ai)

    # =======================================================================
    # ✅ TAB 5 — JD Analyzer
    # =======================================================================
    with tabJD:
        st.subheader("📄 Job Description Analyzer")

        col1, col2 = st.columns(2)

        with col1:
            jd_file = st.file_uploader("Upload JD (PDF)", type=["pdf"])
            jd_text_manual = st.text_area("Paste JD text here", height=200)

            if st.button("Analyze JD"):
                jd_text = extract_jd_text(jd_file, jd_text_manual)
                if not jd_text.strip():
                    st.warning("No JD content found.")
                else:
                    ss.jd_text = jd_text
                    ss.jd_summary = jd_summary(jd_text)
                    ss.jd_skills = extract_jd_skills(jd_text)

        with col2:
            if ss.get("jd_summary"):
                st.write("### JD Summary")
                st.info(ss.jd_summary["summary"])
                st.write("**Must-have:**", ss.jd_summary["must_have"])
                st.write("**Nice-to-have:**", ss.jd_summary["nice_to_have"])

        if ss.get("jd_skills") and ss.skills:
            matched, missing = compare_resume_vs_jd(ss.skills, ss.jd_skills)
            c1, c2 = st.columns(2)
            c1.metric("Matched Skills", len(matched))
            c2.metric("Missing Skills", len(missing))
            st.write("✅ Matched:", matched or "-")
            st.write("❌ Missing:", missing or "-")


    # =======================================================================
    # ✅ TAB Voice — Voice Interview
    # =======================================================================
    with tabVoice:
        render_voice_interview(ss)

    # =======================================================================
    # ✅ TAB 8 — Analytics
    # =======================================================================
    with tab5:
        st.subheader("📊 Performance Analytics")
        rows = ss.analytics.get("mcq_rows", [])
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No analytics yet.")

    # =======================================================================
    # ✅ TAB 9 — Export
    # =======================================================================
    with tab6:
        st.subheader("📄 Export Full Report")

        if st.button("Generate PDF"):
            all_q = deduplicate_text_list(ss.hr_questions + ss.tech_questions)
            ss.mcqs = deduplicate_mcq_list(ss.mcqs)

            pdf_bytes = export_pdf_bytes(
                all_q, ss.answers, ss.mcqs, ss.ats,
                ss.suggestions, ss.analytics["mcq_rows"],
                practice_results=ss.practice_results,
                per_q_time=ss.practice_per_q
            )

            ss.pdf_bytes = pdf_bytes

        if ss.get("pdf_bytes"):
            st.download_button(
                "Download Report",
                ss.pdf_bytes,
                "AI_Interview_Report.pdf",
                "application/pdf"
            )


if __name__ == "__main__":
    main()
