from typing import List, Dict, Tuple
import streamlit as st
from modules.llm import generate_text
from modules.resume_parser import extract_text_from_pdf
from config.roles import SKILL_KEYWORDS, ROLE_SKILLS


def extract_jd_text(uploaded_file, pasted_text: str) -> str:
    if uploaded_file:
        return extract_text_from_pdf(uploaded_file) or ""
    return pasted_text or ""


def extract_jd_skills(jd_text: str) -> List[str]:
    jd = (jd_text or "").lower()
    found = set()
    for kw in SKILL_KEYWORDS:
        if f" {kw} " in f" {jd} ":
            found.add(kw)
    return sorted(found)


def compare_resume_vs_jd(resume_skills: List[str], jd_skills: List[str]) -> Tuple[List[str], List[str]]:
    matched = sorted([s for s in jd_skills if s in resume_skills])
    missing = sorted([s for s in jd_skills if s not in resume_skills])
    return matched, missing


def jd_summary(jd_text: str) -> Dict:
    """
    Use LLM to pull a clean summary (responsibilities, must-have, nice-to-have).
    """
    if not jd_text.strip():
        return {"summary": "", "must_have": [], "nice_to_have": []}
    prompt = f"""Summarize this job description. Provide:
1) A 3-sentence overview
2) 5 must-have skills/requirements
3) 5 nice-to-have skills

JD:
{jd_text}

Format:
OVERVIEW:
<text>
MUST:
- <item> x5
NICE:
- <item> x5
"""
    txt = generate_text(prompt, max_tokens=700, temperature=0.5)
    overview = ""
    must, nice = [], []
    try:
        if "OVERVIEW:" in txt:
            overview = txt.split("OVERVIEW:")[1].split("MUST:")[0].strip()
        if "MUST:" in txt:
            block = txt.split("MUST:")[1].split("NICE:")[0].strip().splitlines()
            for l in block:
                l = l.strip().lstrip("-• ").strip()
                if l:
                    must.append(l)
        if "NICE:" in txt:
            block = txt.split("NICE:")[1].strip().splitlines()
            for l in block:
                l = l.strip().lstrip("-• ").strip()
                if l:
                    nice.append(l)
    except Exception:
        overview = txt.strip()
    return {"summary": overview, "must_have": must[:5], "nice_to_have": nice[:5]}
