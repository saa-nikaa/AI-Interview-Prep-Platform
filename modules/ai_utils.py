import re
from typing import List, Dict

def split_lines(s: str) -> List[str]:
    return [l.strip() for l in s.replace("\r", "\n").split("\n") if l.strip()]

def parse_bulleted(items_text: str) -> List[str]:
    lines = split_lines(items_text)
    out = []
    for l in lines:
        l = re.sub(r"^[\-\•\d\.\)]\s*", "", l)
        out.append(l)
    return out

def parse_ai_mcq_block(txt: str) -> List[Dict]:
    out = []
    blocks = re.split(r"(?m)^\s*[-]{3,}\s*$", txt.strip())
    for b in blocks:
        if not b.strip():
            continue
        q_m = re.search(r"Q\s*:\s*(.+)", b)
        opts = re.findall(r"^[A-D]\)\s*(.+)", b, flags=re.M)
        corr_m = re.search(r"Correct\s*:\s*([A-D])", b)
        exp_m = re.search(r"Explanation\s*:\s*(.+)", b, flags=re.S)
        if q_m and len(opts) >= 4 and corr_m:
            idx = "ABCD".index(corr_m.group(1))
            out.append({
                "question": q_m.group(1).strip(),
                "options": [o.strip() for o in opts[:4]],
                "answer_index": idx,
                "explanation": (exp_m.group(1).strip() if exp_m else ""),
                "difficulty": "",  # optional tag
            })
    return out
