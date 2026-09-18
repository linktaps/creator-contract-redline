# The .docx round trip

Google Docs suggestions and Word tracked changes are the same thing on disk. That makes a round trip possible: export the doc as `.docx`, edit the XML, upload it back, and the edits arrive as native suggestions attributed to whatever author you name.

**This is verified end to end on a real contract.** A full redline authored offline — 154 tracked changes across a 64,000-character agreement — imported with the accepted text byte-identical to the local version, both authors preserved, and the brand's own 15 pending suggestions intact. Formatting held.

**Verified in both directions.** Exporting a Google Doc with pending suggestions yields `w:ins` and `w:del` blocks with each suggester's name intact, including the brand's own pending edits. Uploading a `.docx` containing hand-authored tracked changes produces real suggestions in the Docs sidebar, labelled "From imported document", accept/reject-able clause by clause.

## When it's worth it

The audit script (`scripts/audit_suggestions.py`) uses the export leg and should be used on every review — it is the Pass 1 gate.

The import leg is optional and worth it when there are many edits to make. Its real advantage is not speed but verifiability: if edits are a list of find/replace pairs applied by script, you can assert each one matched exactly once and fail loudly otherwise. Whole categories of browser-editing failure — dropped items, off-by-one selections, insertions landing mid-word, a phrase surviving a replacement that was supposed to remove it — become impossible or immediately visible.

Browser editing remains the right tool for multi-paragraph deletions and anything awkward to express as a string replacement.

## Mechanics

Export with `exportMimeType` set to
`application/vnd.openxmlformats-officedocument.wordprocessingml.document`,
then unzip and work on `word/document.xml`. Rezip and upload with the same MIME type, letting the service convert to a Google Doc.

An insertion and a deletion look like this. `w:id` must be unique across the document; author and date are yours to set.

```xml
<w:ins w:author="creator" w:id="9001" w:date="2026-09-17T20:10:00Z">
  <w:r><w:rPr>…</w:rPr><w:t xml:space="preserve">applicable License </w:t></w:r>
</w:ins>

<w:del w:author="creator" w:id="9002" w:date="2026-09-17T20:10:00Z">
  <w:r><w:rPr>…</w:rPr><w:delText xml:space="preserve"> not</w:delText></w:r>
</w:del>
```

A deletion uses `w:delText`, not `w:t`.

## Formatting: the failure that is invisible until someone opens the document

**Every inserted run must carry an explicit `<w:sz>` and `<w:rFonts>`.** A run authored with a bare `<w:rPr><w:rtl w:val="0"/></w:rPr>` inherits `docDefaults` — typically 12pt in the default face. In a contract typeset at 8.5pt Arial, that clause renders roughly 40% larger than everything around it and in the wrong typeface. Nothing in the text comparison catches it; the words are right and the document looks wrong.

This bites hardest on **whole new clauses** — a Limitation of Liability or a definitions block — because there is no run being edited to copy from. Copy the `<w:rPr>` from the nearest body run anyway:

```xml
<w:rPr>
  <w:rFonts w:ascii="Arial" w:cs="Arial" w:eastAsia="Arial" w:hAnsi="Arial"/>
  <w:color w:val="000000"/><w:sz w:val="17"/><w:szCs w:val="17"/><w:rtl w:val="0"/>
</w:rPr>
```

`audit_suggestions.py` checks this on every run, with no baseline needed: it finds the document's dominant size and face and reports any inserted run that doesn't declare them.

## Deleting a whole paragraph or bullet

Striking every run in a paragraph is only half of it. The paragraph mark has to be deleted too, which in OOXML is a `<w:del>` inside `<w:pPr><w:rPr>`:

```xml
<w:pPr><w:rPr><w:del w:author="creator" w:id="9003" w:date="…"/></w:rPr></w:pPr>
```

Without it, accepting the suggestion removes the words and leaves the empty paragraph — a blank line, or a bullet glyph with nothing after it. `audit_suggestions.py` reports these under **Structure**.

