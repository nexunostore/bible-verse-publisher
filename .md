# Scripture Questions (WordPress plugin)

Admin-only tool that turns a typed Bible question into a draft study page. Exact KJV quotes are pulled from the site's own database (never typed by the AI). An editor reviews the draft and publishes it. Visitors cannot submit questions.

Public pages:

| URL | What it is |
|---|---|
| `/questions/` | Archive: searchable, filterable grid of all published questions |
| `/questions/<slug>/` | A single question/answer page |
| `/question-topic/<topic>/` | Topic archive (currently renders the same template as `/questions/`, see Known quirks) |

---

## Files

```
wp-content/plugins/<plugin-folder>/
├── scripture-questions.php      Main plugin file (all PHP logic)
└── templates/
    ├── common.php               Shared <head> extras (fonts + ALL CSS) and the hero banner
    ├── archive.php              Template for /questions/ and topic pages
    └── single.php               Template for one question page
```

### `scripture-questions.php`
Defines `SQ_DIR` (the plugin folder) and contains everything that is not a template:

1. **Content type + topics.** Registers the `sl_question` post type (archive slug `questions`) and the `sl_qtopic` taxonomy (slug `question-topic`). Activation/deactivation flush rewrite rules.
2. **Template routing.** A `template_include` filter sends `sl_question` archives and `sl_qtopic` pages to `templates/archive.php`, and single questions to `templates/single.php`. The theme's own templates are bypassed.
3. **Admin screen.** *Bible Questions → Ask a Question* (requires `manage_options`). An editor types a question (8 to 300 characters) plus optional writer guidance, and an AJAX call creates a **draft**.
4. **Generation (`sq_ajax_generate` / `sq_call_ai`).** Sends the question to the OpenAI chat completions API with a system prompt that forces a JSON response. Rejects duplicate questions (stored in post meta `_sq_question`).
5. **Bible helpers.** Look up books and KJV verses in the site's own tables, parse references like `Matthew 21:33-35`, build links to the Bible reader.
6. **Rendering (`sq_render_answer`).** Converts the AI's JSON into the page HTML saved as `post_content` (see "How a page is built").

### `templates/common.php`
- `sq_head_extras()` prints Google Fonts (EB Garamond, Inter) and **all the plugin's CSS** in one inline `<style>` block. The CSS covers the hero, the answer body, verse blockquotes, tables, lesson cards, and the archive (cards, search, topic filter).
- `sq_hero($eyebrow, $title, $intro)` prints the purple gradient banner with the site logo.

### `templates/archive.php`
- Queries up to 300 published questions, newest first.
- Search box + topic filter, both **client-side** (plain JS, no page reloads). Each card carries `data-topics` (term slugs) and `data-text` (lowercased title + excerpt).
- **Topic filter:** topics are sorted by question count. The top `$top_n` (default 6) show as buttons next to "All"; the rest are hidden behind a "More topics ▾" button. When a hidden topic is chosen, the "More topics" button turns active and shows that topic's name. Change the number of visible topics by editing `$top_n` at the top of the file.

### `templates/single.php`
- Hero with the question title, date + "All questions" link, `the_content()` (the saved answer HTML), then a footer with "More questions" and "Explore verse connections" buttons, topic chips, and the KJV/AI disclaimer.
- The "Explore verse connections" button only appears if a page with the slug `verse-refs` exists.

---

## How a page is created (end to end)

