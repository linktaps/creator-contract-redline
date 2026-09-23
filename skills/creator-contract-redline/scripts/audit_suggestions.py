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

With --author NAME (the author of OUR suggestions) there is a third:

  counterparty — the other side's pending changes applied, ours rejected
                 (the text they think they are proposing)

Usage
-----
  # summary: how many suggestions, by whom
  python audit_suggestions.py contract.docx

  # write the reconstructions for reading or diffing
  python audit_suggestions.py contract.docx --write-dir ./out

  # the completeness gate: are these phrases still in the accepted version?
  python audit_suggestions.py contract.docx --check phrases.txt

  # ...and tell "never existed" apart from "only in the counterparty's
  # pending text" for phrases found in neither version
  python audit_suggestions.py contract.docx --check phrases.txt --author "Creator Name"

  # the additions gate: is every clause we added there exactly once? A line
  # ending ":: x3" expects three copies (one phrase in every termination route)
  python audit_suggestions.py contract.docx --additions additions.txt

  # re-run of a contract redlined before: is every earlier edit still here, or
  # explained in prior-ok.txt?
  python audit_suggestions.py redline-v2.docx --prior redline-v1.docx --prior-ok prior-ok.txt

  # fidelity against the brand's draft: reject-all text and paragraph count,
  # every other zip part byte-identical, and (with --author) every other
  # author's pending change exactly as they left it
  python audit_suggestions.py redline.docx --baseline brand-draft.docx --author "Creator Name"

  # list every suggestion as an edit pair
  python audit_suggestions.py contract.docx --list

  # coverage: does some label name every must-have item (#1-#16, #23, #24,
  # #reps) and every tagged sub-check (#2a, #4e, ...)? Labels in --check and
  # --additions count, plus every file listed
  python audit_suggestions.py redline.docx --check phrases.txt \\
      --additions additions.txt --coverage declined.md present.txt

phrases.txt and additions.txt hold one entry per line, optionally
"label :: text". Blank lines and lines starting with "# " are ignored. Use
the exact wording from the contract — curly quotes and all. Tabs are compared
as spaces.

--write-dir renders tabs as literal \\t characters (a caption column is
usually a real tab), so any external diff of those files must normalise
whitespace first or it reports false differences in every captioned paragraph.

