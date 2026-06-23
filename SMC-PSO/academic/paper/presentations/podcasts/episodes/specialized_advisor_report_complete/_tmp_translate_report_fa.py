import re
import time
from pathlib import Path
from deep_translator import GoogleTranslator

SRC = Path(r"D:\Projects\main\academic\paper\presentations\podcasts\episodes\specialized_advisor_report_complete\advisor_progress_report.tex")
DST = Path(r"D:\Projects\main\academic\paper\presentations\podcasts\episodes\specialized_advisor_report_complete\advisor_progress_report_fa.tex")

translator = GoogleTranslator(source="en", target="fa")

TOKEN_PREFIX = "@@TR"
TOKEN_SUFFIX = "@@"
PH_PREFIX = "ZXPH"
PH_SUFFIX = "XZ"

PROTECT_PATTERNS = [
    re.compile(r"\$[^$]*\$"),
    re.compile(r"\\(?:eqref|ref|label|cite|texttt|url)\{[^{}]*\}"),
    re.compile(r"https?://\S+"),
    re.compile(r"github\.com/\S+"),
]

FORMAT_PATTERNS = [
    re.compile(r"\\textbf\{([^{}]*)\}"),
    re.compile(r"\\textit\{([^{}]*)\}"),
    re.compile(r"\\emph\{([^{}]*)\}"),
]

TEXTCOLOR_PATTERN = re.compile(r"\\textcolor\{([^{}]*)\}\{([^{}]*)\}")

SECTION_PATTERN = re.compile(r"^(\s*\\(?:section|subsection|subsubsection|paragraph)\{)(.*)(\}\s*)$")
HEADER_PATTERN = re.compile(r"^(\s*\\(?:rhead|lhead)\{)(.*)(\}\s*)$")

# Keep common technical acronyms unchanged.
ABBREV_PATTERN = re.compile(r"\b(?:DIP|SMC|PSO|STA|MPC|FFT|RMS|LTI|SVD|HIL|DOF|CSV|PDF|LaTeX|Lyapunov|Welch|Monte Carlo|Coulomb|Coriolis|Lagrangian|Christoffel|MT-\d+|LT-\d+|QW-\d+)\b")

# token -> (leading_ws, core_text, trailing_ws)
TOKEN_META = {}
CORE_SET = set()


def register_segment(text: str) -> str:
    if not text:
        return text
    if not re.search(r"[A-Za-z]", text):
        return text

    leading = re.match(r"^\s*", text).group(0)
    trailing = re.search(r"\s*$", text).group(0)
    core = text[len(leading):len(text)-len(trailing)] if len(text) >= len(leading) + len(trailing) else text.strip()

    if not core or not re.search(r"[A-Za-z]", core):
        return text

    token = f"{TOKEN_PREFIX}{len(TOKEN_META)}{TOKEN_SUFFIX}"
    TOKEN_META[token] = (leading, core, trailing)
    CORE_SET.add(core)
    return token


def protect(text: str):
    tokens = []

    def put_token(match):
        idx = len(tokens)
        tokens.append(match.group(0))
        return f"{PH_PREFIX}{idx}{PH_SUFFIX}"

    s = text
    for pat in PROTECT_PATTERNS:
        s = pat.sub(put_token, s)

    return s, tokens


def unprotect(text: str, tokens):
    s = text
    for idx, tok in enumerate(tokens):
        s = s.replace(f"{PH_PREFIX}{idx}{PH_SUFFIX}", tok)
    return s


def mark_fragment(text: str) -> str:
    if not re.search(r"[A-Za-z]", text):
        return text

    s = text

    changed = True
    while changed:
        changed = False
        for pat in FORMAT_PATTERNS:
            def repl_fmt(m):
                inner = m.group(1)
                return m.group(0).replace(inner, mark_fragment(inner), 1)

            new_s = pat.sub(repl_fmt, s)
            if new_s != s:
                changed = True
                s = new_s

    def repl_textcolor(m):
        color = m.group(1)
        inner = m.group(2)
        return f"\\textcolor{{{color}}}{{{mark_fragment(inner)}}}"

    s = TEXTCOLOR_PATTERN.sub(repl_textcolor, s)

    protected, tokens = protect(s)

    parts = re.split(rf"({PH_PREFIX}\d+{PH_SUFFIX})", protected)
    for i, part in enumerate(parts):
        if not part:
            continue
        if re.fullmatch(rf"{PH_PREFIX}\d+{PH_SUFFIX}", part):
            continue
        parts[i] = register_segment(part)

    merged = "".join(parts)
    return unprotect(merged, tokens)


