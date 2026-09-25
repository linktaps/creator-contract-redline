#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author tracked changes into a .docx, as native Word / Google Docs suggestions.

    from apply_tracked_changes import Doc

    d = Doc("brand-draft.docx", author="Creator Name")
    d.edit("rep", "sixty (60) days", "thirty (30) days",   label="net-30")
    d.edit("del", " Influencer agrees to pay a termination fee.", label="penalty")
    d.edit("ins_after", "...preceding sentence.", " New sentence.", label="backstop")
    d.edit("del", "the Term", within="During the Term, the Brand", label="term")
    d.save("redline.docx")

Why a script rather than clicking through a browser: every edit asserts its
anchor occurs EXACTLY ONCE and aborts otherwise, so a dropped edit or one
applied twice fails loudly instead of silently. Dropped items are the failure
this whole skill is built around, and this is the cheapest place to make them
impossible.

Re-run it from the pristine brand draft every time rather than editing the
output in place. That keeps the edit list the single source of truth: fixing a
clause means changing one string and re-running, and the reject-all view stays
byte-identical to the draft the brand sent.

Anchors are matched against the document's FLAT TEXT, so an anchor may span
several runs (contracts routinely split a sentence across runs for a single
underlined word). Deleted text (<w:delText>) is not in the flat text; text
inserted by earlier edits in the same script IS — so a `within` context may
legitimately include your own earlier insertions, e.g.
edit("ins_after", ".", new, within="as published by Talent.") after inserting
", as published by Talent" before that period.

Formatting is preserved per fragment: a deletion spanning three runs emits three
<w:r> inside the <w:del>, each keeping its own <w:rPr>.

Edit kinds:
  edit("del",  anchor)              strike anchor
  edit("rep",  anchor, new)         strike anchor, insert new in its place
  edit("ins_after",  anchor, new)   insert new immediately after anchor
  edit("ins_before", anchor, new)   insert new immediately before anchor
      every edit() also takes within= and first=: `within` is a wider string
      that must be unique; `anchor` must occur exactly once inside it (or, with
      first=True, the first occurrence is taken). Narrow the context, never the
      struck text: a non-unique two-word anchor is not a reason to strike more.
  del_multi(anchor, after)          strike anchor as one <w:del> per run. Use it
      when edit() refuses because the anchor spans structural markup — in
      practice almost always bookmarks (comment anchors, _cp_text_*) or
      <w:proofErr> between the runs of one sentence. `after` is unique text
      immediately following anchor; it is the stable reference, because each
      fragment's text leaves the flat index as it is struck. Adjacent
      deletions render as one strike in Word.
  del_para(unique_text)             strike the whole paragraph, runs and mark
  del_blank_para_after(unique_text) strike the blank spacer paragraph after it
  del_para_offset(unique_text, k, expect_prefix)
      strike the k-th paragraph after the one holding unique_text, asserting
      its text starts with expect_prefix ("" = must be blank). This is how the
      second copy of a duplicated paragraph is reached. Delete by offset BEFORE
      deleting the anchor paragraph: once struck, its text leaves the flat
      index and cannot be counted from.
  del_para_range(first_text, last_text, expect_count=None)
      strike a whole block — an exhibit, a release, a series of bullets —from
      the paragraph holding first_text through the one holding last_text,
      blanks and duplicates included, every mark deleted. Use this instead of
      writing a loop: a hand-written one missed the last mark of an exhibit.
  para_after(anchor, [texts])       whole new paragraph(s) after anchor's
      paragraph; "\\t" in a text becomes a real <w:tab/>
  clone_para_after(anchor, subs)    copy anchor's paragraph as a new tracked
      paragraph; subs keyed by exact run text (str) or by index among the
      paragraph's text-bearing runs (int)
  raw_insert_before(marker, xml)    last-resort splice of raw XML; no tracking
  flat()                            the current flat text, for building anchors

Deleting at offset 0 of a run that begins with a <w:tab/> keeps the tab in its
own untouched run ahead of the <w:del>: otherwise accepting the change deletes a
caption tab the edit never meant to touch. An anchor that runs ON into a later
run beginning with a tab or break aborts instead: the flat text has no tab, so
"Use:During" looks like one string, and striking it would take the caption tab
with it.

A paragraph with no sibling paragraph after it (the last in a table cell, text
box or body) keeps its mark when struck: Word cannot delete that mark, so its
text is struck and one empty paragraph remains on accept.

Inserting next to another author's pending insertion never nests <w:ins> in
<w:ins> (Word refuses the file): our insertion goes beside theirs, splitting
their element if the anchor falls inside it. Deleting text they inserted puts
our <w:del> inside their <w:ins>, which records "they inserted, we deleted".

