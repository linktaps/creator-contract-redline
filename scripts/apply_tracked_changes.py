#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author tracked changes into a .docx, as native Word / Google Docs suggestions.

    from apply_tracked_changes import Doc

    d = Doc("brand-draft.docx", author="Creator Name")
    d.edit("rep", "sixty (60) days", "thirty (30) days",   label="net-30")
    d.edit("del", " Influencer agrees to pay a termination fee.", label="penalty")
    d.edit("ins_after", "...preceding sentence.", " New sentence.", label="backstop")
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
underlined word). Each edit asserts its anchor occurs EXACTLY ONCE, so a missed
or doubly-applied edit fails loudly rather than silently.

Formatting is preserved per fragment: a deletion spanning three runs emits three
<w:r> inside the <w:del>, each keeping its own <w:rPr>.

Edit kinds:
  ("del",  anchor)              strike anchor
  ("rep",  anchor, new)         strike anchor, insert new in its place
  ("ins_after",  anchor, new)   insert new immediately after anchor
  ("ins_before", anchor, new)   insert new immediately before anchor
  para_after(anchor, [texts])   whole new paragraph(s) after anchor's paragraph
"""
import re, zipfile

# Whatever name you pass shows on every suggestion in the sidebar, so use the
# creator's or their company's — not a tool name.
DEFAULT_AUTHOR = "creator"
DEFAULT_DATE = "2026-01-01T12:00:00Z"

RUN_FULL = re.compile(r"<w:r(?:\s[^>]*)?>(?P<inner>.*?)</w:r>", re.S)
RPR_RE = re.compile(r"^<w:rPr>.*?</w:rPr>", re.S)
# NOTE the `\s` before the attributes: without it this also matches <w:tab/>,
# since "<w:t" + "ab/" + ">" fits the pattern. That silently captured raw XML
# into the indexed text and would have corrupted every edit near a tab stop.
T_RE = re.compile(r"<w:t(?P<tattr>\s[^>]*)?>(?P<text>.*?)</w:t>", re.S)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def unesc(s):
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


class Doc:
    def __init__(self, path, author=DEFAULT_AUTHOR, date=DEFAULT_DATE):
        self.path = path
        self.author = author
        self.date = date
        self.xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf8")
        self._id = 9000
        self.applied = []

    def nid(self):
        self._id += 1
        return self._id

    # ---------------------------------------------------------------- index
    def _index(self):
        """
        [(xml_start, xml_end, rpr, tattr, text, lead)], plus the flat text.

        A run may hold non-text children before its <w:t> (a <w:tab/> for an
        indent or a caption column is the common case). Those are captured as
        `lead` and stay attached to the head fragment when the run is split —
        rebuilding a run without them silently drops the tab and runs a caption
        into its body text.

        Runs carrying more than one <w:t>, or non-text children after the text,
        are not handled; the indexer aborts rather than guessing.
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

    def _locate(self, anchor, label):
        runs, flat = self._index()
        n = flat.count(anchor)
        if n != 1:
            raise SystemExit(
                f"ABORT [{label}] anchor matched {n} times (expected 1):\n  {anchor!r}"
            )
        pos = flat.index(anchor)
        end = pos + len(anchor)
        # map flat offsets to run indices
        acc, first, last = 0, None, None
        for i, r in enumerate(runs):
            lo, hi = acc, acc + len(r[4])
            if first is None and hi > pos:
                first, off_start = i, pos - lo
            if lo < end <= hi:
                last, off_end = i, end - lo
                break
            acc = hi
        return runs, first, off_start, last, off_end

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
        return (
            f'<w:del w:id="{self.nid()}" w:author="{self.author}" w:date="{self.date}">'
            f"{inner}</w:del>"
        )

    def _ins_xml(self, rpr, tattr, text, lead=""):
        return (
            f'<w:ins w:id="{self.nid()}" w:author="{self.author}" w:date="{self.date}">'
            f"{self._run_xml(rpr, tattr, text, lead)}</w:ins>"
        )

    # ---------------------------------------------------------------- edit
    def edit(self, kind, anchor, new=None, label=""):
        runs, i, a, j, b = self._locate(anchor, label)
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
                    f"destroyed:\n  gap: {gap[:120]!r}\n  Re-anchor within one element."
                )
        head_rpr, head_tattr, head_lead = runs[i][2], runs[i][3], runs[i][5]
        tail_rpr, tail_tattr = runs[j][2], runs[j][3]
        pre = runs[i][4][:a]
        post = runs[j][4][b:]

        # `lead` (a <w:tab/> and friends) must stay on whichever fragment comes
        # first in document order, or the tab is silently dropped.
        pending = [head_lead]

        def take():
            L, pending[0] = pending[0], ""
            return L

        frags = []
        for k in range(i, j + 1):
            t = runs[k][4]
            s = a if k == i else 0
            e = b if k == j else len(t)
            frags.append([runs[k][2], runs[k][3], t[s:e],
                          runs[k][5] if k != i else ""])

        out = []
        if pre:
            out.append(self._run_xml(head_rpr, head_tattr, pre, take()))
        if kind == "ins_before":
            out.append(self._ins_xml(head_rpr, head_tattr, new, take()))
        if kind in ("del", "rep"):
            if frags and pending[0]:
                frags[0][3] = take() + frags[0][3]
            out.append(self._del_xml(frags))
        else:
            for n, (r, ta, t, ld) in enumerate(frags):
                if not t:
                    continue
                out.append(self._run_xml(r, ta, t, (take() if n == 0 else "") + ld))
        if kind == "rep":
            out.append(self._ins_xml(head_rpr, head_tattr, new))
        if kind == "ins_after":
            out.append(self._ins_xml(tail_rpr, tail_tattr, new))
        if post:
            out.append(self._run_xml(tail_rpr, tail_tattr, post, take()))

        self.xml = self.xml[: runs[i][0]] + "".join(out) + self.xml[runs[j][1]:]
        self.applied.append((label or kind, anchor[:55]))

    # ------------------------------------------------------- new paragraphs
    def para_after(self, anchor, texts, label=""):
        runs, i, a, j, b = self._locate(anchor, label)
        end = self.xml.find("</w:p>", runs[j][1])
        if end == -1:
            raise SystemExit(f"ABORT [{label}] no enclosing paragraph")
        end += len("</w:p>")

        pstart = max(self.xml.rfind("<w:p ", 0, runs[i][0]),
                     self.xml.rfind("<w:p>", 0, runs[i][0]))
        phead = self.xml[pstart : runs[i][0]]
        m = re.search(r"<w:pPr>.*?</w:pPr>", phead, re.S)
        ppr_inner = ""
        if m:
            ppr_inner = re.sub(r"<w:rPr>.*?</w:rPr>", "",
                               m.group(0)[len("<w:pPr>"):-len("</w:pPr>")], flags=re.S)

        rpr, tattr = runs[i][2], runs[i][3]
        blocks = []
        for t in texts:
            ppr = (f"<w:pPr>{ppr_inner}<w:rPr>"
                   f'<w:ins w:id="{self.nid()}" w:author="{self.author}" w:date="{self.date}"/>'
                   f"</w:rPr></w:pPr>")
            blocks.append(f"<w:p>{ppr}{self._ins_xml(rpr, tattr, t)}</w:p>")
        self.xml = self.xml[:end] + "".join(blocks) + self.xml[end:]
        self.applied.append((label or "para", f"{len(texts)} new paragraph(s)"))

    # --------------------------------------------- clone a sibling paragraph
    def clone_para_after(self, anchor, subs, label=""):
        """
        Copy the whole <w:p> containing anchor, substitute text, and insert the
        copy after it as a tracked insertion.

        Cloning rather than rebuilding is what preserves <w:tab/> separators and
        the underlined caption run — the things that make a new clause look like
        it belongs to the contract instead of pasted into it.

        subs: {exact run text -> replacement}. Every key must hit exactly once.
        """
        runs, i, a, j, b = self._locate(anchor, label)
        pstart = max(self.xml.rfind("<w:p ", 0, runs[i][0]),
                     self.xml.rfind("<w:p>", 0, runs[i][0]))
        pend = self.xml.find("</w:p>", runs[j][1]) + len("</w:p>")
        para = self.xml[pstart:pend]

        for old, new in subs.items():
            hits = re.findall(r"<w:t(?:\s[^>]*)?>" + re.escape(esc(old)) + r"</w:t>", para)
            if len(hits) != 1:
                raise SystemExit(
                    f"ABORT [{label}] clone substitution {old[:40]!r} hit {len(hits)} times"
                )
            para = para.replace(
                hits[0], f'<w:t xml:space="preserve">{esc(new)}</w:t>'
            )

        m = re.match(r"(<w:p(?:\s[^>]*)?>)(<w:pPr>.*?</w:pPr>)?(.*)</w:p>$", para, re.S)
        if not m:
            raise SystemExit(f"ABORT [{label}] could not decompose paragraph")
        ppr, body = m.group(2) or "", m.group(3)
        ppr_inner = ""
        if ppr:
            ppr_inner = re.sub(r"<w:rPr>.*?</w:rPr>", "",
                               ppr[len("<w:pPr>"):-len("</w:pPr>")], flags=re.S)
        new_ppr = (f"<w:pPr>{ppr_inner}<w:rPr>"
                   f'<w:ins w:id="{self.nid()}" w:author="{self.author}" w:date="{self.date}"/>'
                   f"</w:rPr></w:pPr>")
        block = (f"<w:p>{new_ppr}"
                 f'<w:ins w:id="{self.nid()}" w:author="{self.author}" w:date="{self.date}">'
                 f"{body}</w:ins></w:p>")
        self.xml = self.xml[:pend] + block + self.xml[pend:]
        self.applied.append((label or "clone-para", "1 cloned paragraph"))

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

        zin = zipfile.ZipFile(self.path)
        zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = self.xml.encode("utf8")
            zout.writestr(item, data)
        zout.close()
