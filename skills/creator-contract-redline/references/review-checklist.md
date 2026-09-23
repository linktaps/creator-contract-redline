# Review Checklist

This list is the scope of the review.

**Every item is broken into atomic sub-checks.** Each box is a separate verification with its own answer. An item is not closed until every box under it is resolved. Contracts routinely handle one sub-check acceptably and the next one adversely inside the same paragraph — fixing the first and moving on is how items get half-done.

For each sub-check, record: **present** (acceptable as drafted) / **partial** (exists but one-sided, undefined, or too narrow) / **adverse** (actively harmful) / **missing** (absent entirely).

**Missing means flag, not draft.** Introducing a clause that was never there is a new ask, and whether to make it is the creator's commercial judgment.

**Core and elective.** A sub-check being adverse does not by itself mean edit it. Two tiers:

- **Core** — everything not marked otherwise. Edit it. These are mismatches with terms already
  agreed in writing, one-way clauses, undefined triggers, and grammar. They mirror language the
  brand wrote, cost the brand nothing to grant, and do not need the creator's sign-off.
- **Elective**, marked *(elective)* on the box. **Raise it in the step-4 report for a yes or no;
  do not edit it first.** These are commercial asks that read as aggressive even when they are
  correct — a protection against brand-caused delay, a tightened timing obligation, anything
  that costs the brand money rather than symmetry. Executing one faithfully because the checklist
  lists it is how a redline acquires the item that makes the brand's counsel stop reading.

Two things move a core box into the elective tier for a given deal, and both come from step 2
rather than from the document: **the creator has already conceded it** in correspondence, or
**the brand has already rejected it** in a previous round. Re-opening a settled point needs a
reason, and the creator has it.

