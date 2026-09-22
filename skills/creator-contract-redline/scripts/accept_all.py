#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a clean copy of a redline: every tracked change accepted (this script)
or rejected (reject_all.py, the mirror).

    python accept_all.py redline.docx clean.docx
    python reject_all.py redline.docx original.docx

A clean copy is a deliverable in its own right — the text to hand a second
model, or to read without markup between rounds — so it is checked before it is
written: the output's text must equal audit_suggestions.reconstruct() of the
input, paragraph by paragraph (whitespace-normalised). On any mismatch nothing
is written. Do not re-check it with python-docx's paragraph.text, which
silently skips <w:sdt> content and reports differences that are not there.

Only word/document.xml changes. Every other part is copied byte-for-byte with
its original ZipInfo; tracked changes in headers, footers or footnotes are left
in place with a warning.

A paragraph whose mark is removed (a deleted mark on accept, an inserted mark on
reject) joins the paragraph after it, as in Word: its surviving runs are
prepended to that paragraph, which keeps its own properties. Where there is no
following sibling paragraph (before a table, at the end of a cell or of the
body) Word cannot remove the mark either, so it is kept.

Moved text (w:moveFrom / w:moveTo) is refused: the audit reconstruction does
not model moves, so the result could not be verified. Resolve moves in Word.
"""
import re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_suggestions import reconstruct  # noqa: E402

# Self-closing <w:p/> paragraphs count: a struck paragraph followed by an empty
# spacer written that way must merge into the spacer, or it survives acceptance
# as an empty paragraph that no text comparison can see.
PARA_RE = re.compile(r"<w:p(?:\s[^>]*?)?/>|<w:p(?:\s[^>]*?)?(?<!/)>.*?</w:p>", re.S)
EMPTY_PARA = re.compile(r"<w:p(\s[^>]*?)?/>$")
PARA_PARTS = re.compile(
    r"(<w:p(?:\s[^>]*)?>)"
    r"(<w:pPr>(?:<w:pPrChange\b.*?</w:pPrChange>|(?!<w:pPrChange\b).)*?</w:pPr>|<w:pPr/>)?"
    r"(.*)</w:p>$", re.S)


def _block(tag):
    # container form only; `(?<!/)` keeps a paragraph-mark <w:ins/> out of it
    return re.compile(rf"<w:{tag}\b[^>]*?(?<!/)>.*?</w:{tag}>", re.S)


INS_BLOCK, DEL_BLOCK = _block("ins"), _block("del")
MARK = re.compile(r"<w:(ins|del)\b[^>]*/>")
PR_CHANGES = ("rPrChange", "pPrChange", "sectPrChange", "tblPrChange", "tblGridChange",
              "tcPrChange", "trPrChange", "tblPrExChange", "numberingChange")
LEFTOVER = re.compile(r"<w:(ins|del|moveFrom|moveTo|delText|delInstrText|cellIns|cellDel"
                      r"|cellMerge|\w+Change)\b")


def _mark_kinds(para):
    """Which tracked changes sit on the paragraph MARK itself."""
    m = PARA_PARTS.match(para)
    ppr = (m.group(2) or "") if m else ""
    head = ppr.split("<w:pPrChange", 1)[0]
    rpr = re.search(r"<w:rPr>(.*?)(?:<w:rPrChange\b|</w:rPr>)", head, re.S)
    return set(MARK.findall(rpr.group(1))) if rpr else set()


def _check_supported(xml):
    if re.search(r"<w:move(?:From|To)", xml):
        raise SystemExit("ABORT: document contains moved text (w:moveFrom/w:moveTo), which "
                         "the audit reconstruction cannot verify. Accept or reject the moves "
                         "in Word first.")
    if re.search(r"<w:cell(?:Ins|Del|Merge)\b", xml) or \
            re.search(r"<w:trPr>(?:(?!</w:trPr>).)*?<w:(?:ins|del)\b", xml, re.S):
        raise SystemExit("ABORT: document contains tracked table-structure changes "
                         "(inserted/deleted rows or cells), which this builder does not handle.")


def _structural(xml, mode):
    """Resolve paragraph marks that disappear in this mode, leaving run-level
    changes in place. Walks last-to-first so a chain of removed marks folds
    into the first paragraph that survives."""
    gone = "del" if mode == "accepted" else "ins"
    ms = list(PARA_RE.finditer(xml))
    if not ms:
        return xml, 0
    paras = [m.group(0) for m in ms]
    paras = [f"<w:p{e.group(1) or ''}></w:p>" if (e := EMPTY_PARA.match(p)) else p
             for p in paras]
    gaps = [xml[: ms[0].start()]] + [xml[ms[k - 1].end(): ms[k].start()] for k in range(1, len(ms))]
    tail = xml[ms[-1].end():]
    merges = 0
    for k in reversed(range(len(paras))):
        if gone not in _mark_kinds(paras[k]):
            continue
        n = k + 1
        while n < len(paras) and not gaps[n].strip() and paras[n] == "":
            n += 1
        if n < len(paras) and not gaps[n].strip():
            a, b = PARA_PARTS.match(paras[k]), PARA_PARTS.match(paras[n])
            paras[n] = b.group(1) + (b.group(2) or "") + a.group(3) + b.group(3) + "</w:p>"
            paras[k] = ""
            merges += 1
        else:
            a = PARA_PARTS.match(paras[k])
            ppr = re.sub(rf"<w:{gone}\b[^>]*/>", "", a.group(2), count=1)
            paras[k] = a.group(1) + ppr + a.group(3) + "</w:p>"
    return "".join(g + p for g, p in zip(gaps, paras)) + tail, merges


def _runlevel(xml, mode):
    if mode == "accepted":
        xml = DEL_BLOCK.sub("", xml)
        xml = re.sub(r"<w:ins\b[^>]*?(?<!/)>|</w:ins>", "", xml)
    else:
        xml = INS_BLOCK.sub("", xml)

        def unwrap(m):
            x = re.sub(r"^<w:del\b[^>]*>|</w:del>$", "", m.group(0))
            x = re.sub(r"<(/?)w:delText\b", r"<\1w:t", x)
            return re.sub(r"<(/?)w:delInstrText\b", r"<\1w:instrText", x)
        xml = DEL_BLOCK.sub(unwrap, xml)
    return MARK.sub("", xml)       # the marks that survive this mode


def _formatting(xml, mode):
    if mode == "accepted":
        # The current properties ARE the accepted state; drop the history.
        for tag in PR_CHANGES:
            xml = re.sub(rf"<w:{tag}\b[^>]*?(?:/>|>.*?</w:{tag}>)", "", xml, flags=re.S)
        return xml

    def rpr(m):
        return f"<w:rPr>{m.group(1) or ''}</w:rPr>"
    xml = re.sub(r"<w:rPr>(?:(?!</w:rPr>).)*?<w:rPrChange\b[^>]*>\s*"
                 r"(?:<w:rPr>(.*?)</w:rPr>|<w:rPr/>)\s*</w:rPrChange>\s*</w:rPr>", rpr, xml, flags=re.S)

    def ppr(m):
        cur, old = m.group(1), m.group(2) or ""
        # pPrChange records only paragraph properties: the mark's rPr and any
        # sectPr in the current pPr are not part of it and must be kept.
        keep = "".join(re.findall(r"<w:rPr>.*?</w:rPr>|<w:rPr/>|<w:sectPr\b.*?</w:sectPr>",
                                  cur, re.S))
        return f"<w:pPr>{old}{keep}</w:pPr>"
    xml = re.sub(r"<w:pPr>((?:(?!</w:pPr>).)*?)<w:pPrChange\b[^>]*>\s*"
                 r"(?:<w:pPr>(.*?)</w:pPr>|<w:pPr/>)\s*</w:pPrChange>\s*</w:pPr>", ppr, xml, flags=re.S)
    other = re.search(r"<w:(\w+Change)\b", xml)
    if other:
        raise SystemExit(f"ABORT: rejecting w:{other.group(1)} is not supported; "
                         f"reject it in Word first.")
    return xml


def transform(xml, mode):
    """-> (clean xml, structurally-resolved input xml, merge count)."""
    _check_supported(xml)
    resolved, merges = _structural(xml, mode)
    out = _formatting(_runlevel(resolved, mode), mode)
    left = LEFTOVER.search(out)
    if left:
        raise SystemExit(f"ABORT: tracked-change markup survived: {out[left.start():left.start() + 80]!r}")
    try:
        ET.fromstring(out)
    except ET.ParseError as e:
        raise SystemExit(f"ABORT: output document.xml is not well-formed — {e}")
    return out, resolved, merges


def _audit_safe(xml):
    """Reference input for reconstruct(), same text, minus two things its
    regexes misread: a self-closing mark <w:ins .../> is taken for an open tag
    that runs to the next </w:ins> (reduced here to <w:ins/>, which it still
    recognises as a mark); and a <w:del> inside a <w:ins> is rendered as
    inserted text on accept (dropped here: text inserted then deleted is in
    neither version)."""
    xml = MARK.sub(r"<w:\1/>", xml)
    return INS_BLOCK.sub(lambda m: DEL_BLOCK.sub("", m.group(0)), xml)


def _lines(text):
    return [re.sub(r"\s+", " ", ln).strip() for ln in text.split("\n")]


def verify(out_xml, resolved_xml, mode):
    got = _lines(reconstruct(out_xml, mode))
    want = _lines(reconstruct(_audit_safe(resolved_xml), mode))
    if got == want:
        return
    for n, (g, w) in enumerate(zip(got, want)):
        if g != w:
            break
    else:
        n = min(len(got), len(want))
    raise SystemExit(
        f"ABORT: output text differs from the audit's {mode} reconstruction at paragraph {n} "
        f"({len(got)} vs {len(want)} paragraphs); nothing written.\n"
        f"  output: {(got[n] if n < len(got) else '<none>')[:120]!r}\n"
        f"  audit:  {(want[n] if n < len(want) else '<none>')[:120]!r}"
    )


def build(src, dst, mode):
    with zipfile.ZipFile(src) as zin:
        xml = zin.read("word/document.xml").decode("utf-8")
        out, resolved, merges = transform(xml, mode)
        # The merge step is ours, so it is applied to the reference too; what
        # reconstruct() independently checks is every run-level change.
        verify(out, resolved, mode)
        stray = [i.filename for i in zin.infolist()
                 if i.filename != "word/document.xml" and i.filename.endswith(".xml")
                 and re.search(rb"<w:(?:ins|del)\b", zin.read(i.filename))]
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = out.encode("utf-8") if item.filename == "word/document.xml" \
                    else zin.read(item.filename)
                zout.writestr(item, data)
    for name in stray:
        print(f"WARNING: {name} has tracked changes; left as is", file=sys.stderr)
    return merges


def main(mode, argv=None):
    argv = sys.argv[1:] if argv is None else argv
    verb = "accept" if mode == "accepted" else "reject"
    if len(argv) != 2:
        raise SystemExit(f"usage: {verb}_all.py in.docx out.docx")
    src, dst = argv
    if Path(src).resolve() == Path(dst).resolve():
        raise SystemExit("ABORT: output would overwrite the input")
    merges = build(src, dst, mode)
    print(f"{verb}-all: wrote {dst} (text verified against the audit reconstruction"
          f"{f'; {merges} paragraph mark(s) merged' if merges else ''})")


if __name__ == "__main__":
    main("accepted")
