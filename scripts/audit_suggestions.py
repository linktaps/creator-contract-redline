#!/usr/bin/env python3
"""
audit_suggestions.py — verify what a redline actually did.

Google Docs exports pending suggestions as Word tracked changes. This script
reads an exported .docx and reconstructs two versions of the text:

  accepted  — every suggestion applied (what the contract becomes)
  original  — every suggestion rejected (what the brand sent)

That distinction is the whole point. The plain-text export of a Google Doc
runs insertions and deletions together, so struck language looks identical to
untouched language. Auditing from the text export produces false "still
there" findings and false "resolved" findings in both directions. Auditing
from the tracked changes cannot.

Usage
-----
  # summary: how many suggestions, by whom
  python audit_suggestions.py contract.docx

  # write both reconstructions for reading or diffing
  python audit_suggestions.py contract.docx --write-dir ./out

  # the completeness gate: are these phrases still in the accepted version?
  python audit_suggestions.py contract.docx --check phrases.txt

  # list every suggestion as an edit pair
  python audit_suggestions.py contract.docx --list

phrases.txt holds one phrase per line, optionally "label :: phrase".
Blank lines and lines starting with # are ignored. Use the exact adverse
wording from the contract — curly quotes and all.

Exit code is 1 if any checked phrase is still present, so this can gate a
workflow.
"""

import argparse
import collections
import difflib
import re
import sys
import zipfile
from pathlib import Path

INS_DEL = re.compile(
    r'<w:(ins|del)\s[^>]*?w:author="([^"]*)"[^>]*?>(.*?)</w:\1>', re.S
)
TEXT_RUN = re.compile(
    r"<w:(?:t|delText)(?:\s[^>]*)?>(.*?)</w:(?:t|delText)>", re.S
)
# Text elements and tabs, matched in document order so a tab lands where it
# actually sits rather than being hoisted to the front of the run.
FLOW = re.compile(
    r"<w:(?:t|delText)(?:\s[^>]*)?>(.*?)</w:(?:t|delText)>|<w:tab\s*/>", re.S
)
PARA = re.compile(r"<w:p[ >].*?</w:p>", re.S)
AUTHOR = re.compile(r'w:author="([^"]*)"')

UNESCAPE = [("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"), ("&amp;", "&")]


def unescape(s: str) -> str:
    for a, b in UNESCAPE:
        s = s.replace(a, b)
    return s


