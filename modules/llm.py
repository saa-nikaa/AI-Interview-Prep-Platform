import streamlit as st

USE_LLM = False
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch  # noqa: F401
    USE_LLM = True
except Exception:
    USE_LLM = False

@st.cache_resource(show_spinner=False)
def load_llm():
    if not USE_LLM:
        return None, None
    try:
        model_name = "google/flan-t5-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        return tokenizer, model
    except Exception:
        return None, None


def generate_text(prompt: str, max_tokens: int = 512, temperature: float = 0.9) -> str:
    tok_mod = load_llm()
    if not tok_mod or tok_mod[0] is None:
        return ""
    tokenizer, model = tok_mod
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model.generate(
        **inputs,
        max_length=max_tokens,
        do_sample=True,
        top_p=0.95,
        top_k=40,
        temperature=temperature,
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)
