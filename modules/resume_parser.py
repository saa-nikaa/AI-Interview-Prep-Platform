import pdfplumber
import spacy
import streamlit as st
from typing import List
from config.roles import SKILL_KEYWORDS

@st.cache_resource(show_spinner=False)
def load_spacy():
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def extract_text_from_pdf(file) -> str:
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                text += t + "\n"
    except Exception:
        return ""
    return text

@st.cache_data(show_spinner=False)
def extract_skills(text: str) -> List[str]:
    nlp = load_spacy()
    text_l = (text or "").lower()
    found = set()
    for kw in SKILL_KEYWORDS:
        if f" {kw} " in f" {text_l} ":
            found.add(kw)
    if nlp:
        doc = nlp(text_l)
        for tok in doc:
            t = tok.text.strip()
            if t in SKILL_KEYWORDS:
                found.add(t)
        for chunk in getattr(doc, "noun_chunks", []):
            c = chunk.text.strip()
            if c in SKILL_KEYWORDS:
                found.add(c)
    return sorted(found)
