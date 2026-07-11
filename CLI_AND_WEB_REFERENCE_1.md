# Book Intelligence — Full CLI & Web Reference

Every script in `src/` that runs from the command line, every flag it
accepts, and — where one exists — the exact web page and settings that
produce the same result. All CLI commands assume you're running from the
`src/` directory (`cd src` first); paths like `../library` are relative to
there.

**Quick answer if you only remember one thing:** only two scripts have a web
page at all — `query.py` (→ `/query`) and `writepost.py` (→ `/write`). Maps
have a *partial* web equivalent (view + regenerate with defaults only).
Everything else — imports, backups, restores, removing books, listing
chapters, book reports, top concepts, the raw pipeline — is **CLI-only**.
There's no hidden web page for them; if you want that functionality through
a browser, it would need to be built.

---

## Quick reference table

| Script | Purpose | Web equivalent |
|---|---|---|
| `query.py` | Ask a question across your library | `/query` — full equivalent |
| `writepost.py` | Generate a full blog post | `/write` — full equivalent |
| `knowledge_map.py` | Regenerate the concept map | `/maps` — **defaults only**, no flags |
| `book_map.py` | Regenerate the book-similarity map | `/maps` — **defaults only**, no flags |
| `list_books.py` | List books, optionally by status | None (index page lists books, but no status-only view without pagination) |
| `list_chapters.py` | List a book's stored chapter titles | None (book detail page shows chapters, but not standalone) |
| `book_report.py` | Print one book's stored summary/concepts | None (book detail page shows the same info) |
| `top_concepts.py` | List concepts by how many books share them | None |
| `remove_book.py` | Delete a book from Postgres + Qdrant | None — **CLI only, no confirmation UI** |
| `backup.py` | Back up Postgres + Qdrant (+ optionally library/config) | None |
| `restore.py` | Restore from a backup zip | None |
| `import_bible_json.py` | Bulk-import a folder of Bible JSON files | None |
| `pipeline.py` | Run the EPUB import pipeline (once or watching) | None (this **is** what powers new-book processing; the web UI only shows its *results*, on the homepage's import-jobs list) |

---

## `query.py` — Ask a question across your library

```bash
python query.py "QUESTION" [--deep] [--cloud] [--provider anthropic|openai]
                            [--research] [--max-total N] [--save [PATH]]
                            [--format PATH_OR_TEXT]
```

| Flag | Meaning | Web equivalent |
|---|---|---|
| `QUESTION` (positional, required) | The question to ask | The big text box at the top of `/query` |
| `--deep` | Use the larger/deeper local model (`LLM_MODEL_DEEP`) instead of the fast one. No effect if `--cloud` is also set (cloud writes the answer) or `--research` is set (research always uses the deep model). | Check **"Use deeper local model"** |
| `--cloud` | Send the final synthesis to a cloud provider instead of local. Everything upstream (search, rerank) stays local either way. | Check **"Use cloud model"** |
| `--provider anthropic\|openai` | Which cloud provider `--cloud` uses (overrides `CLOUD_PROVIDER` in `.env` for this one call). Ignored without `--cloud`. | The provider dropdown next to "Use cloud model" |
| `--research` | Broad-topic mode: expands the question into several search angles, merges/caps results across books, writes a blog-ready draft instead of a Q&A answer. Bypasses direct-chapter and named-lookup routing entirely. | Check **"Research mode"** |
| `--max-total N` | Research mode only — cap on total passages sent to the LLM, spread evenly across all matching books (default 40). | **Not exposed on the web page** — web research queries always use the default of 40 |
| `--save [PATH]` | Save the answer to a `.txt` file. Without a path: `../library/answers/<timestamp>_<question-slug>.txt`. With a path: saves there instead. | Click **"Download as .txt"** under the answer (saves to your browser's downloads, not into `library/answers/`) |
| `--format PATH_OR_TEXT` | Custom output structure — a path to a `.txt` file in `library/formats/`, or inline text. Changes *how* the answer is written; keep the question itself short and topical. | The **Output format** dropdown (pick a saved file from `library/formats/`), or expand **"Or paste a custom format instead"** to type/paste one inline |

**Examples:**

```bash
# Direct chapter, local, fast
python query.py "summarize Matthew chapter 2"

# Same, but cloud quality
python query.py "summarize Matthew chapter 2" --cloud

# Explicit provider
python query.py "king david" --cloud --provider openai

# Deeper local model for a hard synthesis question, no cloud cost
python query.py "how do these authors define grace differently" --deep

# Broad research topic, save the draft
python query.py "what does my library say about forgiveness" --research --cloud --save

# Custom format applied to a specific chapter
python query.py "ruth chapter 3" --format ../library/formats/devotional.txt --cloud
```

**Web equivalent of each example**, on `/query`:
1. Type the question, leave every checkbox unchecked.
2. Same, check **Use cloud model**.
3. Same, check **Use cloud model**, set provider dropdown to **ChatGPT (OpenAI)**.
4. Type the question, check **Use deeper local model** only.
5. Type the question, check **Research mode** and **Use cloud model**, click **Download as .txt** after.
6. Type `ruth chapter 3`, check **Use cloud model**, pick `devotional` in the **Output format** dropdown.

---

## `writepost.py` — Generate a full blog post

```bash
python writepost.py "TOPIC" [--format NAME] [--local]
                             [--provider anthropic|openai] [--no-prompt]
```

| Flag | Meaning | Web equivalent |
|---|---|---|
| `TOPIC` (positional, required) | Person, chapter, or broad topic to write about | The **Topic** field on `/write` |
| `--format NAME` | Format name from `library/formats/` (without `.txt`). Without it, you're asked interactively unless `--no-prompt`. | The **Format** dropdown |
| `--local` | Use the local model instead of cloud (free, lower quality). Default is cloud. | Uncheck **"Use cloud"** |
| `--provider anthropic\|openai` | Cloud provider to use (overrides `.env`). Ignored with `--local`. | The provider dropdown next to "Use cloud" |
| `--no-prompt` | Don't interactively ask which format to use — auto-pick the best guess. | N/A — the web page can't prompt interactively anyway, so it always behaves as if `--no-prompt` were passed |

**Examples:**

```bash
# Person profile, cloud (default), auto-picked format
python writepost.py "king david"

# Explicit format
python writepost.py "king david" --format person_profile

# Single chapter study
python writepost.py "ruth chapter 3" --format bible_chapter_study

# Broad topic — falls through to research mode automatically
python writepost.py "what does my library say about grace"

# Local only, no cloud cost
python writepost.py "king david" --local

# Explicit provider
python writepost.py "king david" --provider openai
```

**Web equivalent of each**, on `/write`:
1. Type `king david`, leave Format on its suggested default, leave **Use cloud** checked.
2. Type `king david`, pick `person_profile` in the Format dropdown.
3. Type `ruth chapter 3`, pick `bible_chapter_study`.
4. Type the topic, leave Format as default — it falls to research mode the same way.
5. Type `king david`, uncheck **Use cloud**.
6. Type `king david`, keep **Use cloud** checked, set provider to **ChatGPT (OpenAI)**.

Every `write_post()` run — CLI or web — always saves the finished post to
`library/answers/`, same as `--save` on `query.py` (this one isn't optional
the way it is for `query.py`).

---

## Maps — `knowledge_map.py` and `book_map.py`

These build the two HTML visualizations under `/maps`. The web page can
**view** existing maps and **regenerate** them, but only with default
settings — every flag below is CLI-only.

### `knowledge_map.py`

```bash
python knowledge_map.py [--output PATH] [--min-books N] [--style columns|network]
```

| Flag | Meaning | Web equivalent |
|---|---|---|
| `--output PATH` | Output HTML path (default `../library/knowledge_map.html`) | N/A |
| `--min-books N` | Only include concepts appearing in at least N books (default 1) | N/A — always 1 |
| `--style columns\|network` | `columns` (default): dropdown to focus on one concept at a time. `network`: physics-simulated graph showing everything at once — gets messy on a large library. | N/A — always `columns` |

Web equivalent: on `/maps`, click **Regenerate** under the Knowledge Map
section. This runs `python knowledge_map.py` with zero extra arguments —
identical to running it plain on the CLI with no flags.

### `book_map.py`

```bash
python book_map.py [--output PATH] [--threshold FLOAT] [--max-edges N]
                    [--publisher TEXT] [--title TEXT] [--label-edges]
                    [--cloud] [--model NAME] [--style columns|network]
```

| Flag | Meaning | Web equivalent |
|---|---|---|
| `--output PATH` | Output HTML path (default `library/book_map.html`, or `book_map_<filter>.html` if `--publisher`/`--title` is set) | N/A |
| `--threshold FLOAT` | Cosine similarity cutoff for "same theme" (0–1, higher = stricter). Default 0.78. | N/A |
| `--max-edges N` | Keep only each book's N strongest connections (default 4) — lower if the map is a hairball, raise (or 0 to disable) if too sparse | N/A |
| `--publisher TEXT` | Only include books whose publisher/version matches (e.g. `--publisher KJV`) | N/A |
| `--title TEXT` | Only include books whose title partially matches | N/A |
| `--label-edges` | Use the LLM to label each edge with the actual relationship (one LLM call per edge shown — slower) | N/A |
| `--cloud` | Use Anthropic for edge labeling instead of local (only relevant with `--label-edges`) | N/A |
| `--model NAME` | Local model for edge labeling (defaults to `LLM_MODEL_FAST`) | N/A |
| `--style columns\|network` | Same tradeoff as knowledge_map.py's `--style` | N/A — always `columns` |

Web equivalent: click **Regenerate** under the Book Map section on `/maps` —
runs with zero flags, same as calling it plain.

**If you want a filtered map (KJV-only, --label-edges, a stricter threshold,
etc.), you must run `book_map.py` on the command line** — there's no way to
pass those options through the web page today.

---

## CLI-only scripts (no web page exists)

### `list_books.py` — list books, optionally by status

```bash
python list_books.py [--status pending|processing|complete|failed|duplicate]
```

Closest web equivalent: the homepage (`/`) lists all books with search and a
status filter in the URL/dropdown, but it's paginated (10 per page) rather
than a flat list — useful for browsing, not for scripting.

### `list_chapters.py` — list a book's stored chapter titles

```bash
python list_chapters.py "TITLE"
```

`TITLE` is a partial book title match. Useful for finding the exact
`chapter_title` string `get_chunks_for_chapter()` needs when a chapter
lookup fails. The book detail page (`/book/<id>`) shows chapters too, but
only if you already know the book's ID/URL.

### `book_report.py` — print one book's stored summary + concepts

```bash
python book_report.py "TITLE"
```

Same information as the `/book/<id>` page, formatted for the terminal.

### `top_concepts.py` — list concepts by cross-book frequency

```bash
python top_concepts.py [--limit N] [--search TEXT] [--min-books N]
```

| Flag | Meaning |
|---|---|
| `--limit N` | How many to show (default 20) |
| `--search TEXT` | Only show concepts whose name contains this text, e.g. `--search parable` |
| `--min-books N` | Only show concepts appearing in at least N books (default 1) |

No web page. Closest thing is browsing the Knowledge Map's concept dropdown
manually.

### `remove_book.py` — delete a book from Postgres + Qdrant

```bash
python remove_book.py [TITLE] [--status STATUS] [--yes]
```

| Argument | Meaning |
|---|---|
| `TITLE` (optional) | Partial title to match |
| `--status ...` | Same five status choices as `list_books.py` |
| `--yes` | Skip the confirmation prompt |

**No web page — deliberately.** Deleting a book is destructive and
irreversible without a backup; there's no "Delete" button anywhere in the
UI, and adding one isn't recommended without careful confirmation handling.

### `backup.py` — back up Postgres + Qdrant

```bash
python backup.py [--output DIR] [--include-library] [--include-config]
```

| Flag | Meaning |
|---|---|
| `--output DIR` | Where to write the backup zip (default `../backups`) |
| `--include-library` | Also back up `library/` — your original EPUB/PDF files (the pipeline **moves** originals there on import, so this is the only remaining copy), covers, and generated maps. Off by default since it can be large. |
| `--include-config` | Also back up `.env`, `docker-compose.yml`, `requirements.txt` — needed for full disaster recovery since `.env` holds your API keys and isn't tracked anywhere else. **Puts a secret in the zip — store it securely if you use this flag.** |

No web page. Run this on a schedule (cron/Task Scheduler) rather than
relying on remembering to click something.

### `restore.py` — restore from a backup zip

```bash
python restore.py BACKUP_ZIP [--yes] [--skip-postgres] [--skip-qdrant]
                              [--skip-library] [--skip-config]
```

| Argument | Meaning |
|---|---|
| `BACKUP_ZIP` (required) | Path to a zip created by `backup.py` |
| `--yes` | Skip the confirmation prompt |
| `--skip-postgres` | Don't restore the Postgres dump |
| `--skip-qdrant` | Don't restore the vector collection |
| `--skip-library` | Don't restore `library/` contents |
| `--skip-config` | Don't restore `.env`/`docker-compose.yml`/`requirements.txt` |

No web page — this is a disaster-recovery tool, not a routine one.

### `import_bible_json.py` — bulk-import a folder of Bible JSON files

```bash
python import_bible_json.py BOOKS_DIR [--version LABEL]
```

| Argument | Meaning |
|---|---|
| `BOOKS_DIR` (required) | Path to the "books" folder — one subfolder per Bible book |
| `--version LABEL` | Translation label stored as the publisher field, e.g. `--version ASV` (default `"Bible"`) |

This is how your KJV (and any other translation) gets imported as 66
separate books in the first place. No web page — one-time/occasional setup
tool, not something you'd run from a browser.

### `pipeline.py` — the EPUB import engine

```bash
python pipeline.py --once     # scan incoming/ once and exit
python pipeline.py --watch    # watch incoming/ continuously
```

`--once` and `--watch` are mutually exclusive and one is required. This is
the actual engine that turns files dropped in `incoming/` into parsed,
chunked, embedded, summarized library entries — everything else (word
counts, chapter titles, book records) traces back to a `pipeline.py` run.
The homepage's **import jobs** list shows the *results* of pipeline runs
(status, stage, errors) but there's no button that starts one — you run
`--watch` in the background (or on a schedule) and drop files into
`incoming/` to trigger it.

---

## A note on what "no web equivalent" means in practice

Everything without a checkmark above isn't a gap waiting to be discovered —
it reflects a real design choice in this project: destructive operations
(`remove_book.py`, `restore.py`), infrastructure operations (`backup.py`,
`pipeline.py`, `import_bible_json.py`), and terminal-oriented lookup tools
(`list_books.py`, `list_chapters.py`, `book_report.py`, `top_concepts.py`)
were deliberately left as CLI-only. The web UI wraps the two things you use
repeatedly and casually — asking questions and writing posts — and leaves
the rarer, higher-stakes, or purely-diagnostic operations where a mistyped
click can't do damage.