1. Admin opens **Bible Questions → Ask a Question** and submits a question.
2. `sq_ajax_generate` checks the nonce and capability, validates length, and rejects duplicates.
3. `sq_call_ai` asks the model for JSON: `title, summary, key_passages, sections, table, lessons, perspectives, takeaway, related, topics`. The prompt tells the model **never to type verses**, and to use tokens like `[[Matthew 21:38]]` instead (max 6 per page, ranges up to 6 verses within one chapter).
4. `sq_render_answer` builds the HTML. Each `[[Book C:V]]` token is replaced with the exact KJV text from the database (`sq_quote_html`). Plain references in text (e.g. `Isaiah 5:1-7`) are auto-linked to the Bible reader (`sq_linkify`).
5. A **draft** `sl_question` post is created (title, content, excerpt = summary) with up to 4 topic terms.
6. Post meta saved: `_sq_question` (original question), `_sq_ai` (flag), `_sq_missing` (verses not found in the DB).
7. The editor is redirected to the post editor. Notices appear: "AI-drafted page" and, if any, "Check these quoted verses" listing references that could not be found.
8. A human reviews/edits and presses **Publish**. Only then does it appear on `/questions/`.

### Answer HTML structure (what the CSS in `common.php` styles)

```
.sq-answer
  p.sq-lead                     summary
  p.sq-passages  (.sq-chip)     key passages
  .sq-sec > h2 + p/ul/blockquote.sq-verse
  .sq-tablewrap > table.sq-table   (optional)
  .sq-lessons > .sq-lesson (.sq-num, h3, text)
  .sq-note                      "Where readers differ"
  .sq-take                      "The takeaway"
  .sq-sec  "Keep reading" chips
```

The HTML is generated as a single line on purpose so WordPress's auto-paragraph filter doesn't inject stray `<p>` tags. Keep that in mind if editing the generator.

---

## Configuration (`wp-config.php`)

```php
define('OPENAI_API_KEY', '...');        // required
define('SQ_MODEL', 'model-name');       // optional; falls back to SCE_MODEL, then gpt-4.1-mini
define('SQ_STYLE_NOTES', 'extra writing instructions'); // optional; appended to the system prompt
```

## Dependencies outside this plugin

| Needed | Used for |
|---|---|
| DB tables `{prefix}bible_books` (`slug`, `name`) and `{prefix}bible_verses` (`version`, `book_slug`, `chapter`, `verse`, `text`) with `version = 'KJV'` rows | Verse quotes and reference linking |
| Theme/other plugin function `bsn_page_url_by_template('page-templates/bible-reader.php')` | URL of the Bible reader (falls back to `/read/`) |
| Theme function `bsn_logo_icon()` (optional) | Logo icon in the hero |
| A page with slug `verse-refs` (optional) | "Explore verse connections" button |
| OpenAI API access from the server | Draft generation |

---

## Common tasks

- **Edit the look:** all CSS lives in `sq_head_extras()` in `templates/common.php`.
- **Change how many topic buttons show:** `$top_n` in `templates/archive.php`.
- **Change the writing style or page structure:** the system prompt inside `sq_call_ai()` and the layout in `sq_render_answer()` (keep the JSON keys in sync between them).
- **Change the footer disclaimer or buttons:** `templates/single.php`.
- **After changing post type/taxonomy slugs:** go to Settings → Permalinks and click Save to flush rewrite rules.
- **Caching:** after deploying, purge any page cache/CDN; CSS and JS are inline in the templates, so stale cached pages show old styling.

## Known quirks / limitations

- **Topic pages show all questions.** `is_tax('sl_qtopic')` uses `archive.php`, which runs its own `WP_Query` for all questions instead of the topic being viewed. Clicking a topic chip on a single page therefore lands on a list that isn't filtered by that topic (the filter buttons on the page still work). A fix would be to read the queried term in `archive.php` and preselect it or filter the query.
- **300-question cap** on the archive. Beyond that, add pagination or switch to server-side search.
- Archive search and topic filtering are client-side and only see the 300 loaded cards.
- Generation takes 30 to 90 seconds; a slow or timing-out model shows an error in the admin screen and can simply be retried.
- Quotes come only from the KJV tables. If a reference can't be found it is listed in the draft's "Check these quoted verses" notice and rendered as plain text.
- The theme's own templates are bypassed for these pages; the plugin templates call `wp_head()` and `wp_footer()` themselves, so theme header/footer are not included.
