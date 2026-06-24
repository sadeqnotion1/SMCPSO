#======================================================================================
#============================ verify_references.py ====================================
#======================================================================================
# Source-authenticity verifier for SMC-PSO-beta references.
#
# Reuses the EXISTING pdf-fetcher engine (fetcher.PDFFetcher) -- no new required deps.
# For each reference in a manifest JSON it:
#   1) Confirms the DOI resolves on Crossref and the returned title/year match (metadata check).
#   2) (Legal path) Tries Unpaywall open-access PDF; if found, downloads + extracts text.
#   3) Content checks: single-vs-double inverted pendulum, required keywords, parameter hints.
#   4) Emits an ASCII report (.md + .json). NEVER edits config.bib (stay in scope).
#
# Place this file at:  pdf-fetcher/verify_references.py  (next to fetcher.py / cli.py)
# Run (Windows):       python verify_references.py --manifest references_manifest.json --out report
#
# PDF text extraction is OPTIONAL and guarded (PyMuPDF -> pdftotext -> pdfminer -> skip).
# If none is available, metadata-only verification still runs.
# Sci-Hub fallback is intentionally NOT used here: verification relies on Crossref + legal
# open-access only. Do not add circumvention here.
#======================================================================================

import os
import sys
import re
import json
import argparse
import tempfile

try:
    from fetcher import PDFFetcher
except Exception as e:  # pragma: no cover
    print("[ERROR] Could not import fetcher.PDFFetcher. Run this from the pdf-fetcher/ folder.")
    print("        Detail: %s" % e)
    sys.exit(2)


def norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower())


def token_overlap(a, b):
    wa = set(w for w in norm(a).split() if len(w) >= 4)
    wb = set(w for w in norm(b).split() if len(w) >= 4)
    if not wa:
        return 0.0
    return len(wa & wb) / float(len(wa))