Timestamps: every change carries the time the script ran (UTC, to the second),
or the stamp passed as date=. Nothing is spread out or randomised to look like
typing. w:id starts just above the highest id already in the file, so no id
collides. w16du:dateUtc is written too when the document already declares that
namespace, as current Word does.
"""
import os, re, sys, tempfile, zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_suggestions import SIBLING_GAP, load_document_xml, paragraph_spans  # noqa: E402

# Whatever name you pass shows on every suggestion in the sidebar. There is no
# default: it is the creator's choice (legal name, handle, a manager's), so ask.
DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"

RUN_FULL = re.compile(r"<w:r(?:\s[^>]*)?>(?P<inner>.*?)</w:r>", re.S)
RPR_RE = re.compile(r"^<w:rPr>.*?</w:rPr>", re.S)
# NOTE the `\s` before the attributes: without it this also matches <w:tab/>,
# since "<w:t" + "ab/" + ">" fits the pattern. That silently captured raw XML
# into the indexed text and would have corrupted every edit near a tab stop.
T_RE = re.compile(r"<w:t(?P<tattr>\s[^>]*)?>(?P<text>.*?)</w:t>", re.S)
# Paragraphs and runs NEST: a drawing's text box (<w:txbxContent>) holds whole
# paragraphs inside a run inside a paragraph, and signature lines in contract
# exhibits are commonly drawn that way. A non-greedy <w:p>.*?</w:p> ends the
# outer paragraph at the first inner </w:p>, so anything that walks paragraphs
# has to count depth instead. `(?=[\s>/])` keeps <w:pPr> and <w:rPr> out.
P_TAG = re.compile(r"<w:p(?=[\s>/])[^>]*?(/?)>|</w:p>")
R_TAG = re.compile(r"<w:r(?=[\s>/])[^>]*?(/?)>|</w:r>")
TXBX = re.compile(r"<w:txbxContent\b.*?</w:txbxContent>", re.S)
PPR_CHANGE = re.compile(r"<w:pPrChange\b.*?</w:pPrChange>", re.S)
RPR_CHANGE = re.compile(r"<w:rPrChange\b[^>]*?(?:/>|>.*?</w:rPrChange>)", re.S)
CHANGE_ID = re.compile(r'(<w:(?:rPrChange|pPrChange)\b[^>]*?\bw:id=")(\d+)"')
EMPTY_PARA = re.compile(r"<w:p(\s[^>]*?)?/>$")
# `\s*` after the open tag: a reformatted document.xml puts whitespace between
# <w:p> and <w:pPr>, and missing the pPr there adds a second one beside it.
PARA_PARTS = re.compile(
    r"(<w:p(?:\s[^>]*)?>\s*)"
    r"(<w:pPr>(?:<w:pPrChange\b.*?</w:pPrChange>|(?!<w:pPrChange\b).)*?</w:pPr>|<w:pPr/>)?"
    r"(.*)</w:p>$", re.S)
INS_OPEN = re.compile(r"<w:ins\b[^>]*?(?<!/)>")
NESTED_INS = re.compile(r"<w:ins\b[^>]*?(?<!/)>(?:(?!</w:ins>).)*?<w:ins\b[^>]*?(?<!/)>", re.S)
W_ID = re.compile(r'\bw:id="(\d+)"')


def _strike_run(run):
    """A run's text as deleted text. Text inside a drawing's text box stays
    <w:t>: those are the shape's own paragraphs, and deleting the run deletes
    the whole shape with them."""
    def strike(seg):
        seg = re.sub(r"<w:t(\s[^>]*)?>", lambda x: "<w:delText" + (x.group(1) or "") + ">", seg)
        seg = seg.replace("</w:t>", "</w:delText>")
        seg = seg.replace("<w:delText>", '<w:delText xml:space="preserve">')
        seg = re.sub(r"<w:instrText\b", "<w:delInstrText", seg)
        return seg.replace("</w:instrText>", "</w:delInstrText>")
    out, pos = [], 0
    for m in TXBX.finditer(run):
        out.append(strike(run[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(strike(run[pos:]))
    return "".join(out)


def _balanced_end(xml, start, tag_re, close):
    """End offset of the element opening at `start`, counting nested copies."""
    depth = 0
    for m in tag_re.finditer(xml, start):
        if m.group(0) == close:
            depth -= 1
        elif m.group(1):                 # self-closing
            if depth == 0:
                return m.end()
            continue
        else:
            depth += 1
        if depth == 0:
            return m.end()
    raise SystemExit("ABORT: unbalanced markup (unclosed element)")


def _enclosing_para(xml, pos):
    """(start, end) of the innermost paragraph containing offset `pos`."""
    stack = []
    for m in P_TAG.finditer(xml, 0, pos):
        if m.group(0) == "</w:p>":
            if stack:
                stack.pop()
        elif not m.group(1):
            stack.append(m.start())
    if not stack:
        raise SystemExit("ABORT: text is not inside a paragraph")
    return stack[-1], _balanced_end(xml, stack[-1], P_TAG, "</w:p>")


def _next_para(xml, pos):
    """(start, end) of the sibling paragraph starting at `pos` after
    whitespace, or None when something else comes first (a table, a section
    break, the end of a cell or text box). An empty <w:p/> counts: python-docx
    and some exporters write blank spacers that way, and those are exactly the
    ones del_blank_para_after exists to remove."""
    at = SIBLING_GAP.match(xml, pos).end()
    if xml.startswith("</w:p>", at) or not P_TAG.match(xml, at):
        return None
    return at, _balanced_end(xml, at, P_TAG, "</w:p>")


def _count(hay, needle):
    """Occurrences of needle in hay, overlapping ones included. str.count skips
    overlaps, so "______" inside an eight-underscore blank counted once and an
    anchor that fits three places passed as unique."""
    n, at = 0, hay.find(needle)
    while at != -1 and needle:
        n += 1
        at = hay.find(needle, at + 1)
    return n


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


CHARREF = re.compile(r"&#(?:x([0-9A-Fa-f]+)|([0-9]+));")


def unesc(s):
    # Every entity Word may write, numeric references first and &amp; last, so that
    # text split out of an existing <w:r> is not re-escaped from "&quot;" to "&amp;quot;". Same rule as
    # audit_suggestions.unescape(), which the fidelity check compares against.
    s = CHARREF.sub(lambda m: chr(int(m.group(1), 16) if m.group(1) else int(m.group(2))), s)
    return (s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
             .replace("&apos;", "'").replace("&amp;", "&"))


def _t_xml(tattr, text):
    """<w:t> for text, with each "\\t" as a real <w:tab/> and each line break as
    a real <w:br/> between <w:t> pieces. A raw newline inside <w:t> is shown by
    Word as a space, so a line break written that way silently disappears."""
    x = f"<w:t{tattr}>" + esc(text.replace("\r\n", "\n").replace("\r", "\n")).replace(
        "\t", '</w:t><w:tab/><w:t xml:space="preserve">').replace(
        "\n", '</w:t><w:br/><w:t xml:space="preserve">') + "</w:t>"
    return re.sub(r"<w:t(?:\s[^>]*)?></w:t>", "", x)


def _plain(xml):
    return unesc("".join(m.group("text") for m in T_RE.finditer(xml)))


class Doc:
    def __init__(self, path, author=None, date=None):
        if not author:
            raise SystemExit("ABORT: pass author= — the name the brand sees on every change. "
                             "Ask the creator; never pick one.")
        self.path = path
        self.author = author
        self.xml = load_document_xml(path)
        self.applied = []
        self.date = date or datetime.now(timezone.utc).strftime(DATE_FMT)
        # Ids above everything already present, bookmarks and comments included:
        # a collision makes Word merge or drop one of the two elements.
        # Every part, not just the body: headers, footnotes and comments hold
        # tracked changes and annotations of their own under the same id space.
        with zipfile.ZipFile(path) as z:
            ids = [int(x) for n in z.namelist() if n.endswith(".xml")
                   for x in W_ID.findall(z.read(n).decode("utf-8", "replace"))]
        self._id = max(ids, default=0)
        root = re.search(r"<w:document\b[^>]*>", self.xml)
        self._w16du = bool(root and "xmlns:w16du=" in root.group(0))

    def nid(self):
        self._id += 1
        return self._id

    def _attrs(self):
        who = esc(self.author).replace('"', "&quot;")
        a = f' w:id="{self.nid()}" w:author="{who}" w:date="{self.date}"'
        if self._w16du:
            a += f' w16du:dateUtc="{self.date}"'
        return a

    # ---------------------------------------------------------------- index
    def _index(self):
        """
        [(xml_start, xml_end, rpr, tattr, text, lead, splittable)], plus the
        flat text.

        A run may hold non-text children before its <w:t> (a <w:tab/> for an
        indent or a caption column is the common case). Those are captured as
        `lead` and kept on the first fragment in document order when the run is
        split — rebuilding a run without them silently drops the tab and runs a
        caption into its body text.
        """
        runs, flat = [], []
        pos = 0
        while True:
            m = RUN_FULL.search(self.xml, pos)
            if not m:
                break
            pos = m.end()
            inner = m.group("inner")
            if "<w:txbxContent" in inner:
                # A drawing's run holds whole paragraphs; the non-greedy match
                # ended at the first INNER </w:r> and would give the text box's
                # first run the drawing run's formatting. Index the inner runs
                # themselves instead.
                pos = m.start("inner") + inner.index("<w:txbxContent")
                continue
            rm = RPR_RE.match(inner)
            rpr = rm.group(0) if rm else ""
            rest = inner[len(rpr):]
            ts = list(T_RE.finditer(rest))
            if not ts:
                continue                      # tab-only / break-only run: no text
            t = ts[0]
            tattr = t.group("tattr") or ""
            if "xml:space" not in tattr:
                tattr += ' xml:space="preserve"'

            # A run holding several <w:t> separated by <w:tab/> (section headings
            # like "A. <tab> ADDITIONAL TERMS") is indexed so offsets and
            # uniqueness stay correct, but marked unsplittable: rebuilding one
            # would drop the tab between its pieces. edit() aborts if an anchor
            # actually lands in one.
            splittable = len(ts) == 1 and not rest[t.end():].strip()
            txt = "".join(unesc(x.group("text")) for x in ts)
            lead = rest[: t.start()]          # e.g. a leading <w:tab/>
            runs.append([m.start(), m.end(), rpr, tattr, txt, lead, splittable])
            flat.append(txt)
        return runs, "".join(flat)

    def flat(self):
        return self._index()[1]

    def _map(self, runs, pos, end, label):
        """Flat offsets [pos, end) -> (runs, first, off_start, last, off_end)."""
        acc, first, last = 0, None, None
        for i, r in enumerate(runs):
            lo, hi = acc, acc + len(r[4])
            if first is None and hi > pos:
                first, off_start = i, pos - lo
            if lo < end <= hi:
                last, off_end = i, end - lo
                break
            acc = hi
        if first is None or last is None:
            raise SystemExit(f"ABORT [{label}] could not map anchor to runs")
        return runs, first, off_start, last, off_end

    def _locate(self, anchor, label, within=None, first=False):
        runs, flat = self._index()
        if within is None:
            if first:
                # first= without a context would reintroduce exactly the silent
                # wrong-occurrence edit the exactly-once rule exists to prevent.
                raise SystemExit(f"ABORT [{label}] first=True needs a within= context")
            n = _count(flat, anchor)
            if n != 1:
                raise SystemExit(
                    f"ABORT [{label}] anchor matched {n} times (expected 1):\n  {anchor!r}"
                )
            pos = flat.index(anchor)
        else:
            n = _count(flat, within)
            if n != 1:
                raise SystemExit(
                    f"ABORT [{label}] context matched {n} times (expected 1):\n  {within!r}"
                )
            m = _count(within, anchor)
            if m != 1 and not (first and m > 1):
                raise SystemExit(
                    f"ABORT [{label}] anchor matched {m} times inside context "
                    f"(expected 1; first=True takes the first):\n  {anchor!r}"
                )
            pos = flat.index(within) + within.index(anchor)
        return self._map(runs, pos, pos + len(anchor), label)

    def _locate_before(self, after, anchor, label):
        """anchor = the text immediately before the unique string `after`."""
        runs, flat = self._index()
        n = _count(flat, after)
        if n != 1:
            raise SystemExit(f"ABORT [{label}] after-context matched {n} times (expected 1)")
        end = flat.index(after)
        pos = end - len(anchor)
        if pos < 0 or flat[pos:end] != anchor:
            raise SystemExit(
                f"ABORT [{label}] text before context is {flat[max(pos, 0):end]!r}, "
                f"expected {anchor!r}"
            )
        return self._map(runs, pos, end, label)

    def _run_xml(self, rpr, tattr, text, lead=""):
        return f"<w:r>{rpr}{lead}<w:t{tattr}>{esc(text)}</w:t></w:r>"

    def _del_xml(self, frags):
        """frags: [(rpr, tattr, text, lead)] — one <w:r> each, formatting kept."""
        inner = "".join(
            f"<w:r>{rpr}{lead}<w:delText{tattr}>{esc(t)}</w:delText></w:r>"
            for rpr, tattr, t, lead in frags
            if t
        )
        if not inner:
            return ""
        return f"<w:del{self._attrs()}>{inner}</w:del>"

    def _ins_xml(self, rpr, tattr, text, lead=""):
        # Text we insert has its formatting now; a copied <w:rPrChange> would
        # record the brand's pending formatting change on our words, under
        # their change id.
        rpr = RPR_CHANGE.sub("", rpr)
        return f"<w:ins{self._attrs()}><w:r>{rpr}{lead}{_t_xml(tattr, text)}</w:r></w:ins>"

    def _fresh_change_ids(self, pieces, seen):
        """A run split into pieces copies its <w:rPrChange> into each; the first
        keeps the id, the others get fresh ones, since ids must be unique."""
        def one(x):
            def sub(m):
                if m.group(2) in seen:
                    return f'{m.group(1)}{self.nid()}"'
                seen.add(m.group(2))
                return m.group(0)
            return CHANGE_ID.sub(sub, x)
        return [(ours, one(x)) for ours, x in pieces]

    def _enclosing_ins(self, pos):
        """(open_start, open_end, close_start, close_end) of the <w:ins> holding
        xml position pos, or None. <w:ins> never nests, so the nearest open tag
        before pos either still encloses it or has already closed."""
        start = max(self.xml.rfind("<w:ins ", 0, pos), self.xml.rfind("<w:ins>", 0, pos))
        if start == -1:
            return None
        oe = self.xml.index(">", start) + 1
        if self.xml[oe - 2] == "/":           # a paragraph-mark <w:ins/>, not a wrapper
            return None
        close = self.xml.find("</w:ins>", oe)
        if close == -1 or close < pos:
            return None
        return start, oe, close, close + len("</w:ins>")

    # ---------------------------------------------------------------- edit
    def edit(self, kind, anchor, new=None, label="", within=None, first=False):
        if kind not in ("del", "rep", "ins_after", "ins_before"):
            raise SystemExit(f"ABORT [{label}] unknown edit kind {kind!r}")
        if (kind == "del") != (new is None):
            raise SystemExit(f"ABORT [{label}] {kind!r} {'takes no' if kind == 'del' else 'needs'} new text")
        self._apply(kind, *self._locate(anchor, label, within, first), new, label)
        self.applied.append((label or kind, anchor[:55]))

    def _apply(self, kind, runs, i, a, j, b, new, label):
        for k in range(i, j + 1):
            if not runs[k][6]:
                raise SystemExit(
                    f"ABORT [{label}] anchor lands in an unsplittable run "
                    f"(multiple <w:t> separated by tabs). Re-anchor the edit.\n"
                    f"  run text: {runs[k][4][:80]!r}"
                )
        # The flat text carries no structural separators, so an anchor can span
        # an element boundary without looking like it does. Replacing the whole
        # span then eats the markup in between — a mailto <w:hyperlink> wrapping
        # the run, a </w:p>, a table cell edge — and produces a .docx that every
        # regex-based check still passes and Word refuses to open.
        for k in range(i, j):
            gap = self.xml[runs[k][1]:runs[k + 1][0]]
            if "<" in gap:
                raise SystemExit(
                    f"ABORT [{label}] anchor spans structural markup that would be "
                    f"destroyed:\n  gap: {gap[:120]!r}\n  Re-anchor within one "
                    f"element, or use del_multi() if it is bookmarks/proofErr."
                )
        # A later run's `lead` sits between two characters of the flat text, so
        # an anchor running into it would fold its tab or break into the change
        # and accepting would run a caption into the body text.
        for k in range(i + 1, j + 1):
            if re.search(r"<w:(?:tab|br|cr)\b", runs[k][5]):
                raise SystemExit(
                    f"ABORT [{label}] anchor crosses a tab or line break the flat text does "
                    f"not show, before {runs[k][4][:40]!r}. Anchor on one side of it."
                )
        head_rpr, head_tattr, head_lead = runs[i][2], runs[i][3], runs[i][5]
        tail_rpr, tail_tattr = runs[j][2], runs[j][3]
        pre = runs[i][4][:a]
        post = runs[j][4][b:]

        frags = []
        for k in range(i, j + 1):
            t = runs[k][4]
            s = a if k == i else 0
            e = b if k == j else len(t)
            frags.append((runs[k][2], runs[k][3], t[s:e], runs[k][5] if k != i else ""))

        # pieces: (is_our_insertion, xml). Our insertions are kept apart so they
        # can be lifted out of an enclosing foreign <w:ins> below.
        pieces = []
        # `lead` (a <w:tab/> and friends) precedes all of the run's text, so it
        # stays untouched ahead of every change. Folding it into a deletion at
        # offset 0 made accept-all delete the caption tab.
        if pre:
            pieces.append((False, self._run_xml(head_rpr, head_tattr, pre, head_lead)))
        elif head_lead:
            pieces.append((False, f"<w:r>{head_rpr}{head_lead}</w:r>"))
        if kind == "ins_before":
            pieces.append((True, self._ins_xml(head_rpr, head_tattr, new)))
        if kind in ("del", "rep"):
            pieces.append((False, self._del_xml(frags)))
        else:
            for r, ta, t, ld in frags:
                if t:
                    pieces.append((False, self._run_xml(r, ta, t, ld)))
        if kind == "rep":
            pieces.append((True, self._ins_xml(head_rpr, head_tattr, new)))
        if kind == "ins_after":
            pieces.append((True, self._ins_xml(tail_rpr, tail_tattr, new)))
        if post:
            pieces.append((False, self._run_xml(tail_rpr, tail_tattr, post)))

        pieces = self._fresh_change_ids(pieces, set())
        enc = self._enclosing_ins(runs[i][0])
        if enc is None or not any(ours for ours, _ in pieces):
            self.xml = (self.xml[: runs[i][0]] + "".join(x for _, x in pieces)
                        + self.xml[runs[j][1]:])
            return

        # Inside someone's <w:ins>: <w:ins> may not nest, so close theirs around
        # each of our insertions and reopen it after. The first surviving part
        # keeps their original element (and id); any later part is a copy with a
        # fresh id. At a boundary one side is empty and is simply not emitted,
        # which leaves our insertion as a plain sibling of theirs.
        os_, oe, cs, ce = enc
        open_tag = self.xml[os_:oe]
        seq = ([(False, self.xml[oe:runs[i][0]])] + pieces
               + [(False, self.xml[runs[j][1]:cs])])
        out, buf, reused = [], [], False

        def flush():
            nonlocal reused
            body = "".join(buf)
            buf.clear()
            if not body.strip():
                out.append(body)
                return
            tag = open_tag if not reused else re.sub(
                r'w:id="\d+"', f'w:id="{self.nid()}"', open_tag, count=1)
            reused = True
            out.append(f"{tag}{body}</w:ins>")

        for ours, x in seq:
            if ours:
                flush()
                out.append(x)
            else:
                buf.append(x)
        flush()
        self.xml = self.xml[:os_] + "".join(out) + self.xml[ce:]

    # ------------------------------------------------ deletion across markup
    def del_multi(self, anchor, after, label=""):
        """Delete anchor as one <w:del> per run, so bookmarks/proofErr between
        the runs survive. `after` is unique text immediately following anchor."""
        runs, flat = self._index()
        if _count(flat, after) != 1 or not flat[: flat.index(after)].endswith(anchor):
            raise SystemExit(
                f"ABORT [{label}] anchor is not immediately before a unique `after`:\n"
                f"  anchor {anchor!r}\n  after  {after!r}"
            )
        pos = flat.index(after) - len(anchor)
        end = pos + len(anchor)
        frags, acc = [], 0
        for r in runs:
            lo, hi = acc, acc + len(r[4])
            s, e = max(lo, pos), min(hi, end)
            if s < e:
                frags.append(flat[s:e])
            acc = hi
        # Last-to-first: each struck fragment leaves the flat text, so the next
        # one back is again the text immediately before `after`.
        for n, frag in enumerate(reversed(frags)):
            sub = f"{label}#{len(frags) - n}"
            self._apply("del", *self._locate_before(after, frag, sub), None, sub)
        self.applied.append((label or "del-multi", anchor[:55]))

    # ---------------------------------------------- whole-paragraph deletion
    def _para_span(self, unique_text, label):
        runs, flat = self._index()
        n = _count(flat, unique_text)
        if n != 1:
            raise SystemExit(f"ABORT [{label}] para locator matched {n} times (expected 1)")
        pos, acc, xs = flat.index(unique_text), 0, None
        for r in runs:
            if acc + len(r[4]) > pos:
                xs = r[0]
                break
            acc += len(r[4])
        return _enclosing_para(self.xml, xs)

    @staticmethod
    def _add_mark(ppr, mark):
        """Put a paragraph-mark change into pPr/rPr, in schema order (ins, del
        first in the mark's rPr; rPr before sectPr/pPrChange in pPr)."""
        if not ppr or ppr == "<w:pPr/>":
            return f"<w:pPr><w:rPr>{mark}</w:rPr></w:pPr>"
        head_end = ppr.find("<w:pPrChange")
        head = ppr if head_end == -1 else ppr[:head_end]
        tail = "" if head_end == -1 else ppr[head_end:]
        if "<w:rPr/>" in head:
            return head.replace("<w:rPr/>", f"<w:rPr>{mark}</w:rPr>", 1) + tail
        m = re.search(r"<w:rPr>(<w:ins\b[^>]*/>)?", head)
        if m:
            return head[: m.end()] + mark + head[m.end():] + tail
        cut = re.search(r"<w:sectPr\b", head)
        at = cut.start() if cut else len(head) - (0 if tail else len("</w:pPr>"))
        return head[:at] + f"<w:rPr>{mark}</w:rPr>" + head[at:] + tail

    def _delete_para_xml(self, para, label, last=False):
        e = EMPTY_PARA.match(para)
        if e:
            para = f"<w:p{e.group(1) or ''}></w:p>"
        m = PARA_PARTS.match(para)
        if not m:
            raise SystemExit(f"ABORT [{label}] could not decompose paragraph")
        popen, ppr, body = m.group(1), m.group(2) or "", m.group(3)
        # Already mark-deleted by someone else: a second <w:del/> is invalid.
        # A mark carrying a section break is kept: deleting it merges the
        # section into the next one (a two-column signature layout spreading
        # into the text after it, or headers and footers lost). Striking the
        # text and keeping the mark is what Word does, at the cost of one empty
        # paragraph on accept.
        if "<w:sectPr" in ppr:
            self.applied.append((label or "del-para", "kept a section-break paragraph mark"))
        elif last:
            # The last paragraph of a cell, text box or body: Word cannot
            # delete that mark, and accept-all keeps it.
            self.applied.append((label or "del-para", "kept the last paragraph mark of its container"))
        elif not re.search(r"<w:rPr>(?:<w:ins\b[^>]*/>)?<w:del\b", ppr):
            ppr = self._add_mark(ppr, f"<w:del{self._attrs()}/>")
        out, i = [], 0
        while i < len(body):
            if body.startswith("<w:del ", i) or body.startswith("<w:del>", i):
                # already struck (by anyone): leave their suggestion as it is
                j = body.index("</w:del>", i) + len("</w:del>")
                out.append(body[i:j])
                i = j
                continue
            if R_TAG.match(body, i) and not body.startswith("</w:r>", i):
                j = _balanced_end(body, i, R_TAG, "</w:r>")
                out.append(f"<w:del{self._attrs()}>{_strike_run(body[i:j])}</w:del>")
                i = j
                continue
            # Any other tag passes through — including someone's <w:ins> open
            # tag, so their inserted runs get our <w:del> inside their <w:ins>.
            nxt = body.find("<", i + 1)
            nxt = len(body) if nxt == -1 else nxt
            out.append(body[i:nxt])
            i = nxt
        return popen + ppr + "".join(out) + "</w:p>"

    def del_para(self, unique_text, label=""):
        ps, pe = self._para_span(unique_text, label)
        last = not _next_para(self.xml, pe)
        self.xml = self.xml[:ps] + self._delete_para_xml(self.xml[ps:pe], label, last) + self.xml[pe:]
        self.applied.append((label or "del-para", unique_text[:55]))

    def del_blank_para_after(self, unique_text, label=""):
        ps, pe = self._para_span(unique_text, label)
        nxt = _next_para(self.xml, pe)
        if not nxt:
            raise SystemExit(f"ABORT [{label}] no following sibling paragraph")
        s, e = nxt
        para = self.xml[s:e]
        if _plain(para):
            raise SystemExit(f"ABORT [{label}] following paragraph is not blank: "
                             f"{_plain(para)[:60]!r}")
        last = not _next_para(self.xml, e)
        self.xml = self.xml[:s] + self._delete_para_xml(para, label, last) + self.xml[e:]
        self.applied.append((label or "del-blank", "blank paragraph"))

    def del_para_offset(self, unique_text, k, expect_prefix, label=""):
        """Delete the k-th paragraph after the one containing unique_text
        (k=1 is the next one). Delete by offset BEFORE deleting the anchor
        paragraph itself — once struck, its text is no longer locatable."""
        if k < 1:
            raise SystemExit(f"ABORT [{label}] k must be >= 1")
        ps, pe = self._para_span(unique_text, label)
        pos, last = pe, None
        for _ in range(k):
            last = _next_para(self.xml, pos)
            if not last:
                raise SystemExit(f"ABORT [{label}] ran out of sibling paragraphs")
            pos = last[1]
        para = self.xml[last[0]:last[1]]
        txt = _plain(para)
        if not txt.startswith(expect_prefix) or (expect_prefix == "" and txt.strip()):
            raise SystemExit(f"ABORT [{label}] paragraph text mismatch: {txt[:80]!r}")
        final = not _next_para(self.xml, last[1])
        self.xml = self.xml[:last[0]] + self._delete_para_xml(para, label, final) + self.xml[last[1]:]
        self.applied.append((label or "del-para-offset", txt[:55]))

    def del_para_range(self, first_text, last_text, label="", expect_count=None):
        """Strike every paragraph from the one holding first_text through the
        one holding last_text, inclusive: runs, blank spacers, duplicates and
        every paragraph mark.

        A block — an exhibit, a release, a series of bullets —is otherwise struck
        one paragraph at a time, and the blanks and duplicates in it cannot be
        anchored, so callers are tempted to write their own loop. A hand-written
        loop over an exhibit can strike 36 paragraph marks and miss the last one,
        leaving an empty paragraph behind on accept.

        The range must be consecutive sibling paragraphs: a table or a
        container edge inside it aborts rather than being walked past. A
        paragraph carrying a section break has its text struck and its mark
        kept (see _delete_para_xml). The paragraph after last_text must exist,
        because the final mark of a body or cell cannot be deleted. expect_count, if given, asserts how
        many paragraphs the range holds.
        """
        ps, pe = self._para_span(first_text, label)
        ls, le = self._para_span(last_text, label)
        if ls < ps:
            raise SystemExit(f"ABORT [{label}] last_text comes before first_text")
        spans, pos = [(ps, pe)], pe
        while spans[-1][1] < le:
            nxt = _next_para(self.xml, pos)
            if not nxt or nxt[0] > ls:
                raise SystemExit(f"ABORT [{label}] range is not consecutive sibling paragraphs "
                                 f"(a table, section or container edge sits inside it)")
            spans.append(nxt)
            pos = nxt[1]
        if spans[-1] != (ls, le):
            raise SystemExit(f"ABORT [{label}] could not walk from first_text to last_text")
        if expect_count is not None and len(spans) != expect_count:
            raise SystemExit(f"ABORT [{label}] range holds {len(spans)} paragraphs, "
                             f"expected {expect_count}")
        if not _next_para(self.xml, le):
            raise SystemExit(f"ABORT [{label}] no paragraph follows last_text; the final mark "
                             f"of a body or cell cannot be deleted — end the range one earlier")
        for s, e in reversed(spans):        # last-to-first keeps earlier offsets valid
            self.xml = self.xml[:s] + self._delete_para_xml(self.xml[s:e], label) + self.xml[e:]
        self.applied.append((label or "del-para-range", f"{len(spans)} paragraphs"))

    # ------------------------------------------------------- new paragraphs
    @staticmethod
    def _new_ppr(ppr_inner, mark):
        # The sibling's own mark formatting and change records are not ours to
        # copy, and a copied sectPr would silently add a section break.
        ppr_inner = re.sub(r"<w:rPr>.*?</w:rPr>|<w:rPr/>|<w:sectPr\b.*?</w:sectPr>"
                           r"|<w:pPrChange\b.*?</w:pPrChange>", "", ppr_inner, flags=re.S)
        return f"<w:pPr>{ppr_inner}<w:rPr>{mark}</w:rPr></w:pPr>" if mark else f"<w:pPr>{ppr_inner}</w:pPr>"

    def para_after(self, anchor, texts, label="", within=None, first=False):
        runs, i, a, j, b = self._locate(anchor, label, within, first)
        pstart, end = _enclosing_para(self.xml, runs[i][0])
        m = PARA_PARTS.match(self.xml[pstart:end])
        ppr = (m.group(2) or "") if m else ""
        ppr_inner = ppr[len("<w:pPr>"):-len("</w:pPr>")] if ppr.startswith("<w:pPr>") else ""

        rpr, tattr = RPR_CHANGE.sub("", runs[i][2]), runs[i][3]
        bodies = [f"<w:ins{self._attrs()}><w:r>{rpr}{_t_xml(tattr, t)}</w:r></w:ins>" for t in texts]
        self._insert_paras_after(pstart, end, ppr_inner, bodies)
        self.applied.append((label or "para", f"{len(texts)} new paragraph(s)"))

    def _insert_paras_after(self, pstart, end, ppr_inner, bodies):
        """New tracked paragraphs after the one at [pstart, end).

        Each new paragraph's mark is inserted — except where no sibling
        paragraph follows (the last in a table cell, text box or body). That
        final mark cannot be inserted: Word keeps it, so rejecting would leave
        an empty paragraph behind. Word marks the ANCHOR's mark as inserted
        instead and the last new paragraph inherits the container's final mark,
        so rejecting merges the new paragraphs away into the anchor."""
        last = not _next_para(self.xml, end)
        blocks = []
        for k, body in enumerate(bodies):
            if last and k == len(bodies) - 1:
                new_ppr = self._new_ppr(ppr_inner, "")
            else:
                new_ppr = self._new_ppr(ppr_inner, f"<w:ins{self._attrs()}/>")
            blocks.append(f"<w:p>{new_ppr}{body}</w:p>")
        para = self.xml[pstart:end]
        if last:
            m = PARA_PARTS.match(para)
            ppr = self._add_mark(m.group(2) or "", f"<w:ins{self._attrs()}/>")
            para = m.group(1) + ppr + m.group(3) + "</w:p>"
        self.xml = self.xml[:pstart] + para + "".join(blocks) + self.xml[end:]

    # --------------------------------------------- clone a sibling paragraph
    def clone_para_after(self, anchor, subs, label="", within=None, first=False):
        """
        Copy the whole <w:p> containing anchor, substitute text, and insert the
        copy after it as a tracked insertion.

        Cloning rather than rebuilding is what preserves <w:tab/> separators and
        the underlined caption run — the things that make a new clause look like
        it belongs to the contract instead of pasted into it.

        subs: {exact run text -> replacement}, every key hitting exactly once;
        or {int -> replacement}, the int indexing the paragraph's text-bearing
        runs (0 = first), for siblings whose run texts repeat. An int
        substitution replaces the run's whole text ("\\t" = a real tab) and
        keeps its formatting and leading tab. Int keys apply first.
        """
        runs, i, a, j, b = self._locate(anchor, label, within, first)
        pstart, pend = _enclosing_para(self.xml, runs[i][0])
        para = self.xml[pstart:pend]

        by_index = {k: v for k, v in subs.items() if isinstance(k, int)}
        if by_index:
            text_runs = [m for m in RUN_FULL.finditer(para) if T_RE.search(m.group("inner"))]
            for k in sorted(by_index, reverse=True):
                if not 0 <= k < len(text_runs):
                    raise SystemExit(f"ABORT [{label}] clone run index {k} out of range "
                                     f"(paragraph has {len(text_runs)} text runs)")
                m = text_runs[k]
                inner = m.group("inner")
                rpr = (RPR_RE.match(inner) or [""])[0]
                rest = inner[len(rpr):]
                ts = list(T_RE.finditer(rest))
                tattr = ts[0].group("tattr") or ""
                if "xml:space" not in tattr:
                    tattr += ' xml:space="preserve"'
                new_inner = (rpr + rest[: ts[0].start()] + _t_xml(tattr, by_index[k])
                             + rest[ts[-1].end():])
                s, e = m.start("inner"), m.end("inner")
                para = para[:s] + new_inner + para[e:]

        for old, new in subs.items():
            if isinstance(old, int):
                continue
            hits = re.findall(r"<w:t(?:\s[^>]*)?>" + re.escape(esc(old)) + r"</w:t>", para)
            if len(hits) != 1:
                raise SystemExit(
                    f"ABORT [{label}] clone substitution {old[:40]!r} hit {len(hits)} "
                    f"times; key it by run index instead"
                )
            para = para.replace(hits[0], _t_xml(' xml:space="preserve"', new))

        m = PARA_PARTS.match(para)
        if not m:
            raise SystemExit(f"ABORT [{label}] could not decompose paragraph")
        ppr, body = m.group(2) or "", m.group(3)
        # Wrapping a body that holds someone's pending change in our <w:ins>
        # would nest tracked changes, which Word refuses.
        if re.search(r"<w:(ins|del|moveFrom|moveTo)\b", body):
            raise SystemExit(f"ABORT [{label}] cannot clone a paragraph with pending "
                             f"tracked changes; clone a clean sibling or use para_after")
        # Bookmark and comment anchors are unique per document; a copy would
        # duplicate their ids.
        body = re.sub(r"<w:(bookmarkStart|bookmarkEnd|commentRangeStart|commentRangeEnd)\b[^>]*/>",
                      "", body)
        body = re.sub(r"<w:r(?:\s[^>]*)?>(?:(?!</w:r>).)*?<w:commentReference\b.*?</w:r>",
                      "", body, flags=re.S)
        # A pending formatting change in the sibling is theirs, under their id.
        body = RPR_CHANGE.sub("", body)
        ppr_inner = ppr[len("<w:pPr>"):-len("</w:pPr>")] if ppr.startswith("<w:pPr>") else ""
        self._insert_paras_after(pstart, pend, ppr_inner, [f"<w:ins{self._attrs()}>{body}</w:ins>"])
        self.applied.append((label or "clone-para", "1 cloned paragraph"))

    # ---------------------------------------------------------------- raw
    def raw_insert_before(self, marker, xml_snippet, label=""):
        """Splice raw XML before a unique raw-XML marker. No tracking, no
        guards beyond uniqueness and the parse in save(): the escape hatch."""
        n = self.xml.count(marker)
        if n != 1:
            raise SystemExit(f"ABORT [{label}] raw marker matched {n} times (expected 1)")
        self.xml = self.xml.replace(marker, xml_snippet + marker, 1)
        self.applied.append((label or "raw", marker[:55]))

    # ---------------------------------------------------------------- save
    def save(self, dst):
        # Opening dst for writing truncates it before the input is read: saving
        # over the brand's draft would destroy the one file every re-run starts from.
        if Path(dst).resolve() == Path(self.path).resolve():
            raise SystemExit("ABORT: output would overwrite the input; save to a new file")
        # Parse before writing. The audit parses too, but only after the damaged
        # file exists; this is the cheapest possible gate and it belongs here.
        from xml.etree import ElementTree as ET
        try:
            ET.fromstring(self.xml)
        except ET.ParseError as e:
            raise SystemExit(f"ABORT: document.xml is not well-formed — {e}")
        # Well-formed but invalid: Word refuses a file with <w:ins> in <w:ins>.
        nest = NESTED_INS.search(self.xml)
        if nest:
            raise SystemExit(f"ABORT: nested <w:ins> — {nest.group(0)[:160]!r}")
        # Well-formed but invalid: a paragraph may hold one <w:pPr>.
        for s, e in paragraph_spans(self.xml):
            own = PPR_CHANGE.sub("", TXBX.sub("", self.xml[s:e]))
            if len(re.findall(r"<w:pPr[\s>/]", own)) > 1:
                raise SystemExit(f"ABORT: two <w:pPr> in one paragraph — {self.xml[s:s + 160]!r}")

        # Written beside dst and moved into place, so a crash mid-save never
        # leaves a half-written file under the final name.
        fd, tmp = tempfile.mkstemp(suffix=".docx", dir=os.path.dirname(os.path.abspath(dst)))
        os.close(fd)
        try:
            with zipfile.ZipFile(self.path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    data = zin.read(item.filename)
                    if item.filename == "word/document.xml":
                        data = self.xml.encode("utf8")
                    zout.writestr(item, data)
            os.replace(tmp, dst)
        except BaseException:
            os.unlink(tmp)
            raise