Exit code is 1 if any gating check fails, 2 if an input file is missing.
"""

import argparse
import bisect
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
P_TAG = re.compile(r"<w:p(?=[\s>/])[^>]*?(/?)>|</w:p>")


def paragraph_spans(xml: str):
    """(start, end) of every paragraph not nested inside another, in order.

    Two traps, both met in real contracts. A self-closing <w:p/> is a real
    (empty) paragraph and must be counted. And paragraphs nest: a drawing's text
    box (<w:txbxContent>) holds whole paragraphs inside a run inside a
    paragraph — signature lines in exhibits are commonly drawn that way. A
    non-greedy <w:p>.*?</w:p> ends the outer paragraph at the first inner
    </w:p>, which splits it and misreads its paragraph mark. Counting depth
    keeps a text box's paragraphs as part of the paragraph that holds them.
    """
    spans, depth, start = [], 0, 0
    for m in P_TAG.finditer(xml):
        if m.group(0) == "</w:p>":
            depth -= 1
            if depth == 0:
                spans.append((start, m.end()))
        elif m.group(1):
            if depth == 0:
                spans.append((m.start(), m.end()))
        else:
            if depth == 0:
                start = m.start()
            depth += 1
    return spans


def paragraphs(xml: str):
    return [xml[s:e] for s, e in paragraph_spans(xml)]


AUTHOR = re.compile(r'w:author="([^"]*)"')

UNESCAPE = [("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"), ("&amp;", "&")]


def unescape(s: str) -> str:
    for a, b in UNESCAPE:
        s = s.replace(a, b)
    return s


def tabs_to_spaces(s: str) -> str:
    """Phrase and addition matching treats a tab as a space.

    Reconstructions keep tabs where they sit, but nobody types a tab into a
    phrase list: a phrase that runs across a caption column would otherwise
    never match.
    """
    return s.replace("\t", " ")


def load_document_xml(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as z:
        return z.read("word/document.xml").decode("utf-8")


def load_part(docx_path: Path, name: str):
    """A zip part as text, or None if the package does not have it."""
    with zipfile.ZipFile(docx_path) as z:
        try:
            return z.read(name).decode("utf-8")
        except KeyError:
            return None


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


# Tracked changes nest. Striking text inside another author's pending insertion
# is written <w:ins them><w:del us>…</w:del></w:ins> — "X deleted text Y
# inserted" — and a flat ins-or-del split of the paragraph would credit that
# struck text to the insertion and show it in accept-all. Walking the open and
# close tags with a stack ties every piece of text to every change around it.
# Self-closing <w:ins/> and <w:del/> mark a paragraph mark or a property as
# changed; they contain nothing and never enter the stack.
CHANGE_TAG = (
    r"<w:(?P<open>ins|del)\b(?P<attrs>[^>]*?)(?P<selfclose>/?)>"
    r"|</w:(?P<close>ins|del)>"
)
CHANGE_TAG_RE = re.compile(CHANGE_TAG, re.S)
TEXT_SCAN = re.compile(
    CHANGE_TAG
    + r"|<w:(?:t|delText)(?:\s[^>]*)?>(?P<text>.*?)</w:(?:t|delText)>"
    + r"|(?P<tab><w:tab\s*/>)",
    re.S,
)
RUN_SCAN = re.compile(CHANGE_TAG + r"|(?P<run><w:r\b[^>]*(?<!/)>.*?</w:r>)", re.S)


def scan(fragment: str, pattern):
    """Yield (match, enclosing) for each non-change match of `pattern`.

    `enclosing` is a tuple of (kind, author) for every open <w:ins>/<w:del>
    around the match, outermost first.
    """
    stack = []
    for m in pattern.finditer(fragment):
        if m.group("open"):
            if not m.group("selfclose"):
                a = AUTHOR.search(m.group("attrs"))
                stack.append((m.group("open"), a.group(1) if a else ""))
        elif m.group("close"):
            if stack:
                stack.pop()
        else:
            yield m, tuple(stack)


def acceptor(mode: str, author=None):
    """Which authors' changes a view accepts.

    Without an author, `mode` applies to every change. With one, it applies
    to that author's changes only and everyone else's are resolved the other
    way: ("original", us) is the counterparty's view — their pending changes
    accepted, ours rejected.
    """
    if mode not in ("accepted", "original"):
        raise ValueError(f"mode must be 'accepted' or 'original', not {mode!r}")
    base = mode == "accepted"
    if author is None:
        return lambda who: base
    return lambda who: base if who == author else not base


def kept(enclosing, accepts) -> bool:
    """Inserted content survives if accepted; deleted content if rejected."""
    return all((kind == "ins") == accepts(who) for kind, who in enclosing)


def render(paragraph: str, mode: str, author=None) -> str:
    """mode='accepted' applies suggestions; mode='original' rejects them.

    `author` narrows the mode to one author's changes; see acceptor().
    """
    accepts = acceptor(mode, author)
    out = []
    for m, enclosing in scan(paragraph, TEXT_SCAN):
        if kept(enclosing, accepts):
            out.append("\t" if m.group("tab") else m.group("text"))
    return unescape("".join(out))


def mark_changes(paragraph: str):
    """[(kind, author)] for every tracked change on the paragraph MARK itself.

    A mark can carry two: another author's insertion and our deletion of the
    paragraph they inserted. Only the pPr's own <w:rPr> counts — a pPrChange
    records former properties, not a pending change to the mark.
    """
    ppr = re.match(r"<w:p(?:\s[^>]*)?>\s*(<w:pPr>.*?</w:pPr>)", paragraph, re.S)
    if not ppr:
        return []
    body = ppr.group(1).split("<w:pPrChange")[0]
    rpr = re.search(r"<w:rPr>(.*?)</w:rPr>", body, re.S)
    if not rpr:
        return []
    out = []
    for m in re.finditer(r"<w:(ins|del)\b[^>]*>", rpr.group(1).split("<w:rPrChange")[0]):
        a = AUTHOR.search(m.group(0))
        out.append((m.group(1), a.group(1) if a else ""))
    return out


def mark_change(paragraph: str):
    """'ins', 'del' or None — whether the paragraph MARK itself is tracked."""
    marks = mark_changes(paragraph)
    return marks[0][0] if marks else None


def reconstruct_paragraphs(xml: str, mode: str, author=None):
    """The paragraphs of a view, as a list; see reconstruct()."""
    accepts = acceptor(mode, author)
    out = []
    for p in paragraphs(xml):
        if not all((kind == "ins") == accepts(who) for kind, who in mark_changes(p)):
            continue
        out.append(render(p, mode, author))
    return out


def reconstruct(xml: str, mode: str, author=None) -> str:
    """
    A paragraph whose MARK is tracked disappears entirely in one of the two
    versions, rather than collapsing to a blank line.

    Rejecting an inserted paragraph removes it, mark and all; accepting a
    deleted one does the same. Emitting a line for it regardless makes a clean
    redline look like it left stray blank lines behind — which sends the
    reviewer hunting a defect that is not in the document. This is the mirror
    of the Structure check, which catches the opposite error: runs struck while
    the mark survives.

    `author` is optional: without it `mode` applies to every change; with it,
    to that author's changes only (see acceptor()).
    """
    return "\n".join(reconstruct_paragraphs(xml, mode, author))


def suggestions(xml: str):
    """Yield (author, kind, text) for every tracked change, in document order."""
    for m in INS_DEL.finditer(xml):
        text = unescape(flow_text(m.group(3)))
        if text.strip():
            yield m.group(2), m.group(1), text


# ---------------------------------------------------------------------------
# Effective font face and size
# ---------------------------------------------------------------------------

def rpr_body(fragment: str) -> str:
    """The first <w:rPr> in a run or style, without its tracked former state.

    An <w:rPrChange> holds the formatting *before* a tracked format change,
    inside its own nested <w:rPr>. Reading through it reports the old size as
    the current one.
    """
    m = re.search(r"<w:rPr>(.*?)</w:rPr>", fragment, re.S)
    return m.group(1).split("<w:rPrChange")[0] if m else ""


def rpr_face_size(rpr: str):
    """(face, half-point size) declared by an rPr body; None where unset.

    A theme font reference beats an explicit w:ascii in Word, so it wins here.
    """
    face = size = None
    f = re.search(r"<w:rFonts\b[^>]*>", rpr)
    if f:
        t = re.search(r'w:asciiTheme="([^"]+)"', f.group(0))
        a = re.search(r'w:ascii="([^"]+)"', f.group(0))
        face = f"theme:{t.group(1)}" if t else (a.group(1) if a else None)
    z = re.search(r'<w:sz w:val="(\d+)"', rpr)
    if z:
        size = z.group(1)
    return face, size


class Styles:
    """Just enough of styles.xml to resolve a run's face and size.

    Word resolves character formatting in layers: docDefaults, then the
    paragraph style (and everything it is basedOn), then the character style,
    then the run's own rPr. The nearest layer that declares a property wins.
    """

    def __init__(self, styles_xml):
        self.defaults = (None, None)
        self.styles = {}
        self.default_para = None
        if not styles_xml:
            return
        d = re.search(r"<w:rPrDefault>(.*?)</w:rPrDefault>", styles_xml, re.S)
        if d:
            self.defaults = rpr_face_size(rpr_body(d.group(1)))
        for m in re.finditer(r"<w:style\b([^>]*)>(.*?)</w:style>", styles_xml, re.S):
            attrs, body = m.group(1), m.group(2)
            sid = re.search(r'w:styleId="([^"]+)"', attrs)
            typ = re.search(r'w:type="([^"]+)"', attrs)
            if not sid or not typ:
                continue
            based = re.search(r'<w:basedOn w:val="([^"]+)"', body)
            self.styles[(typ.group(1), sid.group(1))] = (
                based.group(1) if based else None,
                rpr_face_size(rpr_body(body)),
            )
            if typ.group(1) == "paragraph" and re.search(r'w:default="(?:1|true|on)"', attrs):
                self.default_para = sid.group(1)

    def chain(self, typ, sid):
        face = size = None
        seen = set()
        while sid and (typ, sid) in self.styles and sid not in seen:
            seen.add(sid)
            based, (f, s) = self.styles[(typ, sid)]
            face, size = face or f, size or s
            sid = based
        return face, size

    def resolve(self, run_rpr: str, pstyle, rstyle):
        if (pstyle is None or ("paragraph", pstyle) not in self.styles):
            pstyle = self.default_para
        layers = [
            rpr_face_size(run_rpr),
            self.chain("character", rstyle),
            self.chain("paragraph", pstyle),
            self.defaults,
        ]
        face = next((f for f, _ in layers if f), None)
        size = next((s for _, s in layers if s), None)
        return face, size


def paragraph_style(paragraph: str):
    ppr = re.match(r"<w:p(?:\s[^>]*)?>\s*(<w:pPr>.*?</w:pPr>)", paragraph, re.S)
    if not ppr:
        return None
    m = re.search(r'<w:pStyle w:val="([^"]+)"', ppr.group(1).split("<w:pPrChange")[0])
    return m.group(1) if m else None


def describe_font(pair) -> str:
    face, size = pair
    return f"{face or '(no face)'} {int(size) / 2:g}pt" if size else f"{face or '(no face)'} ?pt"


def check_inserted_formatting(xml: str, styles_xml=None):
    """Inserted runs whose effective face or size differs from the text beside them.

    A run authored without <w:sz> or <w:rFonts> inherits — but from where
    depends on the paragraph. In a bulleted list the ListParagraph style
    commonly supplies the face, and every run in the paragraph, the brand's
    own included, declares only <w:sz> and <w:color>. An inserted run that
    copies that rPr exactly renders identically. Comparing raw rPr against the
    document's most common declarations flagged every such run as "inherits
    docDefaults", including edits the counterparty made in Word, and the FAIL
    had to be explained away on every round.

    So both sides are resolved the way Word resolves them — run rPr, then the
    character style, then the paragraph style and its basedOn chain, then
    docDefaults — and an inserted run is compared with the nearest surviving
    (neither inserted nor deleted) run in its own paragraph. Only a paragraph
    with no surviving run (a wholly new clause) is compared with the
    dominant resolved formatting of paragraphs in the same style, and failing
    that of the whole document.

    Returns (dominant, problems): dominant is the (face, size) most body text
    resolves to; problems is [(text, got, expected, where)].
    """
    styles = Styles(styles_xml)
    paras = []
    by_style = collections.defaultdict(collections.Counter)
    overall = collections.Counter()
    for p in paragraphs(xml):
        pstyle = paragraph_style(p)
        runs = []
        for m, enclosing in scan(p, RUN_SCAN):
            run = m.group("run")
            text = unescape(flow_text(run))
            if not text.strip():
                continue  # tabs, breaks, field codes: nothing to size
            rpr = rpr_body(run)
            rs = re.search(r'<w:rStyle w:val="([^"]+)"', rpr)
            resolved = styles.resolve(rpr, pstyle, rs.group(1) if rs else None)
            kinds = {k for k, _ in enclosing}
            state = "del" if "del" in kinds else "ins" if "ins" in kinds else "plain"
            runs.append((state, resolved, text))
            if state == "plain":
                by_style[pstyle][resolved] += len(text)
                overall[resolved] += len(text)
        paras.append((pstyle, runs))

    dominant = overall.most_common(1)[0][0] if overall else None
    problems = []
    for pstyle, runs in paras:
        plain = [i for i, r in enumerate(runs) if r[0] == "plain"]
        for i, (state, resolved, text) in enumerate(runs):
            if state != "ins":
                continue
            if plain:
                # Nearest by run distance; the preceding run wins a tie, since
                # an insertion normally continues the text before it.
                j = min(plain, key=lambda k: (abs(k - i), k > i))
                expected, where = runs[j][1], "beside it"
            elif by_style.get(pstyle):
                expected, where = by_style[pstyle].most_common(1)[0][0], "in this paragraph style"
            else:
                expected, where = dominant, "in the document"
            if expected is not None and resolved != expected:
                problems.append((" ".join(text.split()), resolved, expected, where))
    return dominant, problems


def check_paragraph_structure(xml: str):
    """Paragraphs whose text is entirely struck but whose paragraph mark survives.

    Accepting such a suggestion removes the words and leaves the empty paragraph
    behind — a blank line, or worse a bullet with nothing after it. Deleting a
    whole paragraph means deleting its runs *and* marking its paragraph mark
    deleted, which in OOXML is a <w:del> inside <w:pPr><w:rPr>.

    The exception is a paragraph whose pPr carries a section break (<w:sectPr>).
    Deleting that mark merges its section into the next one — a two-column
    signature block's layout spreads into whatever follows, or the section
    holding the contract's headers and footers loses them. Keeping the mark is
    correct there, and costs one empty paragraph on accept. Those come back as
    kind "section" so they can be reported without failing the check.
    """
    orphans = []
    for p in paragraphs(xml):
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
            kind = ("section" if "<w:sectPr" in ppr_text
                    else "bullet" if "<w:numPr>" in ppr_text else "paragraph")
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
    for p in paragraphs(xml):
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


def paragraph_divergence(base_paras, red_paras):
    """(index, baseline window, redline window) of the first differing paragraph.

    A leaked empty paragraph passes a whitespace-blind text comparison and
    shows up in Word as a blank line, so the count is compared separately and
    this locates where the two lists part company. Whitespace (tabs included)
    is normalised so only a real difference is reported.
    """
    norm = lambda s: " ".join(tabs_to_spaces(s).split())
    b, r = [norm(p) for p in base_paras], [norm(p) for p in red_paras]
    i = next((k for k, (x, y) in enumerate(zip(b, r)) if x != y), min(len(b), len(r)))

    def window(paras):
        joined = " ¶ ".join(paras)
        off = sum(len(p) + 3 for p in paras[:i])
        return joined[max(0, off - 60) : off + 60]

    return i, window(b), window(r)


# ---------------------------------------------------------------------------
# Other authors' changes, and the rest of the package
# ---------------------------------------------------------------------------

def change_elements(xml: str):
    """{w:id: [element]} for every <w:ins>/<w:del>, containers and marks alike."""
    para_spans = [(s, e, xml[s:e]) for s, e in paragraph_spans(xml)]
    starts = [s for s, _, _ in para_spans]

    def paragraph_at(pos):
        k = bisect.bisect_right(starts, pos) - 1
        if k >= 0 and para_spans[k][0] <= pos < para_spans[k][1]:
            return para_spans[k][2]
        return ""

    out = collections.defaultdict(list)
    stack = []
    for m in CHANGE_TAG_RE.finditer(xml):
        if m.group("open"):
            attrs = m.group("attrs")
            a = AUTHOR.search(attrs)
            i = re.search(r'w:id="([^"]*)"', attrs)
            el = {
                "kind": m.group("open"),
                "tag": m.group(0),
                "author": a.group(1) if a else "",
                "id": i.group(1) if i else "",
                "mark": bool(m.group("selfclose")),
                "ancestors": tuple((e["kind"], e["author"]) for e in stack),
                "paragraph": paragraph_at(m.start()),
                "content": "",
                "open_end": m.end(),
            }
            if el["mark"]:
                out[el["id"]].append(el)
            else:
                stack.append(el)
        elif m.group("close") and stack:
            el = stack.pop()
            el["content"] = xml[el["open_end"] : m.start()]
            out[el["id"]].append(el)
    return out


def content_signature(content: str, ours: str):
    """Per-character (text, formatting, other changes) with OUR changes ignored.

    Striking part of another author's insertion splits their run and wraps the
    struck piece in our <w:del>; rejecting our change restores their text
    exactly. So our deletions are looked through, and anything else — a
    changed word, a changed rPr, an insertion of ours nested inside theirs —
    still shows as a difference.
    """
    sig = []
    for m, enclosing in scan(content, RUN_SCAN):
        run = m.group("run")
        foreign = tuple(e for e in enclosing if not (e[0] == "del" and e[1] == ours))
        rpr = " ".join(rpr_body(run).split())
        for ch in unescape(flow_text(run)):
            sig.append((ch, rpr, foreign))
    return sig


def classify_change(base_el, red_el, ours: str) -> str:
    if red_el["tag"] != base_el["tag"]:
        return "changed"
    wrapped = any(k == "del" and a == ours for k, a in red_el["ancestors"]) or any(
        k == "del" and a == ours for k, a in mark_changes(red_el["paragraph"])
    )
    if red_el["content"] == base_el["content"]:
        return "wrapped" if wrapped else "identical"
    if content_signature(red_el["content"], ours) == content_signature(base_el["content"], ours):
        # Only differs by our deletions inside it: acceptable by construction.
        return "wrapped"
    return "changed"


def compare_foreign_changes(base_xml: str, xml: str, ours: str):
    """Every baseline change by someone other than `ours`, located by w:id.

    Returns {author: Counter(status)} and [(author, id, kind, status, text)]
    for the defects. Statuses: identical; wrapped (present unchanged, but now
    inside our deletion or in a paragraph whose mark we deleted — what striking
    a paragraph that holds their suggestion looks like); changed; missing.
    """
    base, red = change_elements(base_xml), change_elements(xml)
    rank = {"identical": 0, "wrapped": 1, "changed": 2}
    counts = collections.defaultdict(collections.Counter)
    defects = []
    for cid, items in base.items():
        for b in items:
            if b["author"] == ours:
                continue
            cands = [r for r in red.get(cid, []) if r["kind"] == b["kind"] and r["author"] == b["author"]]
            if not cands:
                status = "missing"
            else:
                status = min((classify_change(b, r, ours) for r in cands), key=rank.get)
            counts[b["author"]][status] += 1
            if status in ("changed", "missing"):
                text = "paragraph mark" if b["mark"] else " ".join(unescape(flow_text(b["content"])).split())
                defects.append((b["author"], cid, b["kind"], status, text))
    return counts, defects


PROPERTY_PARTS = {
    "docProps/core.xml": "document properties: author, last modified by, dates",
    "docProps/app.xml": "application properties: generating app, counts",
}


def compare_package(base_path: Path, path: Path):
    """(added, removed, changed, baseline parts), word/document.xml excepted."""
    with zipfile.ZipFile(base_path) as zb, zipfile.ZipFile(path) as zr:
        bn = set(zb.namelist()) - {"word/document.xml"}
        rn = set(zr.namelist()) - {"word/document.xml"}
        changed = sorted(n for n in bn & rn if zb.read(n) != zr.read(n))
    return sorted(rn - bn), sorted(bn - rn), changed, bn


def phrase_context(xml: str, phrase: str):
    """Was the clause containing this phrase edited at all?

    Distinguishes two very different states that a plain presence test cannot:
    a clause nobody touched, and a clause where a protective sentence was added
    while the adverse wording was left standing beside it. The second reads as
    done on a tracking table and leaves the contract contradicting itself.
    """
    touched = False
    phrase = tabs_to_spaces(phrase)
    for p in paragraphs(xml):
        if phrase in tabs_to_spaces(render(p, "accepted")):
            if re.search(r"<w:ins\b", p) or re.search(r"<w:del\b", p):
                touched = True
    return touched


def parse_phrases(path: Path):
    """One entry per line: "label :: exact adverse wording".

    Checklist labels start with "#" ("#14 unpaid extension :: ..."), so "#"
    alone cannot mark a comment. The rule is the "# " that no checklist label
    has: a hash FOLLOWED BY WHITESPACE opens a comment, a hash followed by
    anything else opens a label.

    Without that distinction a header comment written in the natural form --
    "# label :: exact wording from the brand's draft" -- parses as a real
    entry, is absent from both versions, and reports as "not found in either"
    forever. It costs one phantom on every run, and a gate that always fails by
    one is a gate people stop reading.
    """
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line == "#" or line[:1] == "#" and line[1:2].isspace():
            continue
        label, sep, phrase = line.partition("::")
        if sep:
            items.append((label.strip(), phrase.strip()))
        else:
            items.append((line[:48], line))
    return items


# Must-have items in references/review-checklist.md, plus the representations
# sweep. Nice-to-haves (#17-#22) are deliberately absent: leaving one out is a
# commercial choice, leaving out a must-have is a review that never looked.
MUST_HAVES = [str(n) for n in range(1, 17)] + ["23", "24", "reps"]
ITEM_LABEL = re.compile(r"#(\d+|reps)([a-z])?\b", re.I)

# Sub-checks the checklist tags "[#4e]" because a whole item can be named while
# they go missing. Naming "#4" satisfies item 4 and none of these; each must be
# named by its own tag. Observed: a second run of the same contract named every
# must-have and still dropped mutual confidentiality, the exclusivity carve-outs,
# the creator's termination consequences and the release scope that the first
# run had made.
SUBCHECKS = {
    "1a": "brand indemnity includes a duty to defend",
    "1b": "brand indemnity reaches materials Brand supplied OR approved",
    "2a": "confidentiality runs both directions",
    "3d": "cap carve-outs include payment obligations",
    "4d": "termination pays for work performed, in every route",
    "4e": "content handover on termination conditioned on payment",
    "4g": "every termination route has a payment consequence",
    "5b": "creator's reciprocal termination right, with its consequences",
    "7a": "grant is non-exclusive",
    "14f": "creator's own turnaround windows (floors, received not shipped)",
    "15d": "unpaid activity carved out of exclusivity",
    "15e": "incidental appearance carved out of exclusivity",
    "15g": "time-window exclusivity bound to the brand's category",
    "22a": "AI / digital-replica limit present, drafted, or offered as recommended",
    "23a": "release and injunction waiver limited to authorized use",
}


def coverage(sources):
    """({item: hits}, {subcheck: hits}) where hits are [(source, label, text)].

    The phrase and additions gates only check what they are given. A review
    that never looked at the indemnity writes no indemnity line, and both gates
    pass. Counting item numbers across every file the review produced is the
    only way to see an item that nobody decided to drop -- it simply was never
    opened. Observed: a review scoped itself to the creator's three-line brief,
    and one-way indemnity, confidentiality, the missing liability cap and the
    morals trigger all went out untouched behind a clean audit.

    A label may name several items ("#1 #3 carve-outs"); each counts. A
    sub-check tag ("#4e") also counts for its item.
    """
    found = {item: [] for item in MUST_HAVES}
    subs = {sub: [] for sub in SUBCHECKS}
    for source, items in sources:
        for label, text in items:
            for m in ITEM_LABEL.finditer(label):
                item = m.group(1).lower()
                if item in found:
                    found[item].append((source, label, text))
                sub = item + (m.group(2) or "").lower()
                if sub in subs:
                    subs[sub].append((source, label, text))
    return found, subs


ADDITION_COUNT = re.compile(r"^(.*?)\s*::\s*x(\d+)$", re.S)


def expected_count(text: str):
    """Split "wording :: x3" into ("wording", 3); plain wording expects 1.

    The checklist asks for some wording in several places -- the same payment
    phrase in every termination route. "Exactly once" failed that on the
    second copy, so a run satisfied the gate by writing it once, in the
    force-majeure clause, and left the termination clause unpaid.
    """
    m = ADDITION_COUNT.match(text)
    return (m.group(1).strip(), int(m.group(2))) if m else (text, 1)


def prior_edits(prior_xml: str, accepted: str):
    """Edits the prior redline made that this one's accepted text lacks.

    Diffs the prior's reject-all against its accept-all word by word; each
    difference is one prior edit. The prior's accept-all is then aligned with
    this redline's, and each edit is judged by its own words, so rewording a
    neighbour does not count as dropping it:

      words it inserted    all still aligned -> carried; none -> DROPPED;
                           some -> CHANGED (the missing words are shown)
      words it struck      back in this redline at the same spot -> DROPPED

    A one-word insertion ("material") is caught as well as a clause.

    Returns (reports, total) where reports is [(state, old, new, missing)].
    """
    words = lambda s: " ".join(s.split()).split(" ")
    old = words(reconstruct(prior_xml, "original"))
    new = words(reconstruct(prior_xml, "accepted"))
    cur = words(accepted)
    kept = [False] * len(new)
    back = []  # (prior index, current words) wherever this run has words the prior lacks
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, new, cur, autojunk=False).get_opcodes():
        if tag == "equal":
            kept[i1:i2] = [True] * (i2 - i1)
        elif j2 > j1:
            back.append((i1, i2, " " + " ".join(cur[j1:j2]) + " "))
    reports, total = [], 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == "equal" or "".join(old[i1:i2]) == "".join(new[j1:j2]):
            continue
        total += 1
        o, n = " ".join(old[i1:i2]), " ".join(new[j1:j2])
        if j2 > j1:
            lost = [w for w, k in zip(new[j1:j2], kept[j1:j2]) if not k]
            if len(lost) == j2 - j1:
                reports.append(("DROPPED", o, n, ""))
            elif lost:
                reports.append(("CHANGED", o, n, " ".join(lost)))
        elif any(a <= j1 <= b and " " + o + " " in s for a, b, s in back):
            reports.append(("DROPPED", o, n, ""))
    return reports, total


def main() -> int:
    # Contract text is printed verbatim; a character the console cannot encode
    # should degrade to "?" rather than abort the audit halfway through.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", type=Path, help="document exported from Google Docs as .docx")
    ap.add_argument("--check", type=Path, help="file of phrases to test against the accepted version")
    ap.add_argument("--additions", type=Path, help="file of added text that must appear exactly once in the accepted version")
    ap.add_argument("--baseline", type=Path, help="the brand's untouched draft (.docx); verifies no text was destroyed")
    ap.add_argument("--author", help="author name of OUR suggestions; enables the counterparty view and, "
                                     "with --baseline, the other-authors check")
    ap.add_argument("--write-dir", type=Path, help="write accepted.txt and original.txt (and counterparty.txt with --author) here")
    ap.add_argument("--list", action="store_true", help="print every suggestion")
    ap.add_argument("--coverage", type=Path, nargs="*", metavar="FILE",
                    help="gate on every must-have checklist item, and every tagged sub-check "
                         "('#4e'), being named by a label in --check, --additions, or these "
                         "files (declined.md, a list of items found present)")
    ap.add_argument("--prior", type=Path, metavar="DOCX",
                    help="an earlier redline of the same contract; gate on every edit it made "
                         "being in this one or explained in --prior-ok")
    ap.add_argument("--prior-ok", type=Path, metavar="FILE",
                    help="'label :: fragment' lines explaining prior edits this redline "
                         "deliberately drops; the fragment is any words of the prior edit")
    args = ap.parse_args()

    for p in (args.docx, args.check, args.additions, args.baseline, args.prior, args.prior_ok,
              *(args.coverage or [])):
        if p is not None and not p.exists():
            print(f"error: {p} not found", file=sys.stderr)
            return 2

    xml = load_document_xml(args.docx)
    accepted = reconstruct(xml, "accepted")
    original_paras = reconstruct_paragraphs(xml, "original")
    original = "\n".join(original_paras)
    counterparty = reconstruct(xml, "original", args.author) if args.author else None
    sugg = list(suggestions(xml))
    authors = sorted(set(AUTHOR.findall(xml)))

    print(f"{args.docx.name}")
    print(f"  suggestions : {len(sugg)}  ({sum(1 for a,k,t in sugg if k=='ins')} insertions, "
          f"{sum(1 for a,k,t in sugg if k=='del')} deletions)")
    print(f"  authors     : {', '.join(authors) if authors else 'none'}")
    print(f"  accepted    : {len(accepted):,} chars")
    print(f"  original    : {len(original):,} chars")
    if counterparty is not None:
        print(f"  counterparty: {len(counterparty):,} chars (others' changes accepted, {args.author}'s rejected)")
        if args.author not in authors:
            print(f"\n  WARNING: no change in this document is by {args.author!r}. Every change will")
            print("  be treated as the counterparty's. Check the spelling against the authors above.")

    if not sugg:
        print("\n  WARNING: no tracked changes found. Either nothing was edited, or the")
        print("  edits were made directly rather than as suggestions.")

    if args.write_dir:
        args.write_dir.mkdir(parents=True, exist_ok=True)
        views = {"accepted.txt": accepted, "original.txt": original}
        if counterparty is not None:
            views["counterparty.txt"] = counterparty
        for name, text in views.items():
            (args.write_dir / name).write_text(text, encoding="utf-8", newline="")
        print(f"\n  wrote {', '.join(views)} to {args.write_dir} (tabs are literal \\t)")

    if args.list:
        print("\nSuggestions in document order:")
        for author, kind, text in sugg:
            verb = "ADD" if kind == "ins" else "DEL"
            flat = " ".join(text.split())
            print(f"  [{author}] {verb}: {flat[:110]}{'…' if len(flat) > 110 else ''}")

    failures = 0

    found = check_paragraph_structure(xml)
    sections = [o for o in found if o[0] == "section"]
    orphans = [o for o in found if o[0] != "section"]
    print("\nStructure check — will any emptied paragraph survive acceptance?\n")
    if not orphans:
        print("  PASS — every fully struck paragraph also has its paragraph mark deleted.")
    for _, text in sections:
        print(f"  NOTE — mark kept on a struck paragraph carrying a section break: \"{text[:60]}…\"")
        print("         Correct: deleting it would merge two sections. One empty paragraph")
        print("         remains on accept.")
    if orphans:
        failures += 1
        print(f"  FAIL — {len(orphans)} paragraph(s) struck without deleting the paragraph mark.")
        print("  Accepting these removes the words and leaves an empty line or bullet behind.\n")
        for kind, text in orphans[:8]:
            print(f"    empty {kind} would remain: \"{text[:90]}…\"")

    dominant, fmt_problems = check_inserted_formatting(xml, load_part(args.docx, "word/styles.xml"))
    print("\nFormatting check — does each inserted run render in the face and size of the text beside it?\n")
    if dominant:
        print(f"  body text resolves to {describe_font(dominant)}")
    if not fmt_problems:
        print("  PASS — every inserted run resolves (run, character style, paragraph style,")
        print("  docDefaults) to the same face and size as the nearest surviving run.")
    else:
        failures += 1
        print(f"  FAIL — {len(fmt_problems)} inserted run(s) resolve to a different face or size than")
        print("  the surrounding text and will render visibly different. Copy the <w:rPr> of")
        print("  the adjacent body run.\n")
        for text, got, expected, where in fmt_problems[:8]:
            print(f"    {describe_font(got)}, but {describe_font(expected)} {where}: \"{text[:70]}…\"")

    if args.baseline:
        base_xml = load_document_xml(args.baseline)
        base_paras = reconstruct_paragraphs(base_xml, "original")
        base = "\n".join(base_paras)
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

        # Paragraph count: the text comparison above is blind to an empty
        # paragraph, which is exactly what a leaked blank spacer or an inserted
        # paragraph without its <w:ins/> mark looks like on reject-all.
        if len(base_paras) == len(original_paras):
            print(f"  PARAGRAPHS: PASS — {len(original_paras)} on reject-all, as in the baseline.")
        else:
            failures += 1
            i, bw, rw = paragraph_divergence(base_paras, original_paras)
            print(f"  PARAGRAPHS: FAIL — {len(base_paras)} in baseline, {len(original_paras)} on reject-all;")
            print(f"  first divergence at paragraph {i} (0-based):")
            print(f"      baseline: …{bw}…")
            print(f"      redline : …{rw}…")
            print("  An extra empty paragraph is usually an inserted paragraph whose mark was")
            print("  not tracked as inserted (<w:ins/> in <w:pPr><w:rPr>).")

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

        # Package: a redline changes word/document.xml and nothing else. Any
        # other part that differs — styles, numbering, settings, and above all
        # the document properties, which record who last saved the file and
        # with what — is a change the creator did not make and cannot see.
        added, removed, changed, base_parts = compare_package(args.baseline, args.docx)
        if not (added or removed or changed):
            present = [n for n in PROPERTY_PARTS if n in base_parts]
            print(f"  PACKAGE: PASS — all {len(base_parts)} other parts byte-identical to the baseline"
                  + (f" (including {' and '.join(present)})" if present else ""))
        else:
            failures += 1
            print(f"  PACKAGE: FAIL — only word/document.xml may differ from the baseline")
            for label, names in (("added", added), ("removed", removed), ("changed", changed)):
                for n in names:
                    note = f"  <- {PROPERTY_PARTS[n]}" if n in PROPERTY_PARTS else ""
                    print(f"          {label}: {n}{note}")

        # Other authors: the claim the creator most wants to make is that the
        # counterparty's own pending suggestions are exactly as they left them.
        print("\nOther authors' changes — are the counterparty's suggestions exactly as they left them?\n")
        if not args.author:
            print("  skipped — pass --author NAME (the author of our suggestions) to run it.")
        else:
            counts, defects = compare_foreign_changes(base_xml, xml, args.author)
            if not counts:
                print(f"  PASS — the baseline has no tracked changes by anyone but {args.author}.")
            for who in sorted(counts):
                c = counts[who]
                print(f"  {who}: {sum(c.values())} in baseline — {c['identical']} identical, "
                      f"{c['wrapped']} wrapped by our deletion, {c['changed']} changed, {c['missing']} missing")
            if counts and not defects:
                print("  PASS — every other author's change is present and unaltered. \"Wrapped by our")
                print("  deletion\" means we struck text that contains their suggestion; rejecting")
                print("  our deletion restores theirs exactly.")
            elif defects:
                failures += 1
                print(f"\n  FAIL — {len(defects)} of another author's changes altered or removed:\n")
                for who, cid, kind, status, text in defects[:12]:
                    print(f"    [{status}] {who} {kind} id={cid}: \"{text[:80]}\"")

    if args.check:
        items = parse_phrases(args.check)
        print(f"\nCompleteness check — is the adverse wording still in the accepted version?\n")
        width = max((len(l) for l, _ in items), default=10)
        acc_n, org_n = tabs_to_spaces(accepted), tabs_to_spaces(original)
        cp_n = tabs_to_spaces(counterparty) if counterparty is not None else None
        # Counted separately from `failures`, which the structure, formatting and
        # fidelity checks also increment. Folding those into this tally makes the
        # printed total disagree with the lines printed above it.
        unresolved = absent = 0
        for label, phrase in items:
            phrase = tabs_to_spaces(phrase)
            n_acc = acc_n.count(phrase)
            n_org = org_n.count(phrase)
            if n_org == 0 and n_acc == 0:
                # Not gating: nothing adverse survives in the accepted text.
                # Usually the phrase existed only in the counterparty's pending
                # text (a mid-edit fragment of theirs), or it was mistyped.
                absent += 1
                n_cp = cp_n.count(phrase) if cp_n is not None else 0
                if n_cp:
                    state = f"only in the counterparty's pending text (x{n_cp}) — not gating"
                else:
                    state = "absent from both — not gating"
            elif n_acc == 0:
                state = f"resolved (was x{n_org})"
            elif n_org == 0:
                unresolved += 1
                failures += 1
                state = f"STILL PRESENT (x{n_acc}) — introduced by a pending insertion"
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
        print(f"\n  {unresolved} of {len(items)} unresolved"
              + (f"; {absent} absent from both (not gating)" if absent else ""))
        print("\n  \"WAS edited\" is the dangerous one: something was changed in that clause")
        print("  while the adverse wording stayed. Usually a protective sentence was added")
        print("  beside the problem instead of replacing it, leaving the clause to")
        print("  contradict itself. Read the whole clause before accepting it as done.")
        print("\n  Counts matter: a phrase can appear in several clauses, or in both the")
        print("  body and an exhibit. 'PARTIAL' means one instance was handled and")
        print("  another was not — check which. A phrase that survives may also have")
        print("  been correctly narrowed by an insertion nearby, so read the context")
        print("  before recording a miss.")
        if absent:
            print("\n  'Absent from both' is either a phrase that only ever existed in the")
            print("  counterparty's pending text or a typo in the phrase list."
                  + ("" if args.author else " Pass --author to\n  tell the two apart."))

    if args.additions:
        items = parse_phrases(args.additions)
        print("\nAdditions check — is every clause we added in the accepted version, as often as intended?\n")
        width = max((len(l) for l, _ in items), default=10)
        acc_n = tabs_to_spaces(accepted)
        bad = 0
        for label, text in items:
            text, want = expected_count(text)
            n = acc_n.count(tabs_to_spaces(text))
            if n == want:
                state = "PASS" if want == 1 else f"PASS (x{n})"
            elif n == 0:
                state = "FAIL — not in the accepted version"
            elif want == 1:
                state = f"FAIL — appears {n} times — check for a duplicate"
            else:
                state = f"FAIL — appears {n} times, expected {want}"
            if n != want:
                bad += 1
                failures += 1
            print(f"  {label:<{width}}  {state}")
        print(f"\n  {bad} of {len(items)} failing")
        if bad:
            print("  Missing usually means an edit aborted or was anchored somewhere else;")
            print("  a duplicate usually means an edit ran twice or a clause was pasted into")
            print("  two places.")

    if args.coverage is not None:
        sources = [(p.name, parse_phrases(p))
                   for p in (args.check, args.additions, *args.coverage) if p is not None]
        found, subs = coverage(sources)
        print("\nCoverage check — was every must-have checklist item looked at?\n")
        if not sources:
            print("  No label files given. Pass --check, --additions, or files after --coverage.")
        missing = [item for item in MUST_HAVES if not found[item]]
        for item in MUST_HAVES:
            hits = found[item]
            if not hits:
                state = "MISSING — no label names this item"
            else:
                by = {}
                for source, _, _ in hits:
                    by[source] = by.get(source, 0) + 1
                state = ", ".join(f"{s} x{n}" if n > 1 else s for s, n in by.items())
                # A line in a coverage file carries its reason ("present (§12)",
                # "conceded 9/22"); show the first so the reader can judge it.
                note = next((t for s, _, t in hits if s not in
                             {p.name for p in (args.check, args.additions) if p}), None)
                if note:
                    state += f" — {' '.join(note.split())[:70]}"
            print(f"  #{item:<5} {state}")
        print(f"\n  {len(missing)} of {len(MUST_HAVES)} must-have items never named")
        if missing:
            failures += 1
            print("  An item no file names was never reviewed — not reviewed and found fine, not")
            print("  reviewed and declined. Review it, then add a phrase, an addition, or a")
            print("  line in declined.md / the present list saying why it needs no edit.")

        print("\n  Tagged sub-checks — the boxes that go missing while their item is named:\n")
        sub_missing = [s for s in SUBCHECKS if not subs[s]]
        for sub, what in SUBCHECKS.items():
            hits = subs[sub]
            state = "MISSING" if not hits else ", ".join(dict.fromkeys(s for s, _, _ in hits))
            print(f"  #{sub:<5} {state:<14} {what}")
        print(f"\n  {len(sub_missing)} of {len(SUBCHECKS)} tagged sub-checks never named")
        if sub_missing:
            failures += 1
            print("  Name each by its tag (\"#4e handover :: ...\") in a phrase, an addition,")
            print("  declined.md or the present list. \"#4\" alone does not cover \"#4e\".")

    if args.prior:
        prior_xml = load_document_xml(args.prior)
        reports, total = prior_edits(prior_xml, accepted)
        oks = parse_phrases(args.prior_ok) if args.prior_ok else []
        norm = lambda s: " ".join(s.split())
        print(f"\nPrior-run check — is every edit {args.prior.name} made also in this redline?\n")
        if "".join(reconstruct(prior_xml, "original").split()) != "".join(original.split()):
            print("  WARNING: the two redlines were not made on the same brand draft; expect")
            print("  false reports wherever the drafts differ.\n")
        unexplained = 0
        for state, old_w, new_w, lost in reports:
            why = next((label for label, frag in oks
                        if norm(frag) and (norm(frag) in old_w or norm(frag) in new_w)), None)
            if why is None:
                unexplained += 1
            print(f"  {state}" + (f" — explained: {why}" if why else ""))
            print(f"      brand : {old_w[:150] or '(nothing — prior inserted here)'}")
            print(f"      prior : {new_w[:150] or '(struck)'}")
            if lost:
                print(f"      lost  : {lost[:150]}")
        print(f"\n  {total - len(reports)} of {total} prior edits carried; "
              f"{len(reports) - unexplained} dropped or changed with a reason; "
              f"{unexplained} unexplained")
        if unexplained:
            failures += 1
            print("  Each unexplained drop is an edit the earlier run made and this one lost.")
            print("  Restore it, or add \"label :: words from the edit\" to --prior-ok saying why")
            print("  it goes (declined by the creator, superseded by a better edit, …). An edit")
            print("  that was reworded, or whose neighbouring words this run changed, also shows")
            print("  here — read it before restoring.")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