def extract_pdf_text(path):
    """Best-effort text extraction. Returns (text, engine) or ('', 'none')."""
    # 1) PyMuPDF
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        if text.strip():
            return text, "pymupdf"
    except Exception:
        pass
    # 2) poppler pdftotext
    try:
        import subprocess
        out = path + ".txt"
        subprocess.run(["pdftotext", "-q", path, out], check=True)
        with open(out, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        try:
            os.remove(out)
        except Exception:
            pass
        if text.strip():
            return text, "pdftotext"
    except Exception:
        pass
    # 3) pdfminer
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(path)
        if text and text.strip():
            return text, "pdfminer"
    except Exception:
        pass
    return "", "none"


def check_content(text, expected):
    """Run single/double + keyword + parameter checks against extracted text."""
    findings = []
    low = text.lower()
    n_double = low.count("double inverted pendulum") + low.count("double pendulum")
    n_single = low.count("single inverted pendulum")
    want = (expected or {}).get("system", "n/a")

    if want == "double":
        if n_double == 0:
            findings.append(("ERROR", "Expected a DOUBLE pendulum paper but found 0 'double pendulum' mentions"))
        else:
            findings.append(("OK", "Found %d 'double pendulum' mention(s)" % n_double))
        if n_single > n_double and n_single > 0:
            findings.append(("WARNING", "More 'single' (%d) than 'double' (%d) mentions -- check it is really a DIP" % (n_single, n_double)))
    elif want == "single":
        findings.append(("INFO", "single=%d double=%d (expected single -- NOT a DIP parameter source)" % (n_single, n_double)))

    for kw in (expected or {}).get("must_contain", []):
        if kw.lower() in low:
            findings.append(("OK", "contains keyword: '%s'" % kw))
        else:
            findings.append(("WARNING", "missing keyword: '%s'" % kw))

    # Parameter hints: look for typical DIP physical-parameter vocabulary
    param_terms = ["mass", "length", "inertia", "moment of inertia", "center of mass", "kg"]
    hit = [t for t in param_terms if t in low]
    if want == "double":
        if len(hit) >= 3:
            findings.append(("OK", "parameter vocabulary present: %s" % ", ".join(hit)))
        else:
            findings.append(("WARNING", "few parameter terms found (%s) -- may not list explicit m/l/I values" % ", ".join(hit) or "none"))
    return findings


def verify_one(fetcher, ref, download_dir, do_pdf):
    key = ref.get("key", "?")
    doi = ref.get("doi")
    expected = ref.get("expected", {})
    result = {"key": key, "doi": doi, "checks": [], "verdict": "UNKNOWN"}

    def add(level, msg):
        result["checks"].append({"level": level, "msg": msg})
        print("  [%s] %s" % (level, msg))

    print("\n=== %s ===" % key)
    if not doi:
        add("INFO", "No DOI (%s). Confirm manually via: %s" % (key, ref.get("alt_locator", "n/a")))
        result["verdict"] = "MANUAL"
        return result

    # 1) Crossref metadata
    meta = fetcher.search_crossref(doi, limit=1)
    if not meta or not meta[0].get("doi"):
        add("ERROR", "DOI did NOT resolve on Crossref -> likely fabricated/incorrect")
        result["verdict"] = "FAIL"
        return result
    m = meta[0]
    result["crossref"] = m
    ratio = token_overlap(ref.get("title", ""), m.get("title", ""))
    add("INFO", "Crossref title: %s (%s)" % (m.get("title"), m.get("year")))
    if ratio >= 0.6:
        add("OK", "title overlap with expected = %.0f%%" % (ratio * 100))
    else:
        add("ERROR", "title overlap only %.0f%% -- DOI may point to a DIFFERENT paper" % (ratio * 100))
    # Year check
    try:
        if ref.get("year") and str(m.get("year")).isdigit():
            if abs(int(m["year"]) - int(ref["year"])) > 1:
                add("WARNING", "year mismatch: manifest=%s crossref=%s" % (ref["year"], m["year"]))
            else:
                add("OK", "year matches (%s)" % m["year"])
    except Exception:
        pass

    # 2/3) Optional PDF content check via legal open access
    if do_pdf:
        pdf_url = fetcher.fetch_from_unpaywall(doi)
        if pdf_url:
            dest = os.path.join(download_dir, key.replace("/", "_") + ".pdf")
            if fetcher.download_pdf(pdf_url, dest):
                text, engine = extract_pdf_text(dest)
                if text:
                    add("INFO", "extracted text via %s (%d chars)" % (engine, len(text)))
                    for level, msg in check_content(text, expected):
                        add(level, msg)
                else:
                    add("WARNING", "PDF downloaded but no text extractor available (install pymupdf or poppler)")
            else:
                add("WARNING", "open-access PDF URL found but download failed (content check skipped)")
        else:
            add("INFO", "no legal open-access PDF (Unpaywall) -- metadata-only verification")

    levels = [c["level"] for c in result["checks"]]
    if "ERROR" in levels:
        result["verdict"] = "FAIL"
    elif "WARNING" in levels:
        result["verdict"] = "REVIEW"
    else:
        result["verdict"] = "PASS"
    return result


def main():
    ap = argparse.ArgumentParser(description="Verify reference authenticity via Crossref + legal open access.")
    ap.add_argument("--manifest", default="references_manifest.json", help="Path to references manifest JSON.")
    ap.add_argument("--out", default="reference_verification", help="Output basename (.md + .json).")
    ap.add_argument("--no-pdf", action="store_true", help="Metadata-only; skip PDF download + content checks.")
    args = ap.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    refs = manifest.get("references", [])
    fetcher = PDFFetcher()

    download_dir = tempfile.mkdtemp(prefix="refverify_")
    results = []
    for ref in refs:
        results.append(verify_one(fetcher, ref, download_dir, do_pdf=not args.no_pdf))

    # Reports
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    lines = ["# Reference verification report", ""]
    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    lines.append("Summary: " + ", ".join("%s=%d" % (k, v) for k, v in sorted(counts.items())))
    lines.append("")
    for r in results:
        lines.append("## %s  ->  %s" % (r["key"], r["verdict"]))
        if r.get("doi"):
            lines.append("- DOI: %s" % r["doi"])
        for c in r["checks"]:
            lines.append("- [%s] %s" % (c["level"], c["msg"]))
        lines.append("")
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n[OK] Wrote %s.md and %s.json" % (args.out, args.out))
    print("[INFO] PDFs (if any) cached under: %s" % download_dir)
    # Non-zero exit if any hard failure, so CI/agents can gate on it
    sys.exit(1 if counts.get("FAIL") else 0)


if __name__ == "__main__":
    main()