def load_document_xml(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as z:
        return z.read("word/document.xml").decode("utf-8")


def segment(paragraph: str):
    """Yield (kind, text) where kind is 'plain', 'ins' or 'del'."""
    pos = 0
    for m in INS_DEL.finditer(paragraph):
        yield "plain", paragraph[pos : m.start()]
        yield m.group(1), m.group(3)
        pos = m.end()
    yield "plain", paragraph[pos:]


def flow_text(chunk: str) -> str:
    """Text of a chunk with tabs in their true positions."""
    out = []
    for m in FLOW.finditer(chunk):
        out.append("\t" if m.group(1) is None else m.group(1))
    return "".join(out)


def render(paragraph: str, mode: str) -> str:
    """mode='accepted' applies suggestions; mode='original' rejects them."""
    out = []
    for kind, chunk in segment(paragraph):
        if kind == "ins" and mode == "original":
            continue
        if kind == "del" and mode == "accepted":
            continue
        out.append(flow_text(chunk))
    return unescape("".join(out))


def reconstruct(xml: str, mode: str) -> str:
    return "\n".join(render(p, mode) for p in PARA.findall(xml))


def suggestions(xml: str):
    """Yield (author, kind, text) for every tracked change, in document order."""
    for m in INS_DEL.finditer(xml):
        text = unescape(flow_text(m.group(3)))
        if text.strip():
            yield m.group(2), m.group(1), text


def dominant_run_props(xml: str):
    """The size and font the body text actually uses."""
    sizes = collections.Counter(re.findall(r'<w:sz w:val="(\d+)"/>', xml))
    fonts = collections.Counter(re.findall(r'<w:rFonts\b[^>]*?w:ascii="([^"]+)"', xml))
    return (sizes.most_common(1)[0][0] if sizes else None,
            fonts.most_common(1)[0][0] if fonts else None)


def check_inserted_formatting(xml: str):
    """Inserted runs that don't carry the document's size/font.

    A run authored without <w:sz> or <w:rFonts> inherits docDefaults, which in a
    contract typeset at 8.5pt is usually 12pt in a different face. The result is
    a clause that is visibly larger than everything around it.

    Only the properties the body text actually declares are required. Plenty of
    contracts set no <w:rFonts> on any run at all and take their typeface from
    styles.xml; in such a document an inserted run without <w:rFonts> matches its
    surroundings exactly, and adding one would make it the anomaly. Demanding a
    property the document never sets reports every insertion as broken — verified
    against two independently authored professional redlines of the same
    agreement, both of which failed this check on every inserted run while
    rendering correctly.
    """
    want_sz, want_font = dominant_run_props(xml)
    problems = []
    for ins in re.finditer(r"<w:ins\b[^>]*>(.*?)</w:ins>", xml, re.S):
        for run in re.finditer(r"<w:r\b[^>]*>(.*?)</w:r>", ins.group(1), re.S):
            body = run.group(1)
            if "<w:t" not in body:
                continue
            rpr = re.search(r"<w:rPr>(.*?)</w:rPr>", body, re.S)
            rpr_text = rpr.group(1) if rpr else ""
            missing = []
            if want_sz and not re.search(r"<w:sz ", rpr_text):
                missing.append("size")
            if want_font and not re.search(r"w:ascii=", rpr_text):
                missing.append("font")
            if missing:
                text = unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", body, re.S)))
                if text.strip():
                    problems.append((missing, " ".join(text.split())))
    return want_sz, want_font, problems
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        label, sep, phrase = line.partition("::")
        if sep:
            # A line with "::" is always an entry, even though checklist
            # labels start with "#" (e.g. "#14 unpaid extension :: ...").
            items.append((label.strip(), phrase.strip()))
        elif line.startswith("#"):
            continue  # comment
        else:
            items.append((line[:48], line))
    return items


def check_paragraph_structure(xml: str):
    """Paragraphs whose text is entirely struck but whose paragraph mark survives.

    Accepting such a suggestion removes the words and leaves the empty paragraph
    behind — a blank line, or worse a bullet with nothing after it. Deleting a
    whole paragraph means deleting its runs *and* marking its paragraph mark
    deleted, which in OOXML is a <w:del> inside <w:pPr><w:rPr>.
    """
    orphans = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        ppr = re.search(r"<w:pPr>(.*?)</w:pPr>", p, re.S)
        ppr_text = ppr.group(1) if ppr else ""
        mark_deleted = bool(
            re.search(r"<w:rPr>(?:(?!</w:rPr>).)*<w:del\b", ppr_text, re.S)
        )
        all_text = "".join(
            re.findall(r"<w:(?:t|delText)(?:\s[^>]*)?>(.*?)</w:(?:t|delText)>", p, re.S)
        )
        del_text = "".join(
            re.findall(r"<w:delText(?:\s[^>]*)?>(.*?)</w:delText>", p, re.S)
        )
        if all_text.strip() and all_text == del_text and not mark_deleted:
            kind = "bullet" if "<w:numPr>" in ppr_text else "paragraph"
            orphans.append((kind, unescape(" ".join(all_text.split()))))
    return orphans


TOGGLES = ("b", "i", "u", "strike", "caps", "smallCaps", "vertAlign", "highlight")
OFF_VALUES = {"0", "false", "none", "baseline", "clear"}


def run_signature(rpr: str):
    """Character formatting of a run, honouring explicit-off values.

    A run property can be present and switched *off*: <w:b w:val="0"/> means not
    bold. Treating the tag's presence as "on" reports formatting changes that
    are not there.
    """
    sig = {}
    for tag in TOGGLES:
        m = re.search(rf"<w:{tag}\b(?![a-zA-Z])[^>]*>", rpr)
        if not m:
            sig[tag] = False
        else:
            v = re.search(r'w:val="([^"]+)"', m.group(0))
            sig[tag] = True if not v else v.group(1) not in OFF_VALUES
    m = re.search(r'<w:sz w:val="(\d+)"', rpr)
    sig["sz"] = m.group(1) if m else None
    m = re.search(r'w:ascii="([^"]+)"', rpr)
    sig["font"] = m.group(1) if m else None
    return tuple(sorted(sig.items()))


def char_formats(xml: str, mode: str = "original"):
    """(text, [signature per character]) for the reconstructed view.

    Comparing per character rather than per run makes the result immune to run
    splitting, which happens constantly: editing one word splits the run that
    contained it, and a run-keyed comparison then reports every split as a
    change.
    """
    text, sigs = [], []
    for p in PARA.findall(xml):
        for kind, chunk in segment(p):
            if kind == "ins" and mode == "original":
                continue
            if kind == "del" and mode == "accepted":
                continue
            for run in re.finditer(r"<w:r\b[^>]*>(.*?)</w:r>", chunk, re.S):
                rb = run.group(1)
                rpr = re.search(r"<w:rPr>(.*?)</w:rPr>", rb, re.S)
                sig = run_signature(rpr.group(1) if rpr else "")
                # Whitespace is skipped so that tab and spacing differences,
                # which LAYOUT reports separately, cannot desynchronise this
                # comparison.
                for ch in unescape(flow_text(rb)):
                    if ch.isspace():
                        continue
                    text.append(ch)
                    sigs.append(sig)
    return "".join(text), sigs


def compare_formatting(base_xml: str, xml: str):
    """Formatting differences on text that exists in both documents."""
    bt, bs = char_formats(base_xml)
    rt, rs = char_formats(xml)
    if bt != rt:
        return None  # text differs; the fidelity check reports that instead
    runs, i = [], 0
    while i < len(bt):
        if bs[i] != rs[i]:
            j = i
            while j < len(bt) and bs[j] != rs[j]:
                j += 1
            db, dr = dict(bs[i]), dict(rs[i])
            changed = {k: (db[k], dr[k]) for k in db if db[k] != dr[k]}
            runs.append((bt[i:j].strip(), changed))
            i = j
        else:
            i += 1
    return runs


def phrase_context(xml: str, phrase: str):
    """Was the clause containing this phrase edited at all?

    Distinguishes two very different states that a plain presence test cannot:
    a clause nobody touched, and a clause where a protective sentence was added
    while the adverse wording was left standing beside it. The second reads as
    done on a tracking table and leaves the contract contradicting itself.
    """
    touched = False
    for p in PARA.findall(xml):
        if phrase in render(p, "accepted"):
            if re.search(r"<w:ins\b", p) or re.search(r"<w:del\b", p):
                touched = True
    return touched


def parse_phrases(path: Path):
    """One entry per line: "label :: exact adverse wording".

    A line containing "::" is always an entry, even though checklist labels
    start with "#" (e.g. "#14 unpaid extension :: ..."). Only a "#" line with
    no "::" is a comment.
    """
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        label, sep, phrase = line.partition("::")
        if sep:
            items.append((label.strip(), phrase.strip()))
        elif line.startswith("#"):
            continue
        else:
            items.append((line[:48], line))
    return items


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", type=Path, help="document exported from Google Docs as .docx")
    ap.add_argument("--check", type=Path, help="file of phrases to test against the accepted version")
    ap.add_argument("--baseline", type=Path, help="the brand's untouched draft (.docx); verifies no text was destroyed")
    ap.add_argument("--write-dir", type=Path, help="write accepted.txt and original.txt here")
    ap.add_argument("--list", action="store_true", help="print every suggestion")
    args = ap.parse_args()

    if not args.docx.exists():
        print(f"error: {args.docx} not found", file=sys.stderr)
        return 2

    xml = load_document_xml(args.docx)
    accepted = reconstruct(xml, "accepted")
    original = reconstruct(xml, "original")
    sugg = list(suggestions(xml))
    authors = sorted(set(AUTHOR.findall(xml)))

    print(f"{args.docx.name}")
    print(f"  suggestions : {len(sugg)}  ({sum(1 for a,k,t in sugg if k=='ins')} insertions, "
          f"{sum(1 for a,k,t in sugg if k=='del')} deletions)")
    print(f"  authors     : {', '.join(authors) if authors else 'none'}")
    print(f"  accepted    : {len(accepted):,} chars")
    print(f"  original    : {len(original):,} chars")

    if not sugg:
        print("\n  WARNING: no tracked changes found. Either nothing was edited, or the")
        print("  edits were made directly rather than as suggestions.")

    if args.write_dir:
        args.write_dir.mkdir(parents=True, exist_ok=True)
        (args.write_dir / "accepted.txt").write_text(accepted, encoding="utf-8")
        (args.write_dir / "original.txt").write_text(original, encoding="utf-8")
        print(f"\n  wrote {args.write_dir}/accepted.txt and original.txt")

    if args.list:
        print("\nSuggestions in document order:")
        for author, kind, text in sugg:
            verb = "ADD" if kind == "ins" else "DEL"
            flat = " ".join(text.split())
            print(f"  [{author}] {verb}: {flat[:110]}{'…' if len(flat) > 110 else ''}")

    failures = 0

    orphans = check_paragraph_structure(xml)
    print("\nStructure check — will any emptied paragraph survive acceptance?\n")
    if not orphans:
        print("  PASS — every fully struck paragraph also has its paragraph mark deleted.")
    else:
        failures += 1
        print(f"  FAIL — {len(orphans)} paragraph(s) struck without deleting the paragraph mark.")
        print("  Accepting these removes the words and leaves an empty line or bullet behind.\n")
        for kind, text in orphans[:8]:
            print(f"    empty {kind} would remain: \"{text[:90]}…\"")

    want_sz, want_font, fmt_problems = check_inserted_formatting(xml)
    print("\nFormatting check — do inserted runs match the document's body text?\n")
    if want_sz:
        print(f"  body text is {int(want_sz)/2:g}pt {want_font or '(unnamed font)'}")
    if not fmt_problems:
        required = ", ".join(x for x in ("size" if want_sz else "", "font" if want_font else "") if x)
        if required:
            print(f"  PASS — every inserted run declares the {required} the body text uses.")
        else:
            print("  PASS — body runs declare neither size nor font, so there is nothing "
                  "for inserted runs to match.")
        if not want_font:
            print("  Note: no run in this document declares a typeface; it comes from styles.xml.")
            print("  Inserted runs therefore inherit exactly as the brand's own text does, and")
            print("  adding an explicit <w:rFonts> would make them the odd ones out.")
    else:
        failures += 1
        print(f"  FAIL — {len(fmt_problems)} inserted run(s) inherit docDefaults instead.")
        print("  These will render at the default size and face, visibly larger than the")
        print("  surrounding text. Copy the <w:rPr> block from an adjacent body run.\n")
        for missing, text in fmt_problems[:8]:
            print(f"    missing {', '.join(missing)}: \"{text[:90]}…\"")

    if args.baseline:
        if not args.baseline.exists():
            print(f"\nerror: baseline {args.baseline} not found", file=sys.stderr)
            return 2
        base_xml = load_document_xml(args.baseline)
        base = reconstruct(base_xml, "original")
        print("\nFidelity check — does rejecting every suggestion restore the brand's draft?\n")

        # Substance: compare with all whitespace removed, so tab and run-splitting
        # artifacts cannot masquerade as lost text.
        if "".join(base.split()) == "".join(original.split()):
            print("  TEXT: PASS — reject-all restores the brand's wording exactly.")
        else:
            failures += 1
            norm = lambda s: " ".join(s.split())
            b_words, r_words = norm(base).split(" "), norm(original).split(" ")
            sm = difflib.SequenceMatcher(None, b_words, r_words, autojunk=False)
            deltas = [
                op for op in sm.get_opcodes()
                if op[0] != "equal"
                and "".join("".join(b_words[op[1]:op[2]]).split())
                    != "".join("".join(r_words[op[3]:op[4]]).split())
            ]
            print(f"  TEXT: FAIL — {len(deltas)} divergence(s). Text was changed outside a")
            print("  suggestion, so rejecting the redline would NOT restore the brand's draft.\n")
            for tag, i1, i2, j1, j2 in deltas[:10]:
                print(f"    [{tag}]")
                print(f"      baseline: …{' '.join(b_words[max(0,i1-10):i2+10])[:160]}…")
                print(f"      redline : …{' '.join(r_words[max(0,j1-10):j2+10])[:160]}…\n")
            print("  Common causes: an edit made outside Suggesting mode, or an undo that")
            print("  overshot and was repaired by retyping. Repair by restoring the original")
            print("  wording and re-making the change as a suggestion.")

        # Structure: layout elements are easy to destroy when authoring XML by hand
        # and invisible in a text comparison. Compare the reject-all views, so that
        # tabs inside newly inserted clauses are not counted as damage and tabs in
        # deleted paragraphs are not counted as losses.
        print()
        base_reject, red_reject = base, original
        nb, nr = base_reject.count("\t"), red_reject.count("\t")
        if nb == nr:
            print(f"  LAYOUT: tab stops intact ({nr})")
        else:
            failures += 1
            verb = "lost" if nr < nb else "gained"
            print(f"  LAYOUT: FAIL — tab stops {nb} in baseline, {nr} on reject-all "
                  f"({abs(nb - nr)} {verb})")
            print("          A tab lost from a caption runs it into the body text.")
            print("          Check any run you replaced that contained a <w:tab/>.")
        # A run with no explicit font or size inherits docDefaults. If the two
        # documents disagree about docDefaults — common when a file has been
        # through a different toolchain — then "inherit" means something
        # different on each side, and any run that lost its <w:rFonts> silently
        # changes typeface.
        def doc_defaults(styles_xml: str):
            d = re.search(r"<w:docDefaults>.*?</w:docDefaults>", styles_xml, re.S)
            g = d.group(0) if d else ""
            f = re.search(r'w:ascii="([^"]+)"', g)
            z = re.search(r'<w:sz w:val="(\d+)"', g)
            return (f.group(1) if f else None, z.group(1) if z else None)

        try:
            with zipfile.ZipFile(args.baseline) as zb, zipfile.ZipFile(args.docx) as zr:
                db = doc_defaults(zb.read("word/styles.xml").decode("utf-8"))
                dr = doc_defaults(zr.read("word/styles.xml").decode("utf-8"))
            if db != dr:
                print(f"\n  DEFAULTS: changed — baseline {db[0] or 'none'}/{db[1] or '?'}, "
                      f"redline {dr[0] or 'none'}/{dr[1] or '?'} (font/half-points)")
                print("            Any run without an explicit font or size now renders")
                print("            differently. Check the TYPE results carefully.")
        except KeyError:
            pass

        fmt = compare_formatting(base_xml, xml)
        if fmt is None:
            print("  TYPE: skipped — reject-all text differs, fix that first")
        elif not fmt:
            print("  TYPE: character formatting on surviving text unchanged")
        else:
            failures += 1
            print(f"  TYPE: FAIL — {len(fmt)} span(s) of surviving text changed formatting")
            for snippet, changed in fmt[:8]:
                bits = ", ".join(f"{k}: {a} -> {b}" for k, (a, b) in changed.items())
                print(f"          \"{snippet[:60]}\" — {bits}")

        nb, nr = base_xml.count('<w:br w:type="page"/>'), xml.count('<w:br w:type="page"/>')
        if nb == nr:
            print(f"  LAYOUT: page breaks intact ({nr})")
        else:
            failures += 1
            print(f"  LAYOUT: FAIL — page breaks {nb} in baseline, {nr} in redline")

    if args.check:
        items = parse_phrases(args.check)
        print(f"\nCompleteness check — is the adverse wording still in the accepted version?\n")
        width = max((len(l) for l, _ in items), default=10)
        # Counted separately from `failures`, which the structure, formatting and
        # fidelity checks also increment. Folding those into this tally makes the
        # printed total disagree with the lines printed above it.
        unresolved = 0
        for label, phrase in items:
            n_acc = accepted.count(phrase)
            n_org = original.count(phrase)
            if n_org == 0:
                state = "not found in either — check the phrase"
                unresolved += 1
                failures += 1
            elif n_acc == 0:
                state = f"resolved (was x{n_org})"
            elif n_acc < n_org:
                state = f"PARTIAL — x{n_org} before, x{n_acc} still present"
                unresolved += 1
                failures += 1
            else:
                unresolved += 1
                failures += 1
                if phrase_context(xml, phrase):
                    state = f"STILL PRESENT (x{n_acc}) — but this clause WAS edited"
                else:
                    state = f"STILL PRESENT (x{n_acc}) — clause untouched"
            print(f"  {label:<{width}}  {state}")
        print(f"\n  {unresolved} of {len(items)} unresolved")
        print("\n  \"WAS edited\" is the dangerous one: something was changed in that clause")
        print("  while the adverse wording stayed. Usually a protective sentence was added")
        print("  beside the problem instead of replacing it, leaving the clause to")
        print("  contradict itself. Read the whole clause before accepting it as done.")
        print("\n  Counts matter: a phrase can appear in several clauses, or in both the")
        print("  body and an exhibit. 'PARTIAL' means one instance was handled and")
        print("  another was not — check which. A phrase that survives may also have")
        print("  been correctly narrowed by an insertion nearby, so read the context")
        print("  before recording a miss.")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