**Expect a rendering artifact, and know where it appears.** A deleted paragraph mark is drawn as a strikethrough at the junction between that paragraph and the next — so the line shows up at the left edge of the *following* paragraph, running across its indent, not on the deleted one. In a bullet list it looks as though an untouched bullet has a stray line beside it; the line belongs to the deleted bullet above.

That is correct markup displayed mid-review, not damage: on accept the deleted bullet vanishes entirely, on reject it returns whole. Worth telling the creator before they spot it, because it looks like corruption and is the most common thing they will ask about.

**Match the label-column convention the source paragraph uses, whichever it is.** Contracts assembled from templates are often inconsistent — the same document may indent most captions with a run of non-breaking spaces and a handful with a real `<w:tab/>`. Copy what the paragraph you are editing already does rather than imposing one convention. Replacing a run that contained a `<w:tab/>` silently drops it and runs the caption into the body text; the baseline check counts tabs for exactly this reason.

## Parse the XML before you ship it

**Every check in `audit_suggestions.py` is a regex.** Fidelity, structure,
formatting, layout, type, the phrase gate and the additions gate all read the
markup as text. None of them parses it. A `document.xml` with an unclosed element
therefore passes the entire audit — perfect reject-all, tabs intact, every phrase
resolved — and then fails the only test that matters, which is a human
double-clicking the file.

```python
from xml.etree import ElementTree as ET
ET.fromstring(xml)          # raises on the damage every other check misses
```

Do it before writing the zip, not after. If a document library is available,
opening the finished file with it is a second, independent check worth the two
seconds it costs.

## Anchors that cross an element boundary

Text runs are not the only thing between two words. A run can sit inside a
`<w:hyperlink>`, a `<w:smartTag>`, a table cell, or simply a different paragraph,
and a flat text index built by concatenating `<w:t>` contents shows none of it.
An anchor can then span a boundary while looking entirely ordinary, and replacing
the whole span deletes the structural markup in between.

This is not hypothetical. A contract's notices clause read:

> Any notices from Influencer must be sent via email to `_______@agency.__.`

The blank is a mailto hyperlink; the full stop after it is not. Anchoring on
`_______@agency.__.` — blank plus period, the obvious choice — spanned the
`</w:hyperlink>` and consumed it. The resulting file passed all eight gates and
Word would not open it.

Before replacing a span, assert that the gap between consecutive runs in it
contains no markup at all:

```python
for k in range(i, j):
    if "<" in xml[runs[k].end : runs[k+1].start]:
        raise SystemExit("anchor spans structural markup — re-anchor it")
```

Then re-anchor inside a single element. Dropping the trailing period was the
whole fix.

The same trap catches `<w:tab/>`-only runs and bookmarks sitting between two text
runs: they are invisible in the flat text, and a span replacement drops them.

**One more regex trap, because it costs an afternoon.** `<w:t([^>]*)>` also
matches `<w:tab/>` — `"<w:t"` + `"ab/"` + `">"` fits the pattern. Indexing with it
silently captures raw XML into the text stream and mis-places every edit near a
tab stop. Require the whitespace: `<w:t(\s[^>]*)?>`.

## Verify every round trip

Two checks, both cheap:

1. `audit_suggestions.py redline.docx --baseline brand-draft.docx` — reject-all must reproduce the brand's draft exactly.
2. Export the imported doc and diff its reconstructed accepted text against the local version. They should match.

**Watch the layout elements.** Authoring XML by hand destroys `<w:tab/>` separators easily — replacing a run that contained one, or rebuilding a paragraph without it. The result is a caption running into its body text. The baseline check counts them; compare before shipping.

**Suggestion counts will not match, and that is expected.** Google merges adjacent tracked changes on import; 154 became 111 with identical content. Compare text, never counts.

## Toolchain changes what "inherit" means