**Tagged boxes.** A few boxes carry a tag such as **[#4e]**. These are the sub-checks that go
missing while their item is still named — mutual confidentiality, the exclusivity carve-outs and
the creator's termination consequences can all disappear behind a coverage gate that sees every
item number. `audit_suggestions.py --coverage` requires each tag to
be named by its own label; "#4" does not cover "#4e".

**Every number has a direction.** Before editing a figure, write down which way favours the
creator: ↑ (longer, more — the creator's own deadlines, the cap, the fee, cure periods for the
creator) or ↓ (shorter, fewer — included revision rounds, the brand's turnaround, exclusivity,
the payment term). A default figure given in a box below is a **floor or a ceiling in that
direction, never a target.** Where the contract is already on the creator's side of it, the box
is *present* and the number is left alone. A contract that gives the creator ten days to deliver
keeps ten days when the default is seven. The same applies when an edit leaves a figure as it
was but attaches it to a different obligation — restructuring a sentence so an existing
forty-eight hours now binds the creator's invoicing is a new deadline on the creator.

**Mutualizing never narrows a right the creator already holds.** Symmetry is the method, not the
goal. Where the brand drafted a creator-side right broadly — a reciprocal morals trigger, a
termination right — making the two sides "match" by narrowing the creator's half is a concession.
Narrow the clause pointed at the creator; leave the creator's own right as drafted.

**Undefined means partial.** Where a box turns on a word — a trigger, a category, a scope, a channel — the answer is what the contract defines that word to mean, not what it sounds like in ordinary English. Record the clause that defines it. If there isn't one, the box is partial even when the natural reading favors the creator. Supplying a definition for a term the contract already uses is an edit, not a new ask.

**Short-form and non-US contracts: absence is not automatically a finding.** This list is shaped
by US long-form agreements — it expects a representations block, a release, a §1542 waiver, a
morals clause, pay-when-paid agency structure, whitelisting terms. A two-page template has none of
them, and running the list literally returns a dozen **missing** results, which under *missing
means flag* becomes a dozen non-findings presented as a review. That buries the real ones.

On a short form, these absences are still real exposure and still get reported:

- no limitation of liability or cap (#3)
- no brand-side indemnity (#1)
- no creator termination right (#4)
- no defined total fee or bounded scope (#24)
- no AI or digital-replica limit (#22), offered as a recommended addition

The rest are recorded as normal at that length and not reported as gaps. **Short does not mean
benign.** A short template carries its danger in penalty, forfeiture and refund clauses rather
than in buried breadth — there is no room to hide anything, so what is there is the whole deal.
Read #4, #20 and #24 hardest on these.

---

## Must-haves

### 1. Mutual indemnity
- [ ] **Agency deals: the indemnity comes from whoever makes the product.** Where the agreement
      is with an agency "for the benefit of its client", and the client does not sign, split the
      new indemnity by who controls the risk. The agency covers its own conduct: its breach, its
      negligence, its edits to the Content. The product, product-defect and approved-claims limbs
      come from the client: the agency procures the client's indemnity for the creator, and the
      creator is made a third-party beneficiary of it, mirroring the third-party-beneficiary
      clause that almost always lets the client sue the creator directly. Putting the client's
      product on the agency asks for something it structurally cannot give (see #20 on
      pay-when-paid), and even if granted it leaves the company that made the product and wrote
      the claims owing the creator nothing. **The same split governs every other brand-side
      duty the redline adds** — the AI limit, confidentiality, non-disparagement, ceasing use
      on termination. Writing "Agency and Client shall…" binds no one on the client's side: the
      client did not sign, and these templates usually say outright that the client "is not
      bound by any of Agency's agreements or covenants". Write "Agency shall, and shall cause
      Client to, …" and make the creator a third-party beneficiary of the client's compliance
      (editing standards §4)
- [ ] **[#1a]** Brand's obligation includes a duty to **defend**, not only "indemnify and hold
      harmless" — **even where the brand's own indemnity has no "defend" to mirror.** Without
      it the creator funds their own lawyers and waits to be reimbursed, which on a health-claim
      suit is the whole cost. Mirroring the brand's clause verbatim drops the word;
      this is the one place the mirror adds a word rather than copying
- [ ] **[#1b]** Covers materials, key messages and claims Brand **supplied or approved**, and
      Brand Marks. "Approved" is the half that matters: most claims in creator content are
      wording the brand approved, not wording it supplied. Do not narrow it to "supplied or
      required" while restructuring the clause — the brand's indemnity for its own approved
      talking points goes with it
- [ ] Covers product defects
- [ ] Covers the brand's own negligence and willful misconduct
- [ ] Covers use of the creator's likeness outside the granted scope
- [ ] Covers **modification or alteration of the Content by Brand**. Where a brand re-cuts a
      creator's video and the edit is what creates the claim, none of the limbs above reaches it —
      brand-supplied materials, product defects and negligence all point elsewhere. Read together
      with #22: the AI clause bounds what the brand may alter, this limb decides who pays when an
      alteration goes wrong
- [ ] Creator's own indemnity is not broader than the brand's in kind (check for production/personal-injury clauses that don't match the work).
      **Narrow the trigger or the heads, not both.** Once the creator's trigger is limited to
      material breach, gross negligence or willful misconduct, heads such as "physical loss or
      damage to property" and "personal injury, disease, illness or death" only describe the
      loss the creator covers when actually at fault — reasonable, and usually matched by the
      heads of the brand's new indemnity. Keep them. Striking them as well leaves the creator
      covering almost nothing, reads as overreach, and buys little. Strike a head only where
      the trigger stays broad and the head cannot arise from the work at all
- [ ] **The brand indemnity's carve-out uses the creator's fault standard.** Mirroring the
      brand's own clause produces "except to the extent … caused by the acts or omissions of
      Influencer", and that exception swallows the indemnity: posting the brand's approved
      health claims is itself an act of the creator's, so the one limb that matters most is the
      one the brand's counsel will say never applies. Write the exception as "caused by
      Influencer's material breach of this Agreement, gross negligence or willful misconduct".
      Mirror the brand's structure and wording everywhere else in the clause; this is the
      one phrase that does not survive the swap
- [ ] **The creator's fault standard is gross negligence.** Where the creator's indemnity or a
      cap carve-out turns on the creator's fault, write "gross negligence or willful misconduct",
      never plain "negligence". The brand's side may stay at "negligence". Narrowing the
      creator's trigger means **replacing** it — "the Services or any breach" becomes "any
      material breach, gross negligence or willful misconduct" — not appending a new fault limb
      beside what is there

### 2. Mutual confidentiality
- [ ] **[#2a]** Obligation runs both directions, not just against the creator
- [ ] Consent requirement is reciprocal ("the other party's consent", not "Brand's consent")
- [ ] Permitted recipients are reciprocal ("its agents", not "Talent's agents")
- [ ] Creator may identify the brand as a client and show published work in a portfolio — and
      **check this box together with the post-term IP restriction in #6.** A portfolio right won
      here is worth nothing if the IP clause separately bars future use of Brand Marks
- [ ] **Grammar check after the party swap** — "Talent shall not disclose" becoming "neither party shall not disclose" is a double negative

### 3. Mutual limitation of liability, with a cap
- [ ] A limitation-of-liability clause exists at all (frequently absent, leaving exposure uncapped)
- [ ] Consequential/indirect damages waived mutually
- [ ] Aggregate cap stated, tied to the fee
- [ ] **[#3d]** Carve-outs present for indemnity, **the brand's payment obligations**,
      out-of-scope use, gross negligence. The payment carve-out is the one that disappears:
      without it the cap limits what the brand owes the creator in fees. **Confidentiality only
      where the brand is the main recipient.** A carve-out is mutual, and in most creator deals
      the creator holds the brand's information, not the reverse — uncapping breach of
      confidentiality then mostly uncaps the creator. Leave confidentiality inside the cap
      unless the creator is sharing something the brand could do real damage with
- [ ] **Carve-outs are not broader against the creator than against the brand.** Checking that
      carve-outs exist is half the check; the other half is which way they cut. An uncapped
      carve-out for "defective or inadequate Services" hands the brand both the standard and the
      remedy — bound it to services that fail to meet the concept and SOW the brand approved, so
      "it did not perform well" is not a breach. Breach-based carve-outs ("relating to the
      Services or any breach") narrow to **material** breach, willful misconduct and **gross**
      negligence — the word "gross" is the edit, see #1. Cross-check #12: an uncapped re-performance obligation lets the brand demand a
      free reshoot instead of paying the rate stated there

### 4. Mutual termination, with payment for work completed
- [ ] Creator can terminate at all
- [ ] Creator can terminate for non-payment specifically
- [ ] **Cure period stated and reciprocal.** The position is **ten (10) business days after
      written notice**, the same for both parties. "A reasonable opportunity to cure" is not a
      stated period — it is an argument about what reasonable meant, held after termination.
      The creator's cure period is a floor (↑): a contract already giving the creator longer
      keeps it. It is a checklist position, not an invented figure (editing standards §8)
- [ ] **[#4d]** Payment on termination covers **all work performed on an approved concept, whether or not
      delivered**, published or approved. "Content created and submitted" is the narrower
      formulation and it is usually the creator's own redline that introduces it — a deal killed
      after the concept is approved and before the shoot has produced no Content at all. **Word
      it as "pre-production and production work performed on a Brand-approved concept, whether or
      not the resulting Post has been delivered, published or approved."** Do not write "concept
      development… whether or not approved": it reads as billing for rejected pitches, and it is
      circular — the approval it disclaims is the thing that made the work billable. Use the same
      phrase in every termination route that pays for work performed, so no route pays on a
      different basis. **It goes into the termination clause's own payment sentence** ("Brand will
      then process payment for…") first. A force-majeure or suspension clause is an additional
      route, not a substitute: putting the phrase only there leaves the termination
      clause paying for "services provided", which reads as finished work. Record it in
      `additions.txt` with the count of routes (`:: x2`), so writing it once fails the gate
- [ ] *(elective)* **Milestone schedule on termination.** Creators who negotiate often ask for
      percentages rather than a phrase: x% on signature, x% on concept submission, x% on draft
      delivery, x% on posting, x% on metrics. It is how concept work gets paid without the
      circular "whether or not approved" wording, and it ends the argument about what "work
      performed" covers. Offer it with the creator's percentages; do not pick them
- [ ] **[#4e]** **Content handover on termination is conditioned on payment**, and is not required at all
      where the creator terminates for the brand's cause. An unconditional "deliver all Content
      within forty-eight (48) hours of termination" hands over the work in the one situation
      where the brand has stopped paying for it. Item 4 checks that the creator gets paid on
      termination; this box checks what the creator has to give up
- [ ] Brand's termination-for-cause trigger is limited to uncured material breach, not any failure
- [ ] **[#4g]** **Every termination route has a payment consequence.** A mutual for-cause sentence and a paid
      for-convenience sentence can sit beside a third route with no payment attached at all —
      "Company may terminate immediately at any time if instructed to do so by Client" is the
      common form. Count the routes, then check each one separately; the unpaid route is the one
      the brand will use
- [ ] **No sum is payable by the creator on termination.** Watch for a "termination fee" that runs
      the wrong way — "Influencer agrees to pay a termination fee equal to fifty percent (50%) of
      the Fee" turns a disputed breach into a five-figure invoice against the creator
- [ ] **No performance-linked reduction of the *whole* fee.** The forfeiture box below looks for
      total loss; this one looks for the commoner small-deal version, a settlement rule paying
      **all** deliverables at a reduced rate because some were late or short — "if Party B fails
      to publish the required number of videos, all videos under this cooperation shall be
      settled at 50% of the agreed fee". It sits in the deliverables or settlement section, not
      in termination, so neither box around it looks there. Ask that any reduction be pro-rated
      to the affected deliverables. Two tells: a recital characterising the reduction as "a
      reasonable commercial adjustment mutually agreed by the parties", which is drafted to
      survive challenge rather than to describe anything, and a matching asymmetry in the same
      clause — under-delivery penalised, over-delivery unpaid
- [ ] **No forfeiture clauses elsewhere in the agreement.** Automatic loss of the whole fee for a
      procedural slip ("should Influencer contact Client directly, Influencer shall automatically
      forfeit the Fee") is a penalty, it is rarely in the termination section where it would be
      noticed, and it survives every edit made to the termination section

### 5. Brand morals clause
- [ ] **The trigger pointed at the creator requires material injury, on an objective standard.**
      Reciprocity is the second question; breadth is the first. "Any act which might tend to
      injure the success of Brand" is satisfied by anything the brand dislikes, decided by the
      brand. "Materially injures" is the ask, and it is a single word. **Only on this trigger.**
      The creator's reciprocal trigger against the brand ("…which might tend to injure the
      success of Influencer") stays as broad as the brand drafted it. Adding "materially" there
      too looks even-handed and narrows the creator's own exit — the creator undercutting
      themselves. The same goes for "reduce" → "materially reduces" and
      "disparaging" → "defamatory": edit the creator-facing standard only
- [ ] **[#5b]** Reciprocal termination right exists for the creator, **with its consequences
      written out** — the five boxes below. A reciprocal trigger with no consequences leaves the
      creator free to leave and nothing else, and a rework that keeps the trigger can drop the
      consequence sentence without anyone noticing. **Attach them to every route the creator
      terminates on other than convenience** — the brand's uncured breach and the morals trigger
      alike: "Upon any termination by Influencer under this Section 11(b) other than for
      convenience, …". A sentence opening "In such event" straight after the morals sentence
      reads as covering that route alone, and leaves termination for non-payment with no
      consequences at all
- [ ] Creator retains fees already paid
- [ ] Creator is paid for all work performed on an approved concept, in the same words as #4
- [ ] Creator may remove or archive posts
- [ ] Brand must cease use of the materials
- [ ] Creator is released from exclusivity

The non-disparagement covenant is almost always a separate bullet sitting immediately above the
morals clause, and it gets skipped because the eye is on the termination language below it. It has
its own three defects:

- [ ] **Non-disparagement is bounded in time** — watch for a bare "will not make any statements
      that…" with no "During the Term". Unbounded, it binds the creator for life
- [ ] **Non-disparagement runs both directions**
- [ ] **The standard is objective.** "Disparage **or reflect unfavorably on**" is unbounded by
      construction: an honest negative word about a product the creator has stopped liking
      breaches it. "Are defamatory of" is the fix, and brands accept it

> **Do not self-extend the duration.** Creators sometimes ask whether non-disparagement should
> run for the usage period rather than the Term, because the posts are still up. No: it is the
> creator's obligation, and every month added is a concession written in the creator's voice.
> "During the Term and any Usage Period" is a fair thing to *concede if the brand asks for it*.
> Record it as the fallback; never volunteer it.

### 6. Retained ownership
- [ ] Ownership stated in the creator's favor
- [ ] Not undercut by an exclusive license elsewhere (see #7)
- [ ] **New Content / derivative approval gate** — check whether the creator needs brand approval to use their own material
- [ ] If an approval gate exists, it is limited to content showing Brand Marks or products
- [ ] If an approval gate exists, it has a deemed-approval window
- [ ] If an approval gate exists, it sunsets with the license term rather than running forever
- [ ] **Post-term restriction on the creator referencing the brand at all.** Check the IP and
      termination clauses, not only confidentiality. An obligation to "cease to use Brand's
      Intellectual Property in any future posts", sitting in a section that survives
      termination, ends organic mentions of the brand forever and takes the portfolio right in
      #2 with it — the confidentiality clause can grant that right and this clause silently
      overrides it. The two boxes are checked together or not at all. Bound the restriction to
      use that implies a continuing endorsement or a live campaign, and carve out factual
      reference to past work
- [ ] **The creator's own marks are reserved as the brand's are.** Where the brand reserves its
      Brand Marks, mirror it: the creator (and any loan-out company or agent) retains all names,
      marks, handles and channel names **owned or controlled by** them; the brand's use is limited
      to their appearance within the Materials; no use on packaging, standalone, or as an
      endorsement outside the Materials; no registration or challenge by the brand. Draw it by
      ownership, not by listing handles — an enumeration of what the creator owns is out of date
      the day they open a new channel. Then sweep the schedules: a "Materials will contain no
      trademarks owned by others" requirement needs the same carve-out, or the creator's own
      handle on screen breaches it

### 7. Non-exclusive license
- [ ] **[#7a]** Grant says non-exclusive (search for "exclusive" in the grant)
- [ ] Grant is not "non-cancellable" / irrevocable
- [ ] **Sublicense scope** limited to affiliates and agencies acting for the brand
- [ ] Grant is bounded by a defined license term

### 8. Paid usage as negotiated; brand handle only absent whitelisting
- [ ] Paid media is not bundled into the base fee (search "support with paid media")
- [ ] **Channel list** checked for media-buy language — "shopper", "retail media", "new media", "online video" reach far beyond organic reposting
- [ ] If paid usage is contracted separately, it is struck here rather than drafted
- [ ] Grant does not extend to placement from the creator's own handle absent a separate allowlisting agreement

### 9. Usage runs from first publication on the creator's feed
- [ ] A usage term exists at all (absence makes the grant perpetual by omission)
- [ ] Trigger is first publication on the creator's channels, not the effective date, **and the
      word the trigger turns on is itself defined.** The presence of a publication-shaped phrase
      does not close this box; "after each live post" satisfies it on its face and defines
      nothing. This box and the one below fail together
- [ ] **The trigger phrase is defined.** "live post", "goes live", "live post date", "content is live" all read as the creator's publication and none of them says so. Name the clause that defines it; if there is none, this is partial and the fix is a definition. The default insertion, which brands do argue about and which is worth the argument: **"a period of sixty (60) consecutive calendar days commencing on the date Influencer first publishes the Content on Influencer's own channel."** "Consecutive calendar" is doing real work — without it, brands argue the window stops and restarts; without the publication anchor, they argue "live" meant the date their paid ads began
- [ ] Every variant of the trigger phrase, across body and exhibits, resolves to that one defined event
- [ ] Term applies per asset
- [ ] Material approved but never published is addressed — payment for it and a license to it are separate questions

> The trigger box and the definition box fail together and look like one item. A clause reading "60 days after each live post" passes the trigger box on its face, which is exactly why the definition box exists underneath it.

> **Leave a per-Post usage grant alone even where it looks like a gap.** Where the Use grant
> covers "results and proceeds" but the Usage Period is defined per Post, material never embodied
> in a Post has no Usage Period start and therefore no usage right at all. That cuts for the
> creator. Do not "fix" it by giving unpublished material a clock.

### 10. Name and likeness limited to promoting the program
- [ ] Not "in perpetuity"
- [ ] Not "for no additional consideration"
- [ ] Runs with the license term
- [ ] Limited to use within the approved materials, not standalone use of name or face
- [ ] AI/digital-replica carve-out present

### 11. Number of revisions

> **Direction matters on this item, and it runs opposite to instinct.** Every other number on
> this checklist is a protection to secure. The included-rounds count is not: each included round
> is unpaid labour, so a **low** count is the creator-favourable state. If the brand offers one,
> take one. Never raise it — not as a redline, and not because the creator's instructions say
> "plus two revisions" without having thought about which way that cuts. If an instruction would
> increase the count, raise the conflict before editing.

- [ ] Rounds included in the fee are stated — **do not increase this number**
- [ ] Turnaround window for brand notes stated
- [ ] Deemed-approval after that window
- [ ] Rate stated for additional rounds or post-approval creative changes. **This is the
      protection on this item**, and it is the one to push on. The count caps the free work; the
      rate is what makes everything past the cap paid. Asked together with #12's reshoot
      question, with the same three answers — a rate, left to mutual agreement, or as drafted

### 12. Reshoot fee
- [ ] **Extra rounds and reshoots are priced, or expressly left to agreement.** Where the contract
      has neither (this box and #11's rate box), ask one step-4 question with three answers:
      1. **A rate** — the creator's figure. A reshoot fee is a production rate, not the whole
         fee (editing standards §8)
      2. **Left to agreement**, drafted as: *"Any additional rounds of notes or re-shoots
         requested by Brand shall be subject to mutual agreement on timing, scope, and
         additional compensation."* The creator is never obliged to do the work unpaid; the
         brand is never obliged to pay until a price is agreed. Creators pick this often, and
         it is a sound position — offer it as a ready answer rather than making them write it
      3. **Leave as drafted** and mention it in the report

      Say the trade-off between 1 and 2 once, then draft whichever they choose. Do not reword
      answer 2, and do not suggest a figure when they have chosen it. **Substitute the
      contract's own term for the brand party before showing the option** — "Agency or Client"
      where there is no "Brand" — so the wording the creator picks is the wording that goes in
      (editing standards §4). A party-name swap is not a rewording
- [ ] **The fee attaches from concept approval, not content approval.** A rate for reshoots
      "requested after approval" excludes the ordinary case, because the brand asking for a
      reshoot is usually the brand declining to approve — it calls the re-creation a revision
      and pays nothing. Anchor it to re-creation of Content after **concept** approval
- [ ] **Read against the liability carve-outs (#3).** An uncapped carve-out for "defective or
      inadequate Services" is a free-reshoot right by another name: the brand demands
      re-performance under the cap exception instead of paying the rate stated here
- [ ] Escape hatches removed — "additional compensation, **if applicable**" lets the brand decide none applies
- [ ] **Creator-paid reshoots are limited to the creator's fault — every limb of the trigger.**
      A sentence making the creator "responsible for re-shooting costs" usually lists several
      triggers: compliance, negligence, willful misconduct, "any failure or shortcoming". Narrow
      the whole list to the creator's uncured material failure, gross negligence or willful
      misconduct; narrowing one limb leaves the others to do the same work. A compliance limb
      may stay for applicable law, but not for "the creative brief" or the brand's
      instructions: that lets the brand declare its own reshoot a compliance failure and pay
      nothing, which undoes the pricing or mutual-agreement answer above it
- [ ] **Punctuation check** — rate insertions near an existing comma or period frequently produce malformed sentences

### 13. Archiving provision
- [ ] **Creator-side**: how long posts must stay live, and measured from what (watch for "one (1) year after the end of the Term", which can mean two years — and for a bare "at least (1) year" with no start at all, see #16)
- [ ] **Brand-side**: how long the brand may retain and use the material
- [ ] "Archival" is defined, not left open
- [ ] **A brand-side "no obligation to remove" is market-normal — condition it, do not attack
      it.** This is how organic usage is ordinarily built: the brand has a window in which to
      post, and once a post is up it is not obliged to delete it afterwards. Redlining the
      removal obligation itself reads as not knowing the market. **The ask is the ad-spend
      condition** — no obligation to remove *provided no paid amplification sits behind the post
      after the usage term expires*. Paid spend past the licensed window is a fresh use of the
      creator's likeness; an evergreen organic post is not
- [ ] **The brand's takedown right is left alone.** Do not strip it and do not bound it. A brand
      has to be able to pull a post when things go wrong — a recall, an IP claim, a regulator, or
      the creator in the press for the wrong reasons — and a trigger list always misses one: a
      list of recall, IP claim and legal requirement leaves out the creator's own scandal,
      the case the brand most needs it for. Removing or listing the triggers
      reads to the brand's counsel as not knowing the market and costs credibility the rest of
      the redline is spending. Record it *present*; the sentence below is the only edit this
      area needs
- [ ] **Creator-side retention and takedown obligations carve out brand breach, non-payment and
      termination.** The creator's minimum-live obligation — one year on the primary feed, and
      the like — is otherwise absolute, so the creator keeps hosting the campaign after the
      brand has stopped performing. A conditional clause appended to the obligation ("unless
      Agency and/or Client are in material breach of this Agreement") costs nothing to ask for
      and is rarely refused

- [ ] **No creator-side obligation with no end date.** #16 hunts durations with no stated
      *start*; this is the mirror, and it passes every other box in this item because a
      permanent obligation is not a mis-measured one. "Unless otherwise agreed by Party A, the
      video shall not be removed from the platform after the release" has no end, and where it
      is backed by a refund clause the creator owes money for taking down their own post years
      later. Every retention obligation needs a date or a duration, not only a carve-out

> **One sentence closes the no-removal and retention boxes, in both directions.** *Except in the
> event of uncured breach of this Agreement, Brand shall have no obligation to remove the
> Content.* It concedes the market-normal position the brand wants, and by making the exception
> mutual it hands the creator the power to compel a takedown for non-payment or a morals breach.
> Prefer it to separate edits: it is shorter, it reads as drafting rather than as an ask, and
> the brand's reviewer has nothing to push back on. It does not touch the brand's own takedown
> right, which stays as drafted.

### 14. Mutual timing
- [ ] **Who controls the posting schedule** — watch for "Brand's decision shall be final and controlling" in the schedule
- [ ] **Extension clause**: term cannot be extended without additional compensation (search "without any additional compensation")
- [ ] **Extension clause**: payment dates are not pushed back by an extension
- [ ] *(elective — raise, never draft)* Brand-caused delay does not move the creator's payment dates
- [ ] *(elective — raise, never draft)* Material timely submitted but unposted due to brand delay is still paid

> These two are the ask experienced creators strike from a redline themselves, as too
> aggressive. Mention them in the step-4 report as a yes/no. **Do not draft either unless the creator says yes** — and a softened version ("payment
> shall be due thirty (30) days after the live date agreed") is still the same ask; softening an
> elective does not make it core.

- [ ] **[#14f]** **The creator's own submission and revision windows are workable.** This item
      otherwise looks only at the brand's timing, and the clauses that bind the creator — first
      draft within seventy-two (72) hours, revisions within forty-eight (48) — go unread because
      they are obligations rather than rights. It is a core edit, not a flag: a report that only
      quotes "72 hours of receiving product" back to the creator has found the problem and left
      it in place. Two parts:
      - **Defaults, as floors: seven (7) days** from receipt of product for a first draft,
        **seventy-two (72) hours** from receipt of feedback for revisions. These are the
        creator's deadlines, so longer favours the creator (↑). Edit only a window **shorter**
        than the default, and only by lengthening it to the default. A window already at or
        above it is *present* and untouched — a contract giving ten days keeps ten days.
        Where the creator names their own figure, use theirs, and apply the same direction
        check to it
      - **The clock starts on an event the creator controls.** Product *received*, not product
        *shipped* — a clock started by a carrier is one the creator cannot manage. This applies
        whatever the length
- [ ] **The brand's own windows run the other way.** "Brand shall submit comments within 48 hours
      prior to each anticipated postdate", a notes-turnaround window, a deemed-approval period —
      here shorter favours the creator (↓). Never apply the floors above to these. Tightening the
      brand's timing costs the brand something, so it is elective
- [ ] **Any option or additional-deliverable right** the brand holds is (a) priced at the creator's
      rate rather than a figure the brand chose, (b) conditioned on the creator's availability
      ("subject to Influencer's prior professional commitments"), and (c) bounded by a date. An
      unconditioned option is a call on the creator's calendar for the length of the term
- [ ] **Deliverable specs can move by email in both directions.** Where the entire-agreement clause
      lets the brand issue instructions by email but requires a signed writing for everything else,
      the brand can adjust a spec informally and the creator cannot. Add to each deliverable spec
      paragraph: "The specifications in this paragraph may be adjusted by mutual written agreement
      (which may be via email)." It costs the brand nothing and saves an amendment for a changed
      runtime or posting day

> Note: this item is the most common false-complete. Appending a sentence about brand-caused delay to the end of the Extension clause does not fix the unpaid-extension language earlier in the same clause. Check every box.

### 15. Explicit non-compete / brand exclusivity
- [ ] Category definition matches what was agreed in correspondence
- [ ] Vague expanders removed ("and accessories", "and related products")
- [ ] Parent-company exclusion stated if that was the deal
- [ ] **[#15d]** **Unpaid activity** carved out — "any services (paid or unpaid)" restricts organic
      mentions. Draw the carve-out by consideration, not by subject: *"Nothing in this Agreement,
      including the Exclusivity Period, restricts content for which Influencer receives no
      compensation or other consideration from a Competitor, or the incidental appearance of
      any Competitive Product in Influencer's content."* A carve-out for content "not made in
      connection with any Competitor" misses the case it exists for — an organic post that
      shows a competing product is arguably made in connection with it
- [ ] **[#15e]** **Incidental appearance** carved out
- [ ] **The carve-outs reach every statement of the restriction.** Exclusivity is often stated
      twice — once as a defined-terms row ("No other cat food content one week before and
      after…") and once in the body. A carve-out opening "the foregoing" reaches only the
      sentence above it; open it with "Nothing in this Agreement, including the Exclusivity
      Period," so it reaches both
- [ ] No right of first refusal extending the restriction beyond the paid term
- [ ] **[#15g]** **Exclusivity drawn by time window rather than by category.** Every box above assumes a
      category definition exists to narrow. "No other sponsor videos on the promotion date"
      defines no category at all — it restricts *every* advertiser rather than competitors, which
      is broader than the category exclusivity the rest of this item is written to cut down, and
      it reads as a scheduling note. Bound it to the brand's own category, or price the blackout.
      **Measure it first.** A spacing rule of a few hours — "not post about any other brands for
      three hours after the branded post" — is how sponsored posts are normally kept from being
      buried, costs the creator almost nothing, and is left alone (*present*). The box is for
      blackouts measured in days or longer, or across the Term
- [ ] Blackout windows run from a defined event — "three (3) days before and after each live post" floats if "live post" floats (see #16)

### 16. Defined terms
- [ ] **Term** defined
- [ ] **License Term** defined
- [ ] **Organic Usage** defined, if the agreement grants it
- [ ] **Paid Usage** defined, if the agreement grants it
- [ ] **Allowlisting** defined, if the agreement grants it — **as its own sentence, never as a
      clause trailing the word.** "whitelisting, being paid promotion run through Influencer's
      own account, that does not require…" leaves the reader to guess whether "that" attaches
      to the whitelisting or to the account. Write a definition with the term in quotes, at
      first use or in the definitions table (editing standards §6b), and state any condition
      as a separate sentence: *"Whitelisting" means paid media placed by or for Brand through
      Influencer's own account or handle. Brand may use Whitelisting only where it does not
      require Influencer to authenticate to, or grant account access through, any third-party
      integration.* Use the contract's own party names (editing standards §4)
- [ ] **live / live post / goes live** defined, wherever any of them appears. It belongs on this
      list and not further down it: "live" governs more clocks in a typical influencer template
      than every capitalized term combined, and it is the one phrase a brand will reinterpret
      after signature
- [ ] Any term the redline introduces (e.g. "Archival Use") is actually defined somewhere

The first five are the terms that are usually capitalized, and "live" is on the list precisely because it is not one of them. But do not read that as *capitalized terms get noticed* — the rest of this item is the part that gets skipped:

- [ ] **Capitalized terms with no definition anywhere.** List every capitalized term, match each
      against the definitions, and report the orphans. An undefined **"Total Fee"** is worse
      than an undefined "live post", not better: both sides read a capital letter as a
      cross-reference to a definition, so neither goes looking, and drafters capitalize
      precisely where a payment or a penalty is calculated from the term. The orphans are
      load-bearing by selection. "Total Fee", "Promotion Date", "the Brief" — a contract can
      withhold and refund percentages of a Total Fee it never states

- [ ] **Every event that starts or stops a clock is defined.** List the clocks first — usage window, exclusivity window, payment clock, feed-retention obligation, revision turnaround, the Term itself — then the event at each end, then the clause defining that event. A blank in the third column is a finding
- [ ] **Lowercase phrases count.** A term does not have to be capitalized to be load-bearing; "live post" carries more weight in most influencer templates than any defined term in them, and gets no scrutiny because it reads like ordinary English
- [ ] **One idea, one phrase.** Variants scattered across body and exhibits ("live post" / "goes live" / "live post date" / "final content is live") mean a single definition has to cover all of them, or be made to, by conforming the language
- [ ] **Two clocks with one meaning are one clock.** If the creator's keep-up obligation and the
      brand's usage period are meant to be the same length, define one and reference it from the
      other ("for the Usage Period"). Two identically measured clocks written in different words
      invite an argument about whether they differ. **Only where the lengths already match.**
      A one-year keep-up obligation beside a sixty-day usage period is two clocks, not one:
      rewriting "at least (1) year" as "for the Usage Period" cuts the creator's obligation
      from a year to sixty days, silently unless the report says so. That is a commercial
      change — raise it, do not make it as a consistency fix
- [ ] **Syndication is not a new publication.** Where a usage period or a fee installment is
      triggered by "publication" of an asset that is syndicated to several platforms, say that
      initial publication is the first channel, and that later syndication of the same asset
      neither restarts the clock nor triggers another installment. A payment restructure the
      creator asked for can create this ambiguity on its own — check it after changing #19
- [ ] **Disclosure hashtags agree everywhere.** Schedules commonly disagree (#ad in one, #BrandPartner
      in another). Harmonise on "#ad and #[Brand]Partner (or such other FTC-compliant disclosure as
      Brand may request)" in every place. A bare partner tag is not FTC-sufficient on its own, so
      "both" is the compliant answer, not a concession — and it is a pure consistency fix
- [ ] **A duration with no stated start.** "must remain on the Influencer's primary feed for at least (1) year" — from when? Deliverable-level and exhibit-level obligations are where this hides, because exhibits are written as scoping notes rather than as contract language
- [ ] Where a term is defined in the body and used in an exhibit (or the reverse), the exhibit is actually incorporated so the definition reaches it

> Define only what the agreement uses. If paid usage is being contracted separately, defining it here is unnecessary and implies it belongs.

> Worked example. A contract grants organic usage "during the Term and for a period of 60 days after each live post thereafter" (§3(a)); ends the Term when "final content is live" (§11(a)); sets exclusivity three days before and after "live content" (§10); pays Net 60 "from the live posting date"; and requires a link-in-bio link to survive 30 days "after each live post date". Five clocks, one undefined event, five different phrasings of it. If the brand reads "live" as its own repost or as approval, every one of those windows starts on a date the creator does not control. The edit is one definition plus a conforming sweep — small, uncontroversial, and worth more than most of the rest of the redline.

### Cross-cutting: read the representations block against the rest of the checklist

Almost every item above has a counterpart buried in the representations and warranties — the long
roman-numeralled paragraph that reviewers skim because it looks like boilerplate. It is not
boilerplate. It re-legislates the same subjects, usually more broadly, and because the operative
clause reads acceptably the item gets marked **present** while the rep quietly governs.

The tell is that a rep states a fact rather than an obligation, so it binds on signature and has no
time limit unless one is written in. "Influencer has not committed and will not commit any act
which…" is breached by something that happened years before the deal existed.

Work back through the items and find each one's rep:

- [ ] **Exclusivity (#15).** The clause restricts "paid services" for three named competitors; rep
      (xx) restricts "any sponsorship, endorsement, promotional, marketing or advertising
      relationship" with any Competitor, and reaches backwards with "has not". The rep is the
      operative restriction, and the clause everyone negotiated is the decoy
- [ ] **Non-disparagement (#5).** Bounded "during the Term" in the conduct clause, unbounded in the
      rep — and the rep often extends to the brand's **competitors**, which no creator would agree
      to if asked directly
- [ ] **Content and IP (#6, #7).** Reps that the content is original and non-infringing are fine;
      reps that no content will contain anything "that can be construed as political" are a
      standing restriction on the creator's whole feed if the drafting does not confine them to the
      deliverables
- [ ] **[#reps-a]** **Anything the rep makes permanent.** A rep with no "during the Term" is
      forever. Adding those three words is the smallest edit in this file and often the largest
      one by effect. **List every rep and covenant with no end date and give each its own row** —
      fixing the morals rep does not fix the one below it. The FTC disclosure covenant is the one
      that gets left: "Influencer hereby agrees not to speak about or refer to Brand … without
      disclosing that Brand paid" binds every mention of the brand for life. Bound it to "during
      the Term and the usage period in Section 3(a)" — the usage period, because the disclosure
      exists for as long as the brand may run the endorsement. Limiting rep (v) can leave
      this one untouched behind a passing `#reps` label
- [ ] **Reps that restrict the creator's other work.** Union membership ("Influencer is not and
      shall not be a member of…"), other client relationships, platform exclusivity. These are
      career terms wearing a warranty's clothes, and they belong in the report even when the
      creator decides to accept them
- [ ] **Schedule reps with no clock.** The schedules carry reps too, and they escape this sweep
      because they read as brief notes. "Talent will promptly notify Brand if Talent's opinion of
      the products changes" is perpetual as drafted. Bound it to "during the Term and any Usage
      Period" — the one place the usage period rather than the Term is the right clock, because
      the rep exists for the FTC's live-endorsement purpose, and the endorsement stays live as long
      as the brand may run it

Conform the rep to the clause rather than negotiating the rep on its own terms. "Rep (xx) should
match the exclusivity you already agreed" is a one-line ask; renegotiating the rep from scratch is
a fight about a paragraph the brand considers standard.

---

## Nice-to-haves

### 17. Raw assets
- [ ] Deliverables limited to final approved assets (search "native files")
- [ ] Raw footage, outtakes, and project files remain the creator's property
- [ ] Separate licence and fee if the brand wants them

### 18. Late payment fees
- [ ] Interest on undisputed overdue amounts
- [ ] Right to suspend performance after a defined period

### 19. Up-front partial payment or rolling per-deliverable payment
- [ ] What triggers the final installment, and what share of the fee it carries
- [ ] Large analytics-contingent holdbacks restructured or reduced
- [ ] Any per-deliverable allocation reflects how the fee was actually built, not a flat division
- [ ] An installment triggered by publication says which publication — see #16 on syndication. A
      restructure to per-deliverable payment is where this ambiguity usually gets introduced

### 20. Net 30
- [ ] *(elective)* Payment term is net 30 or better. It costs the brand money and is the ask
      most often traded away, so it is a yes/no in the elective list — never part of a scope
      bundle. Putting "Net 60 → Net 30" inside "full mutuality" drafts it the moment the
      creator chooses that scope, for a creator who may already have declined it
- [ ] **What survives the payment.** This item checks *when* the creator is paid and never *how
      much arrives*. Each of these discounts an already-agreed rate and belongs in the report as
      what it is — a reduction in the fee, quantified: a processing or handling fee deducted at
      source ("2% of total payments shall be deducted in advance"), charges for a returned
      transfer borne by the creator, currency converted at the brand's own rate, and tax
      liability shifted wholesale ("the price includes all taxes", VAT registration and
      penalties passed down). **Self-billing is the one to flag hardest**: where the creator
      irrevocably authorises the brand to issue invoices on their behalf, the creator no longer
      holds the document they would use to dispute the amount
- [ ] **What starts the clock** — "any other documentation required by Company" lets the brand stop it indefinitely, and "net 60 from the live posting date" starts on an undefined event (see #16)
- [ ] **Pay-when-paid: reword it, do not try to delete it.** "Company has no obligation to pay
      Influencer unless Company receives payment from Client" makes the whole payment term
      conditional — the agency owes nothing until its own client pays, and nothing obliges the
      client to pay on any schedule. **Agencies do not give this up**, because they are not willing
      to carry their client's credit risk on a pass-through deal, and asking them to spends
      goodwill on the one item certain to be refused. Every sub-check below assumes the clause
      stays. Treat deletion as a fallback position to mention, not the edit to make
- [ ] **An outer date.** This is the sub-check that matters and the one most often granted: "in any
      event no later than ninety (90) days after publication, whether or not Company has received
      payment from Client." Without it the obligation may never mature at all. It is the difference
      between *pay-when-paid*, a timing term, and *pay-if-paid*, a condition precedent
- [ ] **A diligence obligation.** The agency must actually invoice its client within a stated
      period and pursue collection. Otherwise the condition is entirely within the hands of the
      party that benefits from it not occurring
- [ ] **The no-liability sentence is subordinated to the outer date** ("Subject to the foregoing,
      Influencer may not hold Company liable…"). A backstop the creator cannot enforce once it
      passes is decoration
- [ ] **"Will not be considered late" is struck.** A sentence deeming late payment not late removes
      the breach along with the deadline — no termination right, no interest, nothing to sue on.
      This one is separable from pay-when-paid itself and is usually conceded
- [ ] **The creator has a remedy against whoever actually holds the money.** Pay-when-paid is
      frequently paired with an instruction to look to the client instead ("Influencer may hold
      Client solely liable"), while the third-party-beneficiary clause runs one way — the client
      can enforce against the creator but the creator is given no rights against the client. Read
      the two together: separately each looks survivable, together they point the creator's only
      remedy at a party the contract gives them no standing to sue. The fix is to give the existing
      sentence effect rather than argue with it — an assignment of the agency's claim against its
      client up to the unpaid fee, plus making the third-party-beneficiary clause reciprocal for
      payment. Both are hard to refuse, because they only make the brand's own sentence work
- [ ] Any narrowing edit did not leave the original open-ended language in place beside it
- [ ] **Conditions that never fire or always fire.** "Subject to payment of amounts then due" on a
      delivery or handover obligation, in a net-30 structure, either blocks every routine request
      (something is always invoiced and not yet paid) or means nothing. Write delivery and
      handover conditions as "provided no undisputed amount is then **past due**"
- [ ] **The payment trigger is stated identically in the fee table and in the operative clause.**
      Template contracts state it twice — once in the defined-terms/fee row and once in the
      compensation paragraph — and a redline that fixes the paragraph and misses the row leaves the
      contract with two answers. The row is the one that reads like a settled commercial term, so
      it is the one the brand will point at

### 21. Whitelisting limits

> If the review resolves this by striking the grant, these sub-checks are **not** n/a — they are the
> fallback position. The brand may simply refuse to give the grant up, and the review should already
> know which of them is worth holding. Record it in the report as the fallback. Usually the one
> that survives is the authentication box: brands keep allowlisting and concede "that does not
> require Influencer and/or Lender to authenticate to third-party integrations".

- [ ] Allowlisting duration tied to the license term
- [ ] Targeting restrictions; no political or issue advertising
- [ ] No indefinite or evergreen advertising permissions
- [ ] Reporting on spend and placement
- [ ] **Third-party rights-management authentication** (rights-management platforms and equivalents) — check separately.
      Where the grant is kept on that condition, draft it with the defined term and the
      condition in separate sentences (#16's Allowlisting box), not as a parenthetical inside
      the grant
- [ ] **Remarketing / custom-audience list handover** — check separately; this reaches the creator's audience data

### 22. Generative AI clause

> Numbered among the nice-to-haves, and **offered on every deal** as a recommended addition, however
> small the fee and however short the form. It is one of the four asks the small-deal cut never
> removes (SKILL.md, *First*): the creator's likeness outlives the deal. Record it under
> **[#22a]** — present, drafted, or offered as recommended and declined — so the coverage gate
> sees it was raised.
- [ ] **Everyone who appears is covered, animals included.** Write the clause over "the Content
      or Influencer's Likeness (including the likeness of any person or animal appearing in the
      Content)", and bar replicas "of Influencer or of any such person or animal". On a pet
      account the animal is the talent, and a clause protecting only "Influencer" — the human
      party — leaves the face of the channel open to cloning
- [ ] Creator's likeness cannot be used as training data
- [ ] No synthetic replicas, voice clones, or digital doubles without separate consent
- [ ] **Flow-down** to agencies, vendors, and platforms
- [ ] Brand's permitted AI editing does not extend to materially altering the creator's
      appearance, voice, or statements. Where the brand is permitted to edit at all, #1 decides
      who carries the claim if an edit creates one

### 23. Release

> Numbered here to keep the numbering above stable. **Treat it with must-have weight wherever the
> contract contains a release** — it is among the most consequential clauses in an influencer
> agreement and among the least read, because it is written as boilerplate and sits near the
> signature block. A release given away here cannot be recovered by any edit made above it.

- [ ] **[#23a]** **The release is limited to authorized use.** A release covering all use of
      the creator's likeness releases the out-of-scope use that #10 and #1 exist to control.
      **Write "authorized use"** — "arising out of the authorized use of such Content by Brand" —
      rather than "in accordance with the rights granted in Section 3": it is two words, it is
      the form brands have accepted, and it cannot go stale when the grant moves. **It goes in
      every place the release reaches**: the release sentence *and* the waiver of injunctive
      relief beneath it ("(i) the authorized use of Content"). Scoping the first and leaving
      the waiver reaching all use means the creator still cannot stop an unlicensed campaign
- [ ] **Defamation is excluded.** Do not release defamation by default. A release that covers
      "any claim for defamation" means an edit that changes what the creator appears to say is
      not actionable — which is exactly the harm #22's AI clause and #1's alteration limb are
      aimed at
- [ ] **Right-of-publicity claims are excluded**, for the same reason: the release swallows the
      usage limits negotiated everywhere else
- [ ] **Injunctive relief is preserved for out-of-scope use.** Damages are an inadequate remedy
      for a likeness still running in a campaign the creator did not license; a waiver of
      equitable relief leaves nothing that can stop it
- [ ] **The released parties are a defined term.** "Brand and its affiliates, agents, licensees
      and assigns" with no definition releases people neither side can name
- [ ] Any §1542-style waiver of unknown claims is checked against all of the above — it extends
      each one to claims that do not exist yet

> **Where the contract's own drafter's note says release, COVID or assumption-of-risk provisions
> "should be removed" for self-produced content, strike the whole block and cite the note** in the
> cover note — it is the brand's instruction, not the creator's ask. Record the fallback (a release
> narrowed to exclude the released parties' negligence, with no §1542 waiver) in the tracking
> table, but do not draft it unless asked. No release beats a narrowed one, and drafting the
> fallback hands the brand a starting position.

### 24. Fee and scope certainty

> Also numbered out of order to keep existing references stable, and also a must-have. **Check
> it first, before anything above it.** Every other item on this list assumes the size of the
> deal is settled and asks what happens around it. None of them asks whether it is settled, so a
> contract can pass the entire checklist without ever stating what the creator is owed or how
> much work they are committing to.

- [ ] **A total fee appears somewhere.** A per-unit rate against an unbounded or
      brand-determined count is not a total. "Fee per dedicated video: USD 55.00" against
      "1-10 dedicated video(s)" is a contract whose value the creator cannot state
- [ ] **Terms that penalties are calculated from are defined.** Where a clause withholds,
      refunds or reduces a percentage of "the Total Fee", that term is doing arithmetic and has
      to have a value (see #16's orphan box)
- [ ] **The deliverable count is bounded by a stated maximum.** A range is a maximum; "as
      specified by Party A" is not
- [ ] **Quantity and scheduling are not set unilaterally after signature.** "The posting
      requirements and corresponding fees are solely determined by Party A's written
      instructions" is an open call on the creator's output, and pairing it with a penalty for
      missing those instructions makes the brand both the source of the obligation and the
      judge of the breach
- [ ] **One mechanism governs the schedule.** A campaign period, a set of mandatory windows and
      a flexible-adjustment clause that overrides both are three answers to the same question;
      the brand will rely on whichever the creator missed
- [ ] **The fee table and the operative clause agree** on the number and on the trigger (see #20)
- [ ] **Deliverable counts are unambiguous.** "6 videos syndicated across three platforms"
      reads as 6 or as 18, and the count multiplies the rate — this is the largest commercial
      term in the document, not a drafting nit
- [ ] **Every requirement sentence in the deliverables spec traces to the correspondence.**
      Compare the schedule against the scope email line by line, not term by term. Extra
      deliverables hide inside spec paragraphs — a "link in bio for 72 hours" can sit between
      the CTA and branded-content-tool sentences and pass a mismatch table that compares only
      fee, exclusivity and platforms. Each untraced **deliverable** goes in the mismatch table.
      Scope emails list deliverables, usage and rate, and almost never the reporting and
      administration around them — post analytics, disclosure mechanics, invoicing steps.
      Silence about those is not a mismatch; judge them on the checklist (an open-ended
      "at written request" tail is still a finding), not strike them for being unmentioned

---

## Outside the list — raise, do not add

Flag these to the creator and let them decide.

- **Releases that indemnify the brand for its own negligence.** Look for "regardless of whether caused by the negligence or willful or reckless misconduct" combined with a duty to defend and indemnify for those same claims. Usually paired with a §1542 waiver extending it to unknown claims. The release clause itself is on the list now — see #23; this bullet is only the indemnity-shaped corner of it.
- **Production and safety provisions that do not match the facts.** COVID-era assumption-of-risk language and cast-and-crew release requirements in a contract for self-shot content at home. Many such contracts contain their own instruction that these be removed when the work is self-produced — quote it back.
- **Personal guarantees and inducement riders** making an individual liable for their company's monetary obligations.
- **Remedies waivers** barring injunctive relief where damages would plainly be inadequate.
- **Forum and process asymmetry.** A binding-arbitration clause qualified by "unless otherwise
  indicated by Company" binds only the creator — the brand keeps the courts and the creator does
  not. Check who may elect, where the seat is (a clause seated in the brand's home city is a real
  cost on a five-figure deal), and whether prevailing-party fees turn a small dispute into an
  uninsurable one. **Raise it as a question; do not make it mutual as a core edit.** Making an
  exclusive venue in the brand's city bind both parties gains the creator little — the brand
  sues there anyway, and can no longer sue in the creator's home courts, which would have been
  cheaper for the creator.
- **Third-party beneficiary clauses that run one way.** The brand's client gets a direct claim
  against the creator; the creator gets no rights against the client. Harmless alone, serious
  beside pay-when-paid (#20).
- **Obligations on the creator's own account beyond the content.** Keeping comments enabled and
  unmoderated for months, keeping the account public for the term, or granting advertiser access to
  an ad account that holds unrelated business. These reach past the deliverable into how the
  creator runs their account, and a creator who manages ads for other clients may not be able to
  comply at all.
- **Insurance and production requirements that do not match self-shot content** — a term-length
  insurance covenant for a video filmed at home with a phone.
- **Schedules incorporated by reference but marked "reserved" or "subject to change"** — terms that do not exist yet but bind on arrival.
- **Drafting errors**: duplicated paragraphs, inconsistent entity names, residual text from another client's template, conflicting disclosure hashtags, and party swaps left half-done by the brand's own template — a creator termination right that fires "in the event that brand believes the contract is materially affected" hands the creator's exit to the brand. Fixing that one (to "Influencer believes") is a correction, and it belongs in the redline even though brands sometimes refuse it; record a refusal in `declined.md` like any other. **Edit a drafting error only when it changes what the contract means** — a half-done party swap, the wrong company or product (another company's name for the brand), an entity name that makes a clause point at nobody. **A wrong party name is never housekeeping**, however much it looks like a typo: trace where it lands first. "Other Co will provide key messages" can sit in the exhibit that decides who supplied the health claims — and the brand indemnity covers claims "supplied or approved by Brand". Left as "Other Co", the claims the creator most needs covered are supplied by someone the indemnity never names. It does not belong among the typos to mention. Everything else is raised in the report as a courtesy and left in the document: an identical sentence appearing twice, a typo whose meaning is obvious, a stray phrase that binds no one. Striking those adds lines to the redline and protects nothing (editing standards §6a). Deleting a confidentiality sentence from §12 because it duplicates §9 word for word leaves the contract meaning exactly the same thing afterwards. Where a duplicate paragraph *is* edited because it carries meaning, fixing one copy and leaving the other is worse than fixing neither.
