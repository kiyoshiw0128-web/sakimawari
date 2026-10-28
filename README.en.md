# sakimawari ("getting ahead of the question")

A Claude Code skill that, before you hand a document to someone, works out **where that reader will push back and what they will ask**. For each question it also proposes **how to fix the document** and **how to prepare an answer**. A version for Microsoft 365 Copilot agents is included.

> **Status: beta (0.1.0).**
> It has been tested on documents written by the author. **It has not yet been evaluated on questions that real managers or audiences actually asked.** Use it as an aid for catching blind spots, not as a guarantee of coverage. The skill and its documentation are written in Japanese; this page is a summary.

Japanese (full): [README.md](README.md)

## Why

The person who wrote a document tends to believe its flow is sound, because the assumptions that make it work live only in their head. They notice the gaps when somebody asks.

sakimawari re-reads the document from other viewpoints and finds the likely questions before you present. Every question comes with:

- the **quoted passage** the question comes from
- a **proposed rewrite** (where a fact is needed that the document lacks, it leaves a placeholder such as `【ここに〇〇】` and never invents one)
- an **answer preparation** outline for when you choose not to change the document

## How it extracts questions (summary)

A claim in a document is treated as a *defeasible inference* (Blair 1998). A **gap** is a place where nobody checked what would defeat the claim; a **question** asks for exactly that defeating condition. The full reasoning is in [docs/theory.md](docs/theory.md) (Japanese).

1. Extract claims; split each into Toulmin's six elements (claim, grounds, warrant, backing, qualifier, rebuttal) and look for missing elements.
2. Re-read from five viewpoints: sentence-level curiosity, a three-part test of each reason (acceptable, relevant, sufficient), role-by-role reading (approver, doer, affected person, skeptical expert), imagining that the plan failed a year later, and vague wording / unverifiable goals.
3. Classify each missing element into one of 16 types (leap in reasoning, missing comparison, unsourced number, hidden assumption, missing alternatives, scope gaps, internal inconsistency, problem–measure mismatch, missing execution details, over-claiming, missing purpose, vague wording, missing success criteria, cause/generalization errors, broken assumptions and side effects, undefined terms).
4. Drop a question if the document already answers it.
5. Assign a weight (high / medium / low) and filter: *if the reader could not answer, would their decision or their conviction change?* If not, the item is not raised. A document with no real gaps gets "no major gaps found".
6. Attach the proposed fix and the answer preparation.

## Install

Claude Code:

```bash
git clone https://github.com/kiyoshiw0128-web/sakimawari.git
mkdir -p ~/.claude/skills
cp -R sakimawari/skills/sakimawari ~/.claude/skills/sakimawari
```

Microsoft 365 Copilot: build `dist/sakimawari.zip` with `python3 scripts/build_copilot_zip.py` (the `dist/` directory is gitignored), paste `copilot/エージェント指示文.md` into the agent Instructions field, and upload the ZIP under Configure > Skills. If you cannot add a skill, paste `copilot/チャット貼り付け.md` into the chat box. A short Custom instructions text is in `copilot/カスタム指示.md`. Field names, character counts, and Microsoft docs are in [copilot/登録手順.md](copilot/登録手順.md) (Japanese).

## What the evidence does and does not show

- On 22 author-written documents (with seeded gaps, near-clean documents, and held-out documents), the skill found almost all seeded gaps (155/162 as top-level questions with Claude Sonnet) and stopped over-flagging clean notices and minutes.
- Adding the viewpoint techniques improved detection only slightly (a few percent, close to run-to-run variance).
- The literature behind each technique was checked to different depths (full text, abstract only, or secondary summaries only); see chapter 11 of [docs/theory.md](docs/theory.md). Several sources study news articles, requirements documents or student quizzes rather than workplace documents.
- Weaker models degrade formatting (overlong diagrams, quotation accuracy). Copilot's behaviour differs from Claude's and must be checked on the real product.

## Repository layout

`skills/sakimawari/` (the skill), `copilot/` (agent instructions and registration notes), `docs/` (theory and design record), `evals/` (test documents, ground truth, scripts, results), `scripts/` (ZIP build, validation).

## License

MIT License. See [LICENSE](LICENSE).
