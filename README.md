# creator-contract-redline

A Claude Skill for redlining creator/influencer contracts on the creator's
behalf, applying every edit as a tracked (Suggested) change in the document so
the creator never has to touch it.

Brand-drafted influencer agreements are written to protect the brand, and most
of the one-sidedness is not malice — it is a template nobody rebalanced. The
skill reads the whole agreement including schedules, compares it against a
fixed checklist of terms that are commonly one-sided, and checks its own work
so no item is quietly dropped.

The result is a redlined `.docx` file that works fully in Google Docs and Word.
The skill only adds tracked suggestions and never silently rewrites the brand's
text, so the brand can accept or reject every change clause by clause.

The cheapest way is to upload a `.docx`. If the contract is a Google Doc, choose
**File → Download → Microsoft Word (.docx)** and upload that file. Claude can
also type the edits straight into a Google Doc in Suggesting mode during a
Claude in Chrome session, but that takes much longer and uses more of your
Claude usage.

> **Not legal advice.** This is a checklist and a set of editing tools, not a
> lawyer. It will be wrong sometimes. Read the redline before you send it and
> the contract before you sign it. See [DISCLAIMER.md](DISCLAIMER.md).

## Quick start

Nothing to install. Give an AI agent the link to this repository along with
the contract:

```
https://github.com/linktaps/creator-contract-redline
```

Attach the contract (a `.docx` works best) and ask something like *"Use the
skill at https://github.com/linktaps/creator-contract-redline to redline this
brand deal for me."*

Optional but helpful: also include anything you've already agreed with the
brand, such as the brief, the deliverables or rate, or emails and DMs about the
deal.

## Is this safe?

Don't take our word for it. Before you use it, have your AI look it over.
Paste this into a new chat:

> Before I use it, review the skill at
> https://github.com/linktaps/creator-contract-redline. Read the instructions
> and every script, and tell me in plain language what it does with my
> contract, whether it sends anything anywhere, and whether anything in it
> looks unsafe.

What it should find: the skill is plain-text instructions plus a few Python
scripts. The scripts use only Python's standard library, make no network
calls, and read and write only the files you give them. The skill tells the AI
never to send, email or share anything with the brand — it hands you the redline
and the cover note to send yourself — and never to upload the contract anywhere,
Google Docs included, without asking you first. The AI service you use does see it, though, which
is the next section.

## Is it legal to run my contract through an AI?

Usually yes, but check two things first. This isn't legal advice (see
[DISCLAIMER.md](DISCLAIMER.md#sharing-your-contract-with-an-ai-service)).

- **The contract's confidentiality clause.** Many brand deals say the terms
  are confidential, or that you can share them only with advisers such as a
  lawyer, agent or accountant. Uploading the contract to an AI service may
  count as sharing it with a third party. If the clause is strict, ask the
  brand, or remove the brand's name, the fee and other identifying details
  before you upload.
- **Your AI service's data terms.** Find out whether your chats are kept, for
  how long, and whether they're used to train models. Business and team plans
  often have stricter terms than personal ones. Turn off training on your
  chats if you can.

Also think before you upload other people's personal details, such as the
brand contact's email address or phone number in the emails and DMs you
include.

## Add it to the Claude desktop app

No coding needed. Takes about a minute, and after that Claude uses the skill
whenever you share a contract, without needing the link.

1. Open the Claude desktop app and go to **Settings → Plugins**.
2. Choose to add a marketplace, and paste this:
   ```
   linktaps/creator-contract-redline
   ```
3. Find **creator-contract-redline** in the list and click **Install**.
4. Start a new chat, attach the contract as a `.docx` (for a Google Doc, use
   **File → Download → Microsoft Word**), and ask
   something like *"Can you redline this brand deal for me?"*, adding any
   brief, deliverables, rate, emails or DMs about the deal.

Claude sends back a marked-up copy with every change as a suggestion the brand
can accept or reject. To get newer versions later, click **Update** on the same
Settings → Plugins screen.

## Install

**Claude Code**, as a plugin marketplace:

```
/plugin marketplace add linktaps/creator-contract-redline
/plugin install creator-contract-redline@creator-contract-redline
```

**Codex CLI**, from the same repository. Codex reads Claude-style marketplaces
directly:

```bash
codex plugin marketplace add https://github.com/linktaps/creator-contract-redline.git
codex plugin add creator-contract-redline@creator-contract-redline
```

Then invoke it as `$creator-contract-redline` in a new thread.

**As a standalone skill**, for either tool: clone anywhere and link the skill
directory into the folder the tool scans. Claude Code scans `~/.claude/skills`,
Codex scans `~/.agents/skills`.

```bash
git clone https://github.com/linktaps/creator-contract-redline.git
ln -s "$PWD/creator-contract-redline/skills/creator-contract-redline" ~/.agents/skills/
```

## How it works

Everything the skill uses lives in
[`skills/creator-contract-redline/`](skills/creator-contract-redline/): the
workflow in [`SKILL.md`](skills/creator-contract-redline/SKILL.md), the
checklist and editing standards in `references/`, and in `scripts/` the tools
that write the tracked changes and audit the finished redline. Each script
documents its own usage at the top of the file.

## License

[MIT](LICENSE).