def mark_table_row(line: str) -> str:
    m = re.match(r"^(.*?)(\\\\.*)$", line)
    if not m:
        return line

    body, tail = m.group(1), m.group(2)
    cells = body.split("&")
    out_cells = [mark_fragment(cell) for cell in cells]
    return "&".join(out_cells) + tail


def convert_line(line: str) -> str:
    nl = "\n" if line.endswith("\n") else ""
    s = line[:-1] if nl else line

    if not s.strip():
        return line

    if s.lstrip().startswith("%"):
        return line

    m = SECTION_PATTERN.match(s)
    if m:
        return f"{m.group(1)}{mark_fragment(m.group(2))}{m.group(3)}{nl}"

    m = HEADER_PATTERN.match(s)
    if m:
        return f"{m.group(1)}{mark_fragment(m.group(2))}{m.group(3)}{nl}"

    if "&" in s and "\\\\" in s:
        return mark_table_row(s) + nl

    if s.lstrip().startswith("\\"):
        if "\\textbf{" in s or "\\textit{" in s or "\\emph{" in s or "\\textcolor{" in s:
            return mark_fragment(s) + nl
        return line

    return mark_fragment(s) + nl


def patch_preamble(content: str) -> str:
    content = content.replace(
        "Compile  : pdflatex advisor_progress_report.tex (twice)",
        "Compile  : xelatex advisor_progress_report_fa.tex (twice)",
    )

    if "\\usepackage{xepersian}" not in content:
        marker = "\\begin{document}"
        insert = (
            "\\usepackage{xepersian}\n"
            "\\settextfont[Scale=1.05]{B Nazanin}\n"
            "\\setlatintextfont{Times New Roman}\n\n"
        )
        if marker in content:
            content = content.replace(marker, insert + marker, 1)

    return content


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def protect_abbrev(text: str):
    mapping = {}

    def repl(m):
        key = f"ZZABBR{len(mapping)}ZZ"
        mapping[key] = m.group(0)
        return key

    return ABBREV_PATTERN.sub(repl, text), mapping


def unprotect_abbrev(text: str, mapping):
    out = text
    for k, v in mapping.items():
        out = out.replace(k, v)
    return out


def translate_core_batch(cores):
    out_map = {}
    cores = list(cores)

    safe_texts = []
    safe_maps = []
    for core in cores:
        safe_core, mapping = protect_abbrev(core)
        safe_texts.append(safe_core)
        safe_maps.append(mapping)

    for batch_idx, batch in enumerate(chunked(list(range(len(safe_texts))), 25), start=1):
        batch_texts = [safe_texts[i] for i in batch]

        translated = None
        for attempt in range(5):
            try:
                translated = translator.translate_batch(batch_texts)
                if isinstance(translated, str):
                    translated = [translated]
                if len(translated) != len(batch_texts):
                    raise RuntimeError("Batch length mismatch")
                break
            except Exception:
                if attempt == 4:
                    translated = []
                    for t in batch_texts:
                        single = None
                        for single_try in range(4):
                            try:
                                single = translator.translate(t)
                                break
                            except Exception:
                                if single_try == 3:
                                    single = t
                                else:
                                    time.sleep(1.0 * (single_try + 1))
                        translated.append(single)
                else:
                    time.sleep(1.2 * (attempt + 1))

        for rel_i, abs_i in enumerate(batch):
            tr_text = translated[rel_i]
            tr_text = unprotect_abbrev(tr_text, safe_maps[abs_i])
            out_map[cores[abs_i]] = tr_text

        print(f"Translated batch {batch_idx} / {(len(safe_texts) + 24) // 25}")

    return out_map


def substitute_tokens(content: str, core_map):
    out = content
    # Replace longer tokens first to avoid accidental substring overlap.
    token_keys = sorted(TOKEN_META.keys(), key=lambda t: int(t[len(TOKEN_PREFIX):-len(TOKEN_SUFFIX)]), reverse=True)

    for token in token_keys:
        leading, core, trailing = TOKEN_META[token]
        translated_core = core_map.get(core, core)
        out = out.replace(token, f"{leading}{translated_core}{trailing}")

    return out


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)

    marked_lines = [convert_line(ln) for ln in lines]
    marked_text = "".join(marked_lines)
    marked_text = patch_preamble(marked_text)

    cores = sorted(CORE_SET)
    print(f"Unique cores to translate: {len(cores)}")

    core_map = translate_core_batch(cores)
    final_text = substitute_tokens(marked_text, core_map)

    DST.write_text(final_text, encoding="utf-8")
    print(f"Wrote: {DST}")


if __name__ == "__main__":
    main()
