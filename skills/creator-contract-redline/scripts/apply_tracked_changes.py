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
ins_after(".", within="as published by Talent.") after inserting
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
      strike a whole block — an exhibit, a release, a run of bullets — from
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
caption tab the edit never meant to touch.

Inserting next to another author's pending insertion never nests <w:ins> in
<w:ins> (Word refuses the file): our insertion goes beside theirs, splitting
their element if the anchor falls inside it. Deleting text they inserted puts
our <w:del> inside their <w:ins>, which records "they inserted, we deleted".

Timestamps: by default each call gets its own w:date, starting now (UTC, to the
minute) and advancing 20-90 s per call, and w:id starts a random 100-900 above
the highest id already in the file. One constant timestamp over a contiguous
id block reads as "not typed in Word". Pass date= for a fixed stamp and seed=
for reproducible output. w16du:dateUtc is written too when the document
already declares that namespace, as current Word does.
"""
import random, re, zipfile
from datetime import datetime, timedelta, timezone

# Whatever name you pass shows on every suggestion in the sidebar, so use the
# creator's or their company's — not a tool name.
DEFAULT_AUTHOR = "creator"
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
EMPTY_PARA = re.compile(r"<w:p(\s[^>]*?)?/>$")
PARA_PARTS = re.compile(
    r"(<w:p(?:\s[^>]*)?>)"
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
    at = pos
    while at < len(xml) and xml[at].isspace():
        at += 1
    if xml.startswith("</w:p>", at) or not P_TAG.match(xml, at):
        return None
    return at, _balanced_end(xml, at, P_TAG, "</w:p>")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def unesc(s):
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def _t_xml(tattr, text):
    """<w:t> for text, with each "\\t" as a real <w:tab/> between <w:t> pieces."""
    x = f"<w:t{tattr}>" + esc(text).replace(
        "\t", '</w:t><w:tab/><w:t xml:space="preserve">') + "</w:t>"
    return re.sub(r"<w:t(?:\s[^>]*)?></w:t>", "", x)


def _plain(xml):
    return unesc("".join(m.group("text") for m in T_RE.finditer(xml)))


class Doc:
    def __init__(self, path, author=DEFAULT_AUTHOR, date=None, start=None, seed=None):
        self.path = path
        self.author = author
        self.xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf8")
        self.applied = []
        self._rng = random.Random(seed)
        self._fixed_date = date
        if start is None:
            start = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        elif isinstance(start, str):
            start = datetime.fromisoformat(start.replace("Z", "+00:00"))
        self._clock = start
        self._groups = 0
        self.date = date or start.strftime(DATE_FMT)
        # Ids above everything already present, bookmarks and comments included:
        # a collision makes Word merge or drop one of the two elements.
        ids = [int(x) for x in W_ID.findall(self.xml)]
        self._id = max(ids, default=0) + self._rng.randint(100, 900)
        root = re.search(r"<w:document\b[^>]*>", self.xml)
        self._w16du = bool(root and "xmlns:w16du=" in root.group(0))

    def nid(self):
        self._id += 1
        return self._id

    def _tick(self):
        """Start a change group: every element one call emits shares a stamp."""
        if self._fixed_date:
            return
        if self._groups:
            self._clock += timedelta(seconds=self._rng.randint(20, 90))
        self._groups += 1
        self.date = self._clock.strftime(DATE_FMT)

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
        for m in RUN_FULL.finditer(self.xml):
            inner = m.group("inner")
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
            n = flat.count(anchor)
            if n != 1:
                raise SystemExit(
                    f"ABORT [{label}] anchor matched {n} times (expected 1):\n  {anchor!r}"
                )
            pos = flat.index(anchor)
        else:
            n = flat.count(within)
            if n != 1:
                raise SystemExit(
                    f"ABORT [{label}] context matched {n} times (expected 1):\n  {within!r}"
                )
            m = within.count(anchor)
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
        n = flat.count(after)
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
        return f"<w:ins{self._attrs()}>{self._run_xml(rpr, tattr, text, lead)}</w:ins>"

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
        self._tick()
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
        if flat.count(after) != 1 or not flat[: flat.index(after)].endswith(anchor):
            raise SystemExit(
                f"ABORT [{label}] anchor is not immediately before a unique `after`:\n"
                f"  anchor {anchor!r}\n  after  {after!r}"
            )
        self._tick()
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
        n = flat.count(unique_text)
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

    def _delete_para_xml(self, para, label):
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
        self._tick()
        self.xml = self.xml[:ps] + self._delete_para_xml(self.xml[ps:pe], label) + self.xml[pe:]
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
        self._tick()
        self.xml = self.xml[:s] + self._delete_para_xml(para, label) + self.xml[e:]
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
        self._tick()
        self.xml = self.xml[:last[0]] + self._delete_para_xml(para, label) + self.xml[last[1]:]
        self.applied.append((label or "del-para-offset", txt[:55]))

    def del_para_range(self, first_text, last_text, label="", expect_count=None):
        """Strike every paragraph from the one holding first_text through the
        one holding last_text, inclusive: runs, blank spacers, duplicates and
        every paragraph mark.

        A block — an exhibit, a release, a run of bullets — is otherwise struck
        one paragraph at a time, and the blanks and duplicates in it cannot be
        anchored, so sessions write their own loop. Observed: a hand-written
        loop over Exhibit 1 struck 36 paragraph marks and missed the last one,
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
        self._tick()
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
        return f"<w:pPr>{ppr_inner}<w:rPr>{mark}</w:rPr></w:pPr>"

    def para_after(self, anchor, texts, label="", within=None, first=False):
        runs, i, a, j, b = self._locate(anchor, label, within, first)
        pstart, end = _enclosing_para(self.xml, runs[i][0])
        m = PARA_PARTS.match(self.xml[pstart:end])
        ppr = (m.group(2) or "") if m else ""
        ppr_inner = ppr[len("<w:pPr>"):-len("</w:pPr>")] if ppr.startswith("<w:pPr>") else ""

        self._tick()
        rpr, tattr = runs[i][2], runs[i][3]
        blocks = []
        for t in texts:
            new_ppr = self._new_ppr(ppr_inner, f"<w:ins{self._attrs()}/>")
            run = f"<w:r>{rpr}{_t_xml(tattr, t)}</w:r>"
            blocks.append(f"<w:p>{new_ppr}<w:ins{self._attrs()}>{run}</w:ins></w:p>")
        self.xml = self.xml[:end] + "".join(blocks) + self.xml[end:]
        self.applied.append((label or "para", f"{len(texts)} new paragraph(s)"))

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
        ppr_inner = ppr[len("<w:pPr>"):-len("</w:pPr>")] if ppr.startswith("<w:pPr>") else ""
        self._tick()
        new_ppr = self._new_ppr(ppr_inner, f"<w:ins{self._attrs()}/>")
        block = f"<w:p>{new_ppr}<w:ins{self._attrs()}>{body}</w:ins></w:p>"
        self.xml = self.xml[:pend] + block + self.xml[pend:]
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
        # Parse before writing. Every check in audit_suggestions.py is a regex,
        # so malformed XML sails through all of them and only fails when a human
        # opens the file. This is the cheapest possible gate and it belongs here.
        from xml.etree import ElementTree as ET
        try:
            ET.fromstring(self.xml)
        except ET.ParseError as e:
            raise SystemExit(f"ABORT: document.xml is not well-formed — {e}")
        # Well-formed but invalid: Word refuses a file with <w:ins> in <w:ins>.
        nest = NESTED_INS.search(self.xml)
        if nest:
            raise SystemExit(f"ABORT: nested <w:ins> — {nest.group(0)[:160]!r}")

        zin = zipfile.ZipFile(self.path)
        zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = self.xml.encode("utf8")
            zout.writestr(item, data)
        zout.close()
