# Query Modes — How Each Option Works

This guide covers the three options on the **Ask Your Library** page (and their
command-line equivalents), what each one actually changes in the pipeline,
which combinations make sense, and which are redundant.

---

## The three options at a glance

| Option | What it changes | Speed | Cost |
|---|---|---|---|
| **Research mode** | *How material is gathered* — multiple search angles instead of one | Slowest | Free (searches are always local) |
| **Deeper local model** | *Which local model writes the answer* — qwen3:14b instead of qwen3:8b | Slower | Free |
| **Cloud model** | *Where the final answer is written* — Anthropic or OpenAI instead of local | Fast | A few cents per query |

The key mental model: **Research mode changes the gathering step; the other
two change the writing step.** Gathering (embeddings, vector search,
reranking) is always local and free, no matter what you check — the only
thing that ever leaves your machine is the final synthesis call, and only
when Cloud is checked.

---

## Research mode

**What it does.** Instead of running one search on your question, it asks the
LLM to break your topic into several distinct search angles (a definition
angle, a contrast angle, a historical angle, a practical angle...), runs a
separate search for each, merges and dedupes the results, caps how many
passages any single book can contribute (so one large commentary can't crowd
out smaller books), and writes a **blog-ready draft** — introduction, themed
body, conclusion — rather than a Q&A-style answer.

**When to use it.** Broad topics you want to *write about*:

- "what does my library say about grace"
- "forgiveness in the old testament"
- "the role of women in the early church"

**When NOT to use it.** Specific references. Research mode **bypasses the
normal routing entirely** — no direct-chapter detection, no named-lookup
matching, no cross-links. If you ask "summarize Matthew chapter 2" with
Research checked, you get a thematic essay assembled from search angles, not
a summary of the actual chapter text. For anything with a book+chapter, a
person's name, a parable, or an event name, leave Research unchecked and let
the router do its job.

**Note:** in Research mode the deeper local model is used **automatically**
(research is already the slow, deliberate path), so the "deeper local model"
checkbox does nothing extra here.

---

## Use deeper local model

**What it does.** Swaps the local synthesis model from `qwen3:8b` (fast) to
`qwen3:14b` (better reasoning, slower). Nothing else changes — same routing,
same searches, same context.

**When to use it.** Questions where the *writing* is the hard part and you're
staying local: comparing how several books treat a topic, synthesizing
study notes, anything where the fast model's answers feel thin.

**When it does nothing:**
- **With Cloud checked** — the cloud model writes the answer; the local model
  choice is irrelevant.
- **With Research checked** — research already forces the deeper model.

So this checkbox only matters in exactly one configuration: normal mode,
local only.

---

## Use cloud model

**What it does.** Sends the final synthesis prompt (the retrieved excerpts +
your question + any format instructions) to a cloud API instead of the local
model. Everything else — embeddings, vector search, reranking, chapter
lookups — stays on your machine. This is the **only** step in the entire
pipeline that ever leaves your machine, and only when this box is checked.

**Provider dropdown:** Anthropic (Claude) or ChatGPT (OpenAI). Requires the
matching API key in `.env` (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY`). The
default provider comes from `CLOUD_PROVIDER` in `.env`; the dropdown
overrides it per-query.

**When to use it.** Anything you intend to publish or keep. Cloud output is
substantially better organized and better written than local output, for a
few cents per query. The house convention: **local for exploration and
debugging, cloud for anything publishable.**

---

## Combination matrix

| Research | Deep | Cloud | What you get | Verdict |
|:---:|:---:|:---:|---|---|
| ☐ | ☐ | ☐ | Normal routing, fast local model | Quick lookups, debugging routing |
| ☐ | ☑ | ☐ | Normal routing, deeper local model | Better free answers for hard questions |
| ☐ | ☐ | ☑ | Normal routing, cloud writes | **Best for chapter summaries, people, parables** |
| ☐ | ☑ | ☑ | Same as above — Deep is ignored | Redundant; uncheck Deep |
| ☑ | ☐ | ☐ | Multi-angle gather, deep local writes | Free drafts on broad topics |
| ☑ | ☑ | ☐ | Same as above — Deep is automatic | Redundant; uncheck Deep |
| ☑ | ☐ | ☑ | Multi-angle gather, cloud writes | **Best for publishable blog drafts** |
| ☑ | ☑ | ☑ | Same as above | Redundant; uncheck Deep |

The two configurations worth remembering:

- **Specific reference** (chapter, person, parable, event):
  Research ☐ + Cloud ☑
- **Broad topic for a blog post**:
  Research ☑ + Cloud ☑

---

## How routing works when Research is OFF

Normal mode routes your question through these checks, in order — the first
hit wins. The status line printed above the answer tells you which one fired:

1. **Direct chapter reference** — "Matthew chapter 2", "John 3", "Ruth 2".
   Summarizes the actual chapter text, then adds study notes from your other
   books. Status line: `(direct chapter reference: 'Matthew' chapter 2)`.
   This outranks everything else, so a chapter question can never be
   hijacked by a person who shares the book's name (Daniel, Ruth, Jonah...).
2. **Named lookup** — a person, parable, miracle, event, feast, covenant,
   location, or king from `library/lookups/`. People entries automatically
   pull in their cross-linked chapters (David brings Goliath, Bathsheba,
   Nathan, his covenant and Psalms). Status line: `(matched named
   reference ...)` or `Found: ... + N cross-linked entries`.
3. **Stored book summary** — "summarize <book>" with no chapter returns the
   book's pre-generated summary and themes instantly (no LLM call).
4. **Book-scoped search** — a book is named but nothing above matched:
   semantic search restricted to that book.
5. **Cross-library search** — nothing matched: semantic search over
   everything, answered with per-book attribution.

Research mode skips all five and goes straight to multi-angle gathering.

---

## Output format (the dropdown above the checkboxes)

Formats from `library/formats/*.txt` control **how the answer is written**,
never **what is searched**. Keep the question short and topical ("Ruth
chapter 3", "king david") and put structure/style requirements in the format
file. Formats combine with every mode. One quirk to know: with a format
selected, the stored-book-summary shortcut (#3 above) is skipped, since
there's no writing step to apply the format to.

---

## Command-line equivalents

```bash
# Normal mode, fast local model
python query.py "summarize Matthew chapter 2"

# Deeper local model
python query.py "how do these books differ on faith and works" --deep

# Cloud (default provider from .env)
python query.py "summarize Matthew chapter 2" --cloud

# Cloud with explicit provider
python query.py "king david" --cloud --provider openai

# Research mode (deep model automatic; add --cloud for best quality)
python query.py "grace in the old testament" --research --cloud

# Save any answer to library/answers/
python query.py "king david" --cloud --save
```

`writepost.py` is the blog-post front end: it defaults to **cloud on** and
always applies a format (auto-suggested from what matched). Use `--local` to
skip cloud, `--provider` to pick one, `--no-prompt` to accept the suggested
format without asking:

```bash
python writepost.py "king david" --format person_profile
python writepost.py "ruth chapter 3" --format bible_chapter_study
python writepost.py "what does my library say about grace"   # falls to research automatically
```

---

## Privacy summary

| Step | Where it runs |
|---|---|
| Embeddings, vector search, reranking | Always local |
| Chapter/lookup routing | Always local |
| Final answer writing | Local, unless Cloud is checked |
| What cloud sees when checked | Only the retrieved excerpts + your question + format instructions |
