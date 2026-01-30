import time
import streamlit as st
from modules.mcq_generator import generate_mcqs
from modules.mcq_ai_generator import generate_ai_mcqs
from modules.dedup import deduplicate_mcq_list


def init_practice_state():
    ss = st.session_state
    ss.setdefault("practice_active", False)
    ss.setdefault("practice_idx", 0)
    ss.setdefault("practice_deadline", 0)
    ss.setdefault("practice_per_q", 60)
    ss.setdefault("practice_results", [])
    ss.setdefault("practice_total_mcqs", 40)


def render_practice_block(ss, DIFFICULTY_SETTINGS, score_fn, use_ai=False):
    st.subheader("Practice Mode ⏱️ (30–60 MCQs)")

    ss.practice_total_mcqs = st.slider("How many questions?", 30, 60, 40, step=5)
    per_q = st.slider("Seconds per question", 20, 180, DIFFICULTY_SETTINGS[ss.level]["time_limit"])

    colA, colB = st.columns(2)

    with colA:
        if st.button("Start Practice"):
            ss.practice_active = True
            ss.practice_per_q = per_q
            ss.practice_idx = 0
            ss.practice_results = []

            # ✅ AI or fallback
            if use_ai:
                ss.mcqs = generate_ai_mcqs(ss.role, ss.skills, ss.practice_total_mcqs, ss.level)
            else:
                ss.mcqs = generate_mcqs(ss.role, ss.skills, ss.practice_total_mcqs, ss.level)

            # ✅ Dedup practice mode questions
            ss.mcqs = deduplicate_mcq_list(ss.mcqs)

            ss.practice_deadline = time.time() + ss.practice_per_q

    with colB:
        if ss.practice_active and st.button("Stop"):
            ss.practice_active = False

    if not ss.practice_active:
        return

    if ss.practice_idx >= len(ss.mcqs):
        ss.practice_active = False
        total = sum(r["score"] for r in ss.practice_results)
        st.success(f"Total Score: {total}")
        return

    m = ss.mcqs[ss.practice_idx]
    st.markdown(f"### Q{ss.practice_idx+1}: {m['question']}")
    choice = st.radio("Choose one:", m["options"], key=f"practice_{ss.practice_idx}")

    time_left = max(0, int(ss.practice_deadline - time.time()))
    st.progress(1 - (time_left / ss.practice_per_q), text=f"Time left: {time_left}s")

    if st.button("Submit & Next"):
        selected_idx = m["options"].index(choice)
        gained = score_fn(selected_idx, m["answer_index"], ss.level, time_left)

        ss.practice_results.append({
            "selected": selected_idx,
            "correct": m["answer_index"],
            "score": gained,
            "time_left": time_left,
        })

        ss.practice_idx += 1
        ss.practice_deadline = time.time() + ss.practice_per_q
        st.rerun()

    if time_left == 0:
        selected_idx = m["options"].index(choice)
        gained = score_fn(selected_idx, m["answer_index"], ss.level, time_left)
        ss.practice_results.append({
            "selected": selected_idx,
            "correct": m["answer_index"],
            "score": gained,
            "time_left": 0,
        })
        ss.practice_idx += 1
        ss.practice_deadline = time.time() + ss.practice_per_q
        st.rerun()