Editing a file in Word and saving it rewrites `styles.xml`. A Google export often declares no default font at all; Word writes `Times New Roman`. That is harmless on its own — but the moment any run loses its explicit `<w:rFonts>`, it stops inheriting nothing and starts inheriting Times New Roman.

This has happened on **surviving brand text**, not just inserted text: seven passages whose run properties were rebuilt with colour and size but no font, rendering the brand's own words in the wrong typeface. Nothing in the text comparison sees it.

**But Google resolves inheritance on import.** Uploading that file into Docs rewrites every affected run with an explicit `Arial`, and the delivered document is clean. Verified directly: seven passages reading `font=NONE (inherits)` in the Word intermediate all read `font=Arial` after import.

So whether this is a defect depends entirely on **which artifact is delivered**:

- The Google Doc is the deliverable → resolved on import. The local-file warning is advisory.
- The `.docx` is emailed to the brand's legal team → real. Those passages render in Times New Roman.

Never assume either way. Run the checks on the imported document and confirm.

Two consequences:

- Never rebuild a run's `<w:rPr>` from scratch. Copy the existing block and modify it — a file that is clean after import is still wrong if anyone opens the intermediate.
- `audit_suggestions.py --baseline` reports **DEFAULTS: changed** when the two documents disagree, and **TYPE** catches the individual runs. Treat a DEFAULTS warning as a reason to read every TYPE result rather than skimming.

## Authoring a swap: insert before you delete

A replacement is an insertion and a deletion at the same offset, and the order matters. Deleted
runs move inside `<w:del>`, which takes them out of the paragraph's editable text — so any offset
computed after the deletion is short by the length of what was removed, and the insertion lands
that far to the right. Insert first, then delete: `<w:ins>` content is likewise excluded from the
editable text, so offsets stay valid for the deletion that follows.

**This defect passes every check in Pass 1.** Verified on a real redline: the individual
insertions and deletions were well-formed, so reject-all reproduced the brand's draft exactly
(TEXT: PASS), and structure, layout and type all passed. Only the version the brand would sign
was corrupted — `re-shouncured material failure on the part ofoting costs`, and a licence clause
with its phrases in scrambled order. `--check` could not see it either, because the adverse
wording genuinely had been struck. It was caught only by dumping the reconstructed accept-all
text and reading it.

## Toggle properties are written explicitly when off

`<w:strike w:val="0"/>`, `<w:b w:val="0"/>` and their siblings mean the property is **disabled**,
and editors emit them constantly. Testing for the presence of the element rather than reading its
value inverts the result. An analysis that checked for `<w:strike>` alone reported that forty-odd
paragraphs of a contract had been struck through — including clauses the creator had just added —
when 399 of the 407 elements carried `w:val="0"` and only 8 runs were genuinely struck. Read the
value, and treat `"0"`, `"false"` and `"none"` as off.

## Cautions

- **Text is split across runs.** A sentence you can see in the document may be several `<w:r>` elements with formatting boundaries between them. Match on a single run's `<w:t>` content, or normalise first. A naive string search across the raw XML will miss phrases that span runs.
- **`w:id` collisions** with existing suggestions cause unpredictable merging. Start your ids well above anything already in the file.
- **Escape XML entities** in text you insert — `&`, `<`, `>`.
- **Round-trip the original first and diff it** against the source before trusting the import on a real contract. Confirm the brand's existing suggestions survived, the label-column layout and tab stops held, and headers and footers are intact. Drift reads as carelessness to the other side's reviewer.
- **Comments probably do not survive.** Check whether any matter before relying on this.
- **Upload as a new file, or update the existing file id deliberately.** Creating a new doc breaks any link already shared with the brand.
- **Payload size.** Some connectors pass file content inline and cap out well below a full contract's base64 size. If the upload leg is unavailable for that reason, the export leg and the audit script still work, and the fallback is to author and verify the edit list locally, then apply it through the browser from a list already proven complete.
